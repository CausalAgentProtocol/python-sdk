# CAP Python SDK

Typed Python SDK for the Causal Agent Protocol (CAP) v0.2.2.

This repository packages three things that usually live in separate projects:

- `cap.core`: protocol constants, request/response envelopes, typed verb contracts, builders, capability-card models, and shared error models
- `cap.client`: an async HTTP client that knows how to serialize CAP requests and validate CAP responses
- `cap.server`: a small FastAPI adapter for registering handlers by verb and validating both inbound payloads and outbound responses

The codebase is intentionally small. The goal is to make CAP request/response handling easy to understand, easy to share across services, and hard to drift from the protocol schema.

## Why This SDK Exists

Most CAP integrations need the same building blocks:

- strongly typed request and response models
- a stable set of canonical constants for reasoning modes, assumptions, and mechanism families
- helpers to build valid request envelopes
- a client that can turn protocol errors into Python exceptions
- a server adapter that validates payloads before and after handler execution

This SDK provides those pieces without forcing a large framework or hidden runtime.

## What Is Included

The repository currently ships models and helpers for:

- CAP core verbs: `meta.capabilities`, `graph.neighbors`, `graph.markov_blanket`, `graph.paths`, `observe.predict`, `intervene.do`
- traversal helpers included by the SDK: `traverse.parents`, `traverse.children`
- capability cards for `meta.capabilities`
- protocol error envelopes
- response provenance helpers for server implementations

## Installation

### From Source

```bash
pip install .
```

If you also need the FastAPI server adapter:

```bash
pip install ".[server]"
```

For local development:

```bash
pip install -e ".[server,dev]"
```

### From PyPI

When published, the distribution name is `cap-protocol`:

```bash
pip install cap-protocol
```

Install the optional server extra with:

```bash
pip install "cap-protocol[server]"
```

The Python import package name is `cap`.

## Quick Start

### Client

```python
import asyncio

from cap.client import AsyncCAPClient


async def main() -> None:
    client = AsyncCAPClient("https://example.com")
    try:
        capabilities = await client.meta_capabilities()
        print(capabilities.result.name)

        neighbors = await client.graph_neighbors(
            node_id="revenue",
            scope="parents",
            max_neighbors=5,
        )
        print(neighbors.result.neighbors)
    finally:
        await client.aclose()


asyncio.run(main())
```

### FastAPI Server

```python
from fastapi import FastAPI, Request

from cap.server import (
    CAPHandlerSuccessSpec,
    CAPProvenanceContext,
    CAPProvenanceHint,
    CAPVerbRegistry,
    GRAPH_NEIGHBORS_CONTRACT,
    build_fastapi_cap_dispatcher,
    register_cap_exception_handlers,
)

app = FastAPI()
registry = CAPVerbRegistry()


@registry.core(GRAPH_NEIGHBORS_CONTRACT)
async def graph_neighbors(payload, request: Request):
    del request
    return CAPHandlerSuccessSpec(
        result={
            "node_id": payload.params.node_id,
            "scope": payload.params.scope,
            "neighbors": [],
            "truncated": False,
            "reasoning_mode": "graph_propagation",
            "identification_status": "identified",
            "assumptions": [],
        },
        provenance_hint=CAPProvenanceHint(algorithm="handwritten-demo"),
    )


async def provenance_context_provider(payload, request: Request) -> CAPProvenanceContext:
    del payload, request
    return CAPProvenanceContext(
        graph_version="dev",
        server_name="example-cap-server",
        server_version="0.1.0",
    )


dispatch = build_fastapi_cap_dispatcher(
    registry=registry,
    provenance_context_provider=provenance_context_provider,
)
register_cap_exception_handlers(app)


@app.post("/api/v1/cap")
async def cap_endpoint(payload: dict, request: Request):
    return await dispatch(payload, request)
```

## How The Code Is Organized

