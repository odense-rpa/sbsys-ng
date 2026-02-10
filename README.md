# SbSys

Python-klient til SbSys ESDH-systemets REST API — sagsbehandling, dokumenter, parter og erindringer.

## Installation

```bash
pip install sbsys
```

## Brug

```python
from sbsys import SbsysClient

async with SbsysClient(
    base_url="https://...",
    token_url="https://...",
    client_id="...",
    client_secret="...",
    username="...",
    password="...",
) as sbsys:
    # Hent sager for en borger
    sager = await sbsys.hent_sager("0101011234")

    # Opret en ny sag ud fra en skabelon
    sag = await sbsys.opret_sag("0101011234", skabelon_id=42)

    # Tilføj journalarknote
    await sbsys.opret_journalarknote(sag.uuid, sag.id, "Overskrift", "Indhold")

    # Opret erindring
    await sbsys.opret_erindring(
        sags_id=sag.id,
        navn="Følg op",
        beskrivelse="Husk at følge op",
        ansvarlig_brugernavn="MIWN",
        erindringstype_navn="Standard",
    )
```

## Funktionalitet

- Sager — opslag, oprettelse, statusopdatering
- Sagsparter — opslag og tilføjelse
- Dokumenter — hent metadata
- Journalarknoter — opslag og oprettelse (inkl. HTML-tabelformat)
- Erindringer — opslag og oprettelse
- Brugere og sagsskabeloner — opslag

## Forudsætninger

- Python 3.13+
- OAuth2-credentials til SbSys

## Licens

MIT
