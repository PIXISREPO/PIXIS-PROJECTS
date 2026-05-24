
# Security Policy

## Supported Versions

This project is intended for active development on the current default branch.

| Version | Supported |
|---------|-----------|
| `main`  | Yes |
| Older commits, tags, and forks | No |

Security fixes are applied to the active repository state on `main`. Users should update to the latest repository version before reporting behavior that may already have been corrected.

## Reporting a Vulnerability

Please do **not** report security vulnerabilities through public GitHub issues, discussions, or pull requests.

Instead, report suspected vulnerabilities privately using one of the following paths:

1. **GitHub Private Vulnerability Reporting**, if it is enabled for this repository.
2. If private reporting is not enabled, contact the maintainer directly through the repository owner account and request a private disclosure channel.

When reporting an issue, include as much of the following as possible:

- A clear description of the vulnerability.
- The affected file, script, service, or installation step.
- The conditions required to reproduce the issue.
- Step-by-step reproduction instructions.
- The expected impact, including whether the issue could affect confidentiality, integrity, or availability.
- Any logs, screenshots, proof-of-concept material, or suggested remediation.

## Scope

This repository contains installer, configuration, service, and runtime assets for a Volumio LCD display workflow. Relevant reports may include, for example:

- Insecure download or update behavior.
- Unsafe file permissions or service configuration.
- Privilege escalation risks in installer or runtime scripts.
- Exposure of secrets, credentials, or sensitive configuration.
- Command injection, path traversal, or unsafe shell execution.
- Weaknesses in the handling of files fetched from the PIXISREPO GitHub repository.

Reports that are primarily feature requests, hardware compatibility issues, or general installation failures without a security impact should be handled through the normal support or issue workflow.

## Disclosure Process

After a private report is received, the maintainer will aim to:

1. Acknowledge receipt within 7 days.
2. Review and validate the report.
3. Assess impact and determine remediation.
4. Prepare and publish a fix when appropriate.
5. Disclose the issue after a fix is available, when coordinated disclosure is appropriate.

Response times may vary depending on maintainer availability, hardware access, and the complexity of reproduction.

## Security Expectations

This project is designed for use on a trusted device and trusted network during installation and runtime. All bootstrap-downloaded files are expected to come from the PIXISREPO GitHub repository, which is the documented single source of truth for installer and runtime assets.

Users should:

- Use the latest version from the repository.
- Avoid modifying the installer to fetch files from untrusted locations.
- Review local configuration changes before deployment.
- Treat public issue trackers as non-confidential.

## Out of Scope

The following are generally out of scope unless a clear security impact is demonstrated:

- Requests for setup help or troubleshooting.
- Missing features or enhancement requests.
- Hardware SPI or display failures with no security consequence.
- Package installation failures caused by external mirrors or transient network issues.
- Reports based solely on theoretical risk without a plausible exploitation path.

## Policy Updates

This policy may be updated as the repository evolves. GitHub supports repository-level security policies through a `SECURITY.md` file placed in the repository root, `docs`, or `.github` directory, and private vulnerability reporting can be enabled at the repository level for coordinated disclosure workflows.[1][2]
