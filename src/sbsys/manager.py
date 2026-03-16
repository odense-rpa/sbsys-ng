"""
SbsysClientManager - A facade/factory for the SbSys client.

This manager simplifies instantiation by providing a single entry point
with lazy-loading, ensuring configuration is validated before the client
is created.
"""

from typing import Optional

from .client import SbsysClient
from .functionality.sager import SagerClient


class SbsysClientManager:
    """
    Manager til nem adgang til SbSys API-klienten.

    VIGTIGT: Brug altid denne manager i stedet for at oprette klienten direkte.
    Dette sikrer korrekt konfiguration og lazy loading.

    Eksempel::

        sbsys = SbsysClientManager(
            base_url="https://sbsyswebapi.example.dk",
            token_url="https://auth.example.dk/token",
            client_id="my-client",
            client_secret="secret",
            username="user",
            password="pass",
        )

        async with sbsys.client as client:
            sager = await client.hent_sager("0101011234")
    """

    def __init__(
        self,
        base_url: str,
        token_url: str,
        client_id: str,
        client_secret: str,
        username: str,
        password: str,
    ):
        """
        Initialise the SbsysClientManager.

        Args:
            base_url: Base URL for the SbSys REST API.
            token_url: Token endpoint for OAuth2 authentication.
            client_id: OAuth2 client ID.
            client_secret: OAuth2 client secret.
            username: Service account username.
            password: Service account password.
        """
        self._base_url = base_url
        self._token_url = token_url
        self._client_id = client_id
        self._client_secret = client_secret
        self._username = username
        self._password = password

        self._client: Optional[SbsysClient] = None
        self._sager_client: Optional[SagerClient] = None

    @property
    def client(self) -> SbsysClient:
        """Get the SbsysClient (lazy-loaded with configuration)."""
        if self._client is None:
            self._client = SbsysClient(
                base_url=self._base_url,
                token_url=self._token_url,
                client_id=self._client_id,
                client_secret=self._client_secret,
                username=self._username,
                password=self._password,
            )
        return self._client

    async def __aenter__(self) -> "SbsysClientManager":
        await self.client.__aenter__()
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.client.__aexit__(*args)

    @property
    def sager(self) -> SagerClient:
        if self._sager_client is None:
            self._sager_client = SagerClient(self.client)
        return self._sager_client
