#!/usr/bin/env python3
"""Generate benchmark APE and coverage figures from summary.csv."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path
from typing import Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", type=Path, default=Path("results/summaries/summary.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("results/figures"))
    args = parser.parse_args(argv)
    groups: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    with args.summary.open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            groups[(row["perturbation_type"], row["method"])].append(row)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    generated = 0
    for perturbation in sorted({key[0] for key in groups}):
        fig, (ape_axis, coverage_axis) = plt.subplots(1, 2, figsize=(10, 4))
        for (kind, method), rows in sorted(groups.items()):
            if kind != perturbation:
                continue
            points = sorted((float(row["severity"]), float(row["penalized_ape_rmse_m"]), float(row["coverage"])) for row in rows)
            ape_axis.plot([p[0] for p in points], [p[1] for p in points], marker="o", label=method)
            coverage_axis.plot([p[0] for p in points], [p[2] for p in points], marker="o", label=method)
        ape_axis.set(xlabel="Severity", ylabel="Penalized APE RMSE [m]", title=f"{perturbation}: accuracy")
        coverage_axis.set(xlabel="Severity", ylabel="Coverage", ylim=(0, 1.05), title=f"{perturbation}: tracking")
        ape_axis.grid(alpha=0.25)
        coverage_axis.grid(alpha=0.25)
        if groups:
            ape_axis.legend()
        fig.tight_layout()
        fig.savefig(args.output_dir / f"{perturbation}.png", dpi=160)
        plt.close(fig)
        generated += 1
    print(f"generated {generated} figure(s) in {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
