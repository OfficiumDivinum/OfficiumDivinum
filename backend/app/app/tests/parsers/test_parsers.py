from pathlib import Path
from typing import Dict

from fastapi.testclient import TestClient

from app import run_parsers


def test_parsers(client: TestClient, superuser_token_headers: Dict[str, str]):
    """Test all the parsers."""
    root = Path("./test-DO-data")
    lang = "Latin"
    versions = ["1960"]

    # test without upload
    for version in versions:
        run_parsers.parse_upload(root, lang, version, pokemon=True, test=True)

        args = {
            "root": root,
            "lang": lang,
            "version": version,
            "client": client,
            "host": "",
            "test_token_headers": superuser_token_headers,
        }

        run_parsers.parse_upload_martyrologies(**args)
        run_parsers.parse_upload_psalms(**args)
        run_parsers.parse_upload_temporal(**args)
        run_parsers.parse_upload_sanctoral(**args)
        run_parsers.parse_upload_hymns(**args)
