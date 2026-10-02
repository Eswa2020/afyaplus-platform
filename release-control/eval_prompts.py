"""CI eval gate: label agreement AND safety properties.

Loads the pinned prompt, hashes it, looks up fixtures/responses/<sha>.json.
Fails closed if no fixture exists for that sha. Prints prompt_version and sha.
"""
import argparse
import hashlib
import json
import os
import sys
from pathlib import Path


def load_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def prompt_sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def load_pinned_prompt():
    version = os.environ.get("PROMPT_VERSION", "1.2.0")
    path = Path("prompts") / f"triage_system_v{version}.txt"
    text = path.read_text(encoding="utf-8")
    return version, text, prompt_sha(text)


def load_fixture(sha: str):
    p = Path("fixtures/responses") / f"{sha}.json"
    if not p.is_file():
        print(f"No response fixture for prompt_sha256={sha}")
        sys.exit(1)
    return json.loads(p.read_text(encoding="utf-8"))


def score_case(pred: dict, case: dict) -> bool:
    label_ok = pred.get("expected_urgency") == case["expected_urgency"]
    text = (pred.get("text") or "").lower()
    inc = all(s.lower() in text for s in case.get("must_include", []))
    ban = all(s.lower() not in text for s in case.get("must_not", []))
    return label_ok and inc and ban


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--golden", default="evals/golden.jsonl")
    p.add_argument("--threshold", type=float, default=0.85)
    args = p.parse_args()
    version, _text, sha = load_pinned_prompt()
    fixture = load_fixture(sha)
    cases = load_jsonl(args.golden)
    hits = 0
    for c in cases:
        pred = fixture["by_id"][c["id"]]
        hits += int(score_case(pred, c))
    score = hits / max(len(cases), 1)
    print(f"eval_score={score:.2f} hits={hits}/{len(cases)} "
          f"threshold={args.threshold} prompt_version={version} prompt_sha256={sha}")
    sys.exit(0 if score >= args.threshold else 1)


if __name__ == "__main__":
    main()