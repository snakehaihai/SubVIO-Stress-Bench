"""Trajectory I/O, timestamp association, and rigid alignment."""

from __future__ import annotations

from pathlib import Path
from typing import Union

import numpy as np


def load_tum(path: Union[str, Path]) -> np.ndarray:
    """Load the first eight columns of a TUM trajectory.

    Comment lines and OpenVINS covariance columns are accepted. Timestamps
    that are clearly nanoseconds are normalized to seconds.
    """
    rows: list[list[float]] = []
    with Path(path).open(encoding="utf-8", errors="replace") as stream:
        for line_number, raw in enumerate(stream, 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.replace(",", " ").split()
            if len(parts) < 8:
                continue
            try:
                row = [float(value) for value in parts[:8]]
            except ValueError as exc:
                raise ValueError(f"{path}:{line_number}: invalid numeric trajectory row") from exc
            if np.all(np.isfinite(row)):
                rows.append(row)
    if not rows:
        raise ValueError(f"no valid TUM rows found in {path}")
    data = np.asarray(rows, dtype=float)
    if np.median(np.abs(data[:, 0])) > 1e10:
        data[:, 0] /= 1e9
    order = np.argsort(data[:, 0])
    return data[order]


def associate_indices(reference: np.ndarray, estimate: np.ndarray, max_diff: float) -> tuple[np.ndarray, np.ndarray]:
    """Return one-to-one timestamp associations as reference/estimate indices."""
    ref_times = reference[:, 0]
    candidates: list[tuple[float, int, int]] = []
    for est_index, timestamp in enumerate(estimate[:, 0]):
        insertion = int(np.searchsorted(ref_times, timestamp))
        for ref_index in (insertion - 1, insertion):
            if 0 <= ref_index < len(ref_times):
                delta = abs(ref_times[ref_index] - timestamp)
                if delta <= max_diff:
                    candidates.append((delta, ref_index, est_index))
    used_ref: set[int] = set()
    used_est: set[int] = set()
    pairs: list[tuple[int, int]] = []
    for _, ref_index, est_index in sorted(candidates):
        if ref_index not in used_ref and est_index not in used_est:
            used_ref.add(ref_index)
            used_est.add(est_index)
            pairs.append((ref_index, est_index))
    if not pairs:
        raise ValueError(f"no timestamp pairs within {max_diff:g} seconds")
    pairs.sort()
    return (
        np.asarray([pair[0] for pair in pairs], dtype=int),
        np.asarray([pair[1] for pair in pairs], dtype=int),
    )


def associate(reference: np.ndarray, estimate: np.ndarray, max_diff: float) -> tuple[np.ndarray, np.ndarray]:
    """Associate each estimate timestamp to the nearest unused reference."""
    ref_indices, est_indices = associate_indices(reference, estimate, max_diff)
    return reference[ref_indices], estimate[est_indices]


def path_length(xyz: np.ndarray) -> float:
    """Return cumulative Euclidean distance along a position sequence."""
    if len(xyz) < 2:
        return 0.0
    return float(np.linalg.norm(np.diff(xyz, axis=0), axis=1).sum())


def align_positions(reference_xyz: np.ndarray, estimate_xyz: np.ndarray, with_scale: bool = False) -> tuple[np.ndarray, dict[str, object]]:
    """Align estimate to reference using Umeyama similarity estimation."""
    if len(reference_xyz) < 3:
        raise ValueError("at least three associated poses are required")
    ref_mean = reference_xyz.mean(axis=0)
    est_mean = estimate_xyz.mean(axis=0)
    ref_centered = reference_xyz - ref_mean
    est_centered = estimate_xyz - est_mean
    covariance = (ref_centered.T @ est_centered) / len(reference_xyz)
    u, singular, vt = np.linalg.svd(covariance)
    correction = np.eye(3)
    if np.linalg.det(u @ vt) < 0:
        correction[-1, -1] = -1
    rotation = u @ correction @ vt
    scale = 1.0
    if with_scale:
        variance = np.mean(np.sum(est_centered**2, axis=1))
        if variance <= np.finfo(float).eps:
            raise ValueError("estimated trajectory has zero positional variance")
        scale = float(np.sum(singular * np.diag(correction)) / variance)
    translation = ref_mean - scale * (rotation @ est_mean)
    aligned = (scale * (rotation @ estimate_xyz.T)).T + translation
    transform = {
        "scale": scale,
        "rotation": rotation.tolist(),
        "translation": translation.tolist(),
    }
    return aligned, transform