| Path | Responsibility |
| --- | --- |
| `cap/core/constants.py` | CAP version and schema constants |
| `cap/core/envelopes.py` | request/response envelope models and raw payload builders |
| `cap/core/contracts.py` | typed request and response models for each supported verb |
| `cap/core/builders.py` | convenience builders for valid request objects and capability-card helpers |
| `cap/core/canonical.py` | canonical reasoning modes, assumptions, mechanism families, and algorithm names |
| `cap/core/capability_card.py` | `meta.capabilities` schema models |
| `cap/core/disclosure.py` | field-level disclosure sanitization helper |
| `cap/core/errors.py` | typed CAP error payloads and `CAPHTTPError` |
| `cap/client/http.py` | async client, route resolution, and HTTP error translation |
| `cap/server/contracts.py` | server-side verb-to-model contract definitions |
| `cap/server/registry.py` | verb registry and extension registration |
| `cap/server/fastapi.py` | FastAPI dispatch adapter and validation pipeline |
| `cap/server/responses.py` | success reduction and provenance construction helpers |
| `cap/server/errors.py` | FastAPI exception handlers that emit CAP error envelopes |

## Request Lifecycle

The easiest way to understand the SDK is to follow one request end to end:

1. A request model is created directly or through a builder in `cap.core.builders`.
2. The client serializes the Pydantic model with `exclude_none=True` and posts it to the resolved CAP route.
3. A CAP server receives a plain JSON body and hands it to the FastAPI dispatcher created by `build_fastapi_cap_dispatcher(...)`.
4. The dispatcher looks up the verb in `CAPVerbRegistry`, validates the body against the registered request model, and calls the matched handler.
5. The handler either returns a full CAP-shaped success payload or a `CAPHandlerSuccessSpec`.
6. If a `CAPHandlerSuccessSpec` is returned, `cap.server.responses.reduce_handler_success(...)` builds the final CAP success envelope, optionally attaching provenance.
7. The dispatcher validates the outgoing payload against the registered response model before returning it.

This means both sides of the protocol are schema-checked:

- client side: response validation happens after every request
- server side: request validation happens before handler execution
- server side: response validation happens before JSON is returned

## Public API Surface

The smallest top-level API looks like this:

```python
from cap import AsyncCAPClient, CAPClientRoutes, CAP_VERSION
```

Most integrations will also import from `cap.core` or `cap.server`.

Stable public exports currently include:

- request/response models in `cap.core`
- request builders in `cap.core`
- capability-card models in `cap.core`
- canonical constants in `cap.core`
- `AsyncCAPClient` and `CAPClientRoutes` in `cap.client`
- `CAPVerbRegistry`, `build_fastapi_cap_dispatcher`, and response/error helpers in `cap.server`

For a guided walkthrough of those exports, see [docs/api-reference.md](docs/api-reference.md).

## Documentation Map

- [docs/architecture.md](docs/architecture.md): code-centric walkthrough of the package structure and request flow
- [docs/api-reference.md](docs/api-reference.md): overview of the public SDK surface and when to use each entry point
- [docs/development.md](docs/development.md): local setup, testing, release notes, and how to add or extend verbs
- [CONTRIBUTING.md](CONTRIBUTING.md): contribution workflow and repository expectations
- [CHANGELOG.md](CHANGELOG.md): public change history starting from open-source readiness work
- [SUPPORT.md](SUPPORT.md): where to ask questions and how to report issues
- [SECURITY.md](SECURITY.md): vulnerability reporting guidance
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md): expected community behavior

## Development

Install the package in editable mode:

```bash
pip install -e ".[server,dev]"
```

Run the current test suite:

```bash
pytest
```

The repository currently has a small smoke-test suite that checks public imports and helper behavior. New protocol changes should add tests close to the touched module.

GitHub Actions CI is configured to run the test suite across Python 3.10 through 3.13 and to verify that the package still builds as both an sdist and a wheel.

## Community Standards

If you plan to use or contribute to the project, start with:

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- [SUPPORT.md](SUPPORT.md)
- [SECURITY.md](SECURITY.md)
- [CHANGELOG.md](CHANGELOG.md)

## License

This project is licensed under the Apache License 2.0. See [LICENSE](LICENSE).

## Project Status

This repository is a compact SDK scaffold extracted from a working CAP implementation. It is a strong base for:

- sharing CAP models across multiple services
- standing up a CAP-compatible FastAPI endpoint
- building internal or external client integrations against CAP servers
- evolving the protocol contract without duplicating schema code in every service
