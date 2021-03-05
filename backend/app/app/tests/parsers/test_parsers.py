from itertools import product
from pathlib import Path
from typing import Dict

import pytest
from fastapi.testclient import TestClient

from app import run_parsers

things = ["martyrologies", "psalms", "temporal", "sanctoral", "hymns"]
things = ["hymns"]
versions = ["1960"]


# @pytest.mark.parametrize("version", versions)
# def test_pokemon(
#     version: str,
#     client: TestClient,
#     superuser_token_headers: Dict[str, str],
# ):
#     """Test all the parsers."""
#     root = Path("app/tests/parsers/test-DO-data")
#     lang = "Latin"

#     # test without upload
#     run_parsers.parse_upload(root, lang, version, pokemon=True, test=True)


@pytest.mark.parametrize("version,thing", product(versions, things))
def test_upload_parsers(
    version: str,
    thing: str,
    client: TestClient,
    superuser_token_headers: Dict[str, str],
):
    """Test all the parsers."""
    root = Path("app/tests/parsers/test-DO-data")
    lang = "Latin"

    args = {
        "root": root,
        "lang": lang,
        "version": version,
        "client": client,
        "host": "",
        "test_token_headers": superuser_token_headers,
    }
    fn = getattr(run_parsers, f"parse_upload_{thing}")
    fn(**args)
