from typing import List, Union

from app import parsers
from app.parsers import Line
from app.schemas import (
    AntiphonCreate,
    HymnCreate,
    LineBase,
    ReadingCreate,
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
    candidates = {
        "Invit": AntiphonCreate,
        "Ant Matutinum": List,
        "Lectio1": ReadingCreate,
        "Responsory2": VersicleCreate,
        "HymnusM Laudes": HymnCreate,
        "Capitulum Laudes": ReadingCreate,
        "Ant 1": AntiphonCreate,
    }
    for candidate, correct_obj in candidates.items():
        resp = parsers.guess_section_obj(candidate)

        if correct_obj.__origin__ in (list, Union):
            assert isinstance(resp, correct_obj.__origin__)
            try:
                possible_types = correct_obj.__args__
                for i in resp:
                    assert any((isinstance(i, t) for t in possible_types))
            except AttributeError:
                pass
    else:
        assert isinstance(resp, correct_obj)
