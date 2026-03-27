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

        borger = await self.hent_borger(cpr)

        if borger is not None:
            return borger
        
        endpoint = "/api/person"

        body = body

        body["CprNummer"] = cpr

        response = await self.client._post(endpoint, body)

        return response