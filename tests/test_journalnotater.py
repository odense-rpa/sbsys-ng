from sbsys.manager import SbsysClientManager


def _normaliser_notat_tekst(note: str) -> str:
    return (
        note.replace("<br/>", "")
        .replace("<br>", "")
        .replace("</br>", "")
        .replace("< /br>", "")
        .replace("</ br>", "")
        .replace("\n", "")
        .replace("\r", "")
        .strip()
    )

async def test_hent_journalnotater(sbsys_manager: SbsysClientManager):
    sags_id = "738081"

    async with sbsys_manager:
        response = await sbsys_manager.journalnotater.hent_journalnotater_på_sag(sags_id)
    
    assert response is not None
    assert response[0]["Overskrift"] == "Test"

async def test_opret_journalnotater(sbsys_manager: SbsysClientManager):
    sags_id = "738081"
    notat_overskrift = "Test opret"
    notat_indhold = (
        "Navn: test test\n"
        "Relation: test\n"
        "Forældremyndighed: Nej\n"
        "Hjemmetlf: test\n"
        "Mobiltlf: test\n"
        "Arbejdstlf: test\n"
        "Adresse: test\n"
        "UniBrugerID: test\n"
        "_____________________________________"
    )

    notat_indhold2 = """Navn: test test 2
    Relation: test2
    Forældremyndighed: ja
    Hjemmetlf: test2
    Mobiltlf: test2
    Arbejdstlf: test2
    Adresse: test2
    UniBrugerID: test2
    _____________________________________"""
    
    
    async with sbsys_manager:
        #response = await sbsys_manager.journalnotater.opret_journalnotater(sags_id, notat_overskrift, notat_indhold)
        #response2 = await sbsys_manager.journalnotater.opret_journalnotater(sags_id, notat_overskrift, notat_indhold2)
        response = None
        response2 = None
    #Kommenteret ud, for at undgå man kommer til at oprette i drift.
    assert response is not None
    assert response["Overskrift"] == notat_overskrift
    assert _normaliser_notat_tekst(response["Note"]) == _normaliser_notat_tekst(notat_indhold)
        
    #Kommenteret ud, for at undgå man kommer til at oprette i drift.
    assert response2 is not None
    assert response2["Overskrift"] == notat_overskrift
    assert _normaliser_notat_tekst(response2["Note"]) == _normaliser_notat_tekst(notat_indhold2)
    
    