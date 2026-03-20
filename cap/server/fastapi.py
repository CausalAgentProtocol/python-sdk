from __future__ import annotations

from collections.abc import Awaitable, Callable
import time
from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from cap.core.errors import CAPErrorBody, CAPHTTPError
from cap.server.responses import (
    CAPHandlerSuccessSpec,
    CAPProvenanceContext,
    reduce_handler_success,
)
from cap.server.registry import CAPDispatchHandler, CAPVerbRegistry

def build_fastapi_cap_dispatcher(
    *,
    registry: CAPVerbRegistry,
    provenance_context_provider: (
        Callable[[Any, Request], CAPProvenanceContext | Awaitable[CAPProvenanceContext]] | None
    ) = None,
    success_reducer: (
        Callable[..., dict[str, Any] | Awaitable[dict[str, Any]]] | None
    ) = None,
) -> Callable[[dict[str, Any], Request], Awaitable[dict[str, Any]]]:
    async def _dispatch(payload: dict[str, Any], request: Request) -> dict[str, Any]:
        verb = payload.get("verb")
        if not isinstance(verb, str):
            raise CAPHTTPError(
                status_code=422,
                message="CAP request must include a string verb.",
                cap_error=CAPErrorBody(
                    code="invalid_request",
                    message="CAP request must include a string verb.",
                ),
            )

        spec = registry.get(verb)
        if spec is None:
            raise CAPHTTPError(
                status_code=400,
                message=f"verb={verb!r} is not supported by this CAP endpoint.",
                cap_error=CAPErrorBody(
                    code="verb_not_supported",
                    message=f"verb={verb!r} is not supported by this CAP endpoint.",
                    details={"supported_verbs": registry.supported_verbs},
                ),
            )

        try:
            typed_payload = spec.request_model.model_validate(payload)
        except ValidationError as exc:
            raise RequestValidationError(exc.errors()) from exc

        started_at = time.perf_counter()
        handler_output = await _call_handler(spec.handler, typed_payload, request)
        if isinstance(handler_output, CAPHandlerSuccessSpec):
            computation_time_ms = max(1, round((time.perf_counter() - started_at) * 1000))
            provenance_context = None
            if provenance_context_provider is not None:
                provenance_context = await _maybe_await(
                    provenance_context_provider(typed_payload, request)
                )
            active_success_reducer = success_reducer or reduce_handler_success
            response_payload = await _maybe_await(
                active_success_reducer(
                    payload=typed_payload,
                    success=handler_output,
                    request=request,
                    provenance_context=provenance_context,
                    computation_time_ms=computation_time_ms,
                )
            )
        else:
            response_payload = handler_output

        response = spec.response_model.model_validate(response_payload)
        return response.model_dump(exclude_none=True, by_alias=True)

    return _dispatch


async def _maybe_await(value: Any) -> Any:
    if isinstance(value, Awaitable):
        return await value
    return value


async def _call_handler(
    handler: CAPDispatchHandler,
    payload: Any,
    request: Request,
) -> Any:
    return await _maybe_await(handler(payload, request))
