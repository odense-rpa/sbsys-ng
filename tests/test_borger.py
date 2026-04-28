from sbsys.manager import SbsysClientManager


async def test_hent_borger(sbsys_manager: SbsysClientManager):
    async with sbsys_manager:
        response = await sbsys_manager.borger.hent_borger("111111-1111")

    assert response is not None
    assert response["Navn"] == "Test Testesen"

async def test_opret_borger_der_findes(sbsys_manager: SbsysClientManager):
    async with sbsys_manager:
        response = await sbsys_manager.borger.opret_borger("111111-1111")
    
    assert response is not None
    assert response["Navn"] == "Test Testesen"

async def test_opret_borger(sbsys_manager: SbsysClientManager):
    async with sbsys_manager:
        #Denne person findes i drift, men testen vil fejle da navnet ikke er korrekt. Lad vær med at oprette i drift via test
        #response = await sbsys_manager.borger.opret_borger("111111-1111", { "Navn": "TestPerson Test"})
        response = None

    assert response is not None
    assert response["Navn"] == "TestPerson Test"
