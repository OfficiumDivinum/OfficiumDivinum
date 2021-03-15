import pytest
from fastapi.encoders import jsonable_encoder

from app import parsers

from .test_parsers import root

kalendars = (root / "Latin/Tabulae").glob("K*.txt")


@pytest.mark.parametrize("fn", kalendars)
def test_regression_kalendarium(data_regression, fn):
    data = jsonable_encoder(parsers.kalendarium.parse_file(fn, "Latin"))
    data_regression.check(data)
