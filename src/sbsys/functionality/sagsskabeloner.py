from sbsys.client import SbsysClient

class SkabelonClient:
    def __init__(self, client: SbsysClient):
        self.client = client

    async def hent_sagsskabeloner(self) -> dict:
        endpoint = "api/sagsskabelon"

        response = await self.client._get(endpoint)
        return response
    
    async def hent_sagsskabelon(self, skabelon_id:int) -> dict:
        endpoint = f"api/sagsskabelon/{skabelon_id}"

        response = await self.client._get(endpoint)

        return response

    