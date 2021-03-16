import logging
import os
from getpass import getpass
from json import JSONDecodeError, dumps
from pathlib import Path
from typing import List, Optional

import typer
from devtools import debug
from fastapi.encoders import jsonable_encoder
from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session

from app.parsers import (
    M2obj,
    P2obj,
    T2obj,
    divinumofficium_structures,
    hymn,
    kalendarium,
)
from app.parsers.chickenfeed import (
    guess_version,
    parse_generic_file,
    parse_prayers_txt,
    parse_translations,
)
from app.parsers.util import EmptyFileError
from app.schemas import MartyrologyCreate, OldDateTemplateCreate, OrdinalsCreate

logger = logging.getLogger(__name__)
verbose = 0
testing = None

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


def upload(things, endpoint: str, client, test_token_headers=None):
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
                debug(jsonable_encoder(entry))
            if not client:  # we are testing
                continue
            if test_token_headers:
                resp = client.post(
                    endpoint, json=jsonable_encoder(entry), headers=test_token_headers
                )
            else:

                resp = client.post(endpoint, json=jsonable_encoder(entry))
            if resp.status_code != 200:
                try:
                    msg = dumps(resp.json(), indent=2)
                except JSONDecodeError:
                    msg = f"{resp.content} + {resp.status_code}"
                raise Exception(f"Failed to upload, response was {msg}")


@app.command()
def parse_upload(
    root: Path,
    lang: str,
    version: str,
    user: Optional[str] = None,
    host: str = "http://localhost",
    martyrologies: Optional[bool] = None,
    psalms: Optional[bool] = None,
    temporal: Optional[bool] = None,
    sanctoral: Optional[bool] = None,
    hymns: Optional[bool] = None,
    pokemon: Optional[bool] = None,
    verbosity: int = 0,
    test: Optional[bool] = None,
):
    """
    Parse and upload something.

    Args:
      root: Path: Root dir containing DO sources (before the Language)
      lang: str: Language.
      version: str: Version to use, e.g. 1960.
      user: str: Username at server.
      host: str: Hostname of server. (Default value = "http://localhost")
      martyrologies: Optional[bool]:  Parse Martyrologies. (Default value = None)
      psalms: Optional[bool]:  Parse Psalms. (Default value = None)
      temporal: Optional[bool]:  Parse Temporal. (Default value = None)
      sanctoral: Optional[bool]:  Parse Sanctoral. (Default value = None)
      hymns: Optional[bool]:  Parse Hymns. (Default value = None)
      pokemon: Optional[bool]:  Parse everything, unless explicitly disabled.  (Default value=None)
      verbosity: int:  How much to print out.
      test: Optional[bool]: Testing mode (skips login and upload).


    Returns:
    """
    global verbose, testing
    verbose = verbosity

    things = [martyrologies, psalms]
    if not things:
        logger.info("No output requested")
        return

    if not test:
        client = crud_login(host=host, user=user)
    else:
        testing = True
        client = None

    functionality = {
        "martyrologies": martyrologies,
        "psalms": psalms,
        "temporal": temporal,
        "sanctoral": sanctoral,
        "hymns": hymns,
    }

    if pokemon:
        for k in functionality.keys():
            functionality[k] = True if functionality[k] is not False else False

    if functionality["martyrologies"]:
        parse_upload_martyrologies(root, lang, version, client, host)

    if functionality["psalms"]:
        parse_upload_psalms(root, lang, version, client, host)

    if functionality["temporal"]:
        parse_upload_temporal(root, lang, version, client, host)

    if functionality["sanctoral"]:
        parse_upload_sanctoral(root, lang, version, client, host)

    if functionality["hymns"]:
        parse_upload_hymns(root, lang, version, client, host)


