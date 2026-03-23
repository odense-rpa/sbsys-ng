from sbsys.manager import SbsysClientManager

async def test_api_me(sbsys_manager: SbsysClientManager):
    async with sbsys_manager:
        response = await sbsys_manager.bruger.api_me()

    assert response is not None
    assert response["Navn"] == "Robot A"

async def test_hent_bruger(sbsys_manager: SbsysClientManager):
    async with sbsys_manager:
        bruger = await sbsys_manager.bruger.api_me()
        response = await sbsys_manager.bruger.hent_bruger(bruger["Id"])
    
    assert response is not None
    assert bruger["Id"] == response["Id"]

async def test_søg_bruger(sbsys_manager: SbsysClientManager):
    async with sbsys_manager:
        response = await sbsys_manager.bruger.find_brugere("","Robot A")
    
    assert response is not None
    assert response[0]["Navn"] == "Robot A"
