from sbsys.manager import SbsysClientManager


async def test_hent_sagsskabeloner(sbsys_manager: SbsysClientManager):
    async with sbsys_manager:
        response = await sbsys_manager.sagsskabeloner.hent_sagsskabeloner()
    assert response is not None


async def test_hent_sagsskabelon(sbsys_manager: SbsysClientManager):
    async with sbsys_manager:
        response = await sbsys_manager.sagsskabeloner.hent_sagsskabelon(332)
    assert response is not None
