# Releasing

This repository publishes the `cap-protocol` package to PyPI through GitHub Actions.

The release trigger is a Git tag, not a branch merge.

That choice keeps package releases tied to an immutable version marker:

- the package version in `pyproject.toml`
- the Git tag, such as `v0.2.3`
- the GitHub Release
- the published PyPI artifact

## Recommended Release Model

Use whichever integration branch fits the team workflow:

- merge directly to `main`
- or merge to `release` first for final verification

In both cases, the actual PyPI publish step should happen only when you tag the exact commit you want to release.

Do not publish on every merge to `main` or `release`. A branch tip moves; a release tag should not.

## One-Time Setup

### 1. Configure PyPI Trusted Publisher

On PyPI, add a Trusted Publisher for this repository.

Recommended values:

- owner: `CausalAgentProtocol`
- repository: `python-sdk`
- workflow filename: `release.yml`
- environment name: `pypi`

If the project already exists on PyPI, add the publisher under the project settings.

If the project does not exist yet, create a pending publisher first and let the first successful publish create the project.

### 2. Create the GitHub environment

In GitHub repository settings, create an environment named `pypi`.

The release workflow publishes from that environment. You can also add environment protection rules if you want manual approval before the publish step runs.

### 3. Keep package metadata current

Before any release, verify:

- `project.version` in `pyproject.toml`
- project URLs
- license metadata
- `CHANGELOG.md`

The release workflow will fail if the pushed tag does not match the package version.

## Release Checklist

Before tagging a release:

1. Merge the intended changes to the branch that represents the release candidate.
2. Update `pyproject.toml` to the new version.
3. Update `CHANGELOG.md` so the versioned release notes exist outside `Unreleased`.
4. Run the test suite locally or confirm CI is green.
5. Make sure the commit you are about to tag is the exact commit you want on PyPI.

## Release Steps

If you release from `main`:

```bash
git checkout main
git pull
git tag v0.2.3
git push origin v0.2.3
```

If you release from `release`:

```bash
git checkout release
git pull
git tag v0.2.3
git push origin v0.2.3
```

After the tag is pushed, [`.github/workflows/release.yml`](../.github/workflows/release.yml) will:

1. build the sdist and wheel
2. run `twine check` on the built distributions
3. publish the distributions to PyPI through Trusted Publishing
4. create a GitHub Release for the same tag

## Manual Build Verification

Maintainers can run the release workflow manually from GitHub Actions with `workflow_dispatch`.

That manual run is for build verification only:

- it still validates package metadata
- it still builds artifacts
- it does not publish to PyPI
- it does not create a GitHub Release unless the workflow is running from a `v*` tag

Use that path when you want to test the workflow changes before pushing a release tag.

## Versioning Notes

This repository currently uses pre-1.0 package versions. Until the project reaches 1.0, treat version bumps deliberately and document the reasoning in `CHANGELOG.md`.

As a general rule:

- patch release: backwards-compatible fixes or small maintenance changes
- minor release: backwards-compatible feature additions or meaningful public surface expansion
- major release: breaking API or contract changes

## Failure Modes

Common release failures:

- the Git tag does not match `pyproject.toml`
- the `pypi` environment does not exist in GitHub
- the Trusted Publisher settings in PyPI do not match this repository or workflow filename
- package metadata is invalid and `twine check` fails

When release automation fails, fix the underlying issue before publishing again. Do not work around the failure by manually uploading a different artifact built from a different commit.
