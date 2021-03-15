from pathlib import Path
from typing import List, Union

import pytest
from devtools import debug

from app import parsers
from app.parsers import Line
from app.schemas import (
    AntiphonCreate,
    BlockCreate,
    HymnCreate,
    LineBase,
    PrayerCreate,
    ReadingCreate,
    RubricCreate,
    VerseCreate,
    VersicleCreate,
)

from .test_parsers import root


def test_markup_line():
    content = "r. Thing and some things. r. Another."
    resp = parsers.markup(content)
    assert resp == "::T::hing and some things. ::A::nother."


def test_parse_versicle():
    prefix = "V."
    content = "Test verse content."
    line = Line(16, " ".join([prefix, content]))
    resp = parsers.parse_versicle(line, "stand on your head")
    assert resp == LineBase(
        lineno=16, content=content, prefix=prefix, rubrics="stand on your head"
    )
    prefix = "R.br."
    content = "Test verse content."
    line = Line(16, " ".join([prefix, content]))
    resp = parsers.parse_versicle(line, "stand on your head again")
    assert resp == LineBase(
        lineno=16, content=content, prefix=prefix, rubrics="stand on your head again"
    )


def test_parse_rubric():
    content = "! Say this whilst jumping up and down."
    line = Line(content=content, lineno=143)
    resp = parsers.is_rubric(line)
    assert resp == [content[2:], ""]
    content = "/:(Fit reverentia):/ Sanctus, * Dóminus."
    line = Line(content=content, lineno=143)
    resp = parsers.is_rubric(line)
    assert resp == ["(Fit reverentia)", "Sanctus, * Dóminus."]


def test_parse_antiphon():
    lineno = 16
    content = "Antiphon * test content."
    resp = parsers.parse_antiphon(Line(lineno, content))
    assert resp == AntiphonCreate(lineno=lineno, content=content)


section_obj_candidates = (
    ("Invit", [], AntiphonCreate),
    ("Ant Matutinum", [], List),
    ("HymnusM Laudes", [], HymnCreate),
    ("Te Deum", [], HymnCreate),
    ("Ant 1", [], AntiphonCreate),
)


@pytest.mark.parametrize("section_name,section,correct_obj", section_obj_candidates)
def test_guess_section_obj(section_name, section, correct_obj):
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


def test_replace():
    replacements = {
        "thing": VersicleCreate(
            language="latin",
            parts=[
                LineBase(content="Benedicámus Dómino.", prefix="V.", lineno=1),
                LineBase(content="Deo grátias.", prefix="R.", lineno=2),
            ],
            title="Benedicamus Domino",
        )
    }
    parsers.parser_vars.replacements = replacements
    verse = [Line(content="&thing", lineno=3)]
    resp = parsers.replace(verse)
    parsers.parser_vars.replacements = None
    assert resp == [replacements["thing"]]


