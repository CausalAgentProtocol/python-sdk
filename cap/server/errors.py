from __future__ import annotations

import json
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from cap.core.envelopes import build_error_payload, normalize_request_id
from cap.core.errors import CAPErrorBody, CAPErrorCode, CAPHTTPError


class CAPAdapterError(Exception):
    def __init__(
        self,
        code: CAPErrorCode,
        message: str,
        *,
        status_code: int,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}


async def extract_cap_request_context(request: Request) -> dict[str, str]:
    body = await request.body()
    payload: dict[str, Any] = {}
    if body:
        try:
            payload = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            payload = {}

    cap_version = (
        payload.get("cap_version") if isinstance(payload.get("cap_version"), str) else "0.2.2"
    )
    request_id = normalize_request_id(
        payload.get("request_id") if isinstance(payload.get("request_id"), str) else None
    )
    verb = payload.get("verb") if isinstance(payload.get("verb"), str) else "unknown"
    return {
        "cap_version": cap_version,
        "request_id": request_id,
        "verb": verb,
    }


def build_cap_error_response(
    *,
    status_code: int,
    context: dict[str, str],
    code: CAPErrorCode,
    message: str,
    details: dict[str, Any] | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=build_error_payload(
            cap_version=context["cap_version"],
            request_id=context["request_id"],
            verb=context["verb"],
            code=code,
            message=message,
            details=details,
        ),
    )


def register_cap_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(CAPHTTPError)
    async def _cap_http_error_handler(request: Request, exc: CAPHTTPError) -> JSONResponse:
        if exc.response_payload:
            return JSONResponse(status_code=exc.status_code, content=exc.response_payload)

        context = await extract_cap_request_context(request)
        cap_error = exc.cap_error or CAPErrorBody(code="upstream_error", message=str(exc))
        return build_cap_error_response(
            status_code=exc.status_code,
            context=context,
            code=cap_error.code,
            message=cap_error.message,
            details=cap_error.details,
        )

    @app.exception_handler(CAPAdapterError)
    async def _cap_adapter_error_handler(request: Request, exc: CAPAdapterError) -> JSONResponse:
        context = await extract_cap_request_context(request)
        return build_cap_error_response(
            status_code=exc.status_code,
            context=context,
            code=exc.code,
            message=exc.message,
            details=exc.details,
        )

    @app.exception_handler(RequestValidationError)
    async def _cap_validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        context = await extract_cap_request_context(request)
        return build_cap_error_response(
            status_code=422,
            context=context,
            code="invalid_request",
            message="CAP request validation failed.",
            details={"errors": exc.errors()},
        )


__all__ = [
    "CAPAdapterError",
    "build_cap_error_response",
    "extract_cap_request_context",
    "register_cap_exception_handlers",
]
