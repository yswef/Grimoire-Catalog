<!-- © ENG.YSWEF — yswefalhmzy@gmail.com -->
# Security policy

## Report privately

Use [GitHub private vulnerability reporting](https://github.com/yswef/grimoire-catalog/security/advisories/new)
when enabled, or email **yswefalhmzy@gmail.com**. The owner must enable private
reporting in repository settings; if it is unavailable, use email. Do not publish
exploits, credentials or sensitive logs in issues or pull requests.

Include affected tool/catalog versions, impact, minimal reproduction and suggested
mitigations. Redact unrelated personal information. There is no guaranteed response
time, paid support tier or bug bounty. Coordinate disclosure with the maintainer.

## Scope and support

The current catalog on `main`, this schema and maintenance scripts are in scope.
Historical catalog revisions and individual tool binaries do not have a promised
support window. Tool vulnerabilities may also be reported through the same private
channel. No production tools are present in the initial catalog.

## Trust boundaries

- SHA256 and byte size detect mismatches with the catalog. They do **not** prove
  publisher identity, absence of malware, or authenticity after account compromise.
- The `yswef` account controls both the catalog and its Release hashes. A compromised
  account could replace both. Use passkeys/2FA, protected branches, signed commits,
  independent artifact review and least-privilege publishing access.
- Binaries are not code-signed. There is no active signing step, certificate or
  signing secret in this repository. The workflow has only a disabled comment
  placeholder. Never tell users to disable SmartScreen or antivirus.
- The validator permits only explicit owned Release URLs; the download helper
  permits HTTPS redirects only to those URLs or the two explicit GitHub asset CDN
  hosts documented in the release process. Do not broaden this policy to a wildcard.
- Catalog validation is not a sandbox. Metadata is untrusted, and consumer-side
  validation, extraction containment, symlink defenses and command handling still
  require verification in the application. No app code was inspected here.

On a leak, revoke/rotate the credential first and notify the owner privately. Do
not attempt force-push cleanup or history rewriting as part of this workflow.
