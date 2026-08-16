"""Evaluate TUM trajectories with deterministic, dependency-light metrics."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Optional, Union

import numpy as np

from .trajectory import align_positions, associate_indices, load_tum, path_length


def evaluate(
    reference_path: Union[str, Path],
    estimate_path: Union[str, Path],
    max_diff: float = 0.02,
    with_scale: bool = False,
    drift_penalty_m_per_s: float = 0.025,
) -> dict[str, Any]:
    """Evaluate one trajectory using the benchmark distance-coverage protocol.

    ``penalized_ape_rmse_m`` includes untracked prefix/tail reference samples.
    Their error grows linearly from zero at the closest tracked boundary using
    ``drift_penalty_m_per_s``. The benchmark configuration states the rate; the
    integration convention; this convention is therefore recorded explicitly.
    """
    reference = load_tum(reference_path)
    estimate = load_tum(estimate_path)
    ref_indices, est_indices = associate_indices(reference, estimate, max_diff)
    matched_ref, matched_est = reference[ref_indices], estimate[est_indices]
    aligned, transform = align_positions(matched_ref[:, 1:4], matched_est[:, 1:4], with_scale)
    errors = np.linalg.norm(matched_ref[:, 1:4] - aligned, axis=1)
    if len(aligned) > 1:
        ref_steps = np.diff(matched_ref[:, 1:4], axis=0)
        est_steps = np.diff(aligned, axis=0)
        rpe = np.linalg.norm(ref_steps - est_steps, axis=1)
        rpe_rmse = float(np.sqrt(np.mean(rpe**2)))
    else:
        rpe_rmse = None
    reference_distance = path_length(reference[:, 1:4])
    tracked_distance = path_length(reference[ref_indices[0] : ref_indices[-1] + 1, 1:4])

    penalty_errors: list[float] = []
    if drift_penalty_m_per_s > 0:
        before = reference[: ref_indices[0], 0]
        after = reference[ref_indices[-1] + 1 :, 0]
        penalty_errors.extend((drift_penalty_m_per_s * (matched_ref[0, 0] - before)).tolist())
        penalty_errors.extend((drift_penalty_m_per_s * (after - matched_ref[-1, 0])).tolist())
    all_errors = np.concatenate((errors, np.asarray(penalty_errors, dtype=float)))
    return {
        "reference": str(Path(reference_path)),
        "estimate": str(Path(estimate_path)),
        "alignment": "similarity" if with_scale else "rigid",
        "max_timestamp_difference_s": max_diff,
        "reference_poses": int(len(reference)),
        "estimate_poses": int(len(estimate)),
        "matched_poses": int(len(matched_ref)),
        "coverage_definition": "ground_truth_path_distance_between_tracking_endpoints / total_ground_truth_path_distance",
        "reference_distance_m": reference_distance,
        "tracked_distance_m": tracked_distance,
        "coverage": min(1.0, tracked_distance / reference_distance) if reference_distance > 0 else 0.0,
        "ape_rmse_m": float(np.sqrt(np.mean(errors**2))),
        "penalized_ape_rmse_m": float(np.sqrt(np.mean(all_errors**2))),
        "drift_penalty_m_per_s": drift_penalty_m_per_s,
        "penalized_reference_poses": len(penalty_errors),
        "ape_mean_m": float(np.mean(errors)),
        "ape_median_m": float(np.median(errors)),
        "ape_max_m": float(np.max(errors)),
        "rpe_translation_rmse_m": rpe_rmse,
        "transform": transform,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reference")
    parser.add_argument("estimate")
    parser.add_argument("--max-diff", type=float, default=0.02)
    parser.add_argument("--correct-scale", action="store_true")
    parser.add_argument("--drift-penalty", type=float, default=0.025)
    parser.add_argument("--output", type=Path)
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    metrics = evaluate(args.reference, args.estimate, args.max_diff, args.correct_scale, args.drift_penalty)
    rendered = json.dumps(metrics, indent=2, ensure_ascii=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
