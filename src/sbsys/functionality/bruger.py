from sbsys.client import SbsysClient

class BrugerClient:
    def __init__(self, client: SbsysClient):
        self.client = client
    
    async def api_me(self) -> dict:
        endpoint = "api/bruger/me?model.select={'Brugernavn': 'true', 'Navn': 'true'}"

        return await self.client._get(endpoint)
    
    async def hent_bruger(self, uuid:str) -> dict:
        endpoint = f"api/bruger/{uuid}"

        return await self.client._get(endpoint)
    
    async def find_brugere(self, initialer:str = "", navn:str ="") -> dict:
        endpont = "api/bruger/search"

        if initialer == "" and navn == "":
            raise ValueError("Ingen værdier givet at søge på")

        body = {
        }

        if initialer != "":
            body["LogonId"] = initialer

        if navn != "":
            body["Navn"] = navn

        return await self.client._post(endpont,body)
        