# Development

This guide covers local setup, testing, packaging, and the common change paths in this repository.

## Local Setup

Install the project in editable mode:

```bash
pip install -e ".[server,dev]"
```

That installs:

- runtime dependencies from `pyproject.toml`
- the optional FastAPI server adapter dependencies
- the local test and build tools from the `dev` extra
- the local package in editable mode

The package requires Python 3.10 or newer.

## Running Tests

Run the current test suite with:

```bash
pytest
```

Current coverage is intentionally small. At the moment, the repository includes a smoke test for:

- public import stability
- recursive field sanitization behavior

If you change public exports, builders, request validation, or server response shaping, add targeted tests for that behavior.

## Continuous Integration

The repository includes [`.github/workflows/ci.yml`](../.github/workflows/ci.yml), which currently:

- runs the test suite on Python 3.10, 3.11, 3.12, and 3.13
- verifies that the package still builds as an sdist and wheel

If you add optional dependencies, supported Python versions, or new test entry points, update the workflow accordingly.

## Packaging Notes

Build configuration lives in `pyproject.toml`.

Important metadata today:

- distribution name: `cap-protocol`
- import package: `cap`
- optional extra: `server`
- typed package marker: `cap/py.typed`

Before a public release, maintainers should also verify:

- license metadata and `LICENSE` file contents stay aligned
- repository URLs
- version bump policy
- release notes or changelog process
- security reporting path in `SECURITY.md`

## Common Change Paths

### Change request or response schemas

Touch these files first:

- `cap/core/contracts.py`
- `cap/core/envelopes.py`
- `cap/core/errors.py`

Then update:

- builders in `cap/core/builders.py`
- exports in `cap/core/__init__.py`
- client methods in `cap/client/http.py` if needed
- server contracts in `cap/server/contracts.py`
- docs and tests

### Add a new client convenience method

Most client ergonomics live in `cap/client/http.py`.

Typical steps:

1. add or reuse a request builder
2. add the typed response model
3. expose a dedicated method on `AsyncCAPClient`
4. update any default verb mappings if the method should participate in the standard registry
5. document the new API and add tests

### Add a new server-supported verb

Typical steps:

1. define request and response models
2. add a `CAPVerbContract`
3. export the contract from `cap/server/__init__.py`
4. register a handler through `CAPVerbRegistry`
5. update the capability-card documentation if the verb is externally visible
6. add tests that cover request validation and response validation

### Extend the capability card

Capability-card schema changes live in `cap/core/capability_card.py`.

When changing this area:

- keep field names stable unless there is a protocol-level reason to change them
- preserve the `$schema` alias behavior
- update examples in `README.md`
- update [api-reference.md](api-reference.md) if public model names change

## Documentation Maintenance

This repository now uses documentation as part of the public API contract. When behavior changes, update:

- `README.md` for project-level overview changes
- `docs/architecture.md` for flow or module-boundary changes
- `docs/api-reference.md` for public import or helper changes
- `CONTRIBUTING.md` for workflow expectations
- `CHANGELOG.md` for user-visible changes
- `SUPPORT.md`, `SECURITY.md`, or `CODE_OF_CONDUCT.md` when community process changes

The rule of thumb is simple:

- if a user would need to read the source to understand a change, the docs should probably be updated too

## Recommended Review Focus

When reviewing changes in this project, prioritize:

- schema compatibility
- public import stability
- request/response validation behavior
- CAP-shaped error behavior
- documentation accuracy

That review order matches the role of the repository: it is primarily a protocol boundary package.
