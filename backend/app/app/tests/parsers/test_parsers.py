from pathlib import Path

from app import run_parsers


def test_parsers():
    """Test all the parsers."""
    root = Path("./test-DO-data")
    lang = "Latin"
    versions = ["1960"]

    # test without upload
    for version in versions:
        run_parsers.parse_upload(root, lang, version, pokemon=True, test=True)
