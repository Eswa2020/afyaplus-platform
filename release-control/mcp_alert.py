"""Challenge 2: check_stock fails 6 of 50 calls and must alert; ping must not.

Exit 0 only if the failing tool alerts AND the healthy control stays quiet.
"""
from mcp_dashboard_sketch import ALERT_THRESHOLD, alert_if_error_rate
from tool_metrics import timed_tool, tool_report


def succeed():
    return "ok"


def boom():
    raise RuntimeError("stock timeout")


def main() -> int:
    for _ in range(44):
        timed_tool("check_stock", succeed)
    for _ in range(6):
        try:
            timed_tool("check_stock", boom)
        except RuntimeError:
            pass
    for _ in range(20):
        timed_tool("ping", succeed)

    report = tool_report()
    stock_alert = alert_if_error_rate("check_stock")
    ping_alert = alert_if_error_rate("ping")

    lines = [
        f"threshold={ALERT_THRESHOLD}",
        f"report={report}",
        f"stock_alert={stock_alert}",
        f"ping_alert={ping_alert}",
    ]
    with open("mcp_alert_notes.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0 if stock_alert and not ping_alert else 1


if __name__ == "__main__":
    raise SystemExit(main())