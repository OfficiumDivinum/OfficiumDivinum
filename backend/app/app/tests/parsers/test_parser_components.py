from typing import List, Union

from devtools import debug

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
        ("Invit", [], AntiphonCreate, None),
        ("Ant Matutinum", [], List, None),
        ("Lectio1", [], ReadingCreate, None),
        ("Responsory2", [], VersicleCreate, None),
        ("HymnusM Laudes", [], HymnCreate, None),
        ("Te Deum", [], HymnCreate, None),
        ("Capitulum Laudes", [], ReadingCreate, None),
        ("Ant 1", [], AntiphonCreate, None),
    )

    for section_name, section, correct_obj, _ in candidates:
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


candidates = (
    (
        (
            Line(
                content="r. Per Dóminum nostrum Jesum Christum, Fílium tuum: qui tecum"
                "vivit et regnat in unitáte Spíritus Sancti, Deus,"
                "per ómnia sǽcula sæculórum.",
                lineno=1,
            ),
            LineBase(content="R. Amen.", lineno=2),
        ),
        PrayerCreate(
            language="latin",
            parts=[
                LineBase(
                    content="r. Per Dóminum nostrum Jesum Christum, Fílium tuum: qui"
                    "tecum vivit et regnat in unitáte Spíritus Sancti, Deus,"
                    "per ómnia sǽcula sæculórum.",
                    lineno=1,
                ),
                LineBase(content="Amen.", prefix="R.", lineno=2),
            ],
            title="per dominum nostrum",
            version=None,
        ),
    ),
    (
        (
            Line(content="V. Benedicámus Dómino.", lineno=1),
            Line(content="R. Deo grátias.", lineno=2),
        ),
        VersicleCreate(
            language="latin",
            parts=[
                LineBase(content="Benedicámus Dómino.", prefix="V.", lineno=1),
                LineBase(content="Deo grátias.", prefix="R.", lineno=2),
            ],
            title="benedicamus domino",
        ),
    ),
    (
        (Line(content="R. Deo grátias.", lineno=1),),
        VersicleCreate(
            language="latin",
            parts=[LineBase(content="Deo grátias.", prefix="R.", lineno=2)],
            title="deo gratias",
        ),
    ),
    (
        (Line(lineno=1, content="Allelúja, allelúja."),),
        LineBase(lineno=1, content="Allelúja, allelúja."),
    ),
)


def test_guess_verse_obj():
    for verses, correct_obj in candidates:
        resp = parsers.guess_verse_obj(verses)
        assert resp is type(correct_obj)


# def test_parse_section():
#     for verses, correct_obj in candidates:
