"""Challenge 1: prove the A/B split lands near its configured percentage.

Runs 100 synthetic keys at PCT_B, writes ab_report.json, exits 1 if B falls
outside [15, 25].
"""
import json

from ab_prompt_flag import assign_variant, load_prompt

PCT_B = 20
N = 100
B_MIN, B_MAX = 15, 25
VERSIONS = {"A": "1.2.0", "B": "1.3.0-candidate"}


def mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def main() -> int:
    # Real per-variant token estimate from the actual prompt files
    tokens_per_variant = {v: 40 + len(load_prompt(ver)) // 4 for v, ver in VERSIONS.items()}

    counts = {"A": 0, "B": 0}
    tokens = {"A": [], "B": []}
    for i in range(N):
        v = assign_variant(f"user-{i}", pct_b=PCT_B)
        counts[v] += 1
        tokens[v].append(tokens_per_variant[v])

    in_band = B_MIN <= counts["B"] <= B_MAX
    report = {
        "n": N,
        "pct_b": PCT_B,
        "counts": counts,
        "versions": VERSIONS,
        "mean_tokens_est": {"A": mean(tokens["A"]), "B": mean(tokens["B"])},
        "b_band": [B_MIN, B_MAX],
        "b_in_band": in_band,
    }
    with open("ab_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"n={N} pct_b={PCT_B} A={counts['A']} B={counts['B']} "
          f"band=[{B_MIN},{B_MAX}] in_band={in_band}")
    return 0 if in_band else 1


if __name__ == "__main__":
    raise SystemExit(main())