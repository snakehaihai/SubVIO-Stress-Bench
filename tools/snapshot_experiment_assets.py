#!/usr/bin/env python3
"""Snapshot local experiment configs and scripts into an ASCII-only bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

import numpy as np
import yaml


HOME = Path.home()

TREES = {
    "airslam/configs/sensitivity": HOME / "Algs/AirSLAM/src/airslam/configs/camera/sensitivity",
    "orbslam3/configs/sensitivity": HOME / "Algs/orb3/sensitivity_experiments/configs/sensitivity",
    "openvins/configs/sensitivity": HOME / "Algs/OpenVINS/src/open_vins/config/CERBERUS/sensitivity",
    "schurvins/configs/sensitivity": HOME / "Algs/schur/src/SchurVINS/svo_ros/param/calib/sensitivity",
}

FILES = {
    "shared/random_directions.json": HOME / "Algs/summaries/sensitivity_experiment/random_directions.json",
    "airslam/configs/cerberus.yaml": HOME / "Algs/AirSLAM/src/airslam/configs/camera/cerberus.yaml",
    "airslam/configs/vo_cerberus.yaml": HOME / "Algs/AirSLAM/src/airslam/configs/visual_odometry/vo_cerberus.yaml",
    "airslam/scripts/generate_sensitivity_configs.py": HOME / "Algs/AirSLAM/src/airslam/scripts/generate_sensitivity_configs.py",
    "airslam/scripts/run_sensitivity.py": HOME / "Algs/AirSLAM/src/airslam/scripts/run_sensitivity.py",
    "airslam/scripts/run_cerberus_composite.sh": HOME / "Algs/AirSLAM/src/airslam/scripts/run_cerberus_composite.sh",
    "orbslam3/configs/CERBERUS.yaml": HOME / "Algs/orb3/Examples/Stereo-Inertial/CERBERUS.yaml",
    "orbslam3/scripts/generate_sensitivity_configs.py": HOME / "Algs/orb3/sensitivity_experiments/generate_sensitivity_configs.py",
    "orbslam3/scripts/run_sensitivity.py": HOME / "Algs/orb3/sensitivity_experiments/run_sensitivity.py",
    "orbslam3/scripts/run_cerberus_composite_kn.sh": HOME / "Algs/orb3/scripts/run_cerberus_composite_kn.sh",
    "orbslam3/scripts/run_cerberus_composite_occ.sh": HOME / "Algs/orb3/scripts/run_cerberus_composite_occ.sh",
    "orbslam3/scripts/run_cerberus_composite_occ30_kn.sh": HOME / "Algs/orb3/scripts/run_cerberus_composite_occ30_kn.sh",
    "openvins/configs/estimator_config.yaml": HOME / "Algs/OpenVINS/src/open_vins/config/CERBERUS/estimator_config.yaml",
    "openvins/configs/kalibr_imu_chain.yaml": HOME / "Algs/OpenVINS/src/open_vins/config/CERBERUS/kalibr_imu_chain.yaml",
    "openvins/configs/kalibr_imucam_chain.yaml": HOME / "Algs/OpenVINS/src/open_vins/config/CERBERUS/kalibr_imucam_chain.yaml",
    "openvins/scripts/generate_sensitivity_configs.py": HOME / "Algs/OpenVINS/scripts/generate_sensitivity_configs.py",
    "openvins/scripts/run_sensitivity.py": HOME / "Algs/OpenVINS/scripts/run_sensitivity.py",
    "openvins/scripts/run_cerberus_composite.sh": HOME / "Algs/OpenVINS/src/open_vins/ov_msckf/scripts/run_cerberus_composite.sh",
    "openvins/scripts/run_cerberus_occ.sh": HOME / "Algs/OpenVINS/src/open_vins/ov_msckf/scripts/run_cerberus_occ.sh",
    "openvins/scripts/run_cerberus_occ30_Kn.sh": HOME / "Algs/OpenVINS/src/open_vins/ov_msckf/scripts/run_cerberus_occ30_Kn.sh",
    "schurvins/configs/CERBERUS_stereo.yaml": HOME / "Algs/schur/src/SchurVINS/svo_ros/param/calib/CERBERUS_stereo.yaml",
    "schurvins/scripts/generate_sensitivity_configs.py": HOME / "Algs/schur/generate_sensitivity_configs.py",
    "schurvins/scripts/run_sensitivity.py": HOME / "Algs/schur/run_sensitivity.py",
    "schurvins/scripts/run_cerberus_in_container.sh": HOME / "Algs/schur/debug/run_cerberus_in_container.sh",
    "dataset/scripts/run_generate_obstacle_fps_datasets.py": HOME / "Datasets/DARPA-CERBERUS/video_processing/run_generate_obstacle_fps_datasets.py",
    "dataset/scripts/run_occ_datasets.py": HOME / "Datasets/DARPA-CERBERUS/video_processing/run_occ_datasets.py",
    "dataset/scripts/run_occ10_20_40_60_80_Kn_datasets.py": HOME / "Datasets/DARPA-CERBERUS/video_processing/run_occ10_20_40_60_80_Kn_datasets.py",
    "dataset/scripts/run_occ30_Kn_datasets.py": HOME / "Datasets/DARPA-CERBERUS/video_processing/run_occ30_Kn_datasets.py",
    "dataset/scripts/run_occ50_70_90_Kn_datasets.py": HOME / "Datasets/DARPA-CERBERUS/video_processing/run_occ50_70_90_Kn_datasets.py",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def plain_types(value):
    if isinstance(value, dict):
        return {key: plain_types(item) for key, item in value.items()}
    if isinstance(value, list):
        return [plain_types(item) for item in value]
    if isinstance(value, tuple):
        return [plain_types(item) for item in value]
    if isinstance(value, np.ndarray):
        return plain_types(value.tolist())
    if isinstance(value, np.generic):
        return value.item()
    return value


def ascii_snapshot(relative: str, data: bytes) -> tuple[bytes, bool]:
    text = data.decode("utf-8-sig")
    normalized_numpy_yaml = "python/object/apply:numpy" in text
    if normalized_numpy_yaml:
        body = "\n".join(line for line in text.splitlines() if not line.startswith("%YAML"))
        value = plain_types(yaml.unsafe_load(body))
        text = "%YAML:1.0\n\n" + yaml.safe_dump(value, sort_keys=False)
    text = text.encode("ascii", errors="ignore").decode("ascii")
    text = "\n".join(line.rstrip() for line in text.splitlines()).rstrip() + "\n"
    if relative == "airslam/scripts/generate_sensitivity_configs.py":
        text = text.replace(
            "data['cam0']['intrinsics'][2] = cx0_base + delta_cx",
            "data['cam0']['intrinsics'][2] = float(cx0_base + delta_cx)",
        ).replace(
            "data['cam0']['intrinsics'][3] = cy0_base + delta_cy",
            "data['cam0']['intrinsics'][3] = float(cy0_base + delta_cy)",
        ).replace(
            "data['cam1']['intrinsics'][2] = cx1_base + delta_cx",
            "data['cam1']['intrinsics'][2] = float(cx1_base + delta_cx)",
        ).replace(
            "data['cam1']['intrinsics'][3] = cy1_base + delta_cy",
            "data['cam1']['intrinsics'][3] = float(cy1_base + delta_cy)",
        )
    return text.encode("ascii"), normalized_numpy_yaml


def iter_sources():
    for destination, source in FILES.items():
        yield destination, source
    for destination_root, source_root in TREES.items():
        for source in sorted(path for path in source_root.rglob("*") if path.is_file()):
            yield str(Path(destination_root) / source.relative_to(source_root)), source


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("experiment_assets/snapshot"))
    parser.add_argument("--replace", action="store_true", help="replace existing snapshot files")
    args = parser.parse_args()
    records = []
    destinations = set()
    for relative, source in iter_sources():
        if relative in destinations:
            raise RuntimeError(f"duplicate destination: {relative}")
        destinations.add(relative)
        if not source.is_file():
            raise FileNotFoundError(source)
        target = args.output / relative
        if target.exists() and not args.replace:
            raise FileExistsError(f"{target} exists; pass --replace to refresh the snapshot")
        original = source.read_bytes()
        snapshot, normalized_numpy_yaml = ascii_snapshot(relative, original)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            target.chmod((target.stat().st_mode & 0o777) | 0o200)
        target.write_bytes(snapshot)
        target.chmod((source.stat().st_mode & 0o777) | 0o200)
        records.append({
            "path": relative,
            "source": "~/" + str(source.relative_to(HOME)),
            "source_sha256": digest(original),
            "snapshot_sha256": digest(snapshot),
            "ascii_sanitized": original != snapshot,
            "numpy_yaml_normalized": normalized_numpy_yaml,
            "bytes": len(snapshot),
        })
    manifest = {"schema_version": 1, "file_count": len(records), "files": records}
    manifest_path = args.output / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="ascii")
    print(f"snapshotted {len(records)} files into {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
