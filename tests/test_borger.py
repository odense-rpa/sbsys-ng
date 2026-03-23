from sbsys.manager import SbsysClientManager


async def test_hent_borger(sbsys_manager: SbsysClientManager):
    async with sbsys_manager:
        response = await sbsys_manager.borger.hent_borger("111111-1111")

    assert response is not None
    assert response["Navn"] == "Test Testesen"
