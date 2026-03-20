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


META_CAPABILITIES_CONTRACT = CAPVerbContract(
    verb="meta.capabilities",
    request_model=MetaCapabilitiesRequest,
    response_model=MetaCapabilitiesResponse,
)
OBSERVE_PREDICT_CONTRACT = CAPVerbContract(
    verb="observe.predict",
    request_model=ObservePredictRequest,
    response_model=ObservePredictResponse,
)
INTERVENE_DO_CONTRACT = CAPVerbContract(
    verb="intervene.do",
    request_model=InterveneDoRequest,
    response_model=InterveneDoResponse,
)
GRAPH_NEIGHBORS_CONTRACT = CAPVerbContract(
    verb="graph.neighbors",
    request_model=GraphNeighborsRequest,
    response_model=GraphNeighborsResponse,
)
GRAPH_MARKOV_BLANKET_CONTRACT = CAPVerbContract(
    verb="graph.markov_blanket",
    request_model=GraphMarkovBlanketRequest,
    response_model=GraphMarkovBlanketResponse,
)
GRAPH_PATHS_CONTRACT = CAPVerbContract(
    verb="graph.paths",
    request_model=GraphPathsRequest,
    response_model=GraphPathsResponse,
)
TRAVERSE_PARENTS_CONTRACT = CAPVerbContract(
    verb="traverse.parents",
    request_model=TraverseParentsRequest,
    response_model=TraverseResponse,
)
TRAVERSE_CHILDREN_CONTRACT = CAPVerbContract(
    verb="traverse.children",
    request_model=TraverseChildrenRequest,
    response_model=TraverseResponse,
)

CORE_VERB_CONTRACTS = {
    contract.verb: contract
    for contract in (
        META_CAPABILITIES_CONTRACT,
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
    "OBSERVE_PREDICT_CONTRACT",
    "TRAVERSE_CHILDREN_CONTRACT",
    "TRAVERSE_PARENTS_CONTRACT",
]
