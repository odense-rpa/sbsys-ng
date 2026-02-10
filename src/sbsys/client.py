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
from sbsys.models import (
    Bruger,
    Dokument,
    Erindring,
    Erindringstype,
    Journalarknote,
    Person,
    Sag,
    Sagspart,
    Skabelon,
    Status,
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
        self._http = httpx.AsyncClient()
        self._skabeloner: list[Skabelon] | None = None

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
        if response.status_code != 200:
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

    # ------------------------------------------------------------------
    # Bruger (users)
    # ------------------------------------------------------------------

    async def api_me(self) -> dict:
        """Get the currently authenticated user."""
        return await self._get(
            'api/bruger/me?model.select={"Brugernavn": "true", "Navn": "true"}'
        )

    async def soeg_brugere(
        self,
        navn: str = "",
        initialer: str = "",
    ) -> list[Bruger]:
        """Search for users by name and/or initials (LogonId)."""
        body: dict[str, str] = {}
        if initialer:
            body["LogonId"] = initialer
        if navn:
            body["Navn"] = navn

        data = await self._post("api/bruger/search", body)
        return [
            Bruger(
                id=row["Id"],
                uuid=row.get("Uuid", ""),
                initialer=row.get("LogonId", ""),
                navn=row.get("Navn", ""),
            )
            for row in data
        ]

    async def _find_bruger(self, brugernavn: str) -> Bruger:
        """Find a single user by LogonId. Raises if not exactly one match."""
        brugere = await self.soeg_brugere(initialer=brugernavn)
        if len(brugere) != 1:
            raise SbsysNotFoundError(
                f"Fandt {len(brugere)} brugere for brugernavn '{brugernavn}'"
            )
        return brugere[0]

    # ------------------------------------------------------------------
    # Sagsskabeloner (case templates)
    # ------------------------------------------------------------------

    async def _hent_sagsskabeloner(self) -> list[Skabelon]:
        """Fetch and cache all case templates."""
        if self._skabeloner is not None:
            return self._skabeloner

        data = await self._get("api/sagsskabelon")
        self._skabeloner = [
            Skabelon(
                id=row["Id"],
                navn=row.get("Navn", ""),
                aktiv=row.get("Aktiv", True),
                beskrivelse=row.get("Beskrivelse", ""),
                display_name=row.get("DisplayName", ""),
                sti=row.get("Sti", ""),
                sags_titel=row.get("SagsTitel", ""),
                identitet=row.get("SagSkabelonIdentity", ""),
                fagomraade_id=row.get("Fagomraade", {}).get("Id")
                if row.get("Fagomraade")
                else None,
                fagomraade=row.get("Fagomraade", {}).get("Navn", "")
                if row.get("Fagomraade")
                else "",
                skabelonsbruger=row.get("Bruger", {}).get("Navn", "")
                if row.get("Bruger")
                else "",
                skabelonsbruger_uuid=row.get("Bruger", {}).get("Uuid", "")
                if row.get("Bruger")
                else "",
                er_beskyttet=row.get("ErBeskyttet", False),
                er_stamdata_angivet=row.get("ErStamdataAngivet", False),
                anvend_sikkerhed_fra_ansaettelsessted=row.get(
                    "AnvendSikkerhedFraAnsaettelsessted", False
                ),
                part_anvend_ikke=row.get("PartAnvendIkke", False),
                part_forlang_altid=row.get("PartForlangAltid", False),
                part_forlang_altid_primaer=row.get("PartForlangAltidPrimaer", False),
            )
            for row in data
        ]
        return self._skabeloner

    async def hent_skabelon(self, skabelon_id: int) -> Skabelon:
        """Get a specific case template by ID."""
        skabeloner = await self._hent_sagsskabeloner()
        for s in skabeloner:
            if s.id == skabelon_id:
                return s
        raise SbsysNotFoundError(f"Skabelon med id {skabelon_id} ikke fundet")

    # ------------------------------------------------------------------
    # Sager (cases)
    # ------------------------------------------------------------------

    def _parse_sag(self, row: dict) -> Sag:
        skabelon = row.get("SagSkabelon") or {}
        fagomraade = row.get("Fagomraade") or {}
        primary_part = row.get("PrimaryPart") or {}
        return Sag(
            uuid=row.get("SagIdentity", ""),
            nummer=row.get("Nummer", ""),
            id=row.get("Id", 0),
            titel=row.get("SagsTitel", ""),
            oprettet=row.get("Opstaaet"),
            oprettet_af_id=row.get("OprettetAf", {}).get("LogonId", ""),
            oprettet_af_navn=row.get("OprettetAf", {}).get("Navn", ""),
            sidst_aendret=row.get("SenestAendret"),
            sidst_aendret_af_id=row.get("SenestAendretAf", {}).get("LogonId", ""),
            sidst_aendret_af_navn=row.get("SenestAendretAf", {}).get("Navn", ""),
            status=row.get("SagsStatus", {}).get("Navn", ""),
            tilstand=row.get("SagsStatus", {}).get("SagsTilstand", ""),
            status_kommentar=row.get("SagsStatus", {}).get("SagsStatusKommentar", ""),
            er_beskyttet=row.get("ErBeskyttet", False),
            er_besluttet=row.get("ErBesluttet", False),
            fagomraade=fagomraade.get("Navn", ""),
            skabelon_navn=skabelon.get("Navn", ""),
            skabelon_id=skabelon.get("Id"),
            primaer_parts_navn=primary_part.get("Navn", ""),
            primaer_parts_cpr=primary_part.get("CPRnummer", ""),
        )

    async def hent_sager(self, cpr: str) -> list[Sag]:
        """Fetch all cases for a person by CPR number."""
        formatted = self._format_cpr(cpr)
        data = await self._post(
            "api/sag/search",
            {"PrimaerPerson": {"CprNummer": formatted}, "Limit": 2000},
        )
        results = data.get("Results", data) if isinstance(data, dict) else data
        if isinstance(results, dict):
            results = [results]
        return list(reversed([self._parse_sag(row) for row in results]))

    async def _hent_sager_sagsnummer(self, nummer: str) -> list[Sag]:
        """Search for cases by case number (private)."""
        data = await self._post(
            "api/sag/search",
            {"Nummer": nummer, "Limit": 100},
        )
        results = data.get("Results", data) if isinstance(data, dict) else data
        if isinstance(results, dict):
            results = [results]
        return [self._parse_sag(row) for row in results]

    async def hent_sager_med_skabelonid(
        self,
        skabelon_id: int,
        *,
        limit: int = 5000,
    ) -> list[Sag]:
        """Fetch all cases matching a template ID, with pagination."""
        all_sager: list[Sag] = []
        skip = 0
        while True:
            data = await self._post(
                "api/sag/search?InkluderParterIResultat=true",
                {"SagsSkabeloner": [skabelon_id], "Limit": limit, "Skip": skip},
            )
            results = data.get("Results", data) if isinstance(data, dict) else data
            if isinstance(results, dict):
                results = [results]
            if not results:
                break
            all_sager.extend(self._parse_sag(row) for row in results)
            if len(results) < limit:
                break
            skip += limit
        all_sager.reverse()
        return all_sager

    async def hent_sager_med_skabelonid_indrejse(
        self,
        skabelon_id: int,
    ) -> list[Sag]:
        """Fetch immigration cases (unnamed primary person) for a template."""
        data = await self._post(
            "api/sag/search?InkluderParterIResultat=true",
            {
                "SagsSkabeloner": [skabelon_id],
                "PrimaerPerson": {"PersonNavn": "Unavngivet"},
                "Limit": 2000,
            },
        )
        results = data.get("Results", data) if isinstance(data, dict) else data
        if isinstance(results, dict):
            results = [results]
        return list(reversed([self._parse_sag(row) for row in results]))

    async def opret_sag(
        self,
        cpr: str,
        skabelon_id: int,
        sagsbehandler_initialer: str = "",
    ) -> Sag:
        """Create a new case from a template.

        Looks up the person by CPR, finds the template, and optionally
        assigns a case handler by initials.
        """
        formatted_cpr = self._format_cpr(cpr)

        # Find sagsbehandler if specified
        bruger_id = 0
        if sagsbehandler_initialer:
            bruger = await self._find_bruger(sagsbehandler_initialer)
            bruger_id = bruger.id

        # Get template
        skabelon = await self.hent_skabelon(skabelon_id)

        # Find person
        person = await self.hent_person(formatted_cpr)
        if person is None:
            raise SbsysNotFoundError(f"Person med CPR {formatted_cpr} ikke fundet")

        body: dict[str, Any] = {
            "SagsTitel": skabelon.sags_titel,
            "PrimaryPart": {"PartId": person.id, "PartType": "Person"},
            "Parts": [{"PartId": person.id, "PartType": "Person"}],
            "SkabelonId": skabelon_id,
        }
        if bruger_id:
            body["SagsbehandlerID"] = bruger_id

        data = await self._post("api/v10/sag/template", body)
        return self._parse_sag(data)

    async def opdater_sag(
        self,
        sags_uuid: str,
        sagstitel: str,
        bruger_uuid: str = "",
    ) -> dict:
        """Update a case's title and optionally its handler."""
        data = await self._get(f"api/sag/{sags_uuid}")

        if sagstitel:
            data["SagsTitel"] = sagstitel

        if bruger_uuid:
            bruger_data = await self._get(
                f"api/bruger/{bruger_uuid}?model.select="
                '{"Id": "true", "AnsaettelsesstedIdentity": "true", '
                '"Brugernavn": "true", "Navn": "true"}'
            )
            data["Behandler"] = bruger_data

        return await self._put(f"api/sag/{sags_uuid}", data)

    async def opdater_sag_v2(
        self,
        sags_uuid: str,
        sagstitel: str,
        bruger_uuid: str = "",
        ansaettelsessted: str = "",
    ) -> dict:
        """Update a case (v2) — title, handler, and employment place."""
        data = await self._get(f"api/sag/{sags_uuid}")

        if sagstitel:
            data["SagsTitel"] = sagstitel
        data["SagIdentity"] = sags_uuid

        if ansaettelsessted:
            alle_steder = await self._get("api/ansaettelsessted/alle")
            sted = next(
                (s for s in alle_steder if str(s.get("Id")) == str(ansaettelsessted)),
                None,
            )
            if sted:
                data.setdefault("Ansaettelsessted", {})["Id"] = sted["Id"]

        if bruger_uuid:
            data.setdefault("Behandler", {})["Uuid"] = bruger_uuid

        return await self._put(f"api/sag/{sags_uuid}", data)

    async def opdater_sagsstatus(
        self,
        sags_uuid: str,
        status: str,
        kommentar: str = "Opdateret af Tyra",
    ) -> bool:
        """Update the status of a case by status name."""
        statusliste = await self.hent_statusliste()
        match = next((s for s in statusliste if s.status == status), None)
        if match is None:
            raise SbsysNotFoundError(f"Status '{status}' ikke fundet")

        await self._put(
            f"api/sag/{sags_uuid}/status",
            {"SagsStatusID": match.id, "Kommentar": kommentar},
        )
        return True

    # ------------------------------------------------------------------
    # Sagsparter (case parties)
    # ------------------------------------------------------------------

    async def hent_sagsparter(self, sag_uuid: str) -> list[Sagspart]:
        """Get all parties on a case."""
        data = await self._get(f"api/sag/{sag_uuid}/part")
        return [
            Sagspart(
                id=row.get("Id", 0),
                type=row.get("PartType", ""),
                cvr=row.get("CVRnummer", ""),
                cpr=row.get("CPRnummer", ""),
                navn=row.get("Navn", ""),
            )
            for row in data
        ]

    async def tilfoej_sagspart(
        self,
        sag_uuid: str,
        person_id: int,
        cpr: str,
        navn: str,
    ) -> bool:
        """Add a person as a party to a case.

        First checks if the person (by CPR) is already a party.
        Returns True if the party was added or already existed.
        """
        formatted_cpr = self._format_cpr(cpr)

        # Check existing parties
        parter = await self.hent_sagsparter(sag_uuid)
        for part in parter:
            if part.cpr == formatted_cpr:
                return True

        # Add new party
        body = {
            "PartId": person_id,
            "PartType": "Person",
            "CPRnummer": formatted_cpr,
            "Navn": navn,
        }
        result = await self._post(f"api/sag/{sag_uuid}/part", body)
        return "true" in str(result).lower() if result else True

    # ------------------------------------------------------------------
    # Dokumenter (documents)
    # ------------------------------------------------------------------

    async def hent_dokumenter(self, sag_uuid: str) -> list[Dokument]:
        """Get document metadata for a case."""
        data = await self._get(f"api/sag/{sag_uuid}/dokumenter")
        return [
            Dokument(
                uuid=row.get("DokumentIdentity", ""),
                navn=row.get("DokumentNavn", ""),
                registrerings_dato=row.get("RegistreringsDato", ""),
                registreret_af_id=row.get("Behandler", {}).get("LogonId", ""),
                registreret_af_navn=row.get("Behandler", {}).get("Navn", ""),
            )
            for row in data
        ]

    # ------------------------------------------------------------------
    # Journalarknoter (journal notes)
    # ------------------------------------------------------------------

    async def hent_journalarknoter(self, sag_uuid: str) -> list[Journalarknote]:
        """Get journal notes for a case."""
        data = await self._get(f"api/sag/{sag_uuid}/journalarknotes")
        return [
            Journalarknote(
                uuid=row.get("Uuid", ""),
                overskrift=row.get("Overskrift", ""),
                indhold=row.get("Note", ""),
                oprettet_dato=row.get("Oprettet", ""),
                oprettet_af_id=row.get("OprettetAf", {}).get("LogonId", "")
                if row.get("OprettetAf")
                else "",
                oprettet_af_navn=row.get("OprettetAf", {}).get("Navn", "")
                if row.get("OprettetAf")
                else "",
            )
            for row in data
        ]

    async def opret_journalarknote(
        self,
        sag_uuid: str,
        sags_id: int,
        overskrift: str,
        indhold: str,
    ) -> dict:
        """Create a journal note on a case."""
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.Z")
        note_content = indhold.replace("\n", "<br />")
        body = {
            "Uuid": sag_uuid,
            "SagID": sags_id,
            "Overskrift": overskrift,
            "Note": note_content,
            "KontaktTidspunkt": now,
        }
        return await self._post("api/journalarknote/create", body)

    async def opret_journalarknote_v2(
        self,
        cpr: str,
        overskrift: str,
        indledning: str,
        skabelon_id: int,
        data: list[dict[str, str]] | None = None,
        afslutning: str = "",
    ) -> dict:
        """Create a journal note on the open case matching a template.

        Builds an HTML body from introduction, optional data table, and
        optional closing text. Finds the matching open case by CPR and
        template ID.
        """
        formatted_cpr = self._format_cpr(cpr)
        sager = await self.hent_sager(formatted_cpr)

        # Find the matching open case
        sag = next(
            (
                s
                for s in sager
                if s.skabelon_id == skabelon_id
                and s.tilstand != "Afsluttet"
                and s.status != "Afsluttet"
            ),
            None,
        )
        if sag is None:
            raise SbsysNotFoundError("Korrekt sag ikke fundet")

        # Build HTML content
        content = _build_journal_html(indledning, data, afslutning)
        return await self.opret_journalarknote(sag.uuid, sag.id, overskrift, content)

    # ------------------------------------------------------------------
    # Person
    # ------------------------------------------------------------------

    async def hent_person(self, cpr: str) -> Person | None:
        """Search for a person by CPR. Returns None if not found."""
        formatted = self._format_cpr(cpr)
        data = await self._post("api/person/search", {"CprNummer": formatted})
        if not data:
            return None
        results = data if isinstance(data, list) else [data]
        if not results:
            return None
        row = results[0]
        return Person(
            id=row.get("Id", 0),
            uuid=row.get("Uuid", row.get("PersonIdentity", "")),
            navn=row.get("Navn", ""),
            cpr=row.get("CprNummer", ""),
        )

    async def opret_person(self, cpr: str) -> bool:
        """Create a person by CPR if they don't already exist.

        Returns True if the person was created, False if they already existed.
        """
        formatted = self._format_cpr(cpr)
        existing = await self.hent_person(formatted)
        if existing is not None:
            return False

        await self._post("api/person", {"CprNummer": formatted})
        return True

    # ------------------------------------------------------------------
    # Statusliste
    # ------------------------------------------------------------------

    async def hent_statusliste(self) -> list[Status]:
        """Fetch the list of available case statuses."""
        data = await self._get("api/sag/sagStatusList")
        return [
            Status(
                id=row.get("Id", 0),
                status=row.get("Navn", ""),
                tilstand=row.get("SagsTilstand", ""),
                kraever_kommentarer=row.get("KraeverKommentarer", False),
            )
            for row in data
        ]

    # ------------------------------------------------------------------
    # Erindringer (reminders)
    # ------------------------------------------------------------------

    async def hent_erindringer(self, sags_id: int) -> list[Erindring]:
        """Get reminders for a case."""
        data = await self._get(f"api/erindring/sag/{sags_id}")
        if isinstance(data, dict):
            data = [data]
        return [
            Erindring(
                har_deadline=row.get("HarDeadline", False),
                deadline=row.get("Deadline", ""),
                deadline_status=row.get("DeadlineStatus", ""),
                synlig_fra=row.get("SynligFra", ""),
                sag_id=row.get("SagId", 0),
                navn=row.get("Navn", ""),
                beskrivelse=row.get("Beskrivelse", ""),
                er_afsluttet=row.get("ErAfsluttet", False),
                erindring_type=row.get("ErindringType", {}),
                ansvarlig=row.get("Ansvarlig", {}),
                opretter=row.get("Opretter", {}),
            )
            for row in data
        ]

    async def _hent_erindringstype(self, navn: str) -> Erindringstype:
        """Find a reminder type by name."""
        data = await self._get("api/erindring/typer")
        match = next((row for row in data if row.get("Navn") == navn), None)
        if match is None:
            raise SbsysNotFoundError(f"Erindringstype '{navn}' ikke fundet")
        return Erindringstype(
            id=match["Id"],
            navn=match.get("Navn", ""),
            display_name=match.get("DisplayName", ""),
            synlighed_i_dage=match.get("SynlighedIDage", 0),
            deadline_i_dage=match.get("DeadlineIDage", 0),
            skjul_erindring=match.get("SkjulErindring", False),
        )

    async def opret_erindring(
        self,
        sags_id: int,
        navn: str,
        beskrivelse: str,
        ansvarlig_brugernavn: str,
        erindringstype_navn: str,
        deadline: datetime | None = None,
        synlig_fra: datetime | None = None,
    ) -> dict:
        """Create a reminder on a case.

        The responsible user is looked up by LogonId (brugernavn).
        The reminder type is looked up by name.
        """
        bruger = await self._find_bruger(ansvarlig_brugernavn)
        ertype = await self._hent_erindringstype(erindringstype_navn)

        body: dict[str, Any] = {
            "SagId": sags_id,
            "ErindringType": {"Id": ertype.id},
            "Beskrivelse": beskrivelse,
            "Navn": navn,
            "Ansvarlig": {"Id": bruger.id},
            "Opretter": {"Id": bruger.id},
        }

        if deadline is not None:
            body["HarDeadline"] = True
            body["Deadline"] = deadline.strftime("%Y-%m-%d %H:%M:%S")
        else:
            body["HarDeadline"] = False
            body["Deadline"] = ""

        if synlig_fra is not None:
            body["SynligFra"] = synlig_fra.strftime("%Y-%m-%d %H:%M:%S")
        else:
            body["SynligFra"] = ""

        return await self._post("api/erindring", body)


# ------------------------------------------------------------------
# Module-level helpers
# ------------------------------------------------------------------


def _build_journal_html(
    indledning: str,
    data: list[dict[str, str]] | None,
    afslutning: str,
) -> str:
    """Build HTML content for a journal note from parts."""
    parts: list[str] = []

    if indledning.strip():
        parts.append(indledning.strip())

    if data:
        columns = list(data[0].keys()) if data else []
        table = '<table style="border: 1px solid black; border-collapse:collapse;">'
        table += "<tr>"
        for col in columns:
            table += (
                '<th style="text-align: left; padding: 0px 10px; '
                f'border: 1px solid black;">{col}</th>'
            )
        table += "</tr>"
        for row in data:
            row_content = "".join(str(row.get(c, "")) for c in columns)
            if row_content.strip():
                table += "<tr>"
                for col in columns:
                    table += (
                        '<td style="padding: 0px 10px; '
                        f'border: 1px solid black;">{row.get(col, "")}</td>'
                    )
                table += "</tr>"
            else:
                # Empty rows become spacer rows
                for _ in range(2):
                    table += "<tr>"
                    for _ in columns:
                        table += "<td></td>"
                    table += "</tr>"
        table += "</table>"
        parts.append(table)

    if afslutning.strip():
        parts.append(afslutning.strip())

    return "<br /><br />".join(parts)
