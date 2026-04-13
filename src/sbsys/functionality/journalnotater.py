from datetime import datetime, timezone
from html import escape

from sbsys.client import SbsysClient

def tekst_til_html(tekst: str) -> str:
    linjer = tekst.split("\n")
    body = "".join(f"{escape(linje)}<br/>" for linje in linjer)
    return body


class JournalnotatClient:
    def __init__(self, client: SbsysClient):
        self.client = client

    async def hent_journalnotater_på_sag(self, sags_id:str) -> dict:
        endpoint = f"api/sag/{sags_id}/journalarknotes"

        return await self.client._get(endpoint)
    
    async def opret_journalnotater(self, sags_id:str, overskrift: str, note_indhold:str) -> dict:
        endpoint = "api/journalarknote/create"

        query = {
            "SagID": sags_id,
            "Overskrift": overskrift,
            "Note": tekst_til_html(note_indhold),
            "KontaktTidspunkt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        }

        return await self.client._post(endpoint, query)