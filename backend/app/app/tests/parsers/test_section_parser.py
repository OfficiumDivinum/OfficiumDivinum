import pytest

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
            "verson": "monastic",
            "title": "hymnus",
        },
    },
    {
        "filename": "Matutinum Special",
        "section_name": "HymnusM Adv",
        "resp": {
            "liturgical_context": ["matutinum"],
            "qualifiers": ["Adv"],
            "verson": "monastic",
            "title": "hymnus",
        },
    },
    {
        "filename": "05-08",
        "section_name": "HymnusM Laudes",
        "resp": {
            "liturgical_context": ["laudes"],
            "verson": "monastic",
            "title": "hymnus",
        },
    },
    {
        "filename": "Major Special",
        "section_name": "HymnusM Day0 Laudes2",
        "resp": {
            "liturgical_context": ["laudes"],
            "verson": "monastic",
            "qualifiers": ["Day0"],
            "title": "hymnus",
        },
    },
    {
        "filename": "Major Special",
        "section_name": "Day0 Versum 2",
        "resp": {
            "liturgical_context": ["laudes", "vesperas"],
            "qualifiers": ["Day0"],
            "title": "versum 2",
        },
    },
    {
        "filename": "Major Special",
        "section_name": "Day0 Laudes2",
        "resp": {
            "liturgical_context": ["laudes"],
            "qualifiers": ["Day0"],
            "title": "Laudes2",
        },
    },
    {
        "filename": "Minor Special",
        "section_name": "Dominica Tertia",
        "resp": {
            "liturgical_context": ["tertiam"],
            "qualifiers": ["Dominica"],
            "title": "Tertia",
        },
    },
    {
        "filename": "Minor Special",
        "section_name": "Adv Tertia",
        "resp": {
            "liturgical_context": ["tertiam"],
            "qualifiers": ["Adv"],
            "title": "Tertia",
        },
    },
    {
        "filename": "Minor Special",
        "section_name": "Responsory Adv Tertia",
        "resp": {
            "liturgical_context": ["tertiam"],
            "qualifiers": ["Adv"],
            "title": "Responsory Tertia",
        },
    },
    {
        "filename": "Minor Special",
        "section_name": "Feria Tertia",
        "resp": {
            "liturgical_context": ["primam", "tertiam", "sextam", "nonam"],
            "qualifiers": ["Feria"],
            "title": "Feria Tertia",
        },
    },
]


@pytest.mark.parametrize("candidate", candidates)
def test_extract_section_information(candidate):
    args = {i: candidate[i] for i in candidate if i != "resp"}
    resp = parsers.extract_section_information(**args)
    assert resp == candidate["resp"]
