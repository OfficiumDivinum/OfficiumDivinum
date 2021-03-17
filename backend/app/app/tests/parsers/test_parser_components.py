from pathlib import Path
from typing import List, Union

import pytest
from devtools import debug

from app import parsers
from app.parsers import Line
from app.parsers.util import Thing
from app.schemas import (
    AntiphonCreate,
    BibleVerseCreate,
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

verse_candidates = (
    (
        Line(1, "20 content"),
        "Exod 1:20-23",
        BibleVerseCreate(
            book="Exod", prefix="1:20", content="content", lineno=1, language="latin"
        ),
    ),
    (
        Line(2, "21 content 2"),
        "Exod 1:20-23",
        BibleVerseCreate(
            book="Exod", prefix="1:21", content="content 2", lineno=2, language="latin"
        ),
    ),
)


@pytest.mark.parametrize("line,ref,correct", verse_candidates)
def test_parse_bible_verse(line, ref, correct):
    assert parsers.parse_bible_verse(line, ref, "latin") == correct


rubrica_candidates = (
    [
        "ex Tempora/Pasc5-4;(rubrica 1570 aut rubrica 1910 aut rubrica divino)",
        "1910",
        {"line": "ex Tempora/Pasc5-4;", "replace_previous": False, "skip_next": False,},
    ],
    [
        "ex Tempora/Pasc5-4;(rubrica 1570 aut rubrica 1910 aut rubrica divino)",
        "1960",
        {"line": None, "replace_previous": False, "skip_next": False,},
    ],
    [
        "(rubrica 1570)",
        "1570",
        {"line": None, "replace_previous": False, "skip_next": False,},
    ],
    [
        "(rubrica 1570)",
        "1960",
        {"line": None, "replace_previous": False, "skip_next": True,},
    ],
    [
        "(rubrica 1570 hæc versus omittitur)",
        "1570",
        {"line": None, "skip_next": False, "replace_previous": True,},
    ],
    [
        "(rubrica 1570 hæc versus omittitur)",
        "1960",
        {"line": None, "replace_previous": False, "skip_next": False,},
    ],
    [
        "(rubrica 1960) Psalm5 Vespera=138",
        "1960",
        {"line": "Psalm5 Vespera=138", "replace_previous": False, "skip_next": False,},
    ],
    [
        "(rubrica 1960) Psalm5 Vespera=138",
        "1955",
        {"line": None, "replace_previous": False, "skip_next": False,},
    ],
    [
        "(rubrica 1960) Psalm5 Vespera=138",
        None,
        {
            "line": "(rubrica 1960) Psalm5 Vespera=138",
            "replace_previous": False,
            "skip_next": False,
        },
    ],
    [
        "(sed rubrica 1955 aut rubrica 1960 loco horum versuum dicuntur)",
        "1955",
        {"line": None, "replace_previous": True, "skip_next": False,},
    ],
    [
        "(sed rubrica 1955 aut rubrica 1960 loco horum versuum dicuntur)",
        "1570",
        {"line": None, "replace_previous": False, "skip_next": True,},
    ],
    [
        "v. a line which doesn't have rubrics in it!",
        "1570",
        {
            "line": "v. a line which doesn't have rubrics in it!",
            "replace_previous": False,
            "skip_next": False,
        },
    ],
    [
        "v. a line which doesn't have rubrics in it! (Allelúja.)",
        "1570",
        {
            "line": "v. a line which doesn't have rubrics in it! (Allelúja.)",
            "replace_previous": False,
            "skip_next": False,
        },
    ],
)


@pytest.mark.parametrize("line,version,resp", rubrica_candidates)
def test_resolve_rubrica(line, version, resp):
    assert parsers.util.resolve_rubrica(line, version) == resp


link_candidates = (
    {
        "fn": "Latin/SanctiM/03-25.txt",
        "linkstr": "@Sancti/03-25:Capitulum Laudes:1-3",
        "targetf": Path("app/tests/parsers/test-DO-data/Latin/Sancti/03-25.txt"),
        "part": "Capitulum Laudes",
        "length": 3,
        "section": None,
    },
    {
        "fn": "Latin/SanctiM/03-25.txt",
        "linkstr": "@Sancti/03-25:Capitulum Laudes:1",
        "targetf": Path("app/tests/parsers/test-DO-data/Latin/Sancti/03-25.txt"),
        "part": "Capitulum Laudes",
        "length": 1,
        "section": None,
    },
    {
        "fn": "Latin/SanctiM/03-25.txt",
        "linkstr": "@Tempora/Epi5-0:Lectio1:",
        "targetf": Path("app/tests/parsers/test-DO-data/Latin/Tempora/Epi5-0.txt"),
        "part": "Lectio1",
        "length": 6,
        "section": "Lectio1",
    },
)


@pytest.mark.parametrize("data", link_candidates)
def test_resolve_link(data):
    fn = root / data["fn"]
    f, p = parsers.deref(data["linkstr"], fn)
    assert f == data["targetf"]
    assert p == data["part"]
    if not p:
        p = data["section"]
    linked_content = parsers.resolve_link(
        data["targetf"], p, True, data["linkstr"], "1960"
    )
    assert len(linked_content[0]) == data["length"]


def test_version_substitution():
    fn = root / "Latin/Sancti/05-25o.txt"
    resp = parsers.parse_file_as_dict(fn, "1960", False, section_key="Oratio")
    assert resp["Oratio"].content[0][0].content.startswith("Deus, qui")
    resp = parsers.parse_file_as_dict(fn, "1570", False, section_key="Oratio")
    assert resp["Oratio"].content[0][0].content.startswith("Da")


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
            versions=["1960"],
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
            sourcefile="Prayers.txt",
            source_section="Per Dominum",
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
            versions=["1960"],
            language="latin",
            parts=[
                LineBase(content="Most of Our Father", lineno=1),
                LineBase(content="Sed libera.", prefix="R.", lineno=2),
            ],
            title="Pater Noster",
            sourcefile="Prayers.txt",
            source_section="Pater Noster",
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
            versions=["1960"],
            language="latin",
            parts=[
                LineBase(content="Benedicámus Dómino.", prefix="V.", lineno=1),
                LineBase(content="Deo grátias.", prefix="R.", lineno=2),
            ],
            title="Benedicamus Domino",
            sourcefile="Prayers.txt",
            source_section="Benedicamus Domino",
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
            versions=["1960"],
            sourcefile="Prayers.txt",
            source_section="credo",
            language="latin",
            title="credo",
            parts=[
                LineBase(content="Credo in Deum.", lineno=1),
                LineBase(content="and other things.", lineno=2),
            ],
        ),
    ),
    (
        [(Line(content="R. Deo grátias.", lineno=1),),],
        VersicleCreate(
            versions=["1960"],
            sourcefile="Prayers.txt",
            source_section="Deo Gratias",
            language="latin",
            parts=[LineBase(content="Deo grátias.", prefix="R.", lineno=1)],
            title="Deo Gratias",
        ),
    ),
    (
        [(Line(lineno=1, content="Allelúja, allelúja."),)],
        LineBase(
            lineno=1,
            content="Allelúja, allelúja.",
            title="Alleluia Duplex",
            sourcefile="Prayers.txt",
            source_section="Alleluia Duplex",
            versions=["1960"],
        ),
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
            versions=["1960"],
            sourcefile="Prayers.txt",
            source_section="Ante",
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
            versions=["1960"],
            sourcefile="Prayers.txt",
            source_section="Lectio1",
            title="Lectio1",
            language="latin",
            parts=[
                LineBase(content="Lectio.", lineno=1),
                BibleVerseCreate(
                    book="Exod",
                    prefix="23:20",
                    content="line 1",
                    lineno=3,
                    language="latin",
                ),
                BibleVerseCreate(
                    book="Exod",
                    prefix="23:21",
                    content="line 2",
                    lineno=4,
                    language="latin",
                ),
            ],
            ref="Exod 23:20-21",
        ),
    ),
    (
        [(Line(content="Nec tantum", lineno=183),)],
        ReadingCreate(
            versions=["1960"],
            sourcefile="/home/john/code/OfficiumDivinum/divinum-officium/web/www/horas/Latin/Sancti/01-00.txt",
            source_section="Lectio6",
            title="Lectio6",
            language="latin",
            parts=[LineBase(content="Nec tantum", lineno=183),],
        ),
    ),
    (
        [
            (
                Line(content="Lectio.", lineno=1),
                Line(content="!In Psalmum quodlibet", lineno=2),
                Line(content="line 1", lineno=3),
                Line(content="line 2", lineno=4),
            )
        ],
        ReadingCreate(
            versions=["1960"],
            sourcefile="Prayers.txt",
            source_section="Lectio1",
            title="Lectio1",
            language="latin",
            parts=[
                LineBase(content="Lectio.", lineno=1),
                LineBase(content="line 1", lineno=3),
                LineBase(content="line 2", lineno=4),
            ],
            ref="In Psalmum quodlibet",
        ),
    ),
    (
        [
            (
                Line(content="Sequéntia ++ sancti Evangélii", lineno=1),
                Line(content="!Matt 2:19-22", lineno=2),
                Line(content="line 1~", lineno=3),
                Line(content="line 2~", lineno=4),
                Line(content="line 3~", lineno=5),
                Line(content="line 4~", lineno=6),
            )
        ],
        ReadingCreate(
            versions=["1960"],
            sourcefile="Prayers.txt",
            source_section="Lectio1",
            title="Lectio1",
            language="latin",
            parts=[
                LineBase(content="Sequéntia ++ sancti Evangélii", lineno=1),
                LineBase(content="line 1 line 2 line 3 line 4", lineno=3),
            ],
            ref="Matt 2:19-22",
        ),
    ),
]

