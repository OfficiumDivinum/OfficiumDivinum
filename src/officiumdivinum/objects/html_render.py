import flask


def render_template(template, **kwargs):
    app = flask.current_app
    try:
        return flask.render_template(template, **kwargs)
    except Exception:
        with app.app_context(), app.test_request_context():
            return flask.render_template(template, **kwargs)
