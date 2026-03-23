# API Reference

This is a hand-written reference for the public SDK surface. It is organized by how you use the package, not by file order.

## Top-Level Package

The top-level `cap` package currently re-exports:

```python
from cap import AsyncCAPClient, CAPClientRoutes, CAP_VERSION
```

Use this when you want the smallest possible import surface.

## `cap.core`

`cap.core` is the public home for protocol models and helper constants.

### Constants and canonical vocabularies

Useful exports include:

- `CAP_VERSION`
- `CAPABILITY_CARD_SCHEMA_URL`
- canonical reasoning-mode constants such as `REASONING_MODE_GRAPH_PROPAGATION`
- canonical assumption constants such as `ASSUMPTION_CAUSAL_SUFFICIENCY`
- canonical identification-status constants such as `IDENTIFICATION_STATUS_IDENTIFIED`
- recommended algorithm names such as `ALGORITHM_PCMCI`

Use these instead of string literals when building capability cards or service responses.

### Envelope models

Shared envelope types come from `cap/core/envelopes.py`:

- `CAPGraphRef`
- `CAPRequestContext`
- `CAPRequestOptions`
- `CAPRequestBase`
- `CAPResponseBase`

Helpers in the same module:

- `normalize_request_id(...)`
- `build_success_payload(...)`
- `build_error_payload(...)`

Use the model classes when you need typed request composition. Use the payload helpers when you already have a dict-shaped result and need a raw protocol envelope.

### Verb contracts

Each first-class verb has a typed request and response model in `cap.core`.

Included request models:

- `MetaCapabilitiesRequest`
- `MetaMethodsRequest`
- `GraphNeighborsRequest`
- `GraphMarkovBlanketRequest`
- `GraphPathsRequest`
- `ObservePredictRequest`
- `InterveneDoRequest`
- `TraverseParentsRequest`
- `TraverseChildrenRequest`

Included response models:

- `MetaCapabilitiesResponse`
- `MetaMethodsResponse`
- `GraphNeighborsResponse`
- `GraphMarkovBlanketResponse`
- `GraphPathsResponse`
- `ObservePredictResponse`
- `InterveneDoResponse`
- `TraverseResponse`

Most request models contain a typed `params` object. Most response models contain a typed `result` object. Traversal responses share a single `TraverseResponse` model with a union literal on `verb`.

### Builders

Request builders are the easiest way to create valid request objects:

- `build_meta_capabilities_request(...)`
- `build_meta_methods_request(verbs=None, detail="compact", include_examples=False, ...)`
- `build_graph_neighbors_request(...)`
- `build_graph_markov_blanket_request(...)`
- `build_graph_paths_request(...)`
- `build_observe_predict_request(...)`
- `build_intervene_do_request(...)`
- `build_traverse_parents_request(...)`
- `build_traverse_children_request(...)`

Capability-card helpers:

- `build_capability_access_tier(...)`
- `build_capability_disclosure_policy(...)`
- `build_extension_namespace(...)`

These helpers are intentionally thin. They do not add hidden transport logic; they mainly centralize object construction and keep examples concise.

### Capability-card models

If you implement `meta.capabilities`, you will usually touch:

- `CapabilityCard`
- `CapabilityProvider`
- `CapabilitySupportedVerbs`
- `CapabilityGraphMetadata`
- `CapabilityAuthentication`
- `CapabilityCausalEngine`
- `CapabilityStructuralMechanisms`
- `CapabilityDetailedCapabilities`
- `CapabilityAccessTier`
- `CapabilityDisclosurePolicy`
- `CapabilityBindings`
- `CapabilityMCPBinding`
- `CapabilityA2ABinding`
- `CapabilityExtensionNamespace`

`CapabilityExtensionNamespace` supports both `additional_params` and `additional_result_fields` so capability cards can describe extension-specific request inputs and non-core result fields.

### Errors and disclosure

Error types:

- `CAPErrorBody`
- `CAPErrorResponse`
- `CAPHTTPError`

Disclosure helper:

