from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Literal, cast

from cap.core.capability_card import (
    CapabilityAccessTier,
    CapabilityDisclosurePolicy,
    CapabilityExtensionNamespace,
)
from cap.core.contracts import (
    MetaMethodsRequest,
    MetaMethodsParams,
    GraphMarkovBlanketParams,
    GraphMarkovBlanketRequest,
    GraphNeighborsParams,
    GraphNeighborsRequest,
    GraphPathsParams,
    GraphPathsRequest,
    InterveneDoParams,
    InterveneDoRequest,
    MetaCapabilitiesRequest,
    NarrateParams,
    NarrateRequest,
    ObservePredictParams,
    ObservePredictRequest,
    TraverseParams,
    TraverseChildrenRequest,
    TraverseParentsRequest,
)
from cap.core.envelopes import CAPGraphRef, CAPRequestContext, CAPRequestOptions


def _request_kwargs(
    *,
    request_id: str | None,
    options: CAPRequestOptions | None,
    graph_ref: CAPGraphRef | None,
) -> dict[str, Any]:
    kwargs: dict[str, Any] = {"request_id": request_id}
    if options is not None:
        kwargs["options"] = options
    if graph_ref is not None:
        kwargs["context"] = CAPRequestContext(graph_ref=graph_ref)
    return kwargs


def build_meta_capabilities_request(
    *,
    request_id: str | None = None,
    options: CAPRequestOptions | None = None,
) -> MetaCapabilitiesRequest:
    return MetaCapabilitiesRequest(
        **_request_kwargs(request_id=request_id, options=options, graph_ref=None)
    )


def build_meta_methods_request(
    *,
    verbs: Sequence[str] | None = None,
    detail: Literal["compact", "full"] = "compact",
    include_examples: bool = False,
    request_id: str | None = None,
    options: CAPRequestOptions | None = None,
) -> MetaMethodsRequest:
    kwargs = _request_kwargs(request_id=request_id, options=options, graph_ref=None)
    if verbs or detail != "compact" or include_examples:
        kwargs["params"] = MetaMethodsParams(
            verbs=list(verbs) if verbs is not None else None,
            detail=cast(Literal["compact", "full"], detail),
            include_examples=include_examples,
        )
    return MetaMethodsRequest(**kwargs)


def build_narrate_request(
    *,
    query: str,
    request_id: str | None = None,
    options: CAPRequestOptions | None = None,
) -> NarrateRequest:
    kwargs = _request_kwargs(request_id=request_id, options=options, graph_ref=None)
    kwargs["params"] = NarrateParams(query=query)
    return NarrateRequest(**kwargs)


def build_graph_neighbors_request(
    *,
    node_id: str,
    scope: Literal["parents", "children"],
    max_neighbors: int = 10,
    graph_ref: CAPGraphRef | None = None,
    request_id: str | None = None,
    options: CAPRequestOptions | None = None,
) -> GraphNeighborsRequest:
    kwargs = _request_kwargs(request_id=request_id, options=options, graph_ref=graph_ref)
    kwargs["params"] = GraphNeighborsParams(
        node_id=node_id,
        scope=cast(Literal["parents", "children"], scope),
        max_neighbors=max_neighbors,
    )
    return GraphNeighborsRequest(**kwargs)


def build_graph_markov_blanket_request(
    *,
    node_id: str,
    max_neighbors: int = 10,
    graph_ref: CAPGraphRef | None = None,
    request_id: str | None = None,
    options: CAPRequestOptions | None = None,
) -> GraphMarkovBlanketRequest:
    kwargs = _request_kwargs(request_id=request_id, options=options, graph_ref=graph_ref)
    kwargs["params"] = GraphMarkovBlanketParams(
        node_id=node_id,
        max_neighbors=max_neighbors,
    )
    return GraphMarkovBlanketRequest(**kwargs)


