"""Shadow scoring: compare control vs candidate urgency labels per request.

Nobody is served the candidate's reply; it is scored offline only.
"""
import json
from pathlib import Path


def read_jsonl_by_id(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return {r["req_id"]: r for r in map(json.loads, f) if r}


def score_shadow(control_path: str, shadow_path: str, out_path: str) -> dict:
    ctrl = read_jsonl_by_id(control_path)
    shad = read_jsonl_by_id(shadow_path)
    ids = sorted(set(ctrl) & set(shad))
    agree = sum(1 for i in ids
                if ctrl[i].get("expected_urgency") == shad[i].get("expected_urgency"))
    report = {
        "n_control": len(ctrl),
        "n_shadow": len(shad),
        "n_joined": len(ids),
        "missing_shadow": sorted(set(ctrl) - set(shad)),
        "urgency_agreement": (agree / len(ids)) if ids else 0.0,
        "disagreements": [i for i in ids
                          if ctrl[i].get("expected_urgency") != shad[i].get("expected_urgency")],
    }
    Path(out_path).write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    print(score_shadow("fixtures/shadow/control.jsonl",
                       "fixtures/shadow/candidate.jsonl",
                       "shadow_report.json"))