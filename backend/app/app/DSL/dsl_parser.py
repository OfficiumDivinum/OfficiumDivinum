"""
Parser for a very basic dsl to describe liturgical dates.  It has fixed methods:

>>> from officiumdivinum.DSL.dsl_parser import specials
>>> specials["Christmas"](2020)
datetime.date(2020, 12, 25)

>>> specials["Easter"](2020)
datetime.date(2020, 4, 12)

>>> specials["Lent"](2020)
datetime.date(2020, 3, 1)

>>> specials["Septuagesima"](2020)
datetime.date(2020, 2, 9)

>>> specials["Epiphany"](2021)
datetime.date(2021, 1, 6)

It also has a parser to turn expressions into dates.  Expressions should evaluate
to only one date in any one year.
"""

from datetime import date

from dateutil import easter
from dateutil.relativedelta import FR
from dateutil.relativedelta import MO
from dateutil.relativedelta import SA
from dateutil.relativedelta import SU
from dateutil.relativedelta import TH
from dateutil.relativedelta import TU
from dateutil.relativedelta import WE
from dateutil.relativedelta import relativedelta
from pyparsing import Group
from pyparsing import Optional
from pyparsing import Regex
from pyparsing import Word
from pyparsing import nums
from pyparsing import oneOf

try:
    from .util import days
    from .util import months
    from .util import ordinals
except ImportError:
    from util import days
    from util import months
    from util import ordinals


class DSLError(Exception):
    pass


weekdays = dict(zip(days, [SU, MO, TU, WE, TH, FR, SA]))

specials = {
    "Easter": easter.easter,
    "Lent": lambda year: easter.easter(year) + relativedelta(weeks=-6, weekday=SU),
    "Advent": lambda year: date(year, 12, 25) + relativedelta(weeks=-4, weekday=SU),
    "Epiphany": lambda year: date(year, 1, 6),
    "Christmas": lambda year: date(year, 12, 25),
    "Septuagesima": lambda year: easter.easter(year)
    + relativedelta(weeks=-9, weekday=SU),
    "Pentecost": lambda year: easter.easter(year) + relativedelta(weeks=7, weekday=SU),
}


def _parse_and(t):
    """Parse AND expression."""
    try:
        t[0]["rhs"]
        return t[0]["lhs"]
    except KeyError:
        return False


def _parse_or(t):
    """Evaluate OR t."""
    try:
        return t[0]["lhs"]
    except KeyError:
        try:
            return t[0]["rhs"]
        except KeyError:
            return False


def _parse_between(t):
    t = t[0]
    d1 = date.fromisoformat(t["date1"])
    d2 = date.fromisoformat(t["date2"])
    weekday = weekdays[t["day"]]
    solution = d1 + relativedelta(weekday=weekday)
    return str(solution) + " " if solution < d2 else "False "


def _parse_timedelta(t):
    t = t[0]
    try:
        cardinal = ordinals.index(t["ordinal"])
    except KeyError:
        cardinal = 1

    d = date.fromisoformat(t["date"])
    if t["delta"] == "before":
        cardinal = -cardinal
    weekday = weekdays[t["day"]]
    if cardinal == 0:
        return d + relativedelta(weekday=weekday)
    elif cardinal == 1:
        delta = d + relativedelta(weekday=weekday)
        if delta == d:
            return d + relativedelta(weeks=cardinal, weekday=weekday)
        else:
            return delta
    else:
        return d + relativedelta(weeks=cardinal, weekday=weekday)


