"""Append-only MCP activity log. Arguments are hashed, never written in plain text."""
import hashlib
import json
import time
from pathlib import Path

LOG = Path("logs/mcp_activity.jsonl")
LOG.parent.mkdir(parents=True, exist_ok=True)


def log_mcp(server: str, tool: str, args: dict, status: str, latency_ms: float,
            trace_id: str = ""):
    args_hash = hashlib.sha256(
        json.dumps(args, sort_keys=True, default=str).encode()).hexdigest()[:16]
    row = {
        "ts": time.time(),
        "trace_id": trace_id,
        "server": server,
        "tool": tool,
        "args_hash": args_hash,
        "status": status,
        "latency_ms": round(latency_ms, 1),
    }
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


if __name__ == "__main__":
    log_mcp("afyaplus-logistics", "list_low_stock",
            {"clinic_id": "C04", "threshold": 10},
            "ok", 12.4, trace_id="3f9a21c4")
    print(LOG.read_text(encoding="utf-8").strip().splitlines()[-1])