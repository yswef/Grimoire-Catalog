<!-- © ENG.YSWEF — yswefalhmzy@gmail.com -->
# Manual GitHub repository settings

These are an **owner checklist**, not settings already applied. No remote settings,
remotes, tags, Releases or pushes were changed by the scaffold.

## Repository identity

- Default branch: `main`. The scaffold had to stay on its assigned working branch;
  the owner must review/integrate it into `main` separately.
- Keep the catalog public and enable Issues.
- Description (verbatim):

  `Official public catalog & releases for Grimoire — a free Windows installer for ENG.YSWEF tools. SHA256-verified downloads, offline-first, no telemetry.`

- Topics: `windows`, `installer`, `package-manager`, `tool-catalog`, `catalog`,
  `sha256`, `tauri`, `rust`, `offline-first`, `privacy`, `arabic`, `yswef`.

## Active branch ruleset targeting main

1. Require pull requests before merging (chosen instead of the linear-history-only
   alternative). Prefer independent review; decide whether a required approval is
   practical for a single-owner repository. Review workflow and support-link changes
   as carefully as catalog edits. Do not allow routine bypasses.
2. Block force pushes and branch deletion.
3. Require signed commits. Commit signing is unrelated to unavailable Windows
   binary signing. Enroll a GitHub-verified signing method before integration.
4. Require the **`validate-catalog`** status check from GitHub Actions. Select the
   observed check after its first successful run, require the branch to be up to
   date, and do not mark unrelated checks as substitutes. Schema, tests and Gitleaks
   all run in this one required job. Workflow has no path filters to skip it.
5. Review admin/bypass permissions and collaborator access. Protect workflow changes
   and consider CODEOWNERS/required owner review as a future enhancement.

**Bootstrap decision:** the supplied base commit is unsigned and uses a GitHub
noreply email. The scaffold's eight commits use the requested public email but have
no signing key provisioned. Do not rewrite existing history. The owner must decide
how to integrate this bootstrap under the intended signature rules and verify that
GitHub shows the intended resulting commits as Verified before enforcing the rule.
A ruleset is not made effective just by documenting it here.

## Security and maintenance

- Enable secret scanning and push protection, including available non-provider
  patterns. Review any bypass request and rotate exposed credentials immediately.
- Enable Dependabot alerts and review weekly `github-actions` update PRs.
  Inline Python dependency pins are **not** covered by this Dependabot configuration;
  maintain them manually until a reviewed lockfile/update strategy is adopted.
- Enable **private vulnerability reporting** and confirm the SECURITY.md reporting
  link works for external users. Email is the fallback.
- Require passkeys or strong 2FA on the `yswef` account, keep recovery codes offline,
  and minimize PAT/app permissions. Catalog and hashes share this account's trust.
- Set Actions default permissions to read-only; do not grant write access to fork
  PRs or enable `pull_request_target` execution of untrusted content. Review/pin
  third-party actions. Gitleaks Action is configured for the stated personal account;
  revisit its licensing if the repository moves to an organization.
- Run the hosted workflow after owner publication; neither its runner behavior nor
  real Release CDN downloads could be tested in this local session.
- Consider immutable Releases where available, independent hash publication, and
  separation of publishing authority; verify current GitHub availability first.

## Owner decisions before public use

- Catalog/docs license: README currently says all rights reserved unless a LICENSE
  says otherwise. No license grant or LICENSE file was invented. Choose a license
  explicitly if reuse should be permitted.
- `config/support.json` intentionally has `license_url: ""`. Populate it only after
  publishing the chosen license; the app must handle an empty URL without linking.
- Confirm permission to publish the supplied wallet-holder name and account number.
  All support remains voluntary: no paid tiers, ads or donation-gated features.
- The requested commit email is public. Check GitHub **Settings → Emails**, verify
  ownership of `yswefalhmzy@gmail.com`, and review "Block command line pushes that
  expose my email." Keep privacy protection if desired and resolve the identity
  policy with the owner; do not silently change identities or rewrite history.
- Verify the unchanged README's app promises (verification, rollback/undo, offline
  cache, bilingual behavior, no telemetry, extraction safety) in the app's own review.
  This repository provides only catalog-side checks.
