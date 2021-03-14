import pytest

from app import parsers

candidates = (
    ("*January*", None),
    (
        "01-25=01-25r=In Conversione S. Pauli Apostoli=4=",
        {
            "date": "01-25",
            "alternative_date": "01-25r",
            "feasts": [{"name": "In Conversione S. Pauli Apostoli", "rank": 4}],
        },
    ),
    (
        "01-23=01-23=S. Raymundi de Penafort Confessoris=2=S. Emerentianae Virginis et Martyris=1=",
        {
            "date": "01-23",
            "alternative_date": "01-23",
            "feasts": [
                {"name": "S. Raymundi de Penafort Confessoris", "rank": 2},
                {"name": "S. Emerentianae Virginis et Martyris", "rank": 1},
            ],
        },
    ),
    (
        "07-29=07-29=Ss. Felicis=Simplicii=Faustini et Beatricis Mart=1=",
        {
            "date": "07-29",
            "alternative_date": "07-29",
            "feasts": [
                {"name": "Ss. Felicis=Simplicii=Faustini et Beatricis Mart", "rank": 1},
            ],
        },
    ),
    (
        "08-09=08-09=Vigilia S. Laurentii Martyris=1.5=",
        {
            "date": "08-09",
            "alternative_date": "08-09",
            "feasts": [
                {"name": "Vigilia S. Laurentii Martyris", "rank": 1.5},
            ],
        },
    ),
)


@pytest.mark.parametrize("line,correct_resp", candidates)
def test_extract_line(line, correct_resp):
    assert parsers.extract_line(line) == correct_resp
