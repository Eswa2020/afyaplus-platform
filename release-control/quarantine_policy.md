# Golden-set quarantine policy

## Purpose
A quarantined golden case is still scored and reported on every run, but it does not
block a merge. Quarantine is for cases that fail for reasons unrelated to the change
under review (stub non-determinism, network variance). It is never a way to merge a
real regression.

## Ceiling
- At most **5%** of the golden set may be quarantined (`MAX_QUAR_RATE = 0.05` in
  `eval_quarantine.py`). Above that, the gate exits 1 regardless of results.
- With the current 3-case golden set, one quarantined case is 33%, so **no quarantine
  is permitted** until the set grows to at least 20 cases. This is intentional: a set
  this small cannot carry flaky debt.

## Entering quarantine
- Add the case id to `fixtures/quarantine.json` in a pull request.
- The PR description must state why the case is flaky and link the failing runs.
- A named owner is responsible for fixing or graduating it.

## Graduating out of quarantine
- A case graduates after **10 consecutive green runs**. Remove its id from
  `fixtures/quarantine.json` in a pull request.
- A case still quarantined after **14 days** must be fixed, rewritten, or deleted
  from the golden set by a reviewed PR. It may not stay in quarantine indefinitely.

## Never
- Never set `continue-on-error: true` on the required eval job.
- Never lower the eval threshold to absorb a flaky case.