from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from cap.core.constants import CAPABILITY_CARD_SCHEMA_URL, CAP_VERSION


class CapabilityProvider(BaseModel):
    name: str
    url: str | None = None


class CapabilitySupportedVerbs(BaseModel):
    core: list[str]
    convenience: list[str] = Field(default_factory=list)
    extensions: list[str] = Field(default_factory=list)


class CapabilityGraphMetadata(BaseModel):
    domains: list[str] = Field(default_factory=list)
    node_count: int | None = None
    edge_count: int | None = None
    node_types: list[str] = Field(default_factory=list)
    edge_types_supported: list[str] = Field(default_factory=list)
    graph_representation: str | None = None
    update_frequency: str | None = None
    temporal_resolution: str | None = None
    coverage_description: str | None = None
    availability: str | None = None
    scope: str | None = None


class CapabilityAuthentication(BaseModel):
    type: Literal["none", "api_key", "oauth2"]
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
    hidden_fields: list[str] = Field(default_factory=list)
    default_response_detail: Literal["summary", "full", "raw"] = "summary"
    notes: list[str] = Field(default_factory=list)


class CapabilityExtensionNamespace(BaseModel):
    schema_url: str | None = None
    verbs: list[str]
    additional_params: dict[str, dict[str, str]] = Field(default_factory=dict)
    additional_result_fields: dict[str, dict[str, str]] = Field(default_factory=dict)
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
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    schema_url: str = Field(default=CAPABILITY_CARD_SCHEMA_URL, alias="$schema")
    name: str
    description: str
    version: str | None = None
    cap_spec_version: Literal["0.3.0"] = CAP_VERSION
    provider: CapabilityProvider | None = None
    endpoint: str
    conformance_level: Literal[0, 0.5, 1, 2]
    conformance_name: Literal["Narrative", "Hybrid", "Observe", "Intervene"]
    pearl_alignment: Literal["below_pearl", "partial_rung_1", "rung_1", "rung_2"] | None = None
    supported_verbs: CapabilitySupportedVerbs
    causal_engine: CapabilityCausalEngine | None = None
    detailed_capabilities: CapabilityDetailedCapabilities | None = None
    assumptions: list[str] = Field(default_factory=list)
    reasoning_modes_supported: list[str] = Field(default_factory=list)
    graph: CapabilityGraphMetadata
    authentication: CapabilityAuthentication
    access_tiers: list[CapabilityAccessTier] = Field(default_factory=list)
    disclosure_policy: CapabilityDisclosurePolicy = Field(default_factory=CapabilityDisclosurePolicy)
    bindings: CapabilityBindings | None = None
    extensions: dict[str, CapabilityExtensionNamespace] = Field(default_factory=dict)

    def model_dump_compact(self, *, by_alias: bool = False) -> dict[str, object]:
        payload = self.model_dump(exclude_none=True, by_alias=by_alias)

        supported_verbs = payload.get("supported_verbs")
        if isinstance(supported_verbs, dict):
            for key in ("convenience", "extensions"):
                if supported_verbs.get(key) == []:
                    supported_verbs.pop(key, None)

        extensions = payload.get("extensions")
        if isinstance(extensions, dict):
            for namespace_payload in extensions.values():
                if isinstance(namespace_payload, dict):
                    for key in ("additional_params", "additional_result_fields", "notes"):
                        if namespace_payload.get(key) == {} or namespace_payload.get(key) == []:
                            namespace_payload.pop(key, None)
            if not extensions:
                payload.pop("extensions", None)

        if payload.get("access_tiers") == []:
            payload.pop("access_tiers", None)

        disclosure_policy = payload.get("disclosure_policy")
        if disclosure_policy == {
            "hidden_fields": [],
            "default_response_detail": "summary",
            "notes": [],
        }:
            payload.pop("disclosure_policy", None)

        bindings = payload.get("bindings")
        if bindings == {}:
            payload.pop("bindings", None)

        return payload


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
