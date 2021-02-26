import schemathesis

from app.main import app

schemathesis.fixups.install()
schema = schemathesis.from_asgi("/api/v1/openapi.json", app)


@schema.parametrize()
def test_api(case, superuser_token_headers):
    case.headers = case.headers or {}
    case.headers.update(superuser_token_headers)
    response = case.call_asgi()
    case.validate_response(response)
