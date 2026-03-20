# Contributing

Thanks for contributing to the CAP Python SDK.

This repository is intentionally small, so most changes affect the public API directly. Please read the code structure first and keep protocol changes explicit and well documented.

## Development Setup

Install the package in editable mode:

```bash
pip install -e ".[server,dev]"
```

Run the test suite:

```bash
pytest
```

The current tests are lightweight. If you add or change protocol behavior, include focused tests in `tests/` or alongside future test modules for the affected package area.

## Repository Layout

| Path | Purpose |
| --- | --- |
| `cap/core` | protocol models, constants, builders, capability-card schema, and shared errors |
| `cap/client` | async HTTP client and route resolution |
| `cap/server` | handler contracts, registry, FastAPI dispatch, and CAP-shaped server responses |
| `tests` | smoke tests for public imports and helper behavior |
| `docs` | architecture, API, and development documentation |

Start with [docs/architecture.md](docs/architecture.md) if you want a code-level walkthrough.

## Community Standards

By participating in this project, you agree to follow:

- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- [SECURITY.md](SECURITY.md) for vulnerability reporting
- [SUPPORT.md](SUPPORT.md) for usage questions and triage
- [CHANGELOG.md](CHANGELOG.md) for public-facing release notes

## Contribution Guidelines

### Keep the schema first

When changing behavior, update the typed models before adding convenience code around them. In this project, the models are the source of truth.

### Preserve the public import surface

`cap/__init__.py`, `cap/client/__init__.py`, `cap/server/__init__.py`, and `cap/core/__init__.py` define the user-facing import paths. If you move or rename exports, update those modules and add tests that protect the new API.

### Add docs with protocol changes

Update the relevant documentation when you change:

- supported verbs
- request or response shapes
- canonical constants
- extension registration rules
- client or server integration flow

For user-visible changes, also update `CHANGELOG.md`.

### Prefer narrow helpers over hidden magic

The SDK is designed to stay readable. Favor simple builders, explicit response reducers, and small utilities over implicit framework behavior.

## Adding A New Verb

Most new verb work touches the same layers:

1. Add request and response models in `cap/core/contracts.py`.
2. Add request builders in `cap/core/builders.py` if the verb should have first-class helper support.
3. Export the new models and helpers from `cap/core/__init__.py`.
4. Register client support in `cap/client/http.py` if the client should expose a dedicated method or default response contract.
5. Add a `CAPVerbContract` in `cap/server/contracts.py`.
6. Export the server contract from `cap/server/__init__.py`.
7. Document the new behavior in `README.md` and the relevant file under `docs/`.
8. Add tests that exercise the new public behavior.

## Review Checklist

Before opening a PR, check that:

- `pytest` passes locally
- documentation matches the actual code paths
- new public models are exported intentionally
- handler examples and request builders still produce valid CAP envelopes
- error paths still return CAP-shaped payloads
- `CHANGELOG.md` reflects user-visible changes when appropriate

## Release Notes

If a change affects the public API, protocol schema, or supported verbs, call that out clearly in the PR description so it can be reflected in release notes later.
