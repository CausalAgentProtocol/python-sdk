from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from cap.core.constants import CAPABILITY_CARD_SCHEMA_URL, CAP_VERSION


class CapabilityProvider(BaseModel):
    name: str
    url: str


class CapabilitySupportedVerbs(BaseModel):
    core: list[str]
    convenience: list[str] = Field(default_factory=list)


class CapabilityGraphMetadata(BaseModel):
    domains: list[str]
    node_count: int
    edge_count: int
    node_types: list[str]
    edge_types_supported: list[str]
    graph_representation: str
    update_frequency: str
    temporal_resolution: str | None = None
    coverage_description: str


class CapabilityAuthentication(BaseModel):
    type: Literal["none", "api_key"]
    details: dict[str, str] = Field(default_factory=dict)


class CapabilityStructuralMechanisms(BaseModel):
    available: bool
    families: list[str] = Field(default_factory=list)
    nodes_with_fitted_mechanisms: int | None = None
    residuals_computable: bool | None = None
    residual_semantics: str | None = None
    mechanism_override_supported: bool | None = None
    counterfactual_ready: bool | None = None


class CapabilityCausalEngine(BaseModel):
    family: str
    algorithm: str | None = None
    discovery_method: str | None = None
    supports_time_lag: bool | None = None
    supports_latent_variables: bool | None = None
    supports_nonlinear: bool | None = None
    supports_instantaneous: bool | None = None
    structural_mechanisms: CapabilityStructuralMechanisms | None = None


class CapabilityDetailedCapabilities(BaseModel):
    graph_discovery: bool | None = None
    graph_traversal: bool | None = None
    temporal_multi_lag: bool | None = None
    effect_estimation: bool | None = None
    intervention_simulation: bool | None = None
    counterfactual_scm: bool | None = None
    latent_confounding_modeled: bool | None = None
    partial_identification: bool | None = None
    uncertainty_quantified: bool | None = None


class CapabilityAccessTier(BaseModel):
    tier: str
    verbs: list[str]
    response_detail: Literal["summary", "full", "raw"]
    hidden_fields: list[str]


class CapabilityDisclosurePolicy(BaseModel):
    hidden_fields: list[str]
    default_response_detail: Literal["summary", "full", "raw"]
    notes: list[str]


class CapabilityExtensionNamespace(BaseModel):
    schema_url: str
    verbs: list[str]
    additional_params: dict[str, dict[str, str]] = Field(default_factory=dict)
    notes: list[str] = Field(default_factory=list)


class CapabilityMCPBinding(BaseModel):
    enabled: bool
    endpoint: str


class CapabilityA2ABinding(BaseModel):
    enabled: bool
    agent_card_url: str


class CapabilityBindings(BaseModel):
    mcp: CapabilityMCPBinding | None = None
    a2a: CapabilityA2ABinding | None = None


class CapabilityCard(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    schema_url: str = Field(default=CAPABILITY_CARD_SCHEMA_URL, alias="$schema")
    name: str
    description: str
    version: str
    cap_spec_version: Literal["0.2.2"] = CAP_VERSION
    provider: CapabilityProvider
    endpoint: str
    conformance_level: Literal[1, 2]
    supported_verbs: CapabilitySupportedVerbs
    causal_engine: CapabilityCausalEngine | None = None
    detailed_capabilities: CapabilityDetailedCapabilities | None = None
    assumptions: list[str]
    reasoning_modes_supported: list[str]
    graph: CapabilityGraphMetadata
    authentication: CapabilityAuthentication
    access_tiers: list[CapabilityAccessTier] = Field(default_factory=list)
    disclosure_policy: CapabilityDisclosurePolicy
    bindings: CapabilityBindings | None = None
    extensions: dict[str, CapabilityExtensionNamespace] = Field(default_factory=dict)


__all__ = [
    "CapabilityAccessTier",
    "CapabilityA2ABinding",
    "CapabilityAuthentication",
    "CapabilityBindings",
    "CapabilityCard",
    "CapabilityCausalEngine",
    "CapabilityDetailedCapabilities",
    "CapabilityDisclosurePolicy",
    "CapabilityExtensionNamespace",
    "CapabilityGraphMetadata",
    "CapabilityMCPBinding",
    "CapabilityProvider",
    "CapabilityStructuralMechanisms",
    "CapabilitySupportedVerbs",
]
