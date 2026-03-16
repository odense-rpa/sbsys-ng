from sbsys.client import SbsysClient
from sbsys.models import Sag


class SagerClient:
    def __init__(self, client: SbsysClient):
        self.client = client

    async def hent_sager(self, cpr:str) -> list[Sag]:
        cpr = self.client._format_cpr(cpr)
        endpoint = "api/sag/search"
        body = {
            "PrimaerPerson": 
                {"CprNummer": cpr}
            }
        response = await self.client._post(endpoint, body)
        return response["Results"]