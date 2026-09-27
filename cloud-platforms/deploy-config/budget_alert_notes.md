# Budget alert, triage-api

## Cap
**450 USD per month**, identical in `azure_budget_triage.json` and `aws_budget.json`.
Derived from the cost model (`cost-optimization/cost-model/cost_model.py`):
0.2018 USD per 1,000 requests x 2,000,000 planned requests = 403.65 USD a month,
plus 11.5% headroom. The course's 400 USD example sits below plan, so its forecast alert
would fire every normal month and get muted. 450 stays quiet on plan, while the retry-storm
scenario from the cost model (484.38 USD) breaks through it.
`check_budgets.py` recomputes the plan from the cost model and confirms both clouds agree.

## Threshold
**80% of actual spend (360 USD), plus a forecast alert at 100%.**
- On plan, 360 USD is reached around day 27, and nothing needs to happen.
- In a retry-storm month it is reached around day 22, leaving about a week inside the same
  billing month to act. An alert at 100% would only report money already spent.
- The forecast alert answers a different question: not "how much have we spent?" but
  "where is this month heading?", so a fast burn is caught before 80% is even reached.

## Recipients
- `finops@afyaplus.ke`: the finance alias, receives both alerts.
- `wanjiru@afyaplus.ke`: owner of triage-api (matches the `afyaplus.owner` label), receives
  the 80% actual alert, so it reaches someone who can change the burn rate, not only report it.

## Response
**When the 80% alert fires, engineering tightens the per-partner rate limit on /triage**
for the partner whose traffic is driving the spend (identified via the `partner` tag).
Chosen because the cost model shows retries and runaway clients, not base traffic, are the
main way this service overruns. It is reversible and leaves other partners' SLO untouched.
If the forecast alert still shows the month exceeding 450 USD after that, the second step is
lowering the replica ceiling from 4 to 2 and accepting higher p95 latency until month end.

## Apply status
Budgets were authored and peer-reviewable as JSON; apply to a live Azure subscription or
AWS account was simulated (no paid account used). The `aws budgets create-budget` command
shape is documented in the course material.