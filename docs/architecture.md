# Architecture

This document explains the repository from the code inward. If you are new to the SDK, start here before reading the API reference.

This SDK currently targets the active CAP `v0.3.0` public surface. The package architecture is organized around the mounted verbs and capability-card models that exist in code today rather than around speculative future protocol revisions.

## Design Goals

The SDK has a simple design:

- keep the protocol schema in typed Pydantic models
- make request construction explicit
- validate responses on both the client and server side
- keep FastAPI integration thin and replaceable
- expose small helpers instead of building a large framework

## Package Layers

### `cap.core`

`cap.core` is the protocol foundation. Everything else depends on it.

For now, that foundation is intentionally the minimal SDK surface needed for `v0.3.0`.

Key modules:

- `constants.py`: protocol version and schema URL constants
- `envelopes.py`: shared CAP request/response envelope models and low-level payload builders
- `contracts.py`: typed request and response contracts for supported verbs
- `builders.py`: convenience functions for assembling valid request objects
- `canonical.py`: canonical strings for assumptions, reasoning modes, mechanism families, and recommended algorithm names
- `capability_card.py`: models for the `meta.capabilities` response schema
- `disclosure.py`: recursive field redaction helper via `sanitize_fields(...)`
- `errors.py`: CAP error body/response models plus the `CAPHTTPError` exception

The practical rule is:

- if the logic is protocol-shaped, it probably belongs in `cap.core`

### `cap.client`

`cap.client` contains the async transport layer.

Its responsibilities are:

- turn typed request models into JSON
- resolve a CAP verb to an HTTP path
- send requests through `httpx.AsyncClient`
- validate the returned payload against the expected response model
- normalize CAP error payloads into a Python exception

The implementation currently lives almost entirely in `cap/client/http.py`.

### `cap.server`

`cap.server` wires protocol models to FastAPI handlers without taking over the application.

Its responsibilities are:

- define the contract for each supported verb
- register handlers by verb
- validate inbound request payloads
- convert handler output into a CAP success envelope
- validate outbound payloads
- translate Python/FastAPI exceptions into CAP error responses

The server package does not implement business logic. It only adapts business logic to the CAP schema.

## Core Data Model

### Request envelopes

Every request extends `CAPRequestBase` from `cap/core/envelopes.py`. It contributes:

- `cap_version`
- `request_id`
- `context`
- `options`

`context` may include a `CAPGraphRef`, which lets a caller point at a specific graph identity or version. `options` currently models timeout and response-detail preferences.

Verb-specific request classes then add:

- a literal `verb`
- a typed `params` model when that verb needs parameters

### Response envelopes

Successful responses extend `CAPResponseBase` through one of two generic shapes in `cap/core/contracts.py`:

- `CAPSuccessResponse[result]`
- `CAPProvenancedSuccessResponse[result]`

This pattern keeps the common envelope fields centralized while allowing each verb to attach a typed `result`.

For core verbs, the typed `result` model defines the canonical minimum fields. A server may still return richer additive result fields without breaking typed parsing.

Error responses use `CAPErrorResponse` from `cap/core/errors.py`.

### Semantic honesty fields

Several result models inherit `SemanticHonestyFields`, which standardizes:

- `reasoning_mode`
- `identification_status`
- `assumptions`

This is important because it encourages services to disclose how an answer was produced instead of only returning a numeric result.

### Capability cards

`meta.capabilities` returns a `CapabilityCard` from `cap/core/capability_card.py`.

`meta.methods` returns method descriptors built from the registered request and response models. This keeps runtime discovery aligned with the same typed contracts the dispatcher validates.

The schema is broken into focused submodels:

- provider metadata
- supported verbs
- graph metadata
- authentication requirements
- access tiers
- disclosure policy
- bindings
- extension namespaces

The `$schema` field is exposed through a Pydantic alias, which keeps JSON output compatible with the expected capability-card schema while still feeling normal in Python.

## Client Request Flow

The main client entry point is `AsyncCAPClient`.

