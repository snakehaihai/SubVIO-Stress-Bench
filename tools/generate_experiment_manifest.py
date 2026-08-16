#!/usr/bin/env python3
"""Expand the benchmark protocol into the complete experiment matrix."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from subvio_bench.protocol import load_protocol  # noqa: E402


FIELDS = ["experiment_id", "family", "method", "sequence", "dimension", "level", "seed", "occlusion_percent", "frame_rate_factor"]


def rows_from_protocol(protocol: dict) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    sensor = protocol["sensor_stress"]
    for method in protocol["methods"]:
        method_id = method.lower().replace("-", "")
        for dimension, specification in sensor["dimensions"].items():
            for seed in sensor["seeds"]:
                for level_index, level in enumerate(specification["levels"]):
                    rows.append({
                        "experiment_id": f"sensor-{method_id}-{dimension}-l{level_index:02d}-s{seed}",
                        "family": "sensor", "method": method, "sequence": sensor["sequence"],
                        "dimension": dimension, "level": level, "seed": seed,
                        "occlusion_percent": "", "frame_rate_factor": "",
                    })
    dynamic = protocol["dynamic_stress"]
    for method in dynamic["methods"]:
        method_id = method.lower().replace("-", "")
        for occ_index, occlusion in enumerate(dynamic["occlusion_percent"]):
            for factor_index, factor in enumerate(dynamic["frame_rate_factor"]):
                rows.append({
                    "experiment_id": f"dynamic-{method_id}-o{occ_index:02d}-d{factor_index:02d}",
                    "family": "dynamic", "method": method, "sequence": dynamic["sequence"],
                    "dimension": "", "level": "", "seed": "",
                    "occlusion_percent": occlusion, "frame_rate_factor": factor,
                })
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", default="configs/benchmark_protocol.yaml")
    parser.add_argument("--output", type=Path, default=Path("results/benchmark/experiment_manifest.csv"))
    args = parser.parse_args()
    rows = rows_from_protocol(load_protocol(args.protocol))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} experiments to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
