# from .update_server import *  # noqa
from pathlib import Path

import jinja2
from flask_api import FlaskAPI
from markdown import markdown

from .bible import get_verses  # noqa
from .martyrology import *  # noqa
from .office import *  # noqa
from .test_api import test_api_page  # noqa


def markdown_no_p(text):
    """Wrap text in markdown without wrapping it in paragaph tags."""

    md = markdown(text)
    p = "<p>"
    end_p = "</p>"
    if md.startswith(p) and md.endswith(end_p):
        md = md[3:-4]
    return jinja2.Markup(md)


def create_app(test_config=None):
    """Create and configure flask app."""
    app = FlaskAPI(__name__, instance_relative_config=True)
    app.jinja_env.filters["markdown"] = markdown_no_p
    app.config.from_mapping(
        SECRET_KEY="dev",
        APP_DATABASE=Path(app.instance_path) / "officiumdivinum.sqlite",
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    with Path("/tmp/instance").open("w") as f:
        f.write(app.instance_path)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    from . import database

    database.init(app)

    from .bible import bible
    from .martyrology import martyrology
    from .office import office
    from .test_api import test_page
    from .update_server import update_server

    app.register_blueprint(office)
    app.register_blueprint(test_page)
    app.register_blueprint(martyrology)
    app.register_blueprint(bible)
    app.register_blueprint(update_server)

    @app.route("/hello")
    def hello():
        return "hello world"

    return app
