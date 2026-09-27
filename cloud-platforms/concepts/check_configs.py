"""Parse every platform concept config and print the fields that matter."""
import json
from pathlib import Path

import yaml


def load(name):
    text = Path(name).read_text(encoding="utf-8")
    return json.loads(text) if name.endswith(".json") else yaml.safe_load(text)


region = load("region_policy.yaml")
print("region_policy:", region["preferred_regions"])

scale = load("scale_choice.yaml")
print("scale_choice:", {name: w["pattern"] for name, w in scale["workloads"].items()})

auto = load("autoscale.yaml")
print("autoscale: min", auto["min_replicas"], "max", auto["max_replicas"])

budget = load("azure_budget.json")
alert = budget["notifications"]["Actual_GreaterThan_80_Percent"]
print("azure_budget:", budget["amount"], budget["timeGrain"], "alert at", alert["threshold"], "%")

iam = load("iam_sketch.yaml")
print("iam allow:", iam["allow"])
print("iam deny:", iam["deny"])

tags = load("tags.json")
print("tags:", tags)