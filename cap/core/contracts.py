from __future__ import annotations

from typing import Annotated, Generic, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field, JsonValue

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
    cap_spec_version: Literal["0.3.0"]


class SemanticHonestyFields(BaseModel):
    reasoning_mode: str
    identification_status: str
    assumptions: list[str] = Field(default_factory=list)


ResultT = TypeVar("ResultT")
MetaMethodDetail = Literal["compact", "full"]


class CAPSuccessResponse(CAPResponseBase, Generic[ResultT]):
    status: Literal["success"] = "success"
    result: ResultT


class CAPProvenancedSuccessResponse(CAPSuccessResponse[ResultT], Generic[ResultT]):
    provenance: CAPProvenance


class MetaCapabilitiesRequest(CAPRequestBase):
    verb: Literal["meta.capabilities"] = "meta.capabilities"


class MetaCapabilitiesResponse(CAPSuccessResponse[CapabilityCard]):
    verb: Literal["meta.capabilities"] = "meta.capabilities"


class CAPMethodFieldDescriptor(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    description: str | None = None
    required: bool
    value_type: str | None = None
    items_type: str | None = None
    enum: list[JsonValue] | None = None
    default: JsonValue | None = None
    min_length: int | None = None
    max_length: int | None = None
    minimum: int | float | None = None
    maximum: int | float | None = None
    examples: list[JsonValue] | None = None


class CAPMethodDescriptor(BaseModel):
    model_config = ConfigDict(extra="forbid")

    verb: str
    surface: Literal["core", "convenience", "extension"]
    description: str | None = None
    arguments: list[CAPMethodFieldDescriptor] = Field(default_factory=list)
    result_fields: list[CAPMethodFieldDescriptor] = Field(default_factory=list)


class MetaMethodsResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    methods: list[CAPMethodDescriptor] = Field(default_factory=list)


class MetaMethodsParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    verbs: list[str] | None = Field(
        default=None,
        description="Specific CAP verbs to describe. Omit or pass an empty list to allow the server to return every supported method.",
    )
    detail: MetaMethodDetail = Field(
        default="compact",
        description="How much per-field metadata to include in the method description payload.",
    )
    include_examples: bool = Field(
        default=False,
        description="Whether to include example values in the returned argument and result-field metadata.",
    )


class MetaMethodsRequest(CAPRequestBase):
    verb: Literal["meta.methods"] = "meta.methods"
    params: MetaMethodsParams | None = None


class MetaMethodsResponse(CAPSuccessResponse[MetaMethodsResult]):
    verb: Literal["meta.methods"] = "meta.methods"


class NarrateParams(BaseModel):
    query: Annotated[
        str,
        Field(
            min_length=1,
            description="Free-text query for a narrative read.",
            json_schema_extra={"examples": ["Why is NVDA moving?"]},
        ),
    ]


class NarrateRequest(CAPRequestBase):
    verb: Literal["narrate"] = "narrate"
    params: NarrateParams


class NarrateResult(BaseModel):
    narrative: Annotated[
        str,
        Field(description="Primary narrative summary returned by the server."),
    ]
    reasoning_mode: str | None = None
    identification_status: str | None = None
    assumptions: list[str] = Field(default_factory=list)


class NarrateResponse(CAPSuccessResponse[NarrateResult]):
    verb: Literal["narrate"] = "narrate"
    provenance: CAPProvenance | None = None


class ObservePredictParams(BaseModel):
    target_node: Annotated[
        str,
        Field(
            min_length=1,
            description="Node identifier to predict under the server's observational mode.",
            json_schema_extra={"examples": ["NVDA_close"]},
        ),
    ]


class ObservePredictRequest(CAPRequestBase):
    verb: Literal["observe.predict"] = "observe.predict"
    params: ObservePredictParams


class ObservePredictResult(BaseModel):
    target_node: Annotated[
        str,
        Field(description="Node identifier that the returned prediction corresponds to."),
    ]
    prediction: Annotated[
        float,
        Field(description="Predicted observational value for the requested target node."),
    ]
    drivers: Annotated[
        list[str],
        Field(
            default_factory=list,
            description="Driver node identifiers surfaced by the server as the main explanatory contributors.",
        ),
    ]


class ObservePredictResponse(CAPProvenancedSuccessResponse[ObservePredictResult]):
    verb: Literal["observe.predict"] = "observe.predict"


class InterveneDoParams(BaseModel):
    treatment_node: Annotated[
        str,
        Field(
            min_length=1,
            description="Node identifier to intervene on.",
            json_schema_extra={"examples": ["DXY_close"]},
        ),
    ]
    treatment_value: Annotated[
        float,
        Field(
            description="Interventional value applied to the treatment node.",
            json_schema_extra={"examples": [1.0]},
        ),
    ]
    outcome_node: Annotated[
        str,
        Field(
            min_length=1,
            description="Outcome node identifier whose effect estimate should be returned.",
            json_schema_extra={"examples": ["BTCUSD_close"]},
        ),
    ]


class InterveneDoRequest(CAPRequestBase):
    verb: Literal["intervene.do"] = "intervene.do"
    params: InterveneDoParams


class InterveneDoResult(SemanticHonestyFields):
    outcome_node: Annotated[
        str,
        Field(description="Outcome node identifier that the reported effect refers to."),
    ]
    effect: Annotated[
        float,
        Field(description="Estimated causal effect for the requested intervention-outcome pair."),
    ]


class InterveneDoResponse(CAPProvenancedSuccessResponse[InterveneDoResult]):
    verb: Literal["intervene.do"] = "intervene.do"


class GraphNeighbor(BaseModel):
    node_id: Annotated[
        str,
        Field(description="Neighbor node identifier."),
    ]
    roles: Annotated[
        list[Literal["parent", "child", "spouse"]],
        Field(
            default_factory=list,
            description="Structural roles the neighbor plays relative to the queried node.",
        ),
    ]


class GraphNeighborsParams(BaseModel):
    node_id: Annotated[
        str,
        Field(
            min_length=1,
            description="Node identifier whose immediate neighbors should be listed.",
            json_schema_extra={"examples": ["NVDA_close"]},
        ),
    ]
    scope: Annotated[
        Literal["parents", "children"],
        Field(
            description="Which immediate structural side of the node to inspect.",
            json_schema_extra={"examples": ["parents"]},
        ),
    ]
    max_neighbors: Annotated[
        int,
        Field(
            default=10,
            ge=0,
            le=100,
            description="Maximum number of neighbor entries to return.",
            json_schema_extra={"examples": [5]},
        ),
    ]


class GraphNeighborsRequest(CAPRequestBase):
    verb: Literal["graph.neighbors"] = "graph.neighbors"
    params: GraphNeighborsParams


class GraphNeighborsResult(SemanticHonestyFields):
    node_id: Annotated[
        str,
        Field(description="Queried node identifier."),
    ]
    scope: Annotated[
        Literal["parents", "children"],
        Field(description="Structural direction used for the lookup."),
    ]
    neighbors: Annotated[
        list[GraphNeighbor],
        Field(default_factory=list, description="Neighbor entries returned by the server."),
    ]
    total_candidate_count: Annotated[
        int | None,
        Field(description="Total number of candidate neighbors before truncation, when disclosed."),
    ] = None
    truncated: Annotated[
        bool,
        Field(description="Whether the returned neighbor list was truncated by server-side limits."),
    ] = False
    edge_semantics: Annotated[
        str | None,
        Field(description="Server disclosure for how to interpret the returned edge relation."),
    ] = None


class GraphNeighborsResponse(CAPProvenancedSuccessResponse[GraphNeighborsResult]):
    verb: Literal["graph.neighbors"] = "graph.neighbors"


class GraphMarkovBlanketParams(BaseModel):
    node_id: Annotated[
        str,
        Field(
            min_length=1,
            description="Node identifier whose Markov blanket should be returned.",
            json_schema_extra={"examples": ["NVDA_close"]},
        ),
    ]
    max_neighbors: Annotated[
        int,
        Field(
            default=10,
            ge=0,
            le=100,
            description="Maximum number of blanket members to return.",
            json_schema_extra={"examples": [8]},
        ),
    ]


class GraphMarkovBlanketRequest(CAPRequestBase):
    verb: Literal["graph.markov_blanket"] = "graph.markov_blanket"
    params: GraphMarkovBlanketParams


class GraphMarkovBlanketResult(SemanticHonestyFields):
    node_id: Annotated[
        str,
        Field(description="Queried node identifier."),
    ]
    neighbors: Annotated[
        list[GraphNeighbor],
        Field(default_factory=list, description="Markov blanket members returned by the server."),
    ]
    total_candidate_count: Annotated[
        int | None,
        Field(description="Total number of blanket candidates before truncation, when disclosed."),
    ] = None
    truncated: Annotated[
        bool,
        Field(description="Whether the returned blanket member list was truncated."),
    ] = False
    edge_semantics: Annotated[
        str | None,
        Field(description="Server disclosure for the blanket membership semantics."),
    ] = None


class GraphMarkovBlanketResponse(CAPProvenancedSuccessResponse[GraphMarkovBlanketResult]):
    verb: Literal["graph.markov_blanket"] = "graph.markov_blanket"


class TraverseParams(BaseModel):
    node_id: Annotated[
        str,
        Field(
            min_length=1,
            description="Node identifier to traverse from.",
            json_schema_extra={"examples": ["NVDA_close"]},
        ),
    ]
    top_k: Annotated[
        int,
        Field(
            default=10,
            ge=0,
            le=100,
            description="Maximum number of traversed node identifiers to return.",
            json_schema_extra={"examples": [10]},
        ),
    ]


class TraverseRequestBase(CAPRequestBase):
    params: TraverseParams


class TraverseParentsRequest(TraverseRequestBase):
    verb: Literal["traverse.parents"] = "traverse.parents"


class TraverseChildrenRequest(TraverseRequestBase):
    verb: Literal["traverse.children"] = "traverse.children"


class TraverseResult(SemanticHonestyFields):
    node_id: Annotated[
        str,
        Field(description="Queried node identifier."),
    ]
    direction: Annotated[
        Literal["parents", "children"],
        Field(description="Traversal direction used to produce the returned node list."),
    ]
    nodes: Annotated[
        list[str],
        Field(default_factory=list, description="Traversed node identifiers in the returned order."),
    ]


class TraverseResponse(CAPProvenancedSuccessResponse[TraverseResult]):
    verb: Literal["traverse.parents", "traverse.children"]


class GraphPathsParams(BaseModel):
    source_node_id: Annotated[
        str,
        Field(
            min_length=1,
            description="Start node identifier for the path query.",
            json_schema_extra={"examples": ["NVDA_close"]},
        ),
    ]
    target_node_id: Annotated[
        str,
        Field(
            min_length=1,
            description="End node identifier for the path query.",
            json_schema_extra={"examples": ["SONY_close"]},
        ),
    ]
    max_paths: Annotated[
        int,
        Field(
            default=3,
            ge=1,
            le=20,
            description="Maximum number of paths to return.",
            json_schema_extra={"examples": [3]},
        ),
    ]


class GraphPathsRequest(CAPRequestBase):
    verb: Literal["graph.paths"] = "graph.paths"
    params: GraphPathsParams


class GraphPathNode(BaseModel):
    node_id: Annotated[str, Field(description="Stable node identifier in the returned path.")]
    node_name: Annotated[str, Field(description="Human-readable node name, when the server exposes one.")]
    node_type: Annotated[str, Field(description="Server-defined node type for the path node.")]
    domain: Annotated[str, Field(description="Domain label associated with the path node.")]


class GraphPathEdge(BaseModel):
    from_node_id: Annotated[str, Field(description="Source node identifier for the path edge.")]
    to_node_id: Annotated[str, Field(description="Target node identifier for the path edge.")]
    edge_type: Annotated[str, Field(description="Server-defined edge type for the returned path edge.")]


class GraphPath(BaseModel):
    distance: Annotated[int, Field(description="Path distance or hop count as disclosed by the server.")]
    nodes: Annotated[
        list[GraphPathNode],
        Field(default_factory=list, description="Ordered nodes that make up one returned path."),
    ]
    edges: Annotated[
        list[GraphPathEdge],
        Field(default_factory=list, description="Ordered edges that make up one returned path."),
    ]


class GraphPathsResult(SemanticHonestyFields):
    source_node_id: Annotated[
        str,
        Field(description="Requested source node identifier."),
    ]
    target_node_id: Annotated[
        str,
        Field(description="Requested target node identifier."),
    ]
    connected: Annotated[
        bool,
        Field(description="Whether the server found at least one path between the requested nodes."),
    ]
    path_count: Annotated[
        int,
        Field(description="Number of returned paths or discovered paths, depending on server disclosure."),
    ]
    paths: Annotated[
        list[GraphPath],
        Field(default_factory=list, description="Returned path entries between source and target."),
    ]


class GraphPathsResponse(CAPProvenancedSuccessResponse[GraphPathsResult]):
    verb: Literal["graph.paths"] = "graph.paths"
