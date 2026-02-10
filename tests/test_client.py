import pytest

from sbsys import Bruger, SbsysClient, Skabelon, Status


@pytest.mark.integration
@pytest.mark.asyncio
async def test_api_me(client: SbsysClient):
    async with client:
        result = await client.api_me()

    assert "Brugernavn" in result or "Navn" in result


@pytest.mark.integration
@pytest.mark.asyncio
async def test_hent_statusliste(client: SbsysClient):
    async with client:
        statusliste = await client.hent_statusliste()

    assert len(statusliste) > 0
    assert all(isinstance(s, Status) for s in statusliste)
    assert all(s.id for s in statusliste)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_soeg_brugere(client: SbsysClient):
    async with client:
        brugere = await client.soeg_brugere(initialer="sh")

    assert len(brugere) > 0
    assert all(isinstance(b, Bruger) for b in brugere)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_hent_sagsskabeloner(client: SbsysClient):
    async with client:
        skabelon = await client._hent_sagsskabeloner()

    assert len(skabelon) > 0
    assert all(isinstance(s, Skabelon) for s in skabelon)
    assert all(s.id for s in skabelon)
