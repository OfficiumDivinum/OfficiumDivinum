"""Parse Divinumofficium's calendar tabulae into feast objects."""
from pathlib import Path

from devtools import debug

from app.DSL import months
from app.parsers.divinumofficium_structures import rank_table_by_calendar
from app.schemas import CommemorationCreate, FeastCreate


def parse_line(line: str, language: str, version: str, fn: Path) -> FeastCreate:
    """Parse a line of a divinumofficium calendar file."""

    line = line.strip()
    if line.startswith("*"):
        return None
    rank_table = rank_table_by_calendar[version]

    parts = line.split("=")
    date, duplicate_date, name, rank = parts[:4]
    try:
        rank_name = rank_table[int(rank)]
        defeatable = False
    except ValueError:
        rank_name = rank_table[int(float(rank) + 0.5)]
        defeatable = True

    month, day = (int(x) for x in date.split("-"))
    if day == 0:
        Type = "de Tempore"
        datestr = "Sun between 2 Jan 5 Jan OR 2 Jan"
    else:
        Type = "Sanctorum"
        datestr = f"{day} {months[month - 1]}"

    commemorations = None

    if len(parts) > 5 and parts[4]:
        commemorations = []
        commemoration_rank = None
        commemoration_rank_name = "Feria"
        for part in parts[4:]:
            try:
                commemoration_rank = float(part)  # noqa
                try:
                    commemoration_rank_name = rank_table[int(part)]
                    commemoration_defeatable = False
                except ValueError:
                    commemoration_rank_name = rank_table[int(float(part) + 0.5)]
                    commemoration_defeatable = True
            except ValueError:
                commemorations.append(part)

        commemorations = [
            CommemorationCreate(
                name=x,
                rank_name=commemoration_rank_name,
                rank_defeatable=commemoration_defeatable,
                language=language,
                version=version,
                datestr=datestr,
                sourcefile=fn.name,
            )
            for x in commemorations
        ]

    qualifiers = None
    if date != duplicate_date:
        qualifiers = duplicate_date[:-1]

    if qualifiers:
        print(qualifiers)

    a = FeastCreate(
        rank_name=rank_name,
        datestr=datestr,
        version=version,
        type_=Type,
        commemorations=commemorations,
        rank_defeatable=defeatable,
        language=language,
        sourcefile=fn.name,
    )
    return a


def parse_file(fn: Path, language: str, version: str):
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
    year = []
    with fn.open() as f:
        for line in f.readlines():
            parsed = parse_line(line, language, version, fn)
            if parsed:
                year.append(parsed)

    return year