def build_graph_paths_request(
    *,
    source_node_id: str,
    target_node_id: str,
    max_paths: int = 3,
    graph_ref: CAPGraphRef | None = None,
    request_id: str | None = None,
    options: CAPRequestOptions | None = None,
) -> GraphPathsRequest:
    kwargs = _request_kwargs(request_id=request_id, options=options, graph_ref=graph_ref)
    kwargs["params"] = GraphPathsParams(
        source_node_id=source_node_id,
        target_node_id=target_node_id,
        max_paths=max_paths,
    )
    return GraphPathsRequest(**kwargs)


def build_observe_predict_request(
    *,
    target_node: str,
    graph_ref: CAPGraphRef | None = None,
    request_id: str | None = None,
    options: CAPRequestOptions | None = None,
) -> ObservePredictRequest:
    kwargs = _request_kwargs(request_id=request_id, options=options, graph_ref=graph_ref)
    kwargs["params"] = ObservePredictParams(target_node=target_node)
    return ObservePredictRequest(**kwargs)


def build_intervene_do_request(
    *,
    treatment_node: str,
    treatment_value: float,
    outcome_node: str,
    graph_ref: CAPGraphRef | None = None,
    request_id: str | None = None,
    options: CAPRequestOptions | None = None,
) -> InterveneDoRequest:
    kwargs = _request_kwargs(request_id=request_id, options=options, graph_ref=graph_ref)
    kwargs["params"] = InterveneDoParams(
        treatment_node=treatment_node,
        treatment_value=treatment_value,
        outcome_node=outcome_node,
    )
    return InterveneDoRequest(**kwargs)


def build_traverse_parents_request(
    *,
    node_id: str,
    top_k: int = 10,
    graph_ref: CAPGraphRef | None = None,
    request_id: str | None = None,
    options: CAPRequestOptions | None = None,
) -> TraverseParentsRequest:
    kwargs = _request_kwargs(request_id=request_id, options=options, graph_ref=graph_ref)
    kwargs["params"] = TraverseParams(
        node_id=node_id,
        top_k=top_k,
    )
    return TraverseParentsRequest(**kwargs)


def build_traverse_children_request(
    *,
    node_id: str,
    top_k: int = 10,
    graph_ref: CAPGraphRef | None = None,
    request_id: str | None = None,
    options: CAPRequestOptions | None = None,
) -> TraverseChildrenRequest:
    kwargs = _request_kwargs(request_id=request_id, options=options, graph_ref=graph_ref)
    kwargs["params"] = TraverseParams(
        node_id=node_id,
        top_k=top_k,
    )
    return TraverseChildrenRequest(**kwargs)


def build_capability_access_tier(
    *,
    tier: str,
    verbs: Sequence[str],
    hidden_fields: Sequence[str],
    response_detail: Literal["summary", "full", "raw"] = "summary",
) -> CapabilityAccessTier:
    return CapabilityAccessTier(
        tier=tier,
        verbs=list(verbs),
        response_detail=response_detail,
        hidden_fields=list(hidden_fields),
    )


def build_capability_disclosure_policy(
    *,
    hidden_fields: Sequence[str],
    notes: Sequence[str] = (),
    default_response_detail: Literal["summary", "full", "raw"] = "summary",
) -> CapabilityDisclosurePolicy:
    return CapabilityDisclosurePolicy(
        hidden_fields=list(hidden_fields),
        default_response_detail=default_response_detail,
        notes=list(notes),
    )


def build_extension_namespace(
    *,
    schema_url: str,
    verbs: Sequence[str],
    additional_params: Mapping[str, Mapping[str, str]] | None = None,
    additional_result_fields: Mapping[str, Mapping[str, str]] | None = None,
    notes: Sequence[str] = (),
) -> CapabilityExtensionNamespace:
    return CapabilityExtensionNamespace(
        schema_url=schema_url,
        verbs=list(verbs),
        additional_params={
            verb: dict(params) for verb, params in (additional_params or {}).items()
        },
        additional_result_fields={
            verb: dict(fields) for verb, fields in (additional_result_fields or {}).items()
        },
        notes=list(notes),
    )
