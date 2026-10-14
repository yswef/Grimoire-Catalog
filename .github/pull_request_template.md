<!-- © ENG.YSWEF — yswefalhmzy@gmail.com -->
## Summary

Describe the change and link any public issue. Report vulnerabilities privately.

## Checklist

- [ ] `python scripts/validate_catalog.py catalog.json` and `python -m pytest -q` pass.
- [ ] The schema passes `Draft202012Validator.check_schema`.
- [ ] IDs are unique and sorted; hashes and sizes came from final Release assets.
- [ ] URLs point to `https://github.com/yswef/.../releases/download/...`.
- [ ] Release artifacts and SHA256SUMS.txt were reviewed independently of the catalog edit.
- [ ] License/redistribution rights and English/Arabic metadata were reviewed where applicable.
- [ ] No secrets, binaries, personal logs or machine-specific paths are included.
- [ ] A secret scan passed; docs and CHANGELOG.md match the change.
- [ ] Donation links remain centralized in config/support.json; no paid tiers or ads.
- [ ] Commits use the required owner identity and contain no attribution trailers.

## Verification

List commands actually run and any checks not run. Mark inapplicable items explicitly.
