"""Discover existing local result trees without modifying or importing them."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Optional


KNOWN_LAYOUTS = {
    "AirSLAM": "AirSLAM/Results_airslam/CERBERUS",
    "ORB-SLAM3": "orb3/Results_orb3/CERBERUS",
    "OpenVINS": "OpenVINS/Results_ov/CERBERUS",
    "SchurVINS": "schur/Results_schur/CERBERUS",
    "Basalt": "basalt/Results_basalt/CERBERUS",
}


def classify(name: str) -> dict[str, object]:
    patterns = [
        ("occlusion", r"occ(?:_p)?(?P<value>\d+(?:\.\d+)?)"),
        ("image_degradation", r"(?:^|_)K(?P<value>\d+(?:\.\d+)?)"),
        ("focal", r"focal[_-]?(?P<value>-?\d+(?:\.\d+)?)"),
        ("principal", r"principal[_-]?(?P<value>-?\d+(?:\.\d+)?)"),
        ("rotation", r"(?:rotation|roll|pitch|yaw)[_-]?(?P<value>-?\d+(?:\.\d+)?)"),
        ("translation", r"(?:translation|tbc_t[xyz])[_-]?(?P<value>-?\d+(?:\.\d+)?)"),
    ]
    found: list[dict[str, object]] = []
    for kind, pattern in patterns:
        match = re.search(pattern, name, re.IGNORECASE)
        if match:
            found.append({"type": kind, "severity": float(match.group("value"))})
    if not found:
        return {"type": "baseline", "severity": 0.0}
    if len(found) == 1:
        return found[0]
    return {"type": "composite", "components": found}


def discover(algorithms_root: Path) -> dict[str, object]:
    methods: dict[str, object] = {}
    total = 0
    for method, relative in KNOWN_LAYOUTS.items():
        root = algorithms_root / relative
        trajectories = []
        if root.is_dir():
            paths = sorted(set(root.rglob("trajectory.txt")) | set(root.rglob("trajectory_v0.txt")))
            for path in paths:
                # Legacy result trees contain a few dangling convenience links.
                # They are not trajectories and must not abort the whole audit.
                if not path.is_file():
                    continue
                trajectories.append({
                    "path": str(path),
                    "relative_path": str(path.relative_to(root)),
                    "bytes": path.stat().st_size,
                    "perturbation": classify(path.parent.name),
                })
        total += len(trajectories)
        methods[method] = {"root": str(root), "trajectory_count": len(trajectories), "trajectories": trajectories}
    return {"schema_version": 1, "algorithms_root": str(algorithms_root), "trajectory_count": total, "methods": methods}


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--algorithms-root", type=Path, default=Path.home() / "Algs")
    parser.add_argument("--output", type=Path, default=Path("results/local_asset_index.json"))
    args = parser.parse_args(argv)
    catalog = discover(args.algorithms_root.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"indexed {catalog['trajectory_count']} trajectories in {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
