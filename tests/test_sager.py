from sbsys.manager import SbsysClientManager
from sbsys import SbsysClient

async def test_hent_sager(sbsys_manager: SbsysClientManager):
    async with sbsys_manager:
        response = await sbsys_manager.sager.hent_sager("111111-1111")
    assert response is not None

async def test_hent_sager_client(sbsys_client: SbsysClient):
    async with sbsys_client:
        response = await sbsys_client.hent_sager("111111-1111")
    assert response is not None