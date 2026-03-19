from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol

from pydantic import BaseModel

from cap_protocol.core.constants import CAP_VERSION
from cap_protocol.core.contracts import CAPProvenance
from cap_protocol.core.envelopes import build_success_payload, normalize_request_id


class CAPRequestEnvelopeLike(Protocol):
    cap_version: str
    request_id: str | None
    verb: str


@dataclass(frozen=True)
class CAPProvenanceHint:
    algorithm: str
    graph_timestamp: str | None = None
    sample_size: int | None = None
    mechanism_family_used: str | None = None
    mechanism_model_version: str | None = None


@dataclass(frozen=True)
class CAPProvenanceContext:
    graph_version: str
    server_name: str
    server_version: str
    graph_timestamp: str | None = None
    cap_spec_version: str = CAP_VERSION


@dataclass(frozen=True)
class CAPHandlerSuccessSpec:
    result: BaseModel | dict[str, Any]
    provenance_hint: CAPProvenanceHint | None = None


def build_cap_success_response(
    *,
    payload: CAPRequestEnvelopeLike,
    result: BaseModel | dict[str, Any],
    provenance: BaseModel | dict[str, Any] | None = None,
) -> dict[str, Any]:
    result_payload = _model_dump(result)
    provenance_payload = _model_dump(provenance)
    return build_success_payload(
        cap_version=payload.cap_version,
        request_id=normalize_request_id(payload.request_id),
        verb=payload.verb,
        result=result_payload,
        provenance=provenance_payload,
    )


def build_handler_success(
    *,
    payload: CAPRequestEnvelopeLike,
    result: BaseModel | dict[str, Any],
    provenance: BaseModel | dict[str, Any] | None = None,
    provenance_factory: Callable[[], BaseModel | dict[str, Any] | None] | None = None,
) -> dict[str, Any]:
    if provenance is not None and provenance_factory is not None:
        raise ValueError("Provide provenance or provenance_factory, not both.")

    resolved_provenance = provenance_factory() if provenance_factory is not None else provenance
    return build_cap_success_response(
        payload=payload,
        result=result,
        provenance=resolved_provenance,
    )


def build_cap_provenance(
    *,
    context: CAPProvenanceContext,
    hint: CAPProvenanceHint,
    computation_time_ms: int,
) -> CAPProvenance:
    return CAPProvenance(
        algorithm=hint.algorithm,
        graph_version=context.graph_version,
        graph_timestamp=hint.graph_timestamp or context.graph_timestamp,
        sample_size=hint.sample_size,
        computation_time_ms=computation_time_ms,
        mechanism_family_used=hint.mechanism_family_used,
        mechanism_model_version=hint.mechanism_model_version,
        server_name=context.server_name,
        server_version=context.server_version,
        cap_spec_version=context.cap_spec_version,
    )


def reduce_handler_success(
    *,
    payload: CAPRequestEnvelopeLike,
    success: CAPHandlerSuccessSpec,
    request: Any,
    provenance_context: CAPProvenanceContext | None,
    computation_time_ms: int,
) -> dict[str, Any]:
    del request

    provenance = None
    if success.provenance_hint is not None:
        if provenance_context is None:
            raise ValueError("provenance_context is required when success includes provenance_hint.")
        provenance = build_cap_provenance(
            context=provenance_context,
            hint=success.provenance_hint,
            computation_time_ms=computation_time_ms,
        )

    return build_cap_success_response(
        payload=payload,
        result=success.result,
        provenance=provenance,
    )


def _model_dump(value: BaseModel | dict[str, Any] | None) -> dict[str, Any] | None:
    if value is None:
        return None
    if isinstance(value, BaseModel):
        return value.model_dump(exclude_none=True)
    return value

__all__ = [
    "CAPHandlerSuccessSpec",
    "CAPProvenanceContext",
    "CAPProvenanceHint",
    "CAPRequestEnvelopeLike",
    "build_cap_provenance",
    "build_cap_success_response",
    "build_handler_success",
    "reduce_handler_success",
]
