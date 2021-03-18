import logging
from unittest.mock import Mock

import pytest
from devtools import debug

from app.parsers import Line, Thing
from app.parsers.util import parse_file_as_dict

from .test_parsers import root

logging.basicConfig(level=logging.DEBUG)


def mock_file(fn: str, lines: list):
    f = Mock()
    o = Mock()
    o.readlines.return_value = lines
    f.name = fn
    f.open.return_value = o
    f.parent = Mock()
    f.parent
    return f


candidates = (
    (
        root / "Latin/TemporaM/Pent11-0.txt",
        {
            "Lectio1": Thing(
                content=[
                    [
                        Line(17, "De libro quarto Regum"),
                        Line(18, "!4 Reg 20:1-3"),
                        Line(
                            19,
                            "1 In diébus illis ægrotáret Ezechías usque ad mortem, et venit ad eum Isaías fílius Amos prophéta dixítque ei: Hæc dicit Dóminus Deus: Prǽcipe dómui tuæ, moriéris enim tu et non vives.",
                        ),
                        Line(
                            20,
                            "2 Qui convértit fáciem suam ad paríetem et orávit Dóminum, dicens:",
                        ),
                        Line(
                            21,
                            "3 Obsecro, Dómine: meménto, quæso, quómodo ambuláverim coram te in veritáte et in corde perfécto et quod plácitum est coram te fécerim. Flevit ítaque Ezechías fletu magno.",
                        ),
                    ]
                ],
                crossref=None,
                sourcefile="app/tests/parsers/test-DO-data/Latin/TemporaM/Pent11-0.txt",
                source_section="Lectio1",
            )
        },
    ),
    (
        root / "Latin/SanctiM/12-27.txt",
        {
            "Lectio2": Thing(
                content=[
                    [
                        Line(24, "!1 Joann. 1:4-7"),
                        Line(
                            25,
                            "4 Et hæc scríbimus vobis ut gaudeátis, et gáudium vestrum sit plenum.",
                        ),
                        Line(
                            26,
                            "5 Et hæc est annuntiátio, quam audívimus ab eo, et annuntiámus vobis: Quóniam Deus lux est, et ténebræ in eo non sunt ullæ.",
                        ),
                        Line(
                            40,
                            "6 Si dixérimus quóniam societátem habémus cum eo, et in ténebris ambulámus, mentímur, et veritátem non facimus.",
                        ),
                        Line(
                            41,
                            "7 Si autem in luce ambulámus sicut et ipse est in luce, societátem habémus ad ínvicem, et sanguis Jesu Christi, Fílii ejus, emúndat nos ab omni peccáto.",
                        ),
                    ]
                ],
                crossref=None,
                sourcefile="app/tests/parsers/test-DO-data/Latin/SanctiM/12-27.txt",
                source_section="Lectio2",
            )
        },
    ),
)


@pytest.mark.parametrize("fn,correct", candidates)
def test_parse_file_as_dict(fn, correct):
    resp = parse_file_as_dict(fn, "1960", follow_only_interesting_links=False)
    debug(resp)
    assert resp == correct
