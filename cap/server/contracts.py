from __future__ import annotations

from dataclasses import dataclass

from pydantic import BaseModel

from cap.core.contracts import (
    GraphMarkovBlanketRequest,
    GraphMarkovBlanketResponse,
    GraphNeighborsRequest,
    GraphNeighborsResponse,
    GraphPathsRequest,
    GraphPathsResponse,
    InterveneDoRequest,
    InterveneDoResponse,
    MetaCapabilitiesRequest,
    MetaCapabilitiesResponse,
    MetaMethodsRequest,
    MetaMethodsResponse,
    NarrateRequest,
    NarrateResponse,
    ObservePredictRequest,
    ObservePredictResponse,
    TraverseChildrenRequest,
    TraverseParentsRequest,
    TraverseResponse,
)


@dataclass(frozen=True)
class CAPVerbContract:
    verb: str
    request_model: type[BaseModel]
    response_model: type[BaseModel]
    description: str | None = None


META_CAPABILITIES_CONTRACT = CAPVerbContract(
    verb="meta.capabilities",
    request_model=MetaCapabilitiesRequest,
    response_model=MetaCapabilitiesResponse,
    description="Return the CAP capability card through the standard CAP response envelope.",
)
META_METHODS_CONTRACT = CAPVerbContract(
    verb="meta.methods",
    request_model=MetaMethodsRequest,
    response_model=MetaMethodsResponse,
    description="Return machine-readable method metadata for the verbs supported by this CAP endpoint.",
)
NARRATE_CONTRACT = CAPVerbContract(
    verb="narrate",
    request_model=NarrateRequest,
    response_model=NarrateResponse,
    description="Return a narrative causal read for a free-text query.",
)
OBSERVE_PREDICT_CONTRACT = CAPVerbContract(
    verb="observe.predict",
    request_model=ObservePredictRequest,
    response_model=ObservePredictResponse,
    description="Return an observational prediction for one target node.",
)
INTERVENE_DO_CONTRACT = CAPVerbContract(
    verb="intervene.do",
    request_model=InterveneDoRequest,
    response_model=InterveneDoResponse,
    description="Return one interventional claim for one treatment and one selected outcome.",
)
GRAPH_NEIGHBORS_CONTRACT = CAPVerbContract(
    verb="graph.neighbors",
    request_model=GraphNeighborsRequest,
    response_model=GraphNeighborsResponse,
    description="Return immediate structural neighbors for a requested node.",
)
GRAPH_MARKOV_BLANKET_CONTRACT = CAPVerbContract(
    verb="graph.markov_blanket",
    request_model=GraphMarkovBlanketRequest,
    response_model=GraphMarkovBlanketResponse,
    description="Return the Markov blanket for a requested node.",
)
GRAPH_PATHS_CONTRACT = CAPVerbContract(
    verb="graph.paths",
    request_model=GraphPathsRequest,
    response_model=GraphPathsResponse,
    description="Return causal paths between two nodes.",
)
TRAVERSE_PARENTS_CONTRACT = CAPVerbContract(
    verb="traverse.parents",
    request_model=TraverseParentsRequest,
    response_model=TraverseResponse,
    description="Return parent node identifiers as a thin convenience traversal surface.",
)
TRAVERSE_CHILDREN_CONTRACT = CAPVerbContract(
    verb="traverse.children",
    request_model=TraverseChildrenRequest,
    response_model=TraverseResponse,
    description="Return child node identifiers as a thin convenience traversal surface.",
)

CORE_VERB_CONTRACTS = {
    contract.verb: contract
    for contract in (
        META_CAPABILITIES_CONTRACT,
        META_METHODS_CONTRACT,
        NARRATE_CONTRACT,
        OBSERVE_PREDICT_CONTRACT,
        INTERVENE_DO_CONTRACT,
        GRAPH_NEIGHBORS_CONTRACT,
        GRAPH_MARKOV_BLANKET_CONTRACT,
        GRAPH_PATHS_CONTRACT,
        TRAVERSE_PARENTS_CONTRACT,
        TRAVERSE_CHILDREN_CONTRACT,
    )
}

__all__ = [
    "CAPVerbContract",
    "CORE_VERB_CONTRACTS",
    "GRAPH_NEIGHBORS_CONTRACT",
    "GRAPH_MARKOV_BLANKET_CONTRACT",
    "GRAPH_PATHS_CONTRACT",
    "INTERVENE_DO_CONTRACT",
    "META_CAPABILITIES_CONTRACT",
    "META_METHODS_CONTRACT",
    "NARRATE_CONTRACT",
    "OBSERVE_PREDICT_CONTRACT",
    "TRAVERSE_CHILDREN_CONTRACT",
    "TRAVERSE_PARENTS_CONTRACT",
]
