"""Test deduper which tries to make life a little easier for us."""
import pytest

from app.parsers import dedup
from app.schemas import LineBase, MartyrologyCreate

# format is [things to pass],{resp}


def test_hash():
    m = MartyrologyCreate(
        title="",
        language="",
        datestr="1 Jan",
        versions=["1960"],
        # parts=None,
        parts=[LineBase(content="line 1")],
    )
    n = MartyrologyCreate(
        title="",
        language="",
        datestr="1 Jan",
        versions=["1961"],
        # parts=None,
        parts=[LineBase(content="line 1")],
    )
    assert m.__custom_hash__() == m.__custom_hash__()
    assert m.__custom_hash__() == n.__custom_hash__()


candidates = (
    (
        (
            MartyrologyCreate(
                title="",
                language="",
                datestr="1 Jan",
                versions=["1960"],
                parts=[LineBase(content="line 1")],
            ),
            MartyrologyCreate(
                title="",
                language="",
                datestr="1 Jan",
                versions=["1570"],
                parts=[LineBase(content="line 1")],
            ),
            MartyrologyCreate(
                title="",
                language="",
                datestr="1 Jan",
                versions=["1570"],
                parts=[LineBase(content="line 1"), LineBase(content="line 2")],
            ),
        ),
        {
            "Martyrologies": [
                MartyrologyCreate(
                    title="",
                    language="",
                    datestr="1 Jan",
                    versions=["1570", "1960"],
                    parts=[LineBase(content="line 1")],
                ),
                MartyrologyCreate(
                    title="",
                    language="",
                    datestr="1 Jan",
                    versions=["1570"],
                    parts=[LineBase(content="line 1"), LineBase(content="line 2")],
                ),
            ]
        },
    ),
    (
        (  # Test with things in a list.
            MartyrologyCreate(
                title="",
                language="",
                datestr="1 Jan",
                versions=["1960"],
                parts=[LineBase(content="line 1")],
            ),
            [
                MartyrologyCreate(
                    title="",
                    language="",
                    datestr="1 Jan",
                    versions=["1570"],
                    parts=[LineBase(content="line 1")],
                ),
                MartyrologyCreate(
                    title="",
                    language="",
                    datestr="1 Jan",
                    versions=["1570"],
                    parts=[LineBase(content="line 1"), LineBase(content="line 2")],
                ),
            ],
        ),
        {
            "Martyrologies": [
                MartyrologyCreate(
                    title="",
                    language="",
                    datestr="1 Jan",
                    versions=["1570", "1960"],
                    parts=[LineBase(content="line 1")],
                ),
                MartyrologyCreate(
                    title="",
                    language="",
                    datestr="1 Jan",
                    versions=["1570"],
                    parts=[LineBase(content="line 1"), LineBase(content="line 2")],
                ),
            ]
        },
    ),
)


@pytest.mark.parametrize("candidate,correct", candidates)
def test_dedup_manual(candidate, correct):
    resp = dedup.dedup(candidate)
    for k, objs in correct.items():
        for i, obj in enumerate(objs):
            assert set(resp[k][i].versions) == set(obj.versions)
            obj.versions = None
            resp[k][i].versions = None
            assert obj == resp[k][i]