- `sanitize_fields(...)`

`CAPHTTPError` is the main exception type surfaced by the client. `sanitize_fields(...)` is a small but useful helper for response filtering.

## `cap.client`

The client package exposes:

- `AsyncCAPClient`
- `CAPClientRoutes`

### `CAPClientRoutes`

`CAPClientRoutes` currently maps all verbs to one endpoint path by default:

```python
CAPClientRoutes(single_entry_path="/cap")
```

Important methods:

- `resolve(verb)`: map a verb to an HTTP path
- `resolve_verb(route)`: convert a route alias such as `graph/neighbors` into `graph.neighbors`

Override this object when your CAP deployment uses a different routing convention.

### `AsyncCAPClient`

Main methods:

- `request(payload, response_model, headers=None)`
- `request_verb(...)`
- `request_route(...)`
- first-class verb helpers such as `meta_capabilities(...)`, `meta_methods(...)`, `graph_neighbors(...)`, `observe_predict(...)`, and `intervene_do(...)`
- `aclose()`

Typical usage pattern:

1. create the client with a `base_url`
2. call a dedicated verb method or `request_verb(...)`
3. receive a validated Pydantic response object
4. catch `CAPHTTPError` for CAP-shaped or HTTP-level failures

## `cap.server`

The server package exposes contracts, registration, dispatch, provenance helpers, and error integration.

### Contracts

Verb contracts are exported as constants:

- `META_CAPABILITIES_CONTRACT`
- `META_METHODS_CONTRACT`
- `GRAPH_NEIGHBORS_CONTRACT`
- `GRAPH_MARKOV_BLANKET_CONTRACT`
- `GRAPH_PATHS_CONTRACT`
- `OBSERVE_PREDICT_CONTRACT`
- `INTERVENE_DO_CONTRACT`
- `TRAVERSE_PARENTS_CONTRACT`
- `TRAVERSE_CHILDREN_CONTRACT`
- `CORE_VERB_CONTRACTS`

These are convenient for registration because they bundle the verb string with both request and response models.

### Registry

`CAPVerbRegistry` is the central server-side router.

Key methods:

- `core(...)`: decorator for core or convenience verbs
- `extension(...)`: decorator for extension verbs
- `register_core_verb(...)`
- `register_core_contract(...)`
- `register_extension(...)`
- `get(verb)`
- `verbs_for_surface(surface)`

Useful properties:

- `supported_verbs`
- `extension_verbs_by_namespace`

### FastAPI adapter

`build_fastapi_cap_dispatcher(...)` creates a callable that:

- finds the matching verb
- validates the inbound payload
- calls the handler
- reduces high-level handler output
- validates the outbound payload

Optional hooks:

- `provenance_context_provider`
- `success_reducer`

Use `success_reducer` only when the default `reduce_handler_success(...)` is not enough for your service.

### Response helpers

The response module exposes:

- `CAPHandlerSuccessSpec`
- `CAPProvenanceHint`
- `CAPProvenanceContext`
- `build_cap_success_response(...)`
- `build_handler_success(...)`
- `build_cap_provenance(...)`
- `reduce_handler_success(...)`

`CAPHandlerSuccessSpec` is the most ergonomic return type for handlers that want the adapter to build the final success envelope.

### Error helpers

Server-side error support includes:

- `CAPAdapterError`
- `build_cap_error_response(...)`
- `extract_cap_request_context(...)`
- `register_cap_exception_handlers(...)`

Use `register_cap_exception_handlers(app)` in FastAPI apps so validation and adapter failures are emitted as CAP-compatible error payloads.

## Which Entry Point Should You Use?

- Use `cap.core` when you need models, builders, constants, or shared schema code.
- Use `cap.client.AsyncCAPClient` when calling a CAP endpoint over HTTP.
- Use `cap.server.CAPVerbRegistry` plus `build_fastapi_cap_dispatcher(...)` when exposing a CAP endpoint from FastAPI.
- Use raw payload helpers only when you intentionally want to work one level below the typed abstractions.
