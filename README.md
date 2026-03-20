# CAP Python SDK

Official Python SDK for building and integrating CAP-compatible systems.

If you are new to CAP itself, start with the [`cap` repository](https://github.com/CausalAgentProtocol/cap) for the protocol overview, getting-started guides, and normative specification. This repository is the Python implementation layer for people who want to call CAP servers or expose CAP-compatible services in Python.

## Choose The Right Repo

- [`cap`](https://github.com/CausalAgentProtocol/cap): learn CAP, read the docs, and track the protocol specification
- [`python-sdk`](https://github.com/CausalAgentProtocol/python-sdk): build CAP clients and CAP-compatible Python servers
- [`cap-reference`](https://github.com/CausalAgentProtocol/cap-reference): inspect a working reference server that exposes CAP over HTTP

## What This SDK Gives You

This repository ships three Python-facing layers that match the code today:

- `cap.core`: typed CAP envelopes, verb contracts, builders, capability-card models, canonical constants, and error models
- `cap.client`: an async HTTP client for calling CAP servers through the standard single-entry CAP route
- `cap.server`: a thin FastAPI adapter for validating requests, dispatching by verb, and returning CAP-shaped responses

Use this SDK when you want to:

- call a CAP server from Python without hand-writing request and response envelopes
- publish a CAP-compatible endpoint in a FastAPI service
- share one typed protocol layer across clients, servers, tests, and internal tooling

## Installation

Install the published package:

```bash
pip install cap-protocol
```

This base install includes the typed protocol models and the HTTP client. It does not install FastAPI.

If you want to use the optional `cap.server` FastAPI adapter:

```bash
pip install "cap-protocol[server]"
```

For local development from source:

```bash
pip install -e ".[server,dev]"
```

The distribution name is `cap-protocol`. The Python import package is `cap`.

## Quickstart: Call A CAP Server

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

The client currently provides first-class methods for:

- `meta.capabilities`
- `graph.neighbors`
- `graph.markov_blanket`
- `graph.paths`
- `observe.predict`
- `intervene.do`
- `traverse.parents`
- `traverse.children`

If you need a custom or extension verb, use `request_verb(...)` or `request_route(...)`.

## Quickstart: Expose A CAP Endpoint In FastAPI

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


@app.post("/cap")
async def cap_endpoint(payload: dict, request: Request):
    return await dispatch(payload, request)
```

This adapter stays intentionally small. It handles CAP-shaped validation and dispatch, but it does not impose a larger server framework or hide your business logic.

## Current Surface Area

The implementation in this repository currently includes:

- typed request and response models for the verbs listed above
- capability-card schema models for `meta.capabilities`
- canonical constants for reasoning modes, assumptions, mechanism families, and related protocol strings
- an async `httpx`-based client with CAP error normalization
- a FastAPI registry and dispatcher that validate both inbound requests and outbound responses

For code-level details, use the docs below rather than treating the README as the full API inventory.

## Where To Go Next

- [CAP docs and specification](https://github.com/CausalAgentProtocol/cap): protocol overview, getting started, and normative CAP behavior
- [docs/api-reference.md](docs/api-reference.md): public Python entry points and imports
- [docs/architecture.md](docs/architecture.md): package boundaries and request flow
- [docs/development.md](docs/development.md): local setup, tests, and common change paths

## Contributing And Community

Use repo-local docs for repo-specific workflows:

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [SUPPORT.md](SUPPORT.md)
- [SECURITY.md](SECURITY.md)
- [CHANGELOG.md](CHANGELOG.md)

Use the CAP organization docs for shared community policy:

- [Org-wide Contributing Guide](https://github.com/CausalAgentProtocol/.github/blob/main/CONTRIBUTING.md)
- [Org-wide Code of Conduct](https://github.com/CausalAgentProtocol/.github/blob/main/CODE_OF_CONDUCT.md)

## License

This project is licensed under the Apache License 2.0. See [LICENSE](LICENSE).
