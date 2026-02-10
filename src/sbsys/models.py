from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Skabelon:
    id: int
    navn: str
    aktiv: bool = True
    beskrivelse: str = ""
    display_name: str = ""
    sti: str = ""
    sags_titel: str = ""
    identitet: str = ""
    fagomraade_id: int | None = None
    fagomraade: str = ""
    skabelonsbruger: str = ""
    skabelonsbruger_uuid: str = ""
    er_beskyttet: bool = False
    er_stamdata_angivet: bool = False
    anvend_sikkerhed_fra_ansaettelsessted: bool = False
    part_anvend_ikke: bool = False
    part_forlang_altid: bool = False
    part_forlang_altid_primaer: bool = False


@dataclass
class Sag:
    uuid: str
    nummer: str = ""
    id: int = 0
    titel: str = ""
    oprettet: datetime | None = None
    oprettet_af_id: str = ""
    oprettet_af_navn: str = ""
    sidst_aendret: datetime | None = None
    sidst_aendret_af_id: str = ""
    sidst_aendret_af_navn: str = ""
    status: str = ""
    tilstand: str = ""
    status_kommentar: str = ""
    er_beskyttet: bool = False
    er_besluttet: bool = False
    fagomraade: str = ""
    skabelon_navn: str = ""
    skabelon_id: int | None = None
    primaer_parts_navn: str = ""
    primaer_parts_cpr: str = ""
    sagsbehandler: str = ""
    sagsbehandler_uuid: str = ""


@dataclass
class Person:
    id: int
    uuid: str = ""
    navn: str = ""
    cpr: str = ""


@dataclass
class Dokument:
    uuid: str
    navn: str = ""
    registrerings_dato: str = ""
    registreret_af_id: str = ""
    registreret_af_navn: str = ""


@dataclass
class Journalarknote:
    uuid: str
    overskrift: str = ""
    indhold: str = ""
    oprettet_dato: str = ""
    oprettet_af_id: str = ""
    oprettet_af_navn: str = ""


@dataclass
class Sagspart:
    id: int
    type: str = ""
    cvr: str = ""
    cpr: str = ""
    navn: str = ""


@dataclass
class Bruger:
    id: int
    uuid: str = ""
    initialer: str = ""
    navn: str = ""


@dataclass
class Status:
    id: int
    status: str = ""
    tilstand: str = ""
    kraever_kommentarer: bool = False


@dataclass
class Erindringstype:
    id: int
    navn: str = ""
    display_name: str = ""
    synlighed_i_dage: int = 0
    deadline_i_dage: int = 0
    skjul_erindring: bool = False


@dataclass
class Erindring:
    har_deadline: bool = False
    deadline: str = ""
    deadline_status: str = ""
    synlig_fra: str = ""
    sag_id: int = 0
    navn: str = ""
    beskrivelse: str = ""
    er_afsluttet: bool = False
    erindring_type: dict = field(default_factory=dict)
    ansvarlig: dict = field(default_factory=dict)
    opretter: dict = field(default_factory=dict)
