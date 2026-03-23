from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, field_validator

from cap.server.errors import register_cap_exception_handlers


class _Payload(BaseModel):
    count: int

    @field_validator("count")
    @classmethod
    def validate_count(cls, value: int) -> int:
        if value < 1:
            raise ValueError("count must be at least 1")
        return value


def test_validation_errors_are_json_safe() -> None:
    app = FastAPI()
    register_cap_exception_handlers(app)

    async def cap_endpoint(payload: _Payload) -> dict[str, int]:
        return {"count": payload.count}

    app.add_api_route("/cap", cap_endpoint, methods=["POST"])

    client = TestClient(app)
    response = client.post(
        "/cap",
        json={
            "cap_version": "0.2.2",
            "request_id": "req-validate",
            "verb": "graph.paths",
            "count": 0,
        },
    )

    assert response.status_code == 422
    payload = response.json()
    assert payload["error"]["code"] == "invalid_request"
    assert payload["error"]["details"]["errors"]
    ctx = payload["error"]["details"]["errors"][0].get("ctx", {})
    assert isinstance(ctx.get("error"), str)
