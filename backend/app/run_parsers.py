import logging
import os
from getpass import getpass
from json import dumps
from pathlib import Path
from typing import Optional

import typer
from devtools import debug
from fastapi.encoders import jsonable_encoder
from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session

from app.parsers import H2obj, K2obj, M2obj, P2obj, T2obj, divinumofficium_structures
from app.schemas import OldDateTemplateCreate, OrdinalsCreate

logger = logging.getLogger(__name__)
verbose = 0

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
    """

    Args:
      host: (Default value = "localhost")
      user: (Default value = "admin@2e0byo.co.uk")

    Returns:

    """
    logger.info("Logging in.")
    oauth = OAuth2Session(client=LegacyApplicationClient(client_id=None))
    token = oauth.fetch_token(
        token_url=f"{host}/api/v1/login/access-token",
        username=user,
        password=getpass(),
    )
    return OAuth2Session(token=token)


def upload(things, endpoint: str, client):
    """
    Upload to server.

    Args:
      things: Things to upload
      endpoint: str: Endpoint to use
      client: Client

    Returns:
    """

    with typer.progressbar(things) as progress:
        for entry in progress:
            if verbose > 1:
                print(dumps(jsonable_encoder(entry), indent=2))
            resp = client.post(endpoint, json=jsonable_encoder(entry))
            if resp.status_code != 200:
                raise Exception(
                    f"Failed to upload, response was {dumps(resp.json(), indent=2)}"
                )


def parse_upload_martyrologies(
    root: Path, lang: str, version: str, client: OAuth2Session, host: str
):
    """
    Parse and upload Martyrologies.

    Args:
      root: Path: Root path.
      lang: str: Language.
      version: str: Version.
      client: OAuth2Session:  Client for server.
      host: str: Server url.
      root: Path:
      lang: str:
      version: str:
      client: OAuth2Session:
      host: str:

    Returns:
    """
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

    endpoint = f"{host}/api/v1/martyrology/"
    upload(martyrology, endpoint, client)


@app.command()
def parse_upload(
    root: Path,
    lang: str,
    version: str,
    user: str,
    host: str = "http://localhost",
    martyrologies: Optional[bool] = None,
    psalms: Optional[bool] = None,
    temporal: Optional[bool] = None,
    sanctoral: Optional[bool] = None,
    hymns: Optional[bool] = None,
    verbosity: int = 0,
):
    """
    Parse and upload something.

    Args:
      root: Path: Root dir containing DO sources (before the Language)
      lang: str: Language.
      version: str: Version to use, e.g. 1960.
      user: str: Username at server.
      host: str: Hostname of server. (Default value = "http://localhost")
      martyrologies: Optional[Bool]:  Parse Martyrologies. (Default value = None)
      psalms: Optional[Bool]:  Parse Psalms. (Default value = None)

    Returns:
    """
    global verbose
    verbose = verbosity

    things = [martyrologies, psalms]
    if not things:
        logger.info("No output requested")
        return

    # client = crud_login(host=host, user=user)
    client = None

    if martyrologies:
        parse_upload_martyrologies(root, lang, version, client, host)

    if psalms:
        parse_upload_psalms(root, lang, version, client, host)

    if temporal:
        parse_upload_temporal(root, lang, version, client, host)

    if sanctoral:
        parse_upload_sanctoral(root, lang, version, client, host)

    if hymns:
        parse_upload_hymns(root, lang, version, client, host)


def parse_upload_psalms(
    root: Path, lang: str, version: str, client: OAuth2Session, host: str
):
    """
    Parse and upload psalms.

    Args:
      root: Path: Root path.
      lang: str: Language.
      version: str: Version.
      client: OAuth2Session:  Client for server.
      host: str: Server url.

    Returns:
    """

    logger.info("Parsing psalm files")
    psalms = []
    for fn in (root / f"{lang}/psalms1").glob("*.txt"):
        psalms.append(P2obj.parse_file(fn, lang, version))

    logger.info("Uploading Psalms to server.")

    verses = []
    for psalm in psalms:
        verses += psalm
    endpoint = f"{host}/api/v1/bible/"
    upload(verses, endpoint, client)


def parse_upload_temporal(
    root: Path, lang: str, version: str, client: OAuth2Session, host: str
):
    """
    Parse and upload Temporal.

    Args:
      root: Path: Root path.
      lang: str: Language.
      version: str: Version.
      client: OAuth2Session:  Client for server.
      host: str: Server url.

    Returns:
    """

    logger.info("Parsing Temporal files")
    feasts = []
    for fn in (root / f"{lang}/Tempora/").glob("*.txt"):
        resp = T2obj.parse_file(fn, lang, version)
        if not resp:
            continue
        else:
            feasts.append(resp)

    logger.info("Uploading Feasts to server.")

    endpoint = f"{host}/api/v1/calendar/feast"
    upload(feasts, endpoint, client)


def parse_upload_sanctoral(
    root: Path, lang: str, version: str, client: OAuth2Session, host: str
):
    """
    Parse and upload Sanctoral.

    Args:
      root: Path: Root path.
      lang: str: Language.
      version: str: Version.
      client: OAuth2Session:  Client for server.
      host: str: Server url.

    Returns:
    """

    logger.info("Parsing Sanctoral files")
    fn = root / f"{lang}/Tabulae/K{version}.txt"
    feasts = K2obj.parse_file(fn, lang, version)

    logger.info("Uploading Feasts to server.")

    endpoint = f"{host}/api/v1/calendar/feast"
    upload(feasts, endpoint, client)


def parse_upload_hymns(
    root: Path, lang: str, version: str, client: OAuth2Session, host: str
):
    """
    Parse and upload Hymns.

    Args:
      root: Path: Root path.
      lang: str: Language.
      version: str: Version.
      client: OAuth2Session:  Client for server.
      host: str: Server url.

    Returns:
    """
    logger.info("Parsing files and extracting all Hymns")
    for fn in (root / f"{lang}/Tempora").glob("*.txt"):
        H2obj.parse_file(fn, lang, version)

    # logger.info("Uploading Hymns to server.")

    # endpoint = f"{host}/api/v1/calendar/feast"
    # upload(feasts, endpoint, client)


if __name__ == "__main__":
    app()