def parse_upload_martyrologies(
    root: Path,
    lang: str,
    version: str,
    client: OAuth2Session,
    host: str,
    test_token_headers=None,
    **kwargs,
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
    martyrologies = []
    for f in files:
        if f.name == "Mobile.txt":
            martyrologies += M2obj.parse_mobile_file(f, lang.lower(), title)
        else:
            martyrologies.append(M2obj.parse_file(f, lang.lower(), title))

    # get correct template str
    if not testing:
        endpoint = f"{host}/api/v1/martyrology/old-date-template/"
        template_id = None
        while not template_id:
            logger.info("getting templates")
            if not test_token_headers:
                resp = client.get(endpoint, params={"skip": 0, "limit": 100})
            else:
                resp = client.get(
                    endpoint,
                    params={"skip": 0, "limit": 100},
                    headers=test_token_headers,
                )
            templates = resp.json()
            print(templates)
            for i in templates:
                if i["language"] == lang.lower():
                    template_id = i["id"]
            if not template_id:
                template = translations[lang.lower()]["old_date_template"]
                logger.info("Pushing template")
                upload([template], endpoint, client, test_token_headers)
    else:
        template = translations[lang.lower()]["old_date_template"]
        template_id = None

    for i in range(len(martyrologies)):
        if template_id:
            martyrologies[i].old_date_template_id = template_id
        else:
            martyrologies[i].old_date_template = template

    # martyrology = martyrology[:1]

    logger.info("Uploading Martyrologies to server.")

    endpoint = f"{host}/api/v1/martyrology/"
    upload(martyrologies, endpoint, client, test_token_headers)

    return martyrologies


def parse_upload_psalms(
    root: Path,
    lang: str,
    version: str,
    client: OAuth2Session,
    host: str,
    test_token_headers=None,
    **kwargs,
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
    upload(verses, endpoint, client, test_token_headers)

    return psalms


def parse_upload_temporal(
    root: Path,
    lang: str,
    version: str,
    client: OAuth2Session,
    host: str,
    test_token_headers=None,
    **kwargs,
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

    endpoint = f"{host}/api/v1/calendar/feast/"
    upload(feasts, endpoint, client, test_token_headers)

    return feasts


def parse_upload_sanctoral(
    root: Path,
    lang: str,
    version: str,
    client: OAuth2Session,
    host: str,
    test_token_headers=None,
    **kwargs,
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
    feasts = kalendarium.parse_file(fn, lang)

    logger.info("Uploading Feasts to server.")

    endpoint = f"{host}/api/v1/calendar/feast/"
    upload(feasts, endpoint, client, test_token_headers)

    return feasts


def parse_upload_hymns(
    root: Path,
    lang: str,
    version: str,
    client: OAuth2Session,
    host: str,
    test_token_headers=None,
    **kwargs,
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
    candidates = [
        "Commune",
        "CommuneM",
        "Sancti",
        "SanctiM",
        "Tempora",
        "TemporaM" "Ordinarium",
    ]

    # candidates = ["CommuneM"]
    generators = [(root / f"{lang}/{i}").glob("*.txt") for i in candidates]

    hymns = []
    for fns in generators:
        for fn in fns:
            resp = hymn.parse_file(fn, lang, version)
            if resp:
                hymns += resp
    # debug(hymns)

    logger.info("Uploading Hymns to server.")

    endpoint = f"{host}/api/v1/hymn/"
    upload(hymns, endpoint, client, test_token_headers)

    return hymns


def parse_martyrology_file(fn: Path, lang: str) -> MartyrologyCreate:

    title = translations[lang.lower()]["martyrology_title"]
    return M2obj.parse_file(fn, lang.lower(), title)


def all_langs(root: Path) -> List[str]:
    """Get all versions from Linguae.txt."""
    return (root / "Linguae.txt").open().readlines()


def guess_psalm_version(fn) -> str:
    lang = fn.parent.parent.name
    if lang == "Latin":
        if fn.parent.name == "PiusXII":
            return "PiusXII"
        else:
            return "clementine"
    else:
        return lang  # should probably have lookup table here


@app.command()
def parser_test(
    root: Path,
    lang: str,
) -> None:

    import typer

    parse_prayers_txt(root, lang)

    root = root / lang
    things = []

    versions = ["1570", "1910", "1955", "1960", "newcal", "DA", "monastic"]
    for version in versions:
        print(f"Parsing for version {version}")

        # conceptually cleaner and faster to do the psalms + martyrology + translate + kalendars first.
        success = []
        failed = []
        errors = []
        martyrologies = []
        translate = []
        calendars = []
        psalms = []

        skip = []

        print("Parsing translations.")
        for fn in (
            root / "Psalterium/Translate.txt",
            root / "Psalterium/Revtrans.txt",
        ):
            skip.append(fn)
            translate.append(parse_translations(fn, lang))

        print("Parsing Martyrologies.")
        with typer.progressbar(list((root / "Martyrologium").glob("**/*.txt"))) as fns:
            for fn in fns:
                skip.append(fn)
                martyrologies.append(parse_martyrology_file(fn, lang))

        print("Parsing Calendars.")
        with typer.progressbar(list((root / "Tabulae/").glob("K*.txt"))) as fns:
            for fn in fns:
                skip.append(fn)
                calendars.append(kalendarium.parse_file(fn, lang))

        print("Parsing Psalms.")
        with typer.progressbar(list(root.glob("/psalms1/*.txt"))) as fns:
            for fn in fns:

                skip.append(fn)
                version = guess_psalm_version(fn)
                psalms.append(P2obj.parse_file(fn, lang, version))
        try:
            with typer.progressbar(list(root.glob("/PiusXII/*.txt"))) as fns:
                for fn in fns:
                    skip.append(fn)
                    version = guess_psalm_version(fn)
                    psalms.append(P2obj.parse_file(fn, lang, version))
        except Exception as e:
            print(e)

        fns = list(root.glob("**/*.txt"))
        fns = [i for i in fns if not i in skip]
        with typer.progressbar() as fns:
            for fn in fns:
                try:
                    things.append(parse_generic_file(Path(fn), version, lang))
                    success.append(fn)
                except (FileNotFoundError, EmptyFileError):
                    pass
                except Exception as e:
                    errors.append(e)
                    failed.append(fn)

        print(
            f"Parsed {(f:=len(failed)) + (s:=len(success))} files of which {s*100/(s+f)}% parsed"
        )
        for i, fn in enumerate(failed):
            print(fn)
            print(f"Errors: {errors[i]}")

    debug(len(things))

    return things, success, errors, failed


if __name__ == "__main__":
    app()
