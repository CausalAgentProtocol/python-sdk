# Security Policy

## Supported Versions

The current support policy is:

| Version Range | Security Support |
| --- | --- |
| `1.x` | Supported on a best-effort basis |
| `<1.0` | Not supported |

## Reporting A Vulnerability

Please do not report security vulnerabilities through public GitHub issues or pull requests.

If you have a private maintainer contact channel, use it. If you do not, open a minimal public issue requesting a secure reporting path and do not include exploit details, proof-of-concept code, secrets, or sensitive environment information.

When reporting a vulnerability, include:

- affected package version
- affected module or file
- vulnerability type and impact
- clear reproduction steps
- any known mitigations or workarounds

## What Maintainers Should Do

Once a report is received, maintainers should:

1. acknowledge receipt as soon as practical
2. confirm the affected versions and impact
3. prepare and review a fix
4. coordinate a release and changelog entry
5. disclose the issue publicly after users have a reasonable upgrade path

## Scope

This policy applies to:

- code in `cap/`
- examples in the repository
- packaging and release metadata for the published SDK

It does not automatically cover third-party services or deployments that embed this package unless the vulnerability is caused by this repository itself.
