from datetime import datetime

from sbsys.client import SbsysClient
from sbsys.functionality.bruger import BrugerClient
from sbsys.exceptions import SbsysNotFoundError

DATO_FORMAT = "%Y-%m-%d %H:%M:%S"


class ErinderingerClient:
    def __init__(self, client: SbsysClient):
        self.client = client
        
    async def hent_erindring(self, erindrings_id: str) -> dict:
        """
        Henter en enkelt erindring ud fra dens ID.

        Args:
            erindrings_id (str): ID på den erindring, der skal hentes.

        Returns:
            dict: Den fundne erindring, som returneres fra SBSYS API'et.
        """
        endpoint = f"/api/erindring/{erindrings_id}"
        
        reponse = await self.client._get(endpoint)
        
        return reponse
        
    async def hent_erindringer_på_sag(self, sags_id: str) -> dict:
        """
        Henter alle erindringer tilknyttet en given sag.

        Args:
            sags_id (str): ID på den sag, hvis erindringer skal hentes.

        Returns:
            dict: Erindringerne tilknyttet sagen, som returneres fra SBSYS API'et.
        """
        endpoint = f"/api/erindring/sag/{sags_id}"
        
        response = await self.client._get(endpoint)
        
        return response
    
    async def hent_erindringstyper(self) -> list[dict]:
        """
        Henter alle tilgængelige erindringstyper.

        Returns:
            list[dict]: En liste af erindringstyper, som returneres fra SBSYS API'et.
        """
        endpoint = "/api/erindring/typer"
        
        response = await self.client._get(endpoint)
        
        return response
    
    async def opdater_erindring(self, erindrings_id: str, body: dict) -> dict:
        
        endpoint = f"/api/erindring/{erindrings_id}"
        
        erindring = await self.hent_erindring(erindrings_id)
        
        if erindring is None or erindring == []:
            raise SbsysNotFoundError("Erindring ikke fundet")
        
        for key in body:
            if key in erindring:
                erindring[key] = body[key]
            else:
                raise ValueError(f"Fejl {key} feltet kan ikke findes på erindringen")

        opdateret_erindring = await self.client._put(endpoint, erindring)
        
        return opdateret_erindring

    async def opret_erindring(
        self,
        sags_id: str,
        navn: str,
        beskrivelse: str,
        erindringstype: str,
        ansvarlig_navn: str,
        deadline: datetime | None = None,
        synlig_fra: datetime | None = None,
    ) -> dict:
        """
        Opretter en ny erindring på en sag.

        Args:
            sags_id (str): ID på den sag, erindringen oprettes på.
            navn (str): Erindringens navn.
            beskrivelse (str): Erindringens beskrivelsestekst.
            erindringstype (str): Navn på erindringstypen (se hent_erindringstyper).
            ansvarlig_navn (str): Navn på den bruger, der er ansvarlig for erindringen.
            deadline (datetime | None): Deadline. Ingen deadline hvis None.
            synlig_fra (datetime | None): Synlig fra. Ingen dato hvis None.

        Returns:
            dict: Den oprettede erindring, som returneres fra SBSYS API'et.

        Raises:
            SbsysNotFoundError: Hvis ansvarlig eller erindringstypen ikke findes.
            ValueError: Hvis navnet på ansvarlig ikke er entydigt.
        """
        endpoint = "api/erindring"

        bruger_client = BrugerClient(self.client)

        brugere = await bruger_client.find_brugere(navn=ansvarlig_navn)
        matches = [b for b in brugere if b.get("Navn") == ansvarlig_navn] or brugere

        if not matches:
            raise SbsysNotFoundError(f"Bruger '{ansvarlig_navn}' ikke fundet")
        if len(matches) > 1:
            raise ValueError(f"Navnet '{ansvarlig_navn}' er ikke entydigt ({len(matches)} brugere fundet)")

        typer = await self.hent_erindringstyper()
        type_match = next(
            (t for t in typer if t.get("Navn", "").casefold() == erindringstype.casefold()),
            None,
        )

        if type_match is None:
            raise SbsysNotFoundError(f"Erindringstype '{erindringstype}' ikke fundet")

        opretter = await bruger_client.api_me()

        body = {
            "HarDeadline": deadline is not None,
            "Deadline": deadline.strftime(DATO_FORMAT) if deadline else None,
            "SynligFra": synlig_fra.strftime(DATO_FORMAT) if synlig_fra else None,
            "Ansvarlig": {"Id": matches[0]["Id"]},
            "Opretter": {"Id": opretter["Id"]},
            "SagId": sags_id,
            "ErindringType": {"Id": type_match["Id"]},
            "Beskrivelse": beskrivelse,
            "Navn": navn,
        }

        return await self.client._post(endpoint, body)
