"""Eval gate with a flaky-case quarantine.

Quarantined cases are still scored and reported, but do not block the merge.
Active failures always block, and so does a quarantine above MAX_QUAR_RATE.
"""
import argparse
import json
from pathlib import Path

from eval_prompts import load_fixture, load_jsonl, load_pinned_prompt, score_case

MAX_QUAR_RATE = 0.05


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--golden", default="evals/golden.jsonl")
    p.add_argument("--quarantine", default="fixtures/quarantine.json")
    args = p.parse_args()

    # TODO 1: golden cases + quarantine ids as a set
    cases = load_jsonl(args.golden)
    quar = set(json.loads(Path(args.quarantine).read_text(encoding="utf-8")))

    # TODO 2: score with the SAME fixture and rules as the real gate
    _version, _text, sha = load_pinned_prompt()
    fixture = load_fixture(sha)

    active_fail = quar_n = quar_fail = 0
    for case in cases:
        ok = score_case(fixture["by_id"][case["id"]], case)
        if case["id"] in quar:
            quar_n += 1
            if not ok:
                quar_fail += 1
                print(f"quarantined failure (non-blocking): {case['id']}")
        elif not ok:
            active_fail += 1
            print(f"ACTIVE FAILURE (blocking): {case['id']}")

    # TODO 3: one summary line on-call can read
    quar_rate = quar_n / max(len(cases), 1)
    print(f"n={len(cases)} active_fail={active_fail} quarantined={quar_n} "
          f"quar_fail={quar_fail} quar_rate={quar_rate:.3f} max_quar_rate={MAX_QUAR_RATE}")
    if quar_rate > MAX_QUAR_RATE:
        print("QUARANTINE OVER CEILING: fix or graduate cases before merging")

    # TODO 4: the exit code is the contract
    return 1 if active_fail > 0 or quar_rate > MAX_QUAR_RATE else 0


if __name__ == "__main__":
    raise SystemExit(main())