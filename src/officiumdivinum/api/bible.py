from flask import Blueprint
from flask import abort
from flask import current_app
from flask import request
from flask_api.decorators import set_renderers
from flask_api.renderers import BrowsableAPIRenderer
from flask_api.renderers import JSONRenderer

from ..bible import Vulgate
from .renderers import objectHTMLRenderer

bible = Blueprint("bible", __name__, url_prefix="/bible")

# from .errors import InvalidInput

versions = {"vulgate": Vulgate("Sixto-Clementine Vulgate")}


@bible.route("/", methods=["Get"])
@set_renderers(JSONRenderer, objectHTMLRenderer, BrowsableAPIRenderer)
def get_verses():

    query = request.get_json()
    if not query:
        args = request.args
        bible = versions[args["version"]]
        if not bible.content:
            bible.load(current_app)

        try:
            start = args["start"]
            end = args["end"] if "end" in args.keys() else None
            verses = bible.get_range(start, end)
            return verses

        except Exception:
            abort(400)

    else:
        print(query)

        bible = versions[query["version"]]
        if not bible.content:
            bible.load(current_app)
        verses = []
        try:
            for book, chapter, verse in query["verses"]:
                verses.append(bible.content[book][chapter][verse])
        except KeyError:
            pass

        try:
            start = query["start"]
            end = query["end"] if "end" in query.keys() else None
            verses += bible.get_range(start, end)
        except KeyError:
            pass

        if not verses:
            abort(400)

        return verses
