import pytest
from sbsys.manager import SbsysClientManager
from sbsys import SbsysClient

async def test_hent_sager(sbsys_manager: SbsysClientManager):
    async with sbsys_manager:
        response = await sbsys_manager.sager.hent_sager_på_borger("111111-1111")
    assert response is not None

async def test_hent_statusliste(sbsys_manager: SbsysClientManager):
    async with sbsys_manager:
        response = await sbsys_manager.sager.hent_statusliste_for_sager()
    assert response is not None
    assert len(response) == 4

async def test_opret_sag(sbsys_manager: SbsysClientManager):
    test_cpr = "111111-1111"
    test_skabelon_id = 332
    test_init = "roboa"
    test_titel = "Tester Titel"

    async with sbsys_manager:
        borger = await sbsys_manager.borger.hent_borger(test_cpr)
        skabelon = await sbsys_manager.sagsskabeloner.hent_sagsskabelon(test_skabelon_id)
        bruger = await sbsys_manager.bruger.find_brugere(test_init)

        assert len(bruger) == 1
        bruger = bruger[0]
        
        #Kommenteret ud for at forhindre fejl opret i drift
        #response = await sbsys_manager.sager.opret_sag(borger["Id"], skabelon["Id"], bruger["Id"], test_titel)
        response = None

    assert response is not None
    assert response["SagsTitel"] == test_titel
    assert response["PrimaryPart"]["CPRnummer"] == test_cpr

async def test_søg_sager(sbsys_manager: SbsysClientManager):
    test_cpr = "111111-1111"
    test_titel = "Tester Titel"

    async with sbsys_manager:
        response = await sbsys_manager.sager.søg_sager(
            {
                "PrimaerPerson":{
                    "CprNummer":test_cpr
                },
                "Titel": test_titel
            }
        )
    
    assert response is not None
    assert response[0]["SagsTitel"] == test_titel

async def test_opdater_sag(sbsys_manager: SbsysClientManager):
    test_cpr = "111111-1111"
    test_titel = "Tester titel"
    ny_titel = "3Ny test 3titel3"

    async with sbsys_manager:
        sager = await sbsys_manager.sager.søg_sager(
            {
                "PrimaerPerson":{
                    "CprNummer":test_cpr
                },
                "Titel": test_titel
            }
        )

        body = {
            "SagsTitel": ny_titel
        } 
        
        response = await sbsys_manager.sager.opdater_sag(sager[0]["Id"],body)
    
    assert response is not None
    assert response["SagsTitel"] == ny_titel

async def test_hent_sagsparter(sbsys_manager: SbsysClientManager):
    test_cpr = "111111-1111"
    test_titel = "Test Titel"

    async with sbsys_manager:
        sager = await sbsys_manager.sager.søg_sager(
            {
                "PrimaerPerson":{
                    "CprNummer":test_cpr
                },
                "Titel": test_titel
            }
        )

        response = await sbsys_manager.sager.hent_sagsparter(sager[0]["SagIdentity"])
    
    assert response is not None

async def test_tilføj_sagspart(sbsys_manager: SbsysClientManager):
    test_cpr = "111111-1111"
    test_cpr_2 = "222222-2222"
    test_titel = "Test Titel"

    async with sbsys_manager:
        sager = await sbsys_manager.sager.søg_sager(
            {
                "PrimaerPerson":{
                    "CprNummer":test_cpr
                },
                "Titel": test_titel
            }
        )

        borger = await sbsys_manager.borger.hent_borger(test_cpr_2)

        #Kommenteret ud for at forhindre fejl opret i drift
        #response = await sbsys_manager.sager.tilføj_sagspart(sager[0]["SagIdentity"], borger["Id"], "Test part", True, test_cpr_2)
        response = None

    assert response is True

async def test_opdater_sags_status(sbsys_manager: SbsysClientManager):
    test_cpr = "111111-1111"
    test_titel = "Tester Titel"

    async with sbsys_manager:
        sager = await sbsys_manager.sager.søg_sager(
            {
                "SagsStatusIds": [
                    6
                ],
                "PrimaerPerson":{
                    "CprNummer":test_cpr
                },
                "Titel": test_titel,
                
            }
        )
        
        #response = await sbsys_manager.sager.opdater_sagsstatus(sager[0]["Id"], "Afsluttet")
        response = None
        
    assert response is not None
    assert response["SagsStatus"]["SagsTilstand"] == "Afsluttet"