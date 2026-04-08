# Changelog

All notable changes to this project will be documented in this file.

The format is inspired by Keep a Changelog and the project aims to follow Semantic Versioning for package releases.

This public changelog starts with the repository documentation and project-metadata hardening for open-source readiness. Earlier internal package history has not been backfilled yet.

## [Unreleased]

### Changed

- aligned `README.md`, `docs/api-reference.md`, and `docs/architecture.md` to the active CAP `v0.3.0` public surface that the SDK models today
- updated SDK protocol constants and capability-card modeling for the `v0.3.0` release line

## [1.0.3] - 2026-03-23

### Added

- capability-card extension metadata can now describe extension-only result fields through `CapabilityExtensionNamespace.additional_result_fields`

### Fixed

- sanitized FastAPI validation error contexts before serializing CAP error responses, so embedded exception objects no longer break JSON responses
- checked out the repository in the GitHub Release job so `gh release create --verify-tag` can resolve the local `.git` metadata; the initial `1.0.2` automation published to PyPI successfully but failed while creating the GitHub Release
- explicitly excluded local `uv.lock` files from source distribution inputs for release hygiene

## [1.0.2] - 2026-03-23

### Added

- `meta.methods` client support, including filtered method lookups
- automated tag-driven PyPI publishing and GitHub Release creation through GitHub Actions
- release operations documentation for version bumps, Trusted Publisher setup, and tag-based publishing

### Changed

- documented the repository release flow around immutable version tags instead of branch-tip publishes

## [1.0.1] - 2026-03-20

### Added

- architecture, API reference, development, and contribution documentation
- community and maintenance documents: code of conduct, support guide, security policy, and changelog
- GitHub issue templates, pull request template, and a basic CI workflow
- an Apache-2.0 `LICENSE` file for public open-source distribution

### Changed

- expanded `README.md` into a code-centric project overview with request lifecycle and module responsibilities
- added development extras, open-source license metadata, and richer project URLs in `pyproject.toml`
- promoted the package version to `1.0.1` for the public PyPI release
