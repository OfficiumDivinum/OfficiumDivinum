import tempfile
from itertools import combinations
from urllib.parse import urlencode

import pytest

from officiumdivinum.api import create_app
from officiumdivinum.api import database as db


@pytest.fixture
def app():
    """Create test app."""

    db_fd, db_path = tempfile.mkstemp()

    app = create_app({"TESTING": True, "APP_DATABASE": db_path})

    with app.app_context():
        db.init(app)
    yield app


@pytest.fixture
def client(app):
    """Client."""
    return app.test_client()


def test_hello_page(client):
    resp = client.get("/hello")
    assert resp.data == b"hello world"


def test_test_page(client, app):
    """
    Test that testpage loads.

    Will drop this when the page is dropped.
    """
    resp = client.get("/test/")
    assert resp.status == "200 OK"


def object_parts(client, endpoint):
    """Get a list of all object parts from endpoint and check we can retrieve them."""
    endpoint += "&"
    url = endpoint + urlencode({"getparts": True})
    resp = client.get(url, headers={"Accept": "application/json"})
    parts = resp.json
    resps = []
    for part in parts:
        url = endpoint + urlencode({"part": part})
        resp = client.get(url).status
        resps.append(resp)

    return resps


def object_endpoint(client, endpoint):
    """Test any endpoint which conforms to the object standard."""
    resps = []
    endpoint += "?"

    url = endpoint + urlencode({"getlangs": True})
    resp = client.get(url, headers={"Accept": "application/json"})
    resps.append(resp.status)
    langs = resp.json

    for lang in langs:
        url = endpoint + urlencode({"getobjs": "true"})
        resp = client.get(url, headers={"Accept": "application/json"})
        resps.append(resp.status)
        offices = resp.json
        for office in offices:
            # test without page
            url = endpoint + urlencode({"office": office, "lang": lang})
            resp = client.get(url).status
            resps.append(resp)
            resps += object_parts(client, url)
            # test with page
            url = endpoint + urlencode({"office": office, "lang": lang, "page": True})
            resp = client.get(url).status
            resps.append(resp)

    for office in offices:
        # test all possible language pairs
        for pair in combinations(langs, 2):
            url = endpoint + urlencode(
                {"office": office, "lang": pair[0], "trans": pair[1], "page": True}
            )
            resp = client.get(url).status
            resps.append(resp)

    assert all(x == "200 OK" for x in resps)


def test_office_endpoint(client):
    object_endpoint(client, "/office/")
