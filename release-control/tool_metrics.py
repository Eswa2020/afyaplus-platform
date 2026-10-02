"""Shared per-tool counters. Import from here; never copy these into another file."""
from collections import defaultdict
from time import perf_counter

_stats = defaultdict(lambda: {"n": 0, "err": 0, "ms_sum": 0.0})


def timed_tool(name: str, fn, *args, **kwargs):
    """Call fn, recording count, latency and error for `name`. Re-raises failures."""
    t0 = perf_counter()
    ok = True
    try:
        return fn(*args, **kwargs)
    except Exception:
        ok = False
        raise
    finally:
        dt = (perf_counter() - t0) * 1000
        _stats[name]["n"] += 1
        _stats[name]["ms_sum"] += dt
        if not ok:
            _stats[name]["err"] += 1


def tool_report() -> dict:
    report = {}
    for name, s in _stats.items():
        n = max(s["n"], 1)
        report[name] = {"n": s["n"], "error_rate": s["err"] / n, "avg_ms": s["ms_sum"] / n}
    return report


if __name__ == "__main__":
    import json

    def succeed():
        return "ok"

    def boom():
        raise RuntimeError("stock timeout")

    for _ in range(3):
        timed_tool("check_stock", succeed)
    try:
        timed_tool("check_stock", boom)
    except RuntimeError:
        pass
    print(json.dumps(tool_report(), indent=2))