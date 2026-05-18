from sbsys.manager import SbsysClientManager


async def test_hent_dokumenter_på_sag(sbsys_manager: SbsysClientManager):
    sags_id = "738100"
    
    async with sbsys_manager:
        response = await sbsys_manager.dokumenter.hent_dokumenter_på_sag(sags_id)
    
    assert response is not None
    assert response[0]["OprettetAf"] == "Robot A"

async def test_hent_dokument_og_underdokumenter(sbsys_manager: SbsysClientManager):
    dokument_id = "625882"
    
    async  with sbsys_manager:
        response = await sbsys_manager.dokumenter.hent_dokument_og_underdokumenter(dokument_id)
    
    assert response is not None
    assert response["Navn"] == "Test dokument"