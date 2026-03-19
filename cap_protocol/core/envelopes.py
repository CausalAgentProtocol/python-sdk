from __future__ import annotations

from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field

from cap_protocol.core.constants import CAP_VERSION


class CAPGraphRef(BaseModel):
    graph_id: str | None = None
    graph_version: str | None = None


class CAPRequestContext(BaseModel):
    graph_ref: CAPGraphRef | None = None


class CAPRequestOptions(BaseModel):
    timeout_ms: int | None = Field(default=None, ge=1)
    response_detail: Literal["summary", "full", "raw"] = "summary"


class CAPRequestBase(BaseModel):
    cap_version: Literal["0.2.2"] = CAP_VERSION
    request_id: str | None = None
    context: CAPRequestContext | None = None
    options: CAPRequestOptions = Field(default_factory=CAPRequestOptions)


class CAPResponseBase(BaseModel):
    cap_version: Literal["0.2.2"] = CAP_VERSION
    request_id: str
    verb: str
    status: Literal["success", "error"]


def normalize_request_id(request_id: str | None) -> str:
    return request_id or str(uuid4())


def build_success_payload(
    *,
    cap_version: str,
    request_id: str,
    verb: str,
    result: dict[str, Any],
    provenance: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "cap_version": cap_version,
        "request_id": normalize_request_id(request_id),
        "verb": verb,
        "status": "success",
        "result": result,
    }
    if provenance is not None:
        payload["provenance"] = provenance
    return payload


def build_error_payload(
    *,
    cap_version: str,
    request_id: str,
    verb: str,
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "cap_version": cap_version,
        "request_id": normalize_request_id(request_id),
        "verb": verb,
        "status": "error",
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
        },
    }
    return payload
