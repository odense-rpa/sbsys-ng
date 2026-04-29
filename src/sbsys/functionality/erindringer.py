from sbsys.client import SbsysClient

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
    
    