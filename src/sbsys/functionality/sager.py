from sbsys.client import SbsysClient
from sbsys.models import Sag


class SagerClient:
    def __init__(self, client: SbsysClient):
        self.client = client

    async def hent_sager_på_borger(self, cpr:str) -> list[Sag]:
        cpr = self.client._format_cpr(cpr)
        endpoint = "api/sag/search"
        body = {
            "PrimaerPerson": 
                {"CprNummer": cpr}
            }
        response = await self.client._post(endpoint, body)
        return response["Results"]

    async def søg_sager(self, query: dict = {}) -> list[dict]:
        body = query
        endpoint = "api/sag/search"
        
        response = await self.client._post(endpoint, body)
        return response["Results"]
    
    async def opret_sag(self, part_id: int, sagsskabelon_id:int, sagsbehandler_id: int|None, sagstitel: str, borger_part:bool = True) -> dict:

        #Undersøg dette endpoint når vi har swagger
        endpoint = "api/v10/sag/template"

        part_type = "Person" if borger_part else "Firma"

        body = {
            "SagsTitel": sagstitel,
            "PrimaryPart": {
                "PartId": part_id, 
                "PartType": part_type
            },
            "Parts": [
                {
                    "PartId": part_id, 
                    "PartType": part_type
                }
            ],
            "SkabelonId": sagsskabelon_id,
        }
        if sagsbehandler_id:
            body["SagsbehandlerID"] = sagsbehandler_id

        return await self.client._post(endpoint, body)
    
    async def opdater_sag(self,  sags_id:str, query: dict) -> dict:
        endpoint = f"api/sag/{sags_id}"

        opdateret_sag = await self.client._put(endpoint, query)
        
        return opdateret_sag
    
    async def hent_statusliste_for_sager(self) -> dict:
        endpoint = "api/sag/sagStatusList"
        data = await self.client._get(endpoint)

        return data