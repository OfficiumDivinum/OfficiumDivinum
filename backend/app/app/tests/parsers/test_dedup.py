"""Test deduper which tries to make life a little easier for us."""
import pytest

from app.parsers import dedup
from app.schemas import LineBase, MartyrologyCreate

# format is [things to pass],{resp}

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
def test_dedup(candidate, correct):
    resp = dedup.dedup(candidate)
    assert resp == correct
    # for k, v in correct.items():
    #     # non-orderable and non-hashable, but we don't care about order
    #     resp_v = resp[k]
    #     assert len(resp_v) == len(v), f"Repsonse for {k} not of correct length"
    #     assert all((x in resp_v for x in v)), f"Response for {k} doesn't match test"