candidates = [
    (
        [
            (
                Line(
                    content="r. Per Dóminum nostrum Jesum Christum, Fílium tuum: qui tecum "
                    "vivit et regnat in unitáte Spíritus Sancti, Deus, "
                    "per ómnia sǽcula sæculórum.",
                    lineno=1,
                ),
                Line(content="R. Amen.", lineno=2),
            )
        ],
        PrayerCreate(
            language="latin",
            parts=[
                LineBase(
                    content="::P::er Dóminum nostrum Jesum Christum, Fílium tuum: qui "
                    "tecum vivit et regnat in unitáte Spíritus Sancti, Deus, "
                    "per ómnia sǽcula sæculórum.",
                    lineno=1,
                ),
                LineBase(content="Amen.", prefix="R.", lineno=2),
            ],
            title="Per Dominum",
            versions=None,
        ),
    ),
    (
        (
            [
                (
                    Line(content="Most of Our Father", lineno=1),
                    Line(content="R. Sed libera.", lineno=2),
                )
            ]
        ),
        PrayerCreate(
            language="latin",
            parts=[
                LineBase(content="Most of Our Father", lineno=1),
                LineBase(content="Sed libera.", prefix="R.", lineno=2),
            ],
            title="Pater Noster",
            versions=None,
        ),
    ),
    (
        [
            (
                Line(content="V. Benedicámus Dómino.", lineno=1),
                Line(content="R. Deo grátias.", lineno=2),
            )
        ],
        VersicleCreate(
            language="latin",
            parts=[
                LineBase(content="Benedicámus Dómino.", prefix="V.", lineno=1),
                LineBase(content="Deo grátias.", prefix="R.", lineno=2),
            ],
            title="Benedicamus Domino",
        ),
    ),
    (
        [
            (
                Line(content="v. Credo in Deum.", lineno=1),
                Line(content="and other things.", lineno=2),
            )
        ],
        BlockCreate(
            language="latin",
            title="credo",
            parts=[
                LineBase(content="Credo in Deum.", lineno=1),
                LineBase(content="and other things.", lineno=2),
            ],
        ),
    ),
    (
        [
            (Line(content="R. Deo grátias.", lineno=1),),
        ],
        VersicleCreate(
            language="latin",
            parts=[LineBase(content="Deo grátias.", prefix="R.", lineno=1)],
            title="Deo Gratias",
        ),
    ),
    (
        [(Line(lineno=1, content="Allelúja, allelúja."),)],
        LineBase(lineno=1, content="Allelúja, allelúja.", title="Alleluia Duplex"),
    ),
    (
        [
            (
                Line(content="/:flexis genibus:/", lineno=1),
                Line(content="v. Apéri Dómine", lineno=2),
                Line(content="R. Amen.", lineno=3),
                Line(content="v. Dómine, in unióne", lineno=4),
            )
        ],
        PrayerCreate(
            title="Ante",
            language="latin",
            parts=[
                LineBase(content="Apéri Dómine", rubrics="flexis genibus", lineno=2),
                LineBase(prefix="R.", content="Amen.", lineno=3),
                LineBase(content="Dómine, in unióne", lineno=4),
            ],
        ),
    ),
    (
        [
            (
                Line(content="Lectio.", lineno=1),
                Line(content="!Exod 23:20-21", lineno=2),
                Line(content="20 line 1", lineno=3),
                Line(content="21 line 2", lineno=4),
            )
        ],
        ReadingCreate(
            title="Lectio1",
            language="latin",
            parts=[
                LineBase(content="Lectio.", lineno=1),
                LineBase(content="20 line 1", lineno=3),
                LineBase(content="21 line 2", lineno=4),
            ],
            ref="Exod 23:20-21",
        ),
    ),
    (
        [
            (
                Line(content="Lectio.", lineno=1),
                Line(content="!In Psalmum quodlibet", lineno=2),
                Line(content="20 line 1", lineno=3),
                Line(content="21 line 2", lineno=4),
            )
        ],
        ReadingCreate(
            title="Lectio1",
            language="latin",
            parts=[
                LineBase(content="Lectio.", lineno=1),
                LineBase(content="20 line 1", lineno=3),
                LineBase(content="21 line 2", lineno=4),
            ],
            ref="In Psalmum quodlibet",
        ),
    ),
    (
        [
            (
                Line(content="Sequéntia ++ sancti Evangélii", lineno=1),
                Line(content="!Matt 2:19-23", lineno=2),
                Line(content="line 1~", lineno=3),
                Line(content="line 2~", lineno=4),
                Line(content="line 3~", lineno=5),
                Line(content="line 4~", lineno=6),
            )
        ],
        ReadingCreate(
            title="Lectio1",
            language="latin",
            parts=[
                LineBase(content="Sequéntia ++ sancti Evangélii", lineno=1),
                LineBase(content="line 1 line 2 line 3 line 4", lineno=3),
            ],
            ref="Matt 2:19-23",
        ),
    ),
]

section_test = (
    (
        [
            (
                Line(content="Te Deum laudámus: * te", lineno=0),
                Line(content="Te ætérnum Patrem * omnis ", lineno=1),
                Line(
                    content="Tibi omnes Ángeli, * tibi: ",
                    lineno=2,
                ),
                Line(
                    content="Tibi Chérubim * et Séraphim:",
                    lineno=3,
                ),
            ),
            (
                Line(
                    content="/:(Fit reverentia):/ Sanctus, * Dóminus.",
                    lineno=4,
                ),
            ),
            (
                Line(
                    content="Pleni sunt cæli et terra * tuæ.",
                    lineno=5,
                ),
            ),
        ],
        HymnCreate(
            title="te deum laudamus te",
            versions=["1960"],
            hymn_version="pius v",
            language="latin",
            parts=[
                VerseCreate(
                    parts=[
                        LineBase(content="Te Deum laudámus: * te", lineno=0),
                        LineBase(content="Te ætérnum Patrem * omnis", lineno=1),
                        LineBase(
                            content="Tibi omnes Ángeli, * tibi:",
                            lineno=2,
                        ),
                        LineBase(
                            content="Tibi Chérubim * et Séraphim:",
                            lineno=3,
                        ),
                    ]
                ),
                VerseCreate(
                    parts=[
                        LineBase(
                            content="Sanctus, * Dóminus.",
                            rubrics="(Fit reverentia)",
                            lineno=4,
                        )
                    ]
                ),
                VerseCreate(
                    parts=[
                        LineBase(
                            content="Pleni sunt cæli et terra * tuæ.",
                            lineno=5,
                        )
                    ]
                ),
            ],
        ),
    ),
    (
        (
            (
                Line(content="v. Collect here", lineno=1),
                Line(content="Dominus_vobiscum", lineno=2),
                Line(content="R. Amen.", lineno=3),
            ),
            (
                Line(content="v. Orémus.", lineno=4),
                Line(content="v. Collect here", lineno=5),
                Line(content="Termination.", lineno=6),
                Line(content="R. Amen.", lineno=7),
            ),
        ),
        [
            PrayerCreate(
                title="Oratio mortuorum",
                parts=[
                    LineBase(content="Collect here", lineno=1),
                    LineBase(content="Dominus_vobiscum", lineno=2),
                    LineBase(prefix="R.", content="Amen.", lineno=3),
                ],
                language="latin",
            ),
            PrayerCreate(
                oremus=True,
                title="Oratio mortuorum",
                parts=[
                    LineBase(content="Collect here", lineno=5),
                    LineBase(content="Termination.", lineno=6),
                    LineBase(prefix="R.", content="Amen.", lineno=7),
                ],
                language="latin",
            ),
        ],
    ),
)


