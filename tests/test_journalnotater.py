from sbsys.manager import SbsysClientManager

async def test_hent_journalnotater(sbsys_manager: SbsysClientManager):
    sags_id = "738081"

    async with sbsys_manager:
        response = await sbsys_manager.journalnotater.hent_journalnotater_på_sag(sags_id)
    
    assert response is not None
    assert response[0]["Overskrift"] == "Test"

async def test_opret_journalnotater(sbsys_manager: SbsysClientManager):
    sags_id = "738081"
    notat_overskrift = "Test opret"
    notat_indhold = ("Dette er en test\n"
                      "på flere linjer\n"
                      "for at se om det virker")
    
    
    async with sbsys_manager:
        #  response = await sbsys_manager.journalnotater.opret_journalnotater(sags_id, notat_overskrift, notat_indhold)
        response = None
    #Kommenteret ud, for at undgå man kommer til at oprette i drift.
    assert response is not None
    assert response["Overskrift"] == notat_overskrift
    