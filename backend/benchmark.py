"""Repeatable loaded-facts/rules benchmark, no network or model calls."""

import json
import platform
import statistics
import time
from backend.gis import ROOT
from backend.rules import assess, load_rules, CHECKS


def main():
    context = json.loads((ROOT / "data/fixtures/2202010009.json").read_text())
    bundle = load_rules()
    inputs = dict(
        lot_depth_ft=80,
        lot_width_ft=40,
        lot_area_sqft=6000,
        building_height_ft=18,
        roof_slope_percent=20,
    )
    durations = []
    for _ in range(100):
        start = time.perf_counter()
        result = assess(
            context,
            "single-family",
            inputs,
            {k: True for k in CHECKS},
            "Hypothetical benchmark scenario",
            bundle,
        )
        durations.append(time.perf_counter() - start)
        assert result["status"] == "evaluated"
    ordered = sorted(durations)
    evidence = {
        "runs": 100,
        "p95_ms": ordered[94] * 1000,
        "median_ms": statistics.median(durations) * 1000,
        "max_ms": max(durations) * 1000,
        "python": platform.python_version(),
        "machine": platform.platform(),
        "cpu": next(
            (
                line.split(":", 1)[1].strip()
                for line in open("/proc/cpuinfo")
                if line.startswith("model name")
            ),
            "unknown",
        ),
        "rule_version": bundle[1],
        "network": False,
        "fact_origin": "recorded GIS + hypothetical project assertions",
    }
    print(json.dumps(evidence, indent=2))
    assert ordered[94] < 1


if __name__ == "__main__":
    main()
