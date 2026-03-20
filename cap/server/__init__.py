from cap.server.contracts import (
    CAPVerbContract,
    CORE_VERB_CONTRACTS,
    GRAPH_MARKOV_BLANKET_CONTRACT,
    GRAPH_NEIGHBORS_CONTRACT,
    GRAPH_PATHS_CONTRACT,
    INTERVENE_DO_CONTRACT,
    META_CAPABILITIES_CONTRACT,
    OBSERVE_PREDICT_CONTRACT,
    TRAVERSE_CHILDREN_CONTRACT,
    TRAVERSE_PARENTS_CONTRACT,
)
from cap.server.responses import (
    CAPHandlerSuccessSpec,
    CAPProvenanceContext,
    CAPProvenanceHint,
    CAPRequestEnvelopeLike,
    build_cap_provenance,
    build_cap_success_response,
    build_handler_success,
    reduce_handler_success,
)
from cap.server.registry import CAPHandlerSurface, CAPVerbRegistry, DispatchSpec

_FASTAPI_EXPORTS = {
    "CAPAdapterError": ("cap.server.errors", "CAPAdapterError"),
    "build_cap_error_response": ("cap.server.errors", "build_cap_error_response"),
    "extract_cap_request_context": ("cap.server.errors", "extract_cap_request_context"),
    "register_cap_exception_handlers": ("cap.server.errors", "register_cap_exception_handlers"),
    "build_fastapi_cap_dispatcher": ("cap.server.fastapi", "build_fastapi_cap_dispatcher"),
}


def __getattr__(name: str) -> object:
    if name not in _FASTAPI_EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    module_name, attr_name = _FASTAPI_EXPORTS[name]
    try:
        module = __import__(module_name, fromlist=[attr_name])
    except ModuleNotFoundError as exc:
        if exc.name == "fastapi":
            raise ModuleNotFoundError(
                "cap.server FastAPI helpers require the optional 'server' dependency. "
                "Install it with `pip install \"cap-protocol[server]\"`."
            ) from exc
        raise

    value = getattr(module, attr_name)
    globals()[name] = value
    return value

__all__ = [
    "CAPAdapterError",
    "CAPHandlerSuccessSpec",
    "CAPHandlerSurface",
    "CAPProvenanceContext",
    "CAPProvenanceHint",
    "CAPRequestEnvelopeLike",
    "CAPVerbContract",
    "CAPVerbRegistry",
    "CORE_VERB_CONTRACTS",
    "DispatchSpec",
    "GRAPH_MARKOV_BLANKET_CONTRACT",
    "GRAPH_NEIGHBORS_CONTRACT",
    "GRAPH_PATHS_CONTRACT",
    "INTERVENE_DO_CONTRACT",
    "META_CAPABILITIES_CONTRACT",
    "OBSERVE_PREDICT_CONTRACT",
    "TRAVERSE_CHILDREN_CONTRACT",
    "TRAVERSE_PARENTS_CONTRACT",
    "build_fastapi_cap_dispatcher",
    "build_cap_provenance",
    "build_cap_error_response",
    "build_cap_success_response",
    "build_handler_success",
    "extract_cap_request_context",
    "reduce_handler_success",
    "register_cap_exception_handlers",
]