@pytest.mark.parametrize("verses,correct_obj", candidates)
def test_guess_verse_obj(verses, correct_obj):
    resp, data = parsers.guess_verse_obj(verses[0], correct_obj.title)
    assert resp is type(correct_obj)
    if type(correct_obj) is type(ReadingCreate):
        assert data["ref"]


@pytest.mark.parametrize("section,correct_obj", [*candidates, *section_test])
def test_parse_section(section, correct_obj):
    if isinstance(correct_obj, list):
        section_name = correct_obj[0].title
    else:
        section_name = correct_obj.title
    if "te deum" in section_name:
        section_name = "Te Deum"
    resp = parsers.parse_section(
        Path("Prayers.txt"), section_name, section, "latin", "1960"
    )
    debug(resp)
    assert resp == correct_obj


def test_parse_replace_section():
    section_name = "DefunctM"
    verse = [
        Line(lineno=1, content="&DV"),
        Line(lineno=2, content="&BD"),
        Line(
            lineno=3,
            content="! Post Laudes diei dicuntur %Matutinum et Laudes Defunctorum%.",
        ),
    ]
    replacements = {
        "DV": VersicleCreate(title="DV", parts=[]),
        "BD": VersicleCreate(title="BD", parts=[]),
    }
    parsers.parser_vars.replacements = replacements
    resp = parsers.parse_section(
        Path("Prayers.txt"), section_name, [verse], "latin", "1960"
    )
    parsers.parser_vars.replacements = None

    expected = [
        VersicleCreate(title="DV", parts=[]),
        VersicleCreate(title="BD", parts=[]),
        RubricCreate(
            content="Post Laudes diei dicuntur %Matutinum et Laudes Defunctorum%."
        ),
    ]
    assert resp == expected


def test_generate_commemoration_links():
    linkstr = "@Commune/C2:Oratio proper Gregem"
    resp = parsers.generate_commemoration_links(linkstr)
    assert resp == (
        "@Commune/C2:Ant 1",
        "@Commune/C2:Versum 1",
        "@Commune/C2:Ant 2",
        "@Commune/C2:Versum 2",
    )


def test_resolve_link():
    fn = root / "Latin/SanctiM/03-25.txt"
    linkstr = "@Sancti/03-25:Capitulum Laudes:1-3"
    targetf, part = parsers.deref(linkstr, fn)
    assert targetf == Path("app/tests/parsers/test-DO-data/Latin/Sancti/03-25.txt")
    assert part == "Capitulum Laudes"
    linked_content = parsers.resolve_link(targetf, part, True, linkstr)
    assert len(linked_content[0]) == 3

    linkstr = "@Sancti/03-25:Capitulum Laudes:1"
    targetf, part = parsers.deref(linkstr, fn)
    assert targetf == Path("app/tests/parsers/test-DO-data/Latin/Sancti/03-25.txt")
    assert part == "Capitulum Laudes"
    linked_content = parsers.resolve_link(targetf, part, True, linkstr)
    assert len(linked_content[0]) == 1


sub_candidates = (
    (
        [
            Line(
                1,
                "Quóniam Nazarǽus vocábitur. Si fixum de Scriptúris posuísset exémplum, numquam díceret: Quod dictum est per prophétas: sed simplíciter: Quod dictum est per prophétam. Nunc autem pluráliter prophétas vocans, osténdit se non verba de Scriptúris sumpsísse, sed sensum. Nazarǽus sanctus interpretátur; sanctum autem Dóminum futúrum omnis Scriptúra commémorat.",
            ),
            Line(2, "&teDeum"),
        ],
        "@Sancti/01-05:Lectio9:s/.* Nazarǽus sanctus /Nazarǽus sanctus /s s/$/~/",
        [
            Line(
                1,
                "Nazarǽus sanctus interpretátur; sanctum autem Dóminum futúrum omnis Scriptúra commémorat.~",
            )
        ],
    ),
    (
        [
            Line(1, "Post tríduum Míchaël.~"),
            Line(2, "Nec ita multo post Bonifátius Papa."),
        ],
        "@:Lectio6:s/.*(Nec ita)/$1/s",
        [Line(2, "Nec ita multo post Bonifátius Papa.")],
    ),
)


@pytest.mark.parametrize("start,linkstr,end", sub_candidates)
def test_substitute_linked_content(start, linkstr, end):
    resp = parsers.substitute_linked_content([start], linkstr)
    assert resp[0] == end


datestr_candidates = (
    ("Adv1-0", "1st Sun after Advent"),
    ("Nativity", None),
    ("10-DU", "Sat between 23 Oct 31 Oct"),
    ("Defuncti", None),
)


@pytest.mark.parametrize("candidate,resp", datestr_candidates)
def test_generate_datestr(candidate: str, resp: str):
    assert parsers.generate_datestr(candidate) == resp