def dsl_parser(datestr: str, year: int) -> date:
    """
    Parse dsl str for a given year.

    >>> from officiumdivinum.DSL.dsl_parser import dsl_parser
    >>> dsl_parser("Easter", 2020)
    datetime.date(2020, 4, 12)

    >>> dsl_parser("1 Jan", 2020)
    datetime.date(2020, 1, 1)

    >>> dsl_parser("Sun between 2 Jan 4 Jan OR 2 Jan", 2016)
    datetime.date(2016, 1, 3)

    >>> dsl_parser("Sun between 2 Jan 4 Jan OR 2 Jan", 2017)
    datetime.date(2017, 1, 2)

    >>> dsl_parser("22nd Sun after Pentecost", 2021)
    datetime.date(2021, 10, 24)

    Parameters
    ----------
    datestr: str : Expression to be parsed.

    year: int : Year in which to evaluate expression


    Returns
    -------
    date
        a date in the year in question.
    """

    # First we convert all possible date representations into isodate strings (yyyy-mm-dd)

    # convert specials
    special = oneOf(specials.keys())
    special.setParseAction(lambda t: str(specials[t[0]](year)) + " ")
    _specials = special[...]
    datestr = _specials.transformString(datestr)

    # convert yearless date expressions into dates
    yearless = Word(nums) + oneOf(months)
    yearless.setParseAction(
        lambda t: str(date(year, months.index(t[1]) + 1, int(t[0]))) + " "
    )
    _yearless = yearless[...]
    datestr = _yearless.transformString(datestr)

    # All dates are now isodates.
    isodate = Regex(r"[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]")

    # handle [ordinals] weekdays + timedeltas
    timedelta = Group(
        Optional(oneOf(ordinals))("ordinal")
        + oneOf(days)("day")
        + oneOf(["before", "after"])("delta")
        + isodate("date")
    )
    timedelta.setParseAction(_parse_timedelta)
    _timedeltas = timedelta[...]
    # datestr = _timedeltas.transformString(datestr)

    # handle betweens

    between = Group(
        Optional(oneOf(ordinals))("ordinal")
        + oneOf(days)("day")
        + "between"
        + isodate("date1")
        + isodate("date2")
    )

    between.setParseAction(_parse_between)
    _betweens = between[...]
    _betweens += _timedeltas
    count = 0
    while any(x in datestr for x in ("after", "before", "between")):
        datestr = _betweens.transformString(datestr)
        if count > 10:
            raise DSLError(f"Recursion limit reached, got as far as {datestr}")
        count += 1

    # At this point we only have calendar dates, components of date
    # expressions ('before', 'after', 'on or before' or 'on or after';
    # ordinal weekdays and 'between' expressions) and operators ('AND'
    # 'OR', 'NOT').  Since operators operate on the *logical status*
    # of operands, and this logical status is False if the operand
    # doesn't evaluate to a date, and otherwise a calendar date, we
    # deal with them last.

    # Then we build parsers for individual objects

    # fail here if we match anything except isodates, 'or' or 'and'
    # illegal = ~(isodate | oneOf(["OR", "AND"]))[1...]

    # At this point the datestr is composed entirely of evaluated date
    # expressions split by logical operators.  We reduce these by looping over them.

    count = 0
    while "OR" in datestr:
        or_expr = Group((isodate("lhs") ^ "False") + "OR" + (isodate("rhs") ^ "False"))
        or_expr.setParseAction(_parse_or)
        _or_expr = or_expr[...]
        datestr = _or_expr.transformString(datestr)
        if count > 10:
            raise DSLError(f"Recursion limit reached, got as far as {datestr}")
        count += 1

    count = 0
    while "AND" in datestr:
        and_expr = Group(
            (isodate("lhs") ^ "False") + "AND" + (isodate("rhs") ^ "False")
        )
        and_expr.setParseAction(_parse_and)
        _and_expr = and_expr[...]
        datestr = _and_expr.transformString(datestr)
        if count > 10:
            raise DSLError(f"Recursion limit reached, got as far as {datestr}")
        count += 1

    # convert dates to datetime.date() objects
    isodate.setParseAction(lambda s, l, t: date.fromisoformat(t[0]))
    _isodates = isodate[...]
    parsed = _isodates.parseString(datestr)
    try:
        return parsed[0]
    except IndexError:
        raise DSLError("Unable to parse")


if __name__ == "__main__":
    import doctest

    doctest.testmod()
