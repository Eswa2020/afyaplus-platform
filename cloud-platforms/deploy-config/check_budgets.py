"""Check that the Azure and AWS budget artifacts describe the same decisions,
and compare the cap against the monthly plan from the cost model."""
import json
import sys
from pathlib import Path

# Reuse the cost model from the cost-optimization topic (one source of truth)
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "cost-optimization" / "cost-model"))
from cost_model import monthly_at  # noqa: E402

PLANNED_MONTHLY_REQUESTS = 2_000_000


def load(name):
    return json.loads(Path(name).read_text(encoding="utf-8"))


azure = load("azure_budget_triage.json")
aws = load("aws_budget.json")
aws_notify = load("aws_budget_notify.json")

azure_cap = float(azure["amount"])
aws_cap = float(aws["BudgetLimit"]["Amount"])

azure_tag = azure["filter"]["tags"]["service"][0]
aws_tag = aws["CostFilters"]["TagKeyValue"][0].split("$", 1)[1]

azure_alerts = sorted((n["thresholdType"].lower(), n["threshold"])
                      for n in azure["notifications"].values())
aws_alerts = sorted((n["Notification"]["NotificationType"].lower(),
                     n["Notification"]["Threshold"]) for n in aws_notify)

plan = monthly_at(PLANNED_MONTHLY_REQUESTS)

print(f"cap:     azure={azure_cap:.0f}  aws={aws_cap:.0f}  match={azure_cap == aws_cap}")
print(f"tag:     azure={azure_tag}  aws={aws_tag}  match={azure_tag == aws_tag}")
print(f"alerts:  azure={azure_alerts}")
print(f"         aws={aws_alerts}  match={azure_alerts == aws_alerts}")
print(f"plan:    {PLANNED_MONTHLY_REQUESTS:,} requests/month = {plan:.2f} USD")
print(f"headroom above plan: {100 * (azure_cap - plan) / plan:.1f}%")
print(f"80% actual alert fires at {0.8 * azure_cap:.2f} USD, "
      f"around day {30 * 0.8 * azure_cap / plan:.0f} of 30 if spend is on plan")