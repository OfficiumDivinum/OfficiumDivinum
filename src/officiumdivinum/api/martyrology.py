from datetime import datetime
from datetime import timedelta

import dateutil.parser as dp
from flask import Blueprint
from flask import jsonify
from flask import request
from flask_api.decorators import set_renderers
from flask_api.renderers import JSONRenderer

from . import database
from .office import get_partlist
from .renderers import objectHTMLRenderer

martyrology = Blueprint("martyrolgy", __name__, url_prefix="/martyrology")


def json_query(day, table):
    old_date, martyrology = database.martyrology_query(day, table)
    return jsonify({"old_date": old_date, "content": martyrology})


@martyrology.route("/", methods=["GET"])
@set_renderers(JSONRenderer, objectHTMLRenderer)
def get_martyrology():
    args = request.args
    try:
        day = dp.parse(args["date"])
    except KeyError:
        day = datetime.now() + timedelta(days=1)
    day = day.date()

    try:
        if args["type"] == "json":
            return json_query(day, "martyrology")
    except KeyError:
        pass

    martyrology = [database.martyrology_query(day, "martyrology")]

    if args.getlist("getparts"):
        return get_partlist(martyrology)

    return martyrology
