from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


CAPErrorCode = Literal[
    "invalid_request",
    "node_not_found",
    "path_not_found",
    "query_type_not_supported",
    "verb_not_supported",
    "invalid_intervention",
    "computation_timeout",
    "service_unavailable",
    "upstream_error",
]


class CAPErrorBody(BaseModel):
    code: CAPErrorCode
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class CAPErrorResponse(BaseModel):
    cap_version: Literal["0.3.0"]
    request_id: str
    verb: str
    status: Literal["error"] = "error"
    error: CAPErrorBody


class CAPHTTPError(Exception):
    def __init__(
        self,
        *,
        status_code: int,
        message: str,
        cap_error: CAPErrorBody | None = None,
        response_payload: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.cap_error = cap_error
        self.response_payload = response_payload or {}
