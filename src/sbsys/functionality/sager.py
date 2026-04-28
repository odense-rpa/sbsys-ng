from sbsys.client import SbsysClient
from sbsys.exceptions import SbsysValidationError


class SagerClient:
    def __init__(self, client: SbsysClient):
        self.client = client

    async def hent_sager_på_borger(self, cpr:str) -> list[dict]:
        cpr = self.client._format_cpr(cpr)
        endpoint = "api/sag/search"
        body = {
            "PrimaerPerson": 
                {"CprNummer": cpr}
            }
        response = await self.client._post(endpoint, body)
        return response["Results"]
    
    async def hent_sag(self, sags_id:str) -> dict:
        endpoint = f"api/sag/{sags_id}"

        response = await self.client._get(endpoint)

        return response

    async def søg_sager(self, query: dict = {}) -> list[dict]:
        body = query
        endpoint = "api/sag/search"
        
        response = await self.client._post(endpoint, body)
        return response["Results"]
    
    async def opret_sag(self, part_id: int, sagsskabelon_id:int, sagsbehandler_id: int, sagstitel: str, borger_part:bool = True) -> dict:
        """
        Opretter en sag ud fra en sagsskabelon.

        Sagen oprettes med den angivne part som både primær part og eneste
        initiale sagspart. Parten oprettes som en person som standard, men kan
        også oprettes som en virksomhed ved at sætte borger_part til False.

        Args:
            part_id (int): ID på den part, der skal knyttes til sagen.
            sagsskabelon_id (int): ID på den sagsskabelon, der skal bruges.
            sagsbehandler_id (int): ID på den sagsbehandler, der skal tildeles sagen.
            sagstitel (str): Titel på den sag, der oprettes.
            borger_part (bool): Om parten er en person. Hvis False behandles parten som firma.

        Returns:
            dict: Den oprettede sag, som returneres fra SBSYS API'et.
        """

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
            "SagsbehandlerID": sagsbehandler_id
        }

        return await self.client._post(endpoint, body)
    
    async def opdater_sag(self, sags_id: str, body: dict) -> dict:
        # Hent en sag og opdater værdierne og send den med her for at opdatere den
        endpoint = f"api/sag/{sags_id}"

        if not body:
            raise SbsysValidationError("body må ikke være en tom")

        # Vi henter sagen, det gør vi fordi at nogle gange matcher felter ikke hvis sagen f.eks. er hentet gennem search
        sag = await self.hent_sag(sags_id)
        
        # Vi opdatere felter i sagen med dem angivet i body
        # Vi gør dette fordi at det er muligt at opdatere sagen med et felt, men hvis det betyder at alle andre felter sættes til null og vi derfor kan risikere at fjerne info på en sag
        for key in body:
            if key in sag:
                
                sag[key] = body[key]
            else:
                raise ValueError(f"Fejl {key} feltet kan ikke findes i sagen")

        opdateret_sag = await self.client._put(endpoint, sag)
        return opdateret_sag
    
    async def hent_statusliste_for_sager(self) -> dict:
        endpoint = "api/sag/sagStatusList"
        data = await self.client._get(endpoint)

        return data
    
    async def hent_sagsparter(self, sags_id: str) -> dict:
        endpoint = f"api/sag/{sags_id}/part"

        response = await self.client._get(endpoint)

        return response
    
    async def tilføj_sagspart(self, sags_id:str, part_id:str, navn:str, person_part:bool = True, cpr:str = "", cvr:str ="") -> dict:
        endpoint = f"api/sag/{sags_id}/part"
        
        query = {
            "PartId":part_id,
            "Navn":navn,
        }

        if person_part:
            query["PartType"] = "Person"
            query["Cprnummer"] = cpr
        else:
            query["PartType"] = "Firma"
            query["Cvrnummer"] = cvr
        
        response = await self.client._post(endpoint, query)

        return response