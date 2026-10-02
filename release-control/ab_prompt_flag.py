"""Sticky A/B prompt assignment. Same sha256 bucket arithmetic as prompt_flag.py."""
import hashlib
import os
from pathlib import Path

PROMPTS = Path("prompts")


def load_prompt(version: str) -> str:
    # Bare semver in `version`; the letter v lives only in the filename.
    return (PROMPTS / f"triage_system_v{version}.txt").read_text(encoding="utf-8")


def bucket_of(user_key: str) -> int:
    return int(hashlib.sha256(user_key.encode()).hexdigest(), 16) % 100


def assign_variant(user_key: str, pct_b: int = 10) -> str:
    return "B" if bucket_of(user_key) < pct_b else "A"


def select_prompt(user_key: str) -> tuple[str, str, str]:
    pct = int(os.getenv("PROMPT_B_PCT", "10"))
    variant = assign_variant(user_key, pct)
    version = os.getenv(
        f"PROMPT_{variant}_VERSION",
        "1.2.0" if variant == "A" else "1.3.0-candidate")
    return variant, version, load_prompt(version)


if __name__ == "__main__":
    # Stickiness AND split: clinic-a is A (bucket 60); kisumu-01 is B (bucket 8)
    for key in ["clinic-a", "clinic-a", "kisumu-01"]:
        variant, version, _ = select_prompt(key)
        print(key, "bucket", bucket_of(key), variant, version)