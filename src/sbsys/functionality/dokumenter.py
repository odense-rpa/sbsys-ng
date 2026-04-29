from sbsys.client import SbsysClient

class DokumenterClient:
    def __init__(self, client: SbsysClient):
        self.client = client
    
    async def hent_dokumenter_på_sag(self, sags_id: str) -> list[dict]:
        endpoint = f"/api/sag/{sags_id}/dokumenter"
        
        response = await self.client._get(endpoint)
        
        return response
    
    async def hent_dokument_og_underdokumenter(self, dokument_id: str) -> dict:
        endpoint = f"/api/dokument/{dokument_id}"
        
        response = await self.client._get(endpoint)
        
        return response