from datetime import datetime

from sbsys.client import SbsysClient

class BorgerClient:
    def __init__(self, client: SbsysClient):
        self.client = client

    async def hent_borger(self, cpr:str) -> dict | None:
        endpoint = "api/person/search"
        
        body = {
            "CprNummer": cpr
        }

        response = await self.client._post(endpoint, body)

        if len(response) > 1:
            raise ValueError("Flere borgere fundet på cpr")
        elif len(response) < 1:
            return None

        return response[0]
    
    async def opret_borger(self, cpr:str, body:dict = {}) -> dict:
        """
        Opretter eller returnerer en borger baseret på CPR-nummer.
        
        Hvis borgeren allerede eksisterer i systemet, returneres den eksisterende borger.
        Hvis borgeren ikke eksisterer, oprettes en ny borger med det angivne CPR-nummer
        og eventuelle yderligere data fra body-parameteren.
        SBSYS synkronisere selv borger med info efter 24 timer. 
        
        Args:
            cpr (str): CPR-nummer på borgeren (påkrævet)
            body (dict): Yderligere data for borgeren (valgfrit, standard: tom dict)
            
        Returns:
            dict: Den oprettede eller eksisterende borger-objekt
        """

        if len(cpr) != 11 or cpr[6] != "-":
            raise ValueError("Ugyldigt cpr-format. Forventet DDMMYY-XXXX")

        if not cpr[:6].isdigit() or not cpr[7:].isdigit():
            raise ValueError("Ugyldigt cpr-format. Forventet DDMMYY-XXXX")

        try:
            datetime.strptime(cpr[:6], "%d%m%y")
        except ValueError as exc:
            raise ValueError("Ugyldig dato i cpr, kan være et midlertidig cppr") from exc
        
        
        
        borger = await self.hent_borger(cpr)

        if borger is not None:
            return borger
        
        endpoint = "/api/person"

        body = body

        body["CprNummer"] = cpr

        response = await self.client._post(endpoint, body)

        return response