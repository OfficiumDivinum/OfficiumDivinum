import logging
import os
from getpass import getpass
from json import dumps
from pathlib import Path

import typer
from fastapi.encoders import jsonable_encoder
from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session

from app.parsers import M2obj, P2obj, divinumofficium_structures
from app.schemas import OldDateTemplateCreate, OrdinalsCreate

logger = logging.getLogger(__name__)

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
    logger.info("Logging in.")
    oauth = OAuth2Session(client=LegacyApplicationClient(client_id=None))
    token = oauth.fetch_token(
        token_url=f"{host}/api/v1/login/access-token",
        username=user,
        password=getpass(),
    )
    return OAuth2Session(token=token)


@app.command()
def parse_upload_martyrologies(
    root: Path,
    lang: str,
    version: str,
    user: str,
    host: str = "http://localhost",
):
    """Parse and upload martyrologies."""

    client = crud_login(host=host, user=user)

    logger.info("Parsing source files.")

    title = translations[lang.lower()]["martyrology_title"]

    root = root / lang
    with_cal = root / f"Martyrologium{version}"
    files = list(with_cal.glob("*.txt"))
    if not files:
        files = (root / "Martyrologium").glob("*.txt")
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

    logger.info("Uploading Martyrologies to server.")

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
    root: Path,
    lang: str,
    version: str,
    user: str,
    host: str = "http://localhost",
):

    client = crud_login(host=host, user=user)

    logger.info("Parsing psalm files")
    psalms = []
    for fn in (root / f"{lang}/psalms1").glob("*.txt"):
        psalms.append(P2obj.parse_file(fn, lang, version))

    logger.info("Uploading Psalms to server.")

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
