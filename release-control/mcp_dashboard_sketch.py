"""Runtime MCP tool dashboard: per-tool error rate with one alert threshold.

The runtime counterpart to scripts/check_mcp_health.py (which runs at deploy time).
"""
import json

from tool_metrics import tool_report

ALERT_THRESHOLD = 0.10  # tuned in the runbook, not in a chat thread


def alert_if_error_rate(tool: str, threshold: float = ALERT_THRESHOLD) -> bool:
    row = tool_report().get(tool) or {"error_rate": 0}
    if row["error_rate"] >= threshold:
        print("ALERT", tool, row)
        return True
    return False


def summary() -> dict:
    return tool_report()


if __name__ == "__main__":
    print(json.dumps(summary(), indent=2))