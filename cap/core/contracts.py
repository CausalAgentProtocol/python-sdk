from __future__ import annotations

from typing import Generic, Literal, TypeVar

from pydantic import BaseModel, Field

from cap.core.capability_card import CapabilityCard
from cap.core.envelopes import CAPRequestBase, CAPResponseBase


class CAPProvenance(BaseModel):
    algorithm: str
    graph_version: str
    graph_timestamp: str | None = None
    sample_size: int | None = None
    computation_time_ms: int
    mechanism_family_used: str | None = None
    mechanism_model_version: str | None = None
    server_name: str
    server_version: str
    cap_spec_version: Literal["0.2.2"]


class SemanticHonestyFields(BaseModel):
    reasoning_mode: str
    identification_status: str
    assumptions: list[str] = Field(default_factory=list)


ResultT = TypeVar("ResultT")


class CAPSuccessResponse(CAPResponseBase, Generic[ResultT]):
    status: Literal["success"] = "success"
    result: ResultT


class CAPProvenancedSuccessResponse(CAPSuccessResponse[ResultT], Generic[ResultT]):
    provenance: CAPProvenance


class MetaCapabilitiesRequest(CAPRequestBase):
    verb: Literal["meta.capabilities"] = "meta.capabilities"


class MetaCapabilitiesResponse(CAPSuccessResponse[CapabilityCard]):
    verb: Literal["meta.capabilities"] = "meta.capabilities"


class ObservePredictParams(BaseModel):
    target_node: str = Field(min_length=1)


class ObservePredictRequest(CAPRequestBase):
    verb: Literal["observe.predict"] = "observe.predict"
    params: ObservePredictParams


class ObservePredictResult(BaseModel):
    target_node: str
    prediction: float
    drivers: list[str] = Field(default_factory=list)


class ObservePredictResponse(CAPProvenancedSuccessResponse[ObservePredictResult]):
    verb: Literal["observe.predict"] = "observe.predict"


class InterveneDoParams(BaseModel):
    treatment_node: str = Field(min_length=1)
    treatment_value: float
    outcome_node: str = Field(min_length=1)


class InterveneDoRequest(CAPRequestBase):
    verb: Literal["intervene.do"] = "intervene.do"
    params: InterveneDoParams


class InterveneDoResult(SemanticHonestyFields):
    outcome_node: str
    effect: float


class InterveneDoResponse(CAPProvenancedSuccessResponse[InterveneDoResult]):
    verb: Literal["intervene.do"] = "intervene.do"


class GraphNeighbor(BaseModel):
    node_id: str
    roles: list[Literal["parent", "child", "spouse"]] = Field(default_factory=list)


class GraphNeighborsParams(BaseModel):
    node_id: str = Field(min_length=1)
    scope: Literal["parents", "children"]
    max_neighbors: int = Field(default=10, ge=0, le=100)


class GraphNeighborsRequest(CAPRequestBase):
    verb: Literal["graph.neighbors"] = "graph.neighbors"
    params: GraphNeighborsParams


class GraphNeighborsResult(SemanticHonestyFields):
    node_id: str
    scope: Literal["parents", "children"]
    neighbors: list[GraphNeighbor] = Field(default_factory=list)
    total_candidate_count: int | None = None
    truncated: bool = False
    edge_semantics: str | None = None


class GraphNeighborsResponse(CAPProvenancedSuccessResponse[GraphNeighborsResult]):
    verb: Literal["graph.neighbors"] = "graph.neighbors"


class GraphMarkovBlanketParams(BaseModel):
    node_id: str = Field(min_length=1)
    max_neighbors: int = Field(default=10, ge=0, le=100)


class GraphMarkovBlanketRequest(CAPRequestBase):
    verb: Literal["graph.markov_blanket"] = "graph.markov_blanket"
    params: GraphMarkovBlanketParams


class GraphMarkovBlanketResult(SemanticHonestyFields):
    node_id: str
    neighbors: list[GraphNeighbor] = Field(default_factory=list)
    total_candidate_count: int | None = None
    truncated: bool = False
    edge_semantics: str | None = None


class GraphMarkovBlanketResponse(CAPProvenancedSuccessResponse[GraphMarkovBlanketResult]):
    verb: Literal["graph.markov_blanket"] = "graph.markov_blanket"


class TraverseParams(BaseModel):
    node_id: str = Field(min_length=1)
    top_k: int = Field(default=10, ge=0, le=100)


class TraverseRequestBase(CAPRequestBase):
    params: TraverseParams


class TraverseParentsRequest(TraverseRequestBase):
    verb: Literal["traverse.parents"] = "traverse.parents"


class TraverseChildrenRequest(TraverseRequestBase):
    verb: Literal["traverse.children"] = "traverse.children"


class TraverseResult(SemanticHonestyFields):
    node_id: str
    direction: Literal["parents", "children"]
    nodes: list[str] = Field(default_factory=list)


class TraverseResponse(CAPProvenancedSuccessResponse[TraverseResult]):
    verb: Literal["traverse.parents", "traverse.children"]


class GraphPathsParams(BaseModel):
    source_node_id: str = Field(min_length=1)
    target_node_id: str = Field(min_length=1)
    max_paths: int = Field(default=3, ge=1, le=20)


class GraphPathsRequest(CAPRequestBase):
    verb: Literal["graph.paths"] = "graph.paths"
    params: GraphPathsParams


class GraphPathNode(BaseModel):
    node_id: str
    node_name: str
    node_type: str
    domain: str


class GraphPathEdge(BaseModel):
    from_node_id: str
    to_node_id: str
    edge_type: str


class GraphPath(BaseModel):
    distance: int
    nodes: list[GraphPathNode] = Field(default_factory=list)
    edges: list[GraphPathEdge] = Field(default_factory=list)


class GraphPathsResult(SemanticHonestyFields):
    source_node_id: str
    target_node_id: str
    connected: bool
    path_count: int
    paths: list[GraphPath] = Field(default_factory=list)


class GraphPathsResponse(CAPProvenancedSuccessResponse[GraphPathsResult]):
    verb: Literal["graph.paths"] = "graph.paths"
