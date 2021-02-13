"""Renderers for various formats."""
from flask import render_template
from flask import request
from flask_api.renderers import BaseRenderer


class objectHTMLRenderer(BaseRenderer):
    """
    Renderer for objects with .html() methods.

    This class is used to render objects: it can render any number of
    objects with an `html()` method.  Additionally, if the request is
    for a *page*, it wraps the output in a `page.html` template.  A
    special case is where the backend returns exactly two objects. Then
    we assume that one is a translation of the other, and return a page
    with translation footer.
    """

    media_type = 'text/html; charset="UTF-8"'

    def render(self, data, media_type, **options):
        print("Got here")
        args = request.args

        try:
            page = True if args["page"].lower() != "false" else False
        except KeyError:
            page = None

        # Force no page if it would make no sense
        if any((args.getlist(x) for x in ("part", "getparts"))):
            page = False

        if page:
            print(len(data))
            if len(data) == 2:
                content, translation = data
                content = content.html()
                translation = translation.html()
            else:
                content = " ".join([x.html() for x in data])
                translation = None
            page = {}
            page["title"] = data[0].name
            page["liturgical_day"] = data[0].liturgical_day
            page["calendar_day"] = data[0].calendar_day
            return render_template(
                "html/page.html", content=content, translation=translation, page=page
            )
        else:
            content = ""
            for thing in data:
                try:
                    content += thing.html()
                except AttributeError:
                    content += f" {thing} "
            return content
