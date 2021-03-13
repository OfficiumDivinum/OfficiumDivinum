import pytest
from devtools import debug

from app import parsers

candidates = [
    {
        "filename": "Matutinum Special",
        "section_name": "Day0 Hymnus",
        "resp": {
            "liturgical_context": ["matutinum"],
            "qualifiers": ["Day0"],
            "title": "hymnus",
        },
    },
    {
        "filename": "Matutinum Special",
        "section_name": "Day0 Hymnus1M",
        "resp": {
            "liturgical_context": ["matutinum"],
            "qualifiers": ["Day0", "Hymnus1"],
            "version": ["monastic"],
            "title": "hymnus",
        },
    },
    {
        "filename": "Matutinum Special",
        "section_name": "HymnusM Adv",
        "resp": {
            "liturgical_context": ["matutinum"],
            "qualifiers": ["Adv"],
            "version": ["monastic"],
            "title": "hymnus",
        },
    },
    {
        "filename": "05-08",
        "section_name": "HymnusM Laudes",
        "resp": {
            "liturgical_context": ["laudes"],
            "version": ["monastic"],
            "title": "hymnus",
        },
    },
    {
        "filename": "Major Special",
        "section_name": "HymnusM Day0 Laudes2",
        "resp": {
            "liturgical_context": ["laudes2"],
            "version": ["monastic"],
            "qualifiers": ["Day0"],
            "title": "hymnus",
        },
    },
    {
        "filename": "Major Special",
        "section_name": "Day0 Versum 2",
        "resp": {
            "liturgical_context": ["laudes", "vespera"],
            "qualifiers": ["Day0"],
            "title": "versum 2",
        },
    },
    {
        "filename": "Major Special",
        "section_name": "Day0 Laudes2",
        "resp": {
            "liturgical_context": ["laudes2"],
            "qualifiers": ["Day0"],
            "title": "laudes2",
        },
    },
    {
        "filename": "Minor Special",
        "section_name": "Dominica Tertia",
        "resp": {
            "liturgical_context": ["tertia"],
            "qualifiers": ["Dominica"],
            "title": "tertia",
        },
    },
    {
        "filename": "Minor Special",
        "section_name": "Adv Tertia",
        "resp": {
            "liturgical_context": ["tertia"],
            "qualifiers": ["Adv"],
            "title": "tertia",
        },
    },
    {
        "filename": "Minor Special",
        "section_name": "Responsory Adv Tertia",
        "resp": {
            "liturgical_context": ["tertia"],
            "qualifiers": ["Adv"],
            "title": "responsory",
        },
    },
    {
        "filename": "Minor Special",
        "section_name": "Feria Tertia",
        "resp": {
            "liturgical_context": ["tertia"],
            "qualifiers": ["Feria"],
            "title": "tertia",
        },
    },
    {
        "filename": "Minor Special",
        "section_name": "Quad5 Nona",
        "resp": {
            "liturgical_context": ["nona"],
            "qualifiers": ["Quad5"],
            "title": "nona",
        },
    },
    {
        "filename": "Minor Special",
        "section_name": "Responsory Pasch Tertia",
        "resp": {
            "liturgical_context": ["tertia"],
            "qualifiers": ["Pasch"],
            "title": "responsory",
        },
    },
]


@pytest.mark.parametrize("candidate", candidates)
def test_extract_section_information(candidate):
    args = {i: candidate[i] for i in candidate if i != "resp"}
    resp = parsers.extract_section_information(**args)
    debug(resp, candidate["resp"])
    assert resp == candidate["resp"]
