from sbsys.client import _build_journal_html
from sbsys.exceptions import SbsysValidationError
from sbsys.models import (
    Bruger,
    Dokument,
    Erindring,
    Erindringstype,
    Journalarknote,
    Person,
    Sag,
    Sagspart,
    Skabelon,
    Status,
)

from sbsys import SbsysClient


def test_skabelon_defaults():
    s = Skabelon(id=1, navn="Test")
    assert s.id == 1
    assert s.navn == "Test"
    assert s.aktiv is True
    assert s.er_beskyttet is False
    assert s.fagomraade_id is None


def test_sag_defaults():
    s = Sag(uuid="abc-123")
    assert s.uuid == "abc-123"
    assert s.nummer == ""
    assert s.id == 0
    assert s.er_beskyttet is False
    assert s.skabelon_id is None


def test_person_construction():
    p = Person(id=42, uuid="p-uuid", navn="John", cpr="010190-1234")
    assert p.id == 42
    assert p.cpr == "010190-1234"


def test_dokument_construction():
    d = Dokument(uuid="d-uuid", navn="test.pdf")
    assert d.uuid == "d-uuid"
    assert d.registreret_af_id == ""


def test_journalarknote_construction():
    j = Journalarknote(uuid="j-uuid", overskrift="Header", indhold="Body")
    assert j.overskrift == "Header"
    assert j.oprettet_af_id == ""


def test_sagspart_construction():
    sp = Sagspart(id=1, type="Person", cpr="010190-1234", navn="John")
    assert sp.type == "Person"
    assert sp.cvr == ""


def test_bruger_construction():
    b = Bruger(id=10, uuid="b-uuid", initialer="JD", navn="John Doe")
    assert b.initialer == "JD"


def test_status_construction():
    s = Status(id=5, status="Aktiv", tilstand="Aaben")
    assert s.kraever_kommentarer is False


def test_erindringstype_construction():
    e = Erindringstype(id=3, navn="Frist")
    assert e.synlighed_i_dage == 0


def test_erindring_defaults():
    e = Erindring()
    assert e.har_deadline is False
    assert e.sag_id == 0
    assert e.erindring_type == {}


# ------------------------------------------------------------------
# CPR formatting
# ------------------------------------------------------------------


def test_format_cpr_with_dash():
    assert SbsysClient._format_cpr("010190-1234") == "010190-1234"


def test_format_cpr_without_dash():
    assert SbsysClient._format_cpr("0101901234") == "010190-1234"


def test_format_cpr_with_whitespace():
    assert SbsysClient._format_cpr("  0101901234  ") == "010190-1234"


def test_format_cpr_invalid():
    try:
        SbsysClient._format_cpr("123")
        assert False, "Should have raised"
    except SbsysValidationError:
        pass


def test_format_cpr_letters():
    try:
        SbsysClient._format_cpr("abcdef-ghij")
        assert False, "Should have raised"
    except SbsysValidationError:
        pass


# ------------------------------------------------------------------
# Journal HTML builder
# ------------------------------------------------------------------


def test_build_journal_html_indledning_only():
    html = _build_journal_html("Intro text", None, "")
    assert html == "Intro text"


def test_build_journal_html_all_parts():
    html = _build_journal_html(
        "Intro",
        [{"Navn": "Alice", "Alder": "30"}, {"Navn": "Bob", "Alder": "25"}],
        "Slut",
    )
    assert "Intro" in html
    assert "Slut" in html
    assert "<table" in html
    assert "Alice" in html
    assert "Bob" in html
    assert "<th" in html
    assert "<br /><br />" in html


def test_build_journal_html_empty_rows():
    html = _build_journal_html(
        "",
        [{"A": "", "B": ""}],
        "",
    )
    assert "<table" in html
    # Empty rows produce spacer <td></td> elements
    assert "<td></td>" in html


def test_build_journal_html_no_data():
    html = _build_journal_html("Intro", None, "Outro")
    assert html == "Intro<br /><br />Outro"
