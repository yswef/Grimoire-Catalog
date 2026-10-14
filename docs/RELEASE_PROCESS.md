<!-- © ENG.YSWEF — yswefalhmzy@gmail.com -->
# Tool release process

This is a manual owner-run process, not an automatic publication workflow. The
initial scaffold does not push, tag, build binaries or create Releases. Work only
with this public repository; no access to app source is needed. Examples below use
`example-tool` and must be replaced with real reviewed artifact metadata.

## 1. Prepare and review final artifacts

1. Confirm the tool is free, without a paid tier or ads, and that redistribution is
   permitted by its stated license. Donations are optional, never a listing fee.
2. Independently inspect/test the Windows 10/11 binary and its provenance in the
   appropriate build environment. Never execute unreviewed assets merely to hash
   them. This repository does not provide or verify those builds.
3. Put final artifacts in a **flat staging folder outside the repository**. Use
   simple ASCII filenames (`A-Z`, `a-z`, digits, `.`, `_`, `-`), no leading hyphen,
   reserved Windows names, links, subdirectories or secrets. Stop all writers.
4. Code signing is currently unavailable. **Disabled placeholder:** once the owner
   provisions a certificate and protected signing infrastructure, separately review
   a signing job. Signing would happen before hashing/uploading, but no signing
   command runs now. Document unsigned binaries and possible SmartScreen warnings.

## 2. Install maintenance dependencies

Use Python 3.11 or newer. From the repository root, create an isolated environment:

```sh
python -m venv .venv
```

Activate it using `. .venv/bin/activate` on POSIX, or
`.venv\Scripts\Activate.ps1` in PowerShell. Then:

```sh
python -m pip install 'jsonschema==4.25.1' 'rfc3339-validator==0.1.4' 'pytest==8.4.2'
```

The RFC3339 dependency is mandatory so `generated_at` validation cannot silently
skip date-time checks. Action refs are pinned; Python transitive dependency locking
and artifact hash pinning remain an owner-reviewed improvement (see SELF_REVIEW).

## 3. Generate and publish checksums

```sh
python scripts/make_sha256sums.py ../release-staging
```

This streams each regular file and atomically writes a sorted `SHA256SUMS.txt` in
that folder, excluding that output from its own digest. Re-running is deterministic
if artifacts have not changed. Unsafe filenames, links, directories and empty
folders are rejected. Checksums use the standard `hex-digest  filename` format.
The staging directory must remain trusted and unchanged during hashing.

In **this public repository's GitHub Releases UI**, the owner chooses a unique
per-tool tag (for example `example-tool-v1.0.0`), uploads the reviewed binary and
`SHA256SUMS.txt`, and publishes the Release before updating the catalog. Do not
replace an existing released asset under the same version/tag; publish a new
version. Include license, platform requirements, unsigned status and provenance
in release notes. This step is not performed by the scaffold.

## 4. Fetch the published bytes and update the catalog

Example in a POSIX shell (PowerShell users may enter it on one line):

```sh
python scripts/add_tool.py \
  --id example-tool --name 'Example Tool' --version 1.0.0 \
  --description 'What the tool does.' --license Proprietary \
  --url 'https://github.com/yswef/grimoire-catalog/releases/download/example-tool-v1.0.0/ExampleTool-Setup.exe' \
  --kind installer --min-windows 10 \
  --data-dir '%APPDATA%\YSWEF\ExampleTool' \
  --name-en 'Example Tool' --name-ar 'أداة مثال' \
  --description-en 'What the tool does.' --description-ar 'وصف وظيفة الأداة.'
```

Required arguments are `--id`, `--name`, `--version`, `--description`, `--license`
and `--url`, for both adds and updates. There are no interactive prompts. The asset
name is derived from the URL, and the hash and size are **computed**, never accepted
as command-line claims. Existing optional metadata/translations are preserved when
omitted; removing them requires a reviewed manual edit. `--kind` defaults to the
existing kind, or `installer` for a new entry. Use `portable` when appropriate.
`--catalog` selects another existing valid catalog for a dry staging run.

The helper validates before downloading, follows at most five redirects, requires
HTTP 200 and nonempty bytes, checks Content-Length if supplied, and hashes the
stream without installing or saving the binary. It uses a 30-second socket timeout,
a best-effort five-minute streaming deadline and a default 2 GiB limit (override
explicitly with `--max-bytes`). It updates `generated_at` to current UTC, sorts by
ID, validates again and atomically replaces the catalog. It detects changes during
the download but is not a locking service: **use one writer at a time**.

Initial URLs must be `https://github.com/yswef/<repo>/releases/download/<tag>/<asset>`.
No credentials, ports, queries or fragments are accepted there. Tags must be one
safe path segment; encoded path separators/traversal are rejected. The asset name
must match exactly. Redirects may go only to another permitted owned Release URL,
`https://release-assets.githubusercontent.com/...`, or
`https://objects.githubusercontent.com/...` (CDN signed queries are allowed).
**TODO:** verify this exact allowlist against the first real published asset; it
was tested offline, not against a live Release. If GitHub changes CDN behavior,
fail closed and review the change rather than allow arbitrary redirects.

Compare the computed digest and size with the independently retained final artifact
and uploaded `SHA256SUMS.txt`. Hashing a downloaded file alone cannot establish that
it was the intended build. English/Arabic catalog text belongs in `name_i18n` and
`description_i18n`; this repository has no UI or application translation files.

## 5. Validate, scan and commit

```sh
python scripts/validate_catalog.py catalog.json
python -m pytest -q
python -c 'import json; from jsonschema import Draft202012Validator; Draft202012Validator.check_schema(json.load(open("catalog.schema.json", encoding="utf-8")))'
gitleaks dir . --redact
gitleaks git . --redact
```

Use Gitleaks 8.30.1 (the CI version), installed from a trusted verified distribution.
Do not commit if a secret is found. The initial local scaffold used detect-secrets
1.5.0 because its environment could not retrieve the Gitleaks binary; hosted CI
still requires Gitleaks. Update CHANGELOG.md, inspect `git diff`, check all files
being staged, and keep binaries, checksums and private scan reports outside Git.

Stage only the intended files, then make an owner-authored Conventional Commit.
For POSIX shells, identities are set **only for this command**:

```sh
git add catalog.json CHANGELOG.md
env GIT_AUTHOR_NAME=yswef GIT_AUTHOR_EMAIL=yswefalhmzy@gmail.com \
    GIT_COMMITTER_NAME=yswef GIT_COMMITTER_EMAIL=yswefalhmzy@gmail.com \
    git commit -m 'feat: update example-tool catalog entry'
```

Do not set identity using `git config`, export it globally, add trailers, backdate,
or rewrite commits. For PowerShell, use a child process with command-local identity
environment variables instead of persistent configuration. Commit signing is a
separate GitHub ruleset requirement, **not binary code signing**: the owner must
arrange a verified signing method before protected integration. See REPO_SETTINGS
for the bootstrap decision around existing unsigned commits.

The owner later submits the branch for review and integrates it to `main` only after
`validate-catalog` passes. Nothing in the initial scaffold pushes automatically.
After publication, independently confirm the `main` catalog and selected download
in Grimoire; consumer behavior is not verified by these Python tests.
