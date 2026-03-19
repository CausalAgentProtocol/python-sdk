# CAP Python SDK

Lightweight Python SDK scaffold for the Causal Agent Protocol (CAP) v0.2.2.

This repository currently provides:

- Typed CAP request and response models built with Pydantic
- Builder helpers for common CAP verbs
- An async HTTP client for CAP servers
- A small FastAPI adapter for wiring CAP verbs to handlers
- Capability card models for `meta.capabilities`

## Package Layout

`cap_protocol/core`

- Protocol constants, request/response envelopes, contracts, builders, errors, and capability card models

`cap_protocol/client`

- `AsyncCAPClient` and route helpers for calling a CAP endpoint

`cap_protocol/server`

- Verb contracts, registry utilities, FastAPI dispatch adapter, and response/error helpers for implementing a CAP server

## Supported Verbs

Core verbs included in the SDK:

- `meta.capabilities`
- `graph.neighbors`
- `graph.markov_blanket`
- `graph.paths`
- `observe.predict`
- `intervene.do`

Traversal contracts also included:

- `traverse.parents`
- `traverse.children`

## Requirements

Install from a local checkout:

```bash
pip install .
```

Once published to PyPI, the intended install command is:

```bash
pip install cap-protocol
```

Base installation includes the core models and async HTTP client. If you also want the FastAPI server adapter, install the optional server extra:

```bash
pip install "cap-protocol[server]"
```

The package keeps the import surface you asked for:

```python
from cap_protocol.core import (
    ASSUMPTION_CAUSAL_SUFFICIENCY,
    ASSUMPTION_FAITHFULNESS,
    ASSUMPTION_LINEARITY,
    ASSUMPTION_NO_INSTANTANEOUS_EFFECTS,
    ASSUMPTION_NO_LATENT_CONFOUNDERS_ADDRESSED,
)
from cap_protocol.core.disclosure import sanitize_fields
```

## Client Example

```python
import asyncio

from cap_protocol.client import AsyncCAPClient


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

You can also call verbs dynamically with `request_verb(...)` or route aliases with `request_route(...)`.

## FastAPI Server Example

```python
from fastapi import FastAPI, Request

from cap_protocol.server import (
    GRAPH_NEIGHBORS_CONTRACT,
    CAPVerbRegistry,
    build_fastapi_cap_dispatcher,
)

app = FastAPI()
registry = CAPVerbRegistry()


@registry.core(GRAPH_NEIGHBORS_CONTRACT)
async def graph_neighbors(payload, request: Request):
    return {
        "request_id": payload.request_id,
        "verb": payload.verb,
        "status": "success",
        "result": {
            "node_id": payload.params.node_id,
            "scope": payload.params.scope,
            "neighbors": [],
            "truncated": False,
            "reasoning_mode": "deterministic",
            "identification_status": "identified",
            "assumptions": [],
        },
        "provenance": {
            "algorithm": "handwritten-demo",
            "graph_version": "dev",
            "computation_time_ms": 1,
            "server_name": "example-cap-server",
            "server_version": "0.1.0",
            "cap_spec_version": "0.2.2",
        },
    }


dispatch = build_fastapi_cap_dispatcher(registry=registry)


@app.post("/api/v1/cap")
async def cap_endpoint(payload: dict, request: Request):
    return await dispatch(payload, request)
```

## Notes

- `CAPClientRoutes` maps all verbs to a single endpoint path by default: `/api/v1/cap`
- `CAPVerbRegistry` supports core, convenience, and extension verbs
- `build_fastapi_cap_dispatcher(...)` validates incoming payloads against the registered request models and validates the outgoing response model before returning it

## Status

This repository is an internal scaffold extracted from a reference implementation and is a good base for:

- sharing CAP request and response schemas across services
- standing up a CAP-compatible FastAPI endpoint
- building internal client integrations against a CAP server
