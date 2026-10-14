<!-- © ENG.YSWEF — yswefalhmzy@gmail.com -->
# Initial scaffold self-review

Review date: 2026-10-13. Status labels distinguish completed fixes from owner work.

| Finding | Status | Assessment / next action |
|---|---|---|
| Contract preservation | fixed | Supplied schema field names/patterns, empty catalog timestamp and support values retained. No `$comment` was added to the catalog because its closed schema forbids it. New comment-capable source/config files have the required header; supplied README is exempt and unchanged. |
| Strictness beyond schema | fixed | Format checking is enabled explicitly. Validator adds duplicate-key/ID rejection, sorted IDs, exact URL/asset matching, SHA full matches, safe Windows components and traversal/query/fragment/credential rejection. These restrictions live outside the unchanged schema; schema-only clients do not inherit them. |
| Remaining schema limitations | needs-owner-decision | Contract permits empty name/description/license, arbitrary min_windows and permissive version syntax (not complete SemVer); optional translations are not required to include both languages. Defaults do not populate instances. Adopt a versioned contract change only after consumer agreement. No consumer was accessed. |
| Account as single trust root | open | SHA256 cannot authenticate a malicious replacement of both asset and catalog. Use passkeys/2FA, signed-commit ruleset, protected PR/check workflow and independent build/hash review. Independent trust roots/attestations need future design. |
| Untrusted download inputs | fixed | Helper validates before I/O, allowlists every redirect, streams bounded bytes, checks length and atomically writes only after validation. Tests cover failures; no shell execution or artifact installation. |
| Real Release transport | open | Sandbox cannot reach GitHub's asset CDN. TODO: owner tests first real asset and redirect policy. Do not claim live downloads or private installer compatibility have passed. |
| Concurrency/local threat model | open | Atomic replacement protects against partial writes; helper notices edits during download but is not fully race-proof. Use a trusted local checkout/staging folder, finalized artifacts and a single writer; malicious concurrent filesystem mutation is outside this scaffold's guarantees. |
| CI supply chain | open | Action refs are pinned to verified upstream commit SHAs, credentials are not persisted, token permissions are read-only and fork PR code receives no publishing privilege. Python direct versions and Gitleaks version are pinned, but transitive packages and downloaded tool bytes lack repository hash locks. TODO: review full dependency locking and provenance. Dependabot covers actions only. |
| Local security scan | open | Gitleaks binary retrieval was blocked by CDN network restrictions. Local pre-commit scanning uses detect-secrets 1.5.0 with verification requests disabled; zero findings are required before committing. Gitleaks is configured in CI but has not run locally or on a hosted runner. No scanner proves absence of all secrets. |
| Donation model | fixed | Shared support values remain centralized and unchanged. New docs/templates consistently describe free tools, optional donations, no ads/paid tiers or paid placement. No checkout, tracking or gating code was added. |
| Public support details | needs-owner-decision | Confirm consent to publish supplied wallet-holder details. No donation endpoint or wallet ownership was independently verified. |
| Catalog licensing | needs-owner-decision | Keep README's all-rights-reserved default. No invented LICENSE; empty license_url remains an explicit TODO after a license decision. |
| README / policy consistency | open | README is immutable input. Its claims that hashes "guarantee" integrity need the account-compromise qualification in SECURITY.md. Its app promises (undo/rollback, extraction defenses, telemetry, layouts, caching) and exact SemVer wording are not established here. TODO: owner reviews those promises independently. |
| Signing | open | Only a disabled binary-signing comment exists; no certificate-dependent build step. Local commits have no signing key. Owner must resolve bootstrap integration and enable the separate signed-commit ruleset without rewriting history. |
| Commit-message policy and checkout handoff | fixed | The initial session reported unwanted trailers injected by the pre-existing commit-msg hook. At the 2026-10-14 handoff, the checkout contained only base commit 9e10696 and the scaffold as untracked files; the previously reported commits were not present in this checkout. Recreate the planned commits from the preserved files, bypassing the known trailer hook with command-local `--no-verify` only after independent tests and secret scanning. Verify each commit body immediately. Do not edit hooks/configuration, overwrite remote history or rewrite any existing commit. |
| Existing history and branch | open | Session must stay on arena/8cab09a5-grimoire-catalog, not main. Pre-existing 9e10696 uses 170477919+yswef@users.noreply.github.com for both identities; cannot make the full-history identity assertion true without forbidden rewriting. Eight new commits use the requested identity. README was already in the base commit, so the docs commit preserves it rather than recommitting a change. |
| Tests and scope | fixed | Offline pytest exercises schema, policy, CLIs, streaming failure paths, translation preservation, checksum determinism and atomic-write failure. Explicit empty-catalog and metaschema checks also run before commits. Hosted CI, Windows binaries, actual signing and app behavior remain unverified. |

The initial scaffold did not authorize remote publication. In the 2026-10-14
follow-up, the owner explicitly authorized documenting, publishing and merging this
work into `main`. Push only the assigned working branch, open a pull request, wait
for the required validation job and merge without bypassing repository protections.
Use an explicit clean squash subject/body rather than automatically collecting
commit messages. GitHub controls the identity/signature of its server-created merge
commit; the exact owner author/committer requirement can be guaranteed for local
commits only. Verify the resulting server commit and report any identity difference.

No remote settings changes, history rewriting or access to the other repository is
part of this work. English documentation/comments are used; Arabic/English catalog
translations are data. There is no UI in this repository.

## Publication handoff — 2026-10-14

- Preserve the supplied README and all three Appendix A contract files.
- Re-run all 72 offline regression tests, empty-catalog validation, the draft
  2020-12 metaschema check and a zero-findings secret scan before committing.
- The earlier local Gitleaks/CDN limitation is not proof that hosted CI will pass;
  record the actual pull-request check result before merging.
- Owner-only settings and product-runtime checks remain open even after integration:
  license choice, empty support license URL, email privacy, account protection,
  signed-commit bootstrap, Windows/app behavior and first real Release download.
- Record the pull-request URL, hosted check evidence and merge outcome in the
  publication audit. Do not describe publication as complete before it succeeds.
