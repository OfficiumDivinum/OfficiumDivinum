import pytest
import schemathesis
from hypothesis import settings

from app.main import app

schemathesis.fixups.install()


@schemathesis.hooks.register
def before_load_schema(context, raw_schema):
    """Remove the /users endpoint entirely, as we test that elsewhere, and trashing the
    first user doesn't help."""
    print(raw_schema["paths"].keys())

    del raw_schema["paths"]["/api/v1/users/"]


schema = schemathesis.from_asgi("/api/v1/openapi.json", app)

schema.add_link(
    source=schema["/api/v1/items/"]["POST"],
    target=schema["/api/v1/items/{id}"]["GET"],
    status_code="201",
    parameters={"id": "$response.body#/id"},
)


@schema.parametrize()
@pytest.mark.xfail(
    reason="Some operations not yet working with schemathesis", strict=False
)
@settings(max_examples=10)
def test_api(case, superuser_token_headers):
    case.headers = case.headers or {}
    case.headers.update(superuser_token_headers)
    response = case.call_asgi()
    case.validate_response(response)
