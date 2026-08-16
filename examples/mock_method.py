#!/usr/bin/env python3
"""Create a deterministic synthetic trajectory for the repository self-test."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

import numpy as np


def write(path: Path, offset: float, ground_truth: Optional[Path] = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    times = np.linspace(0, 4, 5)
    xyz = np.column_stack((times, np.sin(times), np.zeros_like(times)))
    quaternion = np.tile([0.0, 0.0, 0.0, 1.0], (len(times), 1))
    if ground_truth is not None:
        ground_truth.parent.mkdir(parents=True, exist_ok=True)
        np.savetxt(
            ground_truth,
            np.column_stack((times, xyz, quaternion)),
            fmt="%.9f",
        )
    xyz += np.array([3.0, -2.0, 0.5])
    xyz[:, 1] += offset * np.sin(times * 2.0)
    np.savetxt(path, np.column_stack((times, xyz, quaternion)), fmt="%.9f")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--ground-truth", type=Path)
    parser.add_argument("--offset", type=float, default=0.0)
    args = parser.parse_args()
    write(args.output, args.offset, args.ground_truth)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
