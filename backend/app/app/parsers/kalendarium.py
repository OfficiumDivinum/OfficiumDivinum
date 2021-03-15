import re
from pathlib import Path
from typing import Dict, Optional, Union

from devtools import debug

from app.DSL import months
from app.parsers.divinumofficium_structures import rank_table_by_calendar
from app.schemas import CommemorationCreate, FeastCreate

from .util import Line

rank_table = None
version = None

version_names = {"M": "monastic", "NC": "newcal", "1954": "DA", "1888": "1910"}


def get_version(fn: Path):
    global version, rank_table
    v = fn.stem[1:]
    try:
        version = version_names[v]
    except KeyError:
        version = v

    rank_table = rank_table_by_calendar[version]


def num(s: str) -> Union[int, str]:
    try:
        return int(s)
    except ValueError:
        return float(s)


def extract_line(line: str) -> Optional[Dict]:
    """Extract feast info from line."""

    line = line.strip()
    if line.startswith("*"):
        return None

    parts = line.split("=")
    date, alternative_date = parts[:2]
    data = {"date": date, "alternative_date": alternative_date, "feasts": []}
    line = "=".join(parts[2:])
    for match in re.findall(r"((.*?)=([0-9]+\.?[0-9]*)=*)", line):
        data["feasts"].append({"name": match[1], "rank": num(match[2])})
    return data


def parse_line(line: Line, language: str, fn: Path) -> Optional[FeastCreate]:
    """Parse a line of a divinumofficium calendar file."""

    data = extract_line(line.content)
    if not data:
        return None
    month, day = (int(x) for x in data["date"].split("-"))
    lineno = line.lineno
    feasts = sorted(data["feasts"], reverse=True, key=lambda x: x["rank"])

    for feast in feasts:
        if day == 0:
            feast.update(
                {"type_": "de Tempore", "datestr": "Sun between 2 Jan 5 Jan OR 2 Jan"}
            )
        else:
            feast.update(
                {
                    "type_": "Sanctorum",
                    "datestr": f"{day} {months[month - 1]}",
                }
            )
        feast.update(
            {
                "language": language,
                "version": version,
                "sourcefile": fn.name,
                "lineno": lineno,
            }
        )
        try:
            feast["rank_name"] = rank_table[feast["rank"]]
        except TypeError:
            feast["rank_name"] = rank_table[int(feast["rank"] + 0.5)]

        feast["rank_defeatable"] = True if isinstance(feast["rank"], float) else False

    commemorations = [CommemorationCreate(**x) for x in feasts[1:]]
    if not commemorations:
        commemorations = None

    feasts[0]["commemorations"] = commemorations
    return FeastCreate(**feasts[0])


def parse_file(fn: Path, language: str):
    """
    Parse a divinumofficium calendar file.

    Parameters
    ----------
    fn: Path : The file to parse.

    version: str : The version to use to generate feast names, etc.


    Returns
    -------
    A list of FeastCreate objects.
    """
    get_version(fn)
    year = []
    lines = (Line(i, x) for i, x in enumerate(fn.open().readlines()))
    for line in lines:
        parsed = parse_line(line, language, fn)
        if parsed:
            year.append(parsed)

    return year


def main():
    root = Path(
        "/home/john/code/OfficiumDivinum/divinum-officium/web/www/horas/Latin/Tabulae/"
    )
    for fn in root.glob("K*.txt"):
        debug(parse_file(fn, "Latin"))
