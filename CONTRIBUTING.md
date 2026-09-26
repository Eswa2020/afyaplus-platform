# Contributing to afyaplus-platform

## Branches
Branches are named `feature/short-description` (e.g. `feature/rename-title`). A branch should live no longer than a few days before merging back into `master` — the longer a branch lives, the more painful its eventual merge.

## Versions
We use semantic versioning: MAJOR.MINOR.PATCH.
- PATCH (e.g. 1.0.0 → 1.0.1): a bug fix, no change to the API's agreement
- MINOR (e.g. 1.0.0 → 1.1.0): a new, backwards-compatible feature (example: adding rate limiting in Lesson 6 without breaking existing callers)
- MAJOR (e.g. 1.1.0 → 2.0.0): the API's agreement itself changes and callers must adapt (example: renaming a response field)

## Releases
The Docker image tag must always match the Git tag exactly (e.g. image `afyaplus-triage:1.0.0` matches git tag `v1.0.0`). To see the exact code behind any production image, run:
`git checkout v<version>`

## When a merge conflict appears
1. Read the `<<<<<<<` / `=======` / `>>>>>>>` markers to see both versions of the disputed lines
2. Edit the file down to the single version you actually want, deleting all three marker lines
3. Commit the resolution, then **run the service to prove it still works** — this step is the one people skip and regret