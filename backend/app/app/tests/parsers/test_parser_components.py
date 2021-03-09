from typing import List, Union

from app import parsers
from app.parsers import Line
from app.schemas import (
    AntiphonCreate,
    HymnCreate,
    LineBase,
    PrayerCreate,
    ReadingCreate,
    VerseCreate,
    VersicleCreate,
)


def test_parse_versicle():
    prefix = "V."
    content = "Test verse content."
    line = Line(16, " ".join([prefix, content]))
    resp = parsers.parse_versicle(line)
    assert resp == LineBase(lineno=16, content=content, prefix=prefix)


def test_parse_antiphon():
    lineno = 16
    content = "Antiphon * test content."
    resp = parsers.parse_antiphon(Line(lineno, content))
    assert resp == AntiphonCreate(lineno=lineno, content=content)


def test_parse_rubric():
    content = "! Say this whilst jumping up and down."
    line = Line(content=content, lineno=143)
    resp = parsers.parse_rubric(line)
    assert resp == content[2:]


def test_guess_section_obj():
    candidates = (
        ("Invit", [], AntiphonCreate),
        ("Ant Matutinum", [], List),
        ("Lectio1", [], ReadingCreate),
        ("Responsory2", [], VersicleCreate),
        ("HymnusM Laudes", [], HymnCreate),
        ("Capitulum Laudes", [], ReadingCreate),
        ("Ant 1", [], AntiphonCreate),
        (
            "Per Dominum",
            (
                (
                    Line(
                        content="r. Per Dóminum nostrum Jesum Christum, Fílium tuum: qui tecum vivit et regnat in unitáte Spíritus Sancti, Deus, per ómnia sǽcula sæculórum.",
                        lineno=1,
                    ),
                    Line(content="R. Amen.", lineno=2),
                ),
            ),
            PrayerCreate,
        ),
        (
            "Benedicamus Domino",
            (
                (
                    Line(content="V. Benedicámus Dómino.", lineno=1),
                    Line(content="R. Deo grátias.", lineno=2),
                ),
            ),
            VersicleCreate,
        ),
        (
            "Deo Gratias",
            ((Line(content="R. Deo grátias.", lineno=1),),),
            VersicleCreate,
        ),
        (
            "Alleluia Duplex",
            ((Line(lineno=1, content="Allelúja, allelúja."),),),
            LineBase,
        ),
    )
    for section_name, section, correct_obj in candidates:
        resp = parsers.guess_section_obj(section_name, section)

        try:
            if correct_obj.__origin__ in (list, Union):
                assert isinstance(resp, correct_obj.__origin__)
                try:
                    possible_types = correct_obj.__args__
                    for i in resp:
                        assert any((isinstance(i, t) for t in possible_types))
                except AttributeError:
                    pass
            else:
                raise NotImplementedError("Shouldn't be testing any other funny type")
        except AttributeError:
            assert type(resp) is type(correct_obj)
