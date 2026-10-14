<!-- © ENG.YSWEF — yswefalhmzy@gmail.com -->
# Privacy

Effective: 2026-10-13

Grimoire is designed to be free, offline-first, and without telemetry, tracking,
ads, accounts or a paid tier. This repository contains public catalog metadata,
shared support configuration and maintenance scripts; it does not implement the
installer. The private app's runtime behavior has not been audited here.

## Network activity

The product contract calls for fetching the catalog from this repository's `main`
branch and downloading only selected tools from `github.com/yswef/*` Releases.
GitHub may serve the bytes through its asset CDN. Those requests necessarily expose
normal connection information (such as IP address and request headers) to GitHub
and its infrastructure; "no telemetry" does not mean "no network traffic."

The maintenance helper `scripts/add_tool.py` downloads the requested public asset
to compute SHA256 and size. It uses no access token and does not execute the asset.
The other maintenance scripts and regression tests need no network once Python
dependencies are installed. Dependency installation and hosted CI contact their
respective service providers.

## Local and public data

The product is intended to cache catalog data for offline use. Tool-specific
storage, installer logs, retention and uninstall behavior must be verified by the
app/tool maintainer before distribution; this scaffold cannot guarantee them.
Each tool has its own license and may have its own privacy policy.

Issues, pull requests and their attachments are public. Do not post credentials,
private logs, personal filesystem paths or vulnerability details in them. Report
vulnerabilities privately as described in [SECURITY.md](SECURITY.md).

## Voluntary support

Donations are optional and never unlock features or affect catalog placement.
Payment services and wallet operators handle donations under their own policies.
The public wallet details in `config/support.json` are owner-supplied publication
information, not credentials. No donation integration or analytics is implemented
in this repository; support links should be opened only at the user's request.

For privacy questions, contact **yswefalhmzy@gmail.com**. Requests sent by email or
GitHub are handled through those providers. No automated retention/deletion
service is provided by this repository.
