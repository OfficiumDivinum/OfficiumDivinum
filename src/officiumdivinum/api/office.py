"""
Endpoint to serve complete offices.

This endpoint serves complete offices, and any legitimate bits of
them.  Queries may be either in json or as html queries.  The response
is negotiated according to the `Accept:` header of the request, and
currently supports either `application/json` (for serialised objects)
or `text/html` (for rendered objects).

Note that requesting parts of an office automatically suppresses
requesting a page.
"""
from datetime import datetime

from flask import Blueprint
from flask import abort
from flask import request
from flask_api.decorators import set_renderers
from flask_api.renderers import JSONRenderer

from . import database
from .renderers import objectHTMLRenderer

office = Blueprint("office", __name__, url_prefix="/office")


def get_partlist(things):
    """Get list of parts of any object."""
    partlist = []
    for thing in things:
        partlist += list(thing.__dict__.keys())
    return partlist


@office.route("/", methods=["GET"])
@set_renderers(JSONRenderer, objectHTMLRenderer)
def get_office():
    args = request.args

    offices = ["prime"]
    langs = ["latin"]

    if args.getlist("getobjs"):
        return offices

    if args.getlist("getlangs"):
        return langs

    try:
        office = args["office"]
    except KeyError:
        abort(400)

    if office not in offices:
        abort(404)

    language = args["lang"] if "lang" in args.keys() else "latin"
    if language not in langs:
        abort(404)

    translation = (
        args["trans"] if "lang" in args.keys() and "trans" in args.keys() else None
    )
    date = args["date"] if "date" in args.keys() else str(datetime.now().date())
    calendar = args["calendar"] if "calendar" in args.keys() else "1962"
    if not calendar == "1962":
        abort(404)

    things = database.get_office(office, calendar, date, language, translation)

    if args.getlist("getparts"):
        return get_partlist(things)

    parts = args.getlist("part")
    if not parts:
        return things

    else:
        disjointed_members = []
        for part in parts:
            for thing in things:
                obj = getattr(thing, part)
                if not isinstance(obj, list):
                    disjointed_members.append(getattr(thing, part))
                else:
                    disjointed_members += obj
        return disjointed_members
