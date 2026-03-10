# Release Checklist for SubVIO-Stress-Bench

Use this checklist before tagging a public release.

---

## Documentation

- [ ] README.md is complete, accurate, and reflects the current codebase.
- [ ] All `TODO` markers in docs/ have been resolved or acknowledged.
- [ ] Citation BibTeX is finalized with correct paper metadata.
- [ ] Dataset download instructions are complete and tested.
- [ ] Environment setup instructions have been verified on a clean machine.
- [ ] CHANGELOG.md has been updated for this release.

## Code and Scripts

- [ ] All benchmark scripts run end-to-end without errors.
- [ ] Perturbation configurations are finalized and documented.
- [ ] Result aggregation and table generation scripts are tested.
- [ ] No hardcoded absolute paths remain in scripts.
- [ ] No credentials, API keys, or sensitive data are present in the repository.

## Data and Results

- [ ] Example outputs or result summaries are included or linked.
- [ ] Raw data files (if any) are excluded from the repository via `.gitignore`.
- [ ] Large binary files have been reviewed; only essential assets are tracked.

## Repository Health

- [ ] `.gitignore` is comprehensive and covers all generated artifacts.
- [ ] All issue and PR templates are in place under `.github/`.
- [ ] CI workflow passes on the release branch.
- [ ] License is correct and up to date.
- [ ] All external dependencies and their licenses are noted in `requirements.txt`
      or `environment.yml`.

## Final Steps

- [ ] Tag the release: `git tag -a v1.0.0 -m "Initial public release"`.
- [ ] Push the tag: `git push origin v1.0.0`.
- [ ] Create a GitHub Release with release notes.
- [ ] Announce on relevant mailing lists or forums if applicable.
