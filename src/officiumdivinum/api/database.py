"""
Handle database querying.

By abstracting it here we can just use dicts for testing.
"""
import copy
from datetime import timedelta
from pathlib import Path
from typing import Union

import dateutil.parser as dp
import jsonpickle
from flask import current_app

from ..objects import Prime
from ..objects import datastructures  # needed for unpickling.
from .translations import invariants

martyrology = []


def eval_year(year, yearless):
    """

    Parameters
    ----------
    year :

    yearless :

    as_list :
        (Default value = True)

    Returns
    -------


    """
    yeared = {}
    for row in yearless:
        if not row:
            continue
        try:
            date = row.date.resolve(year)
        except AttributeError:
            print(row)
        try:
            yeared[date].append(row)
        except KeyError:
            yeared[date] = [row]

    return yeared


def load_martyrology(app):
    """"""
    global martyrology
    p = Path("martyrology.json")
    if not p.exists():
        p = Path(app.root_path) / p
    with p.open() as f:
        raw_tables["martyrology"] = jsonpickle.decode(
            f.read(), classes=[datastructures.Date, datastructures.Martyrology]
        )


def load_psalms(app):
    """"""

    p = Path(app.root_path) / Path("psalms.json")
    with p.open() as f:
        try:
            raw_tables["psalms"]
        except KeyError:
            raw_tables["psalms"] = {}

        raw_tables["psalms"]["latin"] = jsonpickle.decode(
            f.read(), classes=[datastructures.Psalm, datastructures.Verse]
        )


years = {}

year_tables = {"martyrology": None}
raw_tables = {}


def assemble_martyrology(candidates: list, year: int):
    """
    Assemble and resolve martyrolgy (easy, as we just stuff them together.)

    Parameters
    ----------
    candidates : list : candidates for the day.

    year : int : year.

    Returns
    -------
    """
    extra_info = []
    for candidate in candidates:
        try:
            old_date, content = candidate.render(year)
            template = copy.copy(candidate)
        except AttributeError:
            extra_info += candidate.content

    template.content = extra_info + content
    template.year = year
    return template


def raw_query(day, table):
    """
    Query table for data on day.

    Parameters
    ----------
    day :

    table :


    Returns
    -------
    """
    global raw_tables, year_tables
    year = day.year
    try:
        return year_tables[table][year][day]
    except (KeyError, TypeError):
        this_year = eval_year(year, raw_tables[table])
        try:
            year_tables[table][year] = this_year
        except (KeyError, TypeError):
            year_tables[table] = {year: this_year}
        return year_tables[table][year][day]


def martyrology_query(day, table):
    """

    Parameters
    ----------
    day :

    table :


    Returns
    -------


    """
    candidates = raw_query(day, table)
    return assemble_martyrology(candidates, day.year)


def init(app):
    """Start database."""
    load_martyrology(app)
    load_psalms(app)


def get_psalm(psalm, language, start=None, stop=None):
    psalm = raw_tables["psalms"][language][f"Psalm{psalm}"]
    if not stop and not start:
        return psalm
    else:
        verses = []
        for verse in psalm.verses:
            if verse.number >= start and verse.number <= stop:
                verses.append(verse)
        psalm.verses = verses
        return psalm


def get_office(
    office: str,
    calendar: str,
    datestr: str,
    language: str,
    translation: Union[str, None],
):
    """
    Get a particular office by calendar date.

    Note that this currently just returns a made-up prime office.

    Parameters
    ----------
    office : str : Office name to get.

    calendar : str : Calendar to use.

    datestr : str : Date (as string, to parse with dateutils).

    language: str : Main Language.

    translation: Union[str : Second Language.

    None] : Or not


    Returns
    -------
    Office
          An object based on Office() for the relevant office.
    """
    inv = invariants[language]
    today = dp.parse(datestr).date()
    tomorrow = today + timedelta(days=1)

    office = Prime(
        "Ad Primam",
        language,
        datastructures.Incipit(
            "Incipit", [inv["deus in adjutorium"], inv["gloria"], inv["laus tibi"]]
        ),
        inv["iam lucis"],
        datastructures.Antiphon(
            "Misericordia tua, * Domine ante oculos meos: et complacui in veritate tua."
        ),
        [
            get_psalm("25", language),
            get_psalm("51", language),
            get_psalm("52", language),
        ],
        [inv["christe, fili dei per annum"], inv["exurge christe per annum"]],
        martyrology_query(tomorrow, "martyrology"),
        datastructures.Reading(
            "Lectio Brevis",
            "2 Thess 3:5",
            [
                datastructures.StrObj(
                    "Dóminus autem dírigat corda et córpora nostra in caritáte Dei et patiéntia Christi."
                )
            ],
        ),
        inv,
    )
    office.liturgical_day = "Feria Quarta"
    office.calendar_day = "10 Februarius MMXXI"

    if translation:
        translation = copy.copy(office)

        return [office, translation]
    else:
        return [office]