### Dedicated verb methods

Methods like `graph_neighbors(...)` and `intervene_do(...)`:

1. call a builder from `cap.core.builders`
2. pass the typed request object to `request(...)`
3. post JSON to the resolved route
4. validate the JSON response into the expected Pydantic response model

This path is the safest option because both request and response shapes are explicit.

### Generic request methods

`request_verb(...)` and `request_route(...)` are escape hatches.

They are useful when:

- a service exposes an extension verb
- you already have raw params
- you want to map route aliases like `graph/neighbors` back to `graph.neighbors`

These methods construct a `CAPClientGenericRequest`, which is intentionally looser than the first-class verb builders.

### Error normalization

If the HTTP response status is an error, the client tries to parse the body as a `CAPErrorResponse`. When that works, it raises `CAPHTTPError` with:

- `status_code`
- `cap_error`
- `response_payload`

If the body is not a valid CAP error envelope, the exception still carries the HTTP status and any parsed JSON payload.

## Server Dispatch Flow

The server path starts with `CAPVerbRegistry` and ends with `build_fastapi_cap_dispatcher(...)`.

### Step 1: register handlers

Handlers are registered against a `CAPVerbContract` or a raw verb string. Each registration records:

- request model
- response model
- surface type: `core`, `convenience`, or `extension`
- handler callable

The registry also enforces naming rules:

- core verbs must look like `namespace.name`
- extension verbs are namespaced as `extensions.<namespace>.<name>`

### Step 2: validate the inbound payload

The FastAPI dispatcher extracts `payload["verb"]`, finds the matching `DispatchSpec`, and validates the body with the registered request model.

If validation fails, FastAPI raises `RequestValidationError`, which can later be converted into a CAP error response by `register_cap_exception_handlers(...)`. The exception handler also normalizes validation contexts so embedded Python exception objects become JSON-safe strings.

### Step 3: execute the handler

The dispatcher accepts both sync-like return values and awaitables. A handler can return:

- a fully formed CAP success payload as `dict[str, Any]`
- a `CAPHandlerSuccessSpec`, which is the preferred high-level path

### Step 4: reduce handler success

If the handler returns `CAPHandlerSuccessSpec`, `reduce_handler_success(...)`:

- builds provenance when `provenance_hint` is present
- wraps the result in a standard CAP success envelope
- normalizes `request_id`

This keeps business handlers focused on the result while the adapter fills in protocol boilerplate.

### Step 5: validate the outbound payload

Before anything is returned to FastAPI, the dispatcher validates the payload against the registered response model. This is an important guardrail because it catches malformed success payloads before they leave the server.

## Provenance Model

Server provenance is deliberately split into two inputs:

- `CAPProvenanceHint`: per-response details such as algorithm, sample size, or mechanism model
- `CAPProvenanceContext`: service-wide context such as graph version and server version

`build_cap_provenance(...)` combines those two with measured `computation_time_ms`.

This is a good separation because:

- handlers usually know algorithm-level details
- the application shell usually knows deployment-level metadata

## Extension Story

Extension verbs are first-class in the registry even though the repo currently ships only core and traversal contracts.

Use `registry.extension(...)` when you need a verb like:

```text
extensions.<namespace>.<name>
```

This keeps non-standard verbs discoverable and avoids colliding with protocol-defined namespaces.

Capability-card support for extensions lives in `CapabilityExtensionNamespace` and the `extensions` field on `CapabilityCard`. Extension namespaces can describe both extra request inputs through `additional_params` and extension-only result fields through `additional_result_fields`.

## Disclosure Story

`sanitize_fields(...)` recursively removes forbidden keys from dictionaries and lists.

This is intentionally small, but it gives services a reusable building block for:

- hiding sensitive implementation fields
- enforcing tier-based visibility
- applying disclosure policy before returning CAP payloads

## What To Read Next

- Read [api-reference.md](api-reference.md) for the public surface area.
- Read [development.md](development.md) for setup, tests, and how to add new verbs.
