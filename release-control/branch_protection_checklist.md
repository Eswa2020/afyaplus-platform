# Branch Protection Checklist, afyaplus-platform (`master`)

## Enforcement status
<!-- Keep ONE of these two lines -->
- Public repository: rules below are configured live in Settings > Branches on `master`.
- Private repository on GitHub Free: branch protection is not enforced on this plan.
  This file is the settings proposal; evidence is the green CI run plus this policy.

## Rules
| Rule | Setting | Evidence |
|---|---|---|
| Require a pull request before merging | YES | evidence/branch_protection/pr_required.png |
| Required status checks | `ci / lint-test`, `ci / eval`, `ci / mcp-health` (names copied from a completed run) | evidence/branch_protection/required_checks.png |
| Require branches to be up to date before merging | YES | same screenshot |
| Required approving reviews | **0**, see exception below | evidence/branch_protection/pr_required.png |
| Require review from Code Owners | Documented in `.github/CODEOWNERS`; enforced when a second maintainer joins | .github/CODEOWNERS |
| Include administrators (no bypass) | YES | evidence/branch_protection/admins.png |
| Allow force pushes | NO | same screenshot |
| Allow deletions | NO | same screenshot |

## Documented exception: required approvals = 0
This is a single-maintainer repository. GitHub does not let a PR author approve their
own PR, so requiring 1 approval would block every merge. Review intent is carried by
CODEOWNERS and by the required checks, which no one can bypass.
**In a team this becomes 1 approval plus Code Owner review on `release-control/prompts/`,
`evals/`, `fixtures/` and `.github/workflows/`.**

## Incident mapping: Friday's temperature PR
| What happened | Rule that blocks it now |
|---|---|
| Temperature changed and merged with zero checks | `ci / eval` fails closed on golden urgency drift; merge disabled while red |
| A prompt edited without new recorded evidence | `eval_prompts.py` exits 1: no fixture for the new prompt sha256 |
| A logistics tool renamed in the same release | `ci / mcp-health` fails: `missing tools {'check_stock'}` |
| A "quick hotfix" pushed straight to `master` | Require-PR plus no admin bypass removes that path |
| The gate weakened inside the same PR | CODEOWNERS on `.github/workflows/` and `evals/` routes those edits to the owner |

## Check names (must match exactly)
Workflow `name: ci` + job ids `lint-test`, `eval`, `mcp-health` produce:
`ci / lint-test`, `ci / eval`, `ci / mcp-health`.
A rule naming a check nothing produces would leave `master` silently unlocked.