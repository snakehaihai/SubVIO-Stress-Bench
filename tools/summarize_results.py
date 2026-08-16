#!/usr/bin/env python3
"""Aggregate per-run metrics into stable CSV and JSON tables."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Optional


FIELDS = [
    "experiment_id", "method", "sequence", "perturbation_type", "severity",
    "penalized_ape_rmse_m", "ape_rmse_m", "ape_mean_m", "ape_median_m", "ape_max_m",
    "rpe_translation_rmse_m", "coverage", "reference_distance_m",
    "tracked_distance_m", "drift_penalty_m_per_s", "matched_poses", "estimate_poses",
]


def collect(results_dir: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for path in sorted(results_dir.rglob("metrics.json")):
        metrics = json.loads(path.read_text(encoding="utf-8"))
        perturbation = metrics.get("perturbation") or {}
        row = {field: metrics.get(field) for field in FIELDS}
        row["perturbation_type"] = perturbation.get("type", "none")
        row["severity"] = perturbation.get("severity", 0)
        rows.append(row)
    return rows


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args(argv)
    output = args.output_dir or args.results_dir / "summaries"
    output.mkdir(parents=True, exist_ok=True)
    rows = collect(args.results_dir)
    (output / "summary.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (output / "summary.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} rows to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
