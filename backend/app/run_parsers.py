import os
from getpass import getpass
from json import dumps
from pathlib import Path
from typing import List

import typer
from fastapi.encoders import jsonable_encoder
from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session

from app.parsers import M2obj, P2obj, divinumofficium_structures
from app.schemas import OldDateTemplateCreate, OrdinalsCreate

app = typer.Typer()

# required if uploading to localhost, as https not setup locally
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

translations = {
    "latin": {
        "martyrology_title": "Martyrologium",
        "old_date_template": OldDateTemplateCreate(
            content="{{julian_date}} Luna {{ordinals[age] | capitalize}} Anno Domini {{year}}",
            language="latin",
            ordinals=OrdinalsCreate(
                language="latin",
                content=divinumofficium_structures.latin_feminine_ordinals,
            ),
        ),
    }
}


def crud_login(host="localhost", user="admin@2e0byo.co.uk"):
    oauth = OAuth2Session(client=LegacyApplicationClient(client_id=None))
    token = oauth.fetch_token(
        token_url=f"{host}/api/v1/login/access-token",
        username=user,
        password=getpass(),
    )
    return OAuth2Session(token=token)


@app.command()
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
    with_cal = root / f"Martyrologium{calendar}"
    files = list(with_cal.glob("*.txt"))
    if not files:
        files = (root / "Martyrologium").glob("*.txt")
    title = translations[lang.lower()]["martyrology_title"]
    parse_upload_martyrologies(client, files, host, lang, title)


def parse_upload_martyrologies(
    client,
    files: List[Path],
    host: str,
    lang: str,
    title: str,
):
    """Parse and upload martyrologies."""
    martyrology = []
    for f in files:
        if f.name == "Mobile.txt":
            martyrology += M2obj.parse_mobile_file(f, lang.lower(), title)
        else:
            martyrology.append(M2obj.parse_file(f, lang.lower(), title))

    # get correct template str
    # endpoint = f"{host}/api/v1/martyrology/old-date-template/"
    # try:
    #     resp = client.get(endpoint, params={"skip": 0, "limit": 100})
    #     templates = resp.json()
    # except JSONDecodeError:
    #     print(resp.raw)
    #     templates = []
    # template_id = None
    # for i in templates:
    #     if i["language"] == lang.lower():
    #         template_id = i["id"]
    # if not template_id:
    template_id = None
    template = translations[lang.lower()]["old_date_template"]

    # martyrology = martyrology[:1]

    print("Uploading Martyrologies to server.")

    with typer.progressbar(martyrology) as progress:
        for entry in progress:
            endpoint = f"{host}/api/v1/martyrology/"
            if template_id:
                entry.old_date_template_id = template_id
            else:
                entry.old_date_template = template
            # print(dumps(jsonable_encoder(entry), indent=2))
            resp = client.post(endpoint, json=jsonable_encoder(entry))
            if resp.status_code != 200:
                raise Exception(
                    f"Failed to upload, response was {dumps(resp.json(), indent=2)}"
                )


@app.command()
def parse_upload_psalms(
    lang: str,
    version: str,
    root: Path,
    user: str,
    host: str = "http://localhost",
):
    print("Logging in.")

    client = crud_login(host=host, user=user)

    print("Parsing psalm files")
    psalms = []
    for fn in (root / f"{lang}/psalms1").glob("*.txt"):
        psalms.append(P2obj.parse_file(fn, lang, version))

    print("Uploading Psalms to server.")

    verses = []
    for psalm in psalms:
        verses += psalm

    with typer.progressbar(verses) as progress:
        for entry in progress:
            endpoint = f"{host}/api/v1/bible/"
            # print(dumps(jsonable_encoder(entry), indent=2))
            resp = client.post(endpoint, json=jsonable_encoder(entry))
            if resp.status_code != 200:
                raise Exception(
                    f"Failed to upload, response was {dumps(resp.json(), indent=2)}"
                )


if __name__ == "__main__":
    app()
