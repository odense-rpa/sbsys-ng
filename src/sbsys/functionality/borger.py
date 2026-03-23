from sbsys.client import SbsysClient

class BorgerClient:
    def __init__(self, client: SbsysClient):
        self.client = client

    async def hent_borger(self, cpr:str) -> dict:
        endpoint = "api/person/search"
        
        body = {
            "CprNummer": cpr
        }

        response = await self.client._post(endpoint, body)

        if len(response) > 1:
            raise ValueError("Flere borgere fundet på cpr")

        return response[0]