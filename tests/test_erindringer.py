import random
import string
import pytest
from sbsys.manager import SbsysClientManager

async def test_hent_erindringer_på_sag(sbsys_manager: SbsysClientManager):
    sags_id = "738100"
       
    async with sbsys_manager:
        response = await sbsys_manager.erindringer.hent_erindringer_på_sag(sags_id)
    
    assert response is not None
    assert response[0]["Navn"] == "Test erindring for erindringens skyld"
    

async def test_hent_erindring(sbsys_manager: SbsysClientManager):
    erindrings_id = "809243"
    
    async with sbsys_manager:
        response = await sbsys_manager.erindringer.hent_erindring(erindrings_id)
    
    assert response is not None
    assert response["Navn"] == "Test erindring for erindringens skyld"
    
async def test_hent_erindringstyper(sbsys_manager: SbsysClientManager):
    async with sbsys_manager:
        respone = await sbsys_manager.erindringer.hent_erindringstyper()
    
    assert respone is not None
    assert len(respone) > 5

async def test_opdater_erindring(sbsys_manager: SbsysClientManager):
    erindrings_id = "809243"
    
    async with sbsys_manager:
        ny_beskrivelse = "Dette er en opdateret test beskrivelse " + random.choice(string.ascii_letters)
        
        body = {
            "Beskrivelse": ny_beskrivelse
        }
        
        response = await sbsys_manager.erindringer.opdater_erindring(erindrings_id, body)
    
    assert response is not None
    assert response["Beskrivelse"] == ny_beskrivelse