from pathlib import Path

from flask import Blueprint
from flask import current_app

test_page = Blueprint("test", __name__, url_prefix="/test/")


@test_page.route("/")
def test_api_page():
    testpage = Path(current_app.root_path) / "static/test.html"
    with testpage.open() as f:
        data = f.read()
    return data