section_test = (
    (
        [
            (
                Line(content="Te Deum laudámus: * te", lineno=0),
                Line(content="Te ætérnum Patrem * omnis ", lineno=1),
                Line(content="Tibi omnes Ángeli, * tibi: ", lineno=2,),
                Line(content="Tibi Chérubim * et Séraphim:", lineno=3,),
            ),
            (Line(content="/:(Fit reverentia):/ Sanctus, * Dóminus.", lineno=4,),),
            (Line(content="Pleni sunt cæli et terra * tuæ.", lineno=5,),),
        ],
        HymnCreate(
            versions=["1960"],
            sourcefile="Prayers.txt",
            source_section="Te Deum",
            title="te deum laudamus te",
            hymn_version="pius v",
            language="latin",
            parts=[
                VerseCreate(
                    parts=[
                        LineBase(content="Te Deum laudámus: * te", lineno=0),
                        LineBase(content="Te ætérnum Patrem * omnis", lineno=1),
                        LineBase(content="Tibi omnes Ángeli, * tibi:", lineno=2,),
                        LineBase(content="Tibi Chérubim * et Séraphim:", lineno=3,),
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
                        LineBase(content="Pleni sunt cæli et terra * tuæ.", lineno=5,)
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
                versions=["1960"],
                sourcefile="Prayers.txt",
                source_section="Oratio mortuorum",
                title="Oratio mortuorum",
                parts=[
                    LineBase(content="Collect here", lineno=1),
                    LineBase(content="Dominus_vobiscum", lineno=2),
                    LineBase(prefix="R.", content="Amen.", lineno=3),
                ],
                language="latin",
            ),
            PrayerCreate(
                versions=["1960"],
                sourcefile="Prayers.txt",
                source_section="Oratio mortuorum",
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
    (
        (
            (
                Line(
                    content="v. Concede, misericors Deus, fragilitati nostrae", lineno=1
                ),
                Line(content="$Per eumdem", lineno=2),
            ),
        ),
        PrayerCreate(
            versions=["1960"],
            sourcefile="Commune/C12P.txt",
            source_section="Oratio Sexta",
            title="Oratio Sexta",
            parts=[
                LineBase(
                    content="Concede, misericors Deus, fragilitati nostrae", lineno=1
                ),
                LineBase(content="$Per eumdem", lineno=2),
            ],
            language="latin",
        ),
    ),
    (
        [
            [
                Line(lineno=157, content="Justifíceris, Dómine, * in judicáris.;;50",),
                Line(lineno=158, content="Dóminus * tamquam ovis suum.;;89",),
                Line(lineno=159, content="Contrítum est * cor , ossa mea.;;35",),
                Line(lineno=160, content="Exhortátus es * in , tua, Dómine.;;224",),
                Line(lineno=161, content="Oblátus est * quia ipse portávit.;;146",),
            ]
        ],
        [
            AntiphonCreate(
                versions=["1960"],
                sourcefile="Prayers.txt",
                source_section="Ant Laudes",
                liturgical_context="Laudes",
                language="latin",
                lineno=157,
                content="Justifíceris, Dómine, * in judicáris.",
            ),
            AntiphonCreate(
                versions=["1960"],
                sourcefile="Prayers.txt",
                source_section="Ant Laudes",
                liturgical_context="Laudes",
                language="latin",
                lineno=158,
                content="Dóminus * tamquam ovis suum.",
            ),
            AntiphonCreate(
                versions=["1960"],
                sourcefile="Prayers.txt",
                source_section="Ant Laudes",
                liturgical_context="Laudes",
                language="latin",
                lineno=159,
                content="Contrítum est * cor , ossa mea.",
            ),
            AntiphonCreate(
                versions=["1960"],
                sourcefile="Prayers.txt",
                source_section="Ant Laudes",
                liturgical_context="Laudes",
                language="latin",
                lineno=160,
                content="Exhortátus es * in , tua, Dómine.",
            ),
            AntiphonCreate(
                versions=["1960"],
                sourcefile="Prayers.txt",
                source_section="Ant Laudes",
                liturgical_context="Laudes",
                language="latin",
                lineno=161,
                content="Oblátus est * quia ipse portávit.",
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
        section_name = correct_obj[0].source_section
    else:
        section_name = correct_obj.source_section
    if "te deum" in section_name:
        section_name = "Te Deum"

    try:
        sourcefile = correct_obj.sourcefile
    except AttributeError:
        sourcefile = "Prayers.txt"
    kwargs = {"sourcefile": sourcefile, "source_section": section_name}

    resp = parsers.parse_section(
        Path(sourcefile), section_name, Thing(section, **kwargs), "latin", "1960",
    )
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
        Path("Prayers.txt"), section_name, Thing([verse]), "latin", "1960"
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


datestr_candidates = (
    ("Adv1-0", "1st Sun after Advent"),
    ("Nativity", None),
    ("10-DU", "Sat between 23 Oct 31 Oct"),
    ("Defuncti", "3 Nov"),
)


@pytest.mark.parametrize("candidate,resp", datestr_candidates)
def test_generate_datestr(candidate: str, resp: str):
    assert parsers.generate_datestr(candidate) == resp


header_rubrica_candidates = (
    ["[Responsory1](rubrica tridentina aut rubrica divino)", "1910", True],
    ["[Responsory1](rubrica tridentina aut rubrica divino)", "1960", False],
    ["[Responsory1](rubrica tridentina aut rubrica divino)", "1570", True],
    ["[Section]", "nonesuch", True],
    ["[Section](rubrica inextans)", None, True],
)


@pytest.mark.parametrize("line,version,resp", header_rubrica_candidates)
def test_resolve_rubrica_header(line, version, resp):
    assert parsers.util.resolve_rubrica_header(line, version) == resp


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
    (
        [
            Line(1, "Post tríduum Míchaël.~"),
            Line(2, "Nec ita multo post Bonifátius Papa."),
        ],
        "@:Lectio6:s/.*(Nec ita)/$1/s",
        [Line(2, "Nec ita multo post Bonifátius Papa.")],
    ),
    (
        [
            Line(1, "Justifíceris, Dómine, * in sermónibus tuis,"),
            Line(2, "Dóminus * tamquam ovis ad víctimam ductus est, et"),
            Line(3, "Contrítum est * cor meum in médio mei,"),
            Line(4, "Exhortátus es * in virtúte tua, et in"),
            Line(5, "Oblátus est * quia ipse vóluit, et"),
        ],
        r"Tempora/Quad6-4::s/\n/_/smg s/_/;;50\n/ s/_/;;89\n/ s/_/;;35\n/ s/_/;;224\n/ s/$/;;146\n/s",
        [
            Line(1, "Justifíceris, Dómine, * in sermónibus tuis,;;50"),
            Line(2, "Dóminus * tamquam ovis ad víctimam ductus est, et;;89"),
            Line(3, "Contrítum est * cor meum in médio mei,;;35"),
            Line(4, "Exhortátus es * in virtúte tua, et in;;224"),
            Line(5, "Oblátus est * quia ipse vóluit, et;;146"),
        ],
    ),
)


@pytest.mark.parametrize("start,linkstr,end", sub_candidates)
def test_substitute_linked_content(start, linkstr, end):
    resp = parsers.substitute_linked_content([start], linkstr)
    assert resp[0] == end
