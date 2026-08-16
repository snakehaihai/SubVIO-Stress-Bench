#!/usr/bin/env python3
"""Plot ground truth and one or more noise-affected TUM trajectories."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from subvio_bench.trajectory import align_positions, associate_indices, load_tum  # noqa: E402


def parse_estimate(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("estimate must use LABEL=PATH")
    label, path = value.split("=", 1)
    if not label.strip() or not path.strip():
        raise argparse.ArgumentTypeError("estimate must use non-empty LABEL=PATH")
    return label.strip(), Path(path)


def cumulative_distance(xyz: np.ndarray) -> np.ndarray:
    if len(xyz) < 2:
        return np.zeros(len(xyz))
    return np.concatenate(([0.0], np.cumsum(np.linalg.norm(np.diff(xyz, axis=0), axis=1))))


def aligned_trajectory(reference: np.ndarray, estimate: np.ndarray, max_diff: float) -> tuple[np.ndarray, np.ndarray, float]:
    ref_indices, est_indices = associate_indices(reference, estimate, max_diff)
    reference_xyz = reference[ref_indices, 1:4]
    estimate_xyz = estimate[est_indices, 1:4]
    aligned_xyz, _ = align_positions(reference_xyz, estimate_xyz, with_scale=False)
    error = np.linalg.norm(reference_xyz - aligned_xyz, axis=1)
    return reference_xyz, aligned_xyz, float(np.sqrt(np.mean(error**2)))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ground-truth", required=True, type=Path)
    parser.add_argument(
        "--estimate",
        required=True,
        action="append",
        type=parse_estimate,
        metavar="LABEL=PATH",
        help="repeat for each perturbed trajectory",
    )
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--max-diff", type=float, default=0.02)
    parser.add_argument("--title", default="Trajectory deformation under sensor perturbations")
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    reference = load_tum(args.ground_truth)
    figure, (axis_xy, axis_z) = plt.subplots(
        2, 1, figsize=(8, 8), gridspec_kw={"height_ratios": [4, 1]}
    )
    axis_xy.plot(reference[:, 1], reference[:, 2], color="black", linewidth=2.5, label="Ground truth")
    reference_distance = cumulative_distance(reference[:, 1:4])
    axis_z.plot(reference_distance, reference[:, 3], color="black", linewidth=2.5)

    for label, path in args.estimate:
        estimate = load_tum(path)
        matched_reference, aligned, rmse = aligned_trajectory(reference, estimate, args.max_diff)
        axis_xy.plot(aligned[:, 0], aligned[:, 1], linewidth=1.3, label=f"{label} (RMSE {rmse:.4f} m)")
        axis_z.plot(cumulative_distance(aligned), aligned[:, 2], linewidth=1.1, label=label)

    axis_xy.set_title(args.title)
    axis_xy.set_xlabel("X [m]")
    axis_xy.set_ylabel("Y [m]")
    axis_xy.set_aspect("equal", adjustable="datalim")
    axis_xy.grid(alpha=0.3)
    axis_xy.legend(fontsize=8)
    axis_z.set_title("Height profile")
    axis_z.set_xlabel("Distance traveled [m]")
    axis_z.set_ylabel("Z [m]")
    axis_z.grid(alpha=0.3)
    figure.tight_layout()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(args.output, dpi=180, bbox_inches="tight")
    plt.close(figure)
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
