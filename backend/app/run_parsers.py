import os
from getpass import getpass
from pathlib import Path

import typer
from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session

from app.parsers import M2obj

# required if uploading to localhost, as https not setup locally
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

translations = {"latin": {"martyrology_title": "Martyrologium"}}


def crud_login(host="localhost", user="admin@2e0byo.co.uk"):
    oauth = OAuth2Session(client=LegacyApplicationClient(client_id=None))
    token = oauth.fetch_token(
        token_url=f"{host}/api/v1/login/access-token",
        username=user,
        password=getpass(),
    )
    return OAuth2Session(token=token)


def crud_pokemon(
    lang: str,
    calendar: str,
    root: str,
    user: str,
    host: str = "http://localhost",
):
    """
    Catch them all!

    Get all the relevant data for a particular calendar from a
    supplied root (which should be a cloned divinumofficium
    repository's web directory.)

    Parameters
    ----------

    lang: str : The language, e.g. `Latin`.

    calendar: str : The calendar.

    root: str : The root, as a string.

    Returns
    -------
    List
        Lists of Feast and Martyrology objects.
    """
    print("Logging in.")

    client = crud_login(host=host, user=user)

    print("Parsing source files.")

    root = Path(f"{root}/{lang}").expanduser()
    title = translations[lang]["martyrology_title"]
    parse_upload_martyrologies(client, root, host, lang, title)


def parse_upload_martyrologies(
    client,
    root: Path,
    host: str,
    lang: str,
    title: str,
):
    """Parse and upload martyrologies."""
    martyrology = []
    for f in (root / "Martyrologium").glob("*.txt"):
        if f.name == "Mobile.txt":
            martyrology += M2obj.parse_mobile_file(f)
        else:
            martyrology.append(M2obj.parse_file(f))

    # get correct template str
    endpoint = f"{host}/api/v1/martyrology/old-date-template/"
    templates = client.get(endpoint, params={"skip": 0, "limit": 100}).json()
    template_id = None
    for i in templates:
        if i["language"] == lang.lower():
            template_id = i["id"]
    if not template_id:
        raise Exception(f"No template found for {lang}")

    print("Uploading Martyrologies to server.")

    with typer.progressbar(martyrology) as progress:
        for entry in progress:
            if "julian_date" not in entry.keys():
                entry["julian_date"] = None
            endpoint = f"{host}/api/v1/martyrology/"
            data = {
                "title": title,
                "rubrics": None,
                "parts": [],
                "datestr": entry["datestr"],
                "language": lang.lower(),
                "old_date_template_id": template_id,
                "julian_date": entry["julian_date"],
            }
            for par in entry["content"]:
                data["parts"].append(
                    {"prefix": None, "suffix": None, "rubrics": None, "content": par}
                )
            resp = client.post(endpoint, json=data)
            if resp.status_code != 200:
                raise Exception(f"Failed to upload, response was {resp.json()}")


if __name__ == "__main__":
    typer.run(crud_pokemon)
