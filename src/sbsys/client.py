from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

import httpx

from sbsys.exceptions import (
    SbsysAuthenticationError,
    SbsysNotFoundError,
    SbsysValidationError,
)


_CPR_RE = re.compile(r"^(\d{6})-?(\d{4})$")


class SbsysClient:
    """Async client for the SbSys case management REST API."""

    def __init__(
        self,
        base_url: str,
        token_url: str,
        client_id: str,
        client_secret: str,
        username: str,
        password: str,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._token_url = token_url
        self._client_id = client_id
        self._client_secret = client_secret
        self._username = username
        self._password = password
        self._token: str = ""
        self._token_expires: datetime = datetime(2000, 1, 1, tzinfo=timezone.utc)
        self._http = httpx.AsyncClient(verify=False, timeout=30.0)

    # ------------------------------------------------------------------
    # Context manager
    # ------------------------------------------------------------------

    async def __aenter__(self) -> SbsysClient:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self._http.aclose()

    # ------------------------------------------------------------------
    # Token management
    # ------------------------------------------------------------------

    async def _get_token(self) -> None:
        now = datetime.now(timezone.utc)
        if self._token and now < self._token_expires:
            return

        response = await self._http.post(
            self._token_url,
            data={
                "grant_type": "password",
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "username": self._username,
                "password": self._password,
            },
        )
        content_type = response.headers.get("content-type", "")
        if response.status_code != 200 or "json" not in content_type:
            raise SbsysAuthenticationError(
                f"Token request failed ({response.status_code}): {response.text}"
            )

        data = response.json()
        self._token = data["access_token"]
        expires_in = int(data.get("expires_in", 3600))
        from datetime import timedelta

        self._token_expires = now + timedelta(seconds=expires_in - 60)

    # ------------------------------------------------------------------
    # HTTP helpers
    # ------------------------------------------------------------------

    async def _get(self, path: str) -> Any:
        await self._get_token()
        response = await self._http.get(
            f"{self._base_url}/{path}",
            headers={
                "Authorization": f"Bearer {self._token}",
                "Accept": "application/json",
            },
        )
        response.raise_for_status()
        return response.json()

    async def _post(self, path: str, body: dict | list | None = None) -> Any:
        await self._get_token()
        response = await self._http.post(
            f"{self._base_url}/{path}",
            json=body,
            headers={
                "Authorization": f"Bearer {self._token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        )
        response.raise_for_status()
        if response.headers.get("content-type", "").startswith("application/json"):
            return response.json()
        return response.text

    async def _put(self, path: str, body: dict | None = None) -> Any:
        await self._get_token()
        response = await self._http.put(
            f"{self._base_url}/{path}",
            json=body,
            headers={
                "Authorization": f"Bearer {self._token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        )
        response.raise_for_status()
        if response.headers.get("content-type", "").startswith("application/json"):
            return response.json()
        return response.text

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    @staticmethod
    def _format_cpr(cpr: str) -> str:
        """Ensure CPR is in DDMMYY-NNNN format."""
        m = _CPR_RE.match(cpr.strip())
        if not m:
            raise SbsysValidationError(f"Ugyldigt CPR-nummer: {cpr}")
        return f"{m.group(1)}-{m.group(2)}"