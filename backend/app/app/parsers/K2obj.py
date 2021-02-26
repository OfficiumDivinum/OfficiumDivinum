"""Parse Divinumofficium's calendar tabulae into feast objects."""

from pathlib import Path

from app.DSL import months
from app.DSL.divinumofficium_structures import rank_table_by_calendar
from app.schemas import CommemorationCreate, FeastCreate


def parse_line(line: str, version: str) -> FeastCreate:
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

    commemorations = None

    if len(parts) > 5 and parts[4]:
        commemorations = []
        commemoration_rank = None
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
                commemorations.append(
                    CommemorationCreate(
                        name=part,
                        rank_name=commemoration_rank_name,
                        defeatable=commemoration_defeatable,
                    )
                )

    qualifiers = None
    if date != duplicate_date:
        qualifiers = duplicate_date[:-1]

    if qualifiers:
        print(qualifiers)

    month, day = (int(x) for x in date.split("-"))
    if day == 0:
        Type = "de Tempore"
        datestr = "Sun between 2 Jan 5 Jan OR 2 Jan"
    else:
        Type = "Sanctorum"
        datestr = f"{day} {months[month - 1]}"
    return FeastCreate(
        rank_name=rank_name,
        datestr=datestr,
        version=version,
        type_=Type,
        commemorations=commemorations,
        defeatable=defeatable,
    )


def parse_file(fn: Path, version: str):
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
            parsed = parse_line(line, version)
            if parsed:
                year.append(parsed)

    return year
