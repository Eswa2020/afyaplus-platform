"""One JSONL row per triage request: variant, version, latency, token estimate.

The message itself is never written; only a short hash for correlating repeats.
"""
import hashlib
import json
import time
from pathlib import Path

from ab_prompt_flag import select_prompt

LOG = Path("logs/ab_requests.jsonl")
LOG.parent.mkdir(parents=True, exist_ok=True)


def handle_triage(user_key: str, message: str) -> dict:
    t0 = time.perf_counter()
    variant, version, system = select_prompt(user_key)
    # Stub model; wire the Week 6 /triage call in when ready.
    # Labels use the golden-set vocabulary: low | medium | high.
    out = {
        "expected_urgency": "medium",
        "advice": "Please visit a clinic if symptoms persist or worsen. This is not a diagnosis.",
        "variant": variant,
        "prompt_version": version,
        "system_chars": len(system),
    }
    ms = (time.perf_counter() - t0) * 1000
    row = {
        "user_key": user_key,
        "variant": variant,
        "prompt_version": version,
        "latency_ms": round(ms, 2),
        "tokens_est": 40 + len(message.split()) + len(system) // 4,
        "message_hash": hashlib.sha256(message.strip().lower().encode()).hexdigest()[:8],
    }
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
    return out