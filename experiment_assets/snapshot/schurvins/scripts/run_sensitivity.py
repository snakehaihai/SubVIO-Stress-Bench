#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
SchurVINS CERBERUS


/ws/results/CERBERUS/sensitivity/seqN/
     acc_noise/
        seed0/
           acc_noise_0.0x_seed0/  (trajectory, evo)
           acc_noise_0.5x_seed0/
           ...
        seed1/
        seed2/
     gyro_noise/
     ...
     summary.csv  ()

Usage:
  python3 run_sensitivity.py --dimension acc_noise
  python3 run_sensitivity.py --dimension all --seq seq1
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple, List
import numpy as np
import yaml
import glob


#
DIMENSIONS = [
    "acc_noise",
    "gyro_noise",
    "acc_bias",
    "gyro_bias",
    "rotation",
    "translation",
    "focal",
    "principal",
    "distortion",
]

# seeds
SEEDS = [0, 1, 2]


def cleanup_ros_processes() -> None:
    """ROS"""
    subprocess.run("pkill -9 -f rosmaster 2>/dev/null || true", shell=True)
    subprocess.run("pkill -9 -f roslaunch 2>/dev/null || true", shell=True)
    subprocess.run("pkill -9 -f svo_node 2>/dev/null || true", shell=True)
    subprocess.run("pkill -9 -f ros 2>/dev/null || true", shell=True)
    time.sleep(3)


def resolve_runtime_paths() -> Tuple[str, str, str, str]:
    """
    : config_dir, result_base, workspace, launch_file
    """
    #  /home/zyy/Algs/schur/
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # config dir -
    config_dir = os.path.join(script_dir, "src/SchurVINS/svo_ros/param/calib/sensitivity")
    if not os.path.exists(config_dir):
        #
        if os.path.exists("/ws/src/SchurVINS/svo_ros/param/calib/sensitivity"):
            config_dir = "/ws/src/SchurVINS/svo_ros/param/calib/sensitivity"
            workspace = "/ws"
        elif os.path.exists("/home/zyy/Algs/schur/src/SchurVINS/svo_ros/param/calib/sensitivity"):
            config_dir = "/home/zyy/Algs/schur/src/SchurVINS/svo_ros/param/calib/sensitivity"
            workspace = "/ws"
        else:
            config_dir = "/home/zyy/Algs/schur/src/SchurVINS/svo_ros/param/calib/sensitivity"
            workspace = "/ws"
    else:
        workspace = "/ws"

    # results base
    if os.path.exists("/ws/results/CERBERUS"):
        result_base = "/ws/results/CERBERUS"
    else:
        result_base = "/home/zyy/Algs/schur/results/CERBERUS"

    # launch file -
    launch_file = os.path.join(script_dir, "src/SchurVINS/svo_ros/launch/frontend/CERBERUS_stereo_frontend_imu.launch")
    if not os.path.exists(launch_file):
        #
        if os.path.exists("/ws/src/SchurVINS/svo_ros/launch/frontend/CERBERUS_stereo_frontend_imu.launch"):
            launch_file = "/ws/src/SchurVINS/svo_ros/launch/frontend/CERBERUS_stereo_frontend_imu.launch"
        elif os.path.exists("/home/zyy/Algs/schur/src/SchurVINS/svo_ros/launch/frontend/CERBERUS_stereo_frontend_imu.launch"):
            launch_file = "/home/zyy/Algs/schur/src/SchurVINS/svo_ros/launch/frontend/CERBERUS_stereo_frontend_imu.launch"
        else:
            launch_file = "/home/zyy/Algs/schur/src/SchurVINS/svo_ros/launch/frontend/CERBERUS_stereo_frontend_imu.launch"

    return config_dir, result_base, workspace, launch_file


def find_original_baseline_result(sequence: str) -> Optional[str]:
    """baseline"""
    candidates = [
        f"/ws/results/CERBERUS/Original/{sequence}/trajectory.txt",
        f"/ws/results/CERBERUS/original/{sequence}/trajectory.txt",
        f"/ws/results/CERBERUS/baseline/{sequence}/trajectory.txt",
        f"/ws/results/CERBERUS/Baseline/{sequence}/trajectory.txt",
        f"/home/zyy/Algs/schur/results/CERBERUS/Original/{sequence}/trajectory.txt",
    ]
    for p in candidates:
        if os.path.exists(p) and os.path.getsize(p) > 100:
            return p
    return None


def ensure_dir(path: str) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)


def try_symlink_or_copy(src: str, dst: str) -> None:
    """"""
    ensure_dir(os.path.dirname(dst))
    if os.path.exists(dst):
        return
    try:
        os.symlink(src, dst)
    except Exception:
        shutil.copy2(src, dst)


def build_roslaunch_cmd(workspace: str, launch_file: str, calib_file: str, bag_file: str, output_dir: str) -> str:
    """roslaunch"""
    # SchurVINSlaunchcalib_file
    # roslaunchcalib_filebag
    return (
        f"cd {workspace} && "
        f"source devel/setup.bash && "
        f"timeout 600 bash -c '"
        f"roslaunch svo_ros frontend/CERBERUS_stereo_frontend_imu.launch calib_file:={calib_file} & "
        f"LAUNCH_PID=$!; "
        f"sleep 5; "
        f"rosbag play {bag_file} --clock --rate=1.0; "
        f"sleep 2; "
        f"kill $LAUNCH_PID 2>/dev/null; "
        f"pkill -f svo_node 2>/dev/null; "
        f"wait' 2>&1; exit 0"
    )


def run_one(cmd: str, timeout_sec: int = 600) -> bool:
    """"""
    cleanup_ros_processes()
    try:
        proc = subprocess.run(
            cmd,
            shell=True,
            executable="/bin/bash",
            stdin=subprocess.DEVNULL,
            timeout=timeout_sec,
        )
        return proc.returncode == 0
    except subprocess.TimeoutExpired:
        print("   Timeout (10min). Cleaning up...")
        cleanup_ros_processes()
        return False
    finally:
        cleanup_ros_processes()


def load_tum_trajectory(file_path: str) -> np.ndarray:
    """TUM"""
    traj = []
    if not os.path.exists(file_path):
        return np.array([])
    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) >= 8:
                traj.append([float(x) for x in parts[:8]])
    return np.array(traj) if traj else np.array([])


def umeyama_alignment(src_points: np.ndarray, dst_points: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """UmeyamaSE3"""
    assert src_points.shape == dst_points.shape and src_points.shape[1] == 3
    assert src_points.shape[0] > 0

    n = src_points.shape[0]
    src_centroid = np.mean(src_points, axis=0)
    dst_centroid = np.mean(dst_points, axis=0)

    src_centered = src_points - src_centroid
    dst_centered = dst_points - dst_centroid

    H = src_centered.T @ dst_centered
    U, S, Vt = np.linalg.svd(H)

    R = Vt.T @ U.T

    if np.linalg.det(R) < 0:
        Vt[-1, :] *= -1
        R = Vt.T @ U.T

    t = dst_centroid - R @ src_centroid

    return R, t


def apply_se3_transform(points: np.ndarray, R: np.ndarray, t: np.ndarray) -> np.ndarray:
    """SE3"""
    return (R @ points.T).T + t


def compute_coverage_metrics(gt_path: str, est_path: str, time_tolerance: float = 0.05) -> dict:
    """"""
    gt = load_tum_trajectory(gt_path)
    est = load_tum_trajectory(est_path)

    if gt.size == 0 or est.size == 0:
        return {
            "coverage_pct": 0.0,
            "rmse": None,
            "ate": None,
            "status": "CRASHED",
        }

    #
    matched_pairs = []
    for i, est_t in enumerate(est[:, 0]):
        gt_idx = np.argmin(np.abs(gt[:, 0] - est_t))
        if np.abs(gt[gt_idx, 0] - est_t) < time_tolerance:
            matched_pairs.append((gt_idx, i))

    if len(matched_pairs) == 0:
        return {
            "coverage_pct": 0.0,
            "rmse": None,
            "ate": None,
            "status": "CRASHED",
        }

    # Coverage
    matched_times = [gt[gt_idx, 0] for gt_idx, _ in matched_pairs]
    matched_duration = max(matched_times) - min(matched_times)
    gt_duration = gt[-1, 0] - gt[0, 0]
    coverage_pct = (matched_duration / gt_duration) * 100.0 if gt_duration > 0 else 0.0

    # Status
    time_diff = abs(est[-1, 0] - gt[-1, 0])
    if coverage_pct < 80.0 or time_diff > 10.0:
        status = "CRASHED"
    else:
        status = "COMPLETED"

    # SE3
    matched_gt_positions = np.array([gt[gt_idx, 1:4] for gt_idx, _ in matched_pairs])
    matched_est_positions = np.array([est[est_idx, 1:4] for _, est_idx in matched_pairs])

    R, t = umeyama_alignment(matched_est_positions, matched_gt_positions)
    matched_est_positions_aligned = apply_se3_transform(matched_est_positions, R, t)

    # RMSE & ATE
    errors = []
    for i, (gt_idx, est_idx) in enumerate(matched_pairs):
        gt_pos = gt[gt_idx, 1:4]
        est_pos_aligned = matched_est_positions_aligned[i]
        error = np.linalg.norm(gt_pos - est_pos_aligned)
        errors.append(error)

    errors = np.array(errors)
    rmse = np.sqrt(np.mean(errors ** 2))
    ate = np.mean(errors)

    return {
        "coverage_pct": round(coverage_pct, 2),
        "rmse": round(rmse, 4) if rmse is not None else None,
        "ate": round(ate, 4) if ate is not None else None,
        "status": status,
    }


def evo_ape_rmse(gt_path: str, est_path: str) -> Optional[float]:
    """evo_apeRMSE"""
    cmd = f"evo_ape tum {gt_path} {est_path} -as --no_warnings"
    r = subprocess.run(cmd, shell=True, executable="/bin/bash", capture_output=True, text=True)
    if r.returncode != 0:
        return None
    m = re.search(r"\brmse\s+([0-9]*\.?[0-9]+)", r.stdout, flags=re.IGNORECASE)
    if not m:
        return None
    try:
        return float(m.group(1))
    except Exception:
        return None


def parse_test_point_from_filename(filename: str, dimension: str) -> Optional[float]:
    """"""
    patterns = {
        "acc_noise": r"_([0-9]+\.?[0-9]*)x_",
        "gyro_noise": r"_([0-9]+\.?[0-9]*)x_",
        "acc_bias": r"_([0-9]+\.?[0-9]*)x_",
        "gyro_bias": r"_([0-9]+\.?[0-9]*)x_",
        "rotation": r"_([0-9]+\.?[0-9]*)deg_",
        "translation": r"_([0-9]+\.?[0-9]*)cm_",
        "focal": r"_([0-9]+\.?[0-9]*)x_",
        "principal": r"_([0-9]+\.?[0-9]*)px_",
        "distortion": r"_([0-9]+\.?[0-9]*)x_",
    }

    pattern = patterns.get(dimension)
    if not pattern:
        return None

    m = re.search(pattern, filename)
    if not m:
        return None

    try:
        return float(m.group(1))
    except Exception:
        return None


@dataclass
class EvalRow:
    dimension: str
    seed: int
    test_point: float
    coverage_pct: float
    status: str
    rmse: Optional[float]
    ate: Optional[float]
    duration: float


def find_trajectory_file(result_dir: str) -> Optional[str]:
    """"""
    candidates = [
        os.path.join(result_dir, "trajectory.txt"),
        os.path.join(result_dir, "trajectory_v0.txt"),
        os.path.join(result_dir, "traj.txt"),
    ]
    for p in candidates:
        if os.path.exists(p) and os.path.getsize(p) > 100:
            return p
    return None


def run_experiments_for_dimension(
    dimension: str,
    sequence: str,
    config_dir: str,
    result_base: str,
    workspace: str,
    launch_file: str,
    gt_root: str,
    gt_file_suffix: str,
    baseline_src: Optional[str],
) -> List[EvalRow]:
    """"""
    print(f"\n{'='*60}")
    print(f": {dimension}")
    print(f"{'='*60}")

    dimension_config_dir = os.path.join(config_dir, dimension)
    if not os.path.exists(dimension_config_dir):
        print(f"   : {dimension_config_dir}")
        return []

    #
    config_files = sorted(glob.glob(os.path.join(dimension_config_dir, "*.yaml")))
    if not config_files:
        print(f"   ")
        return []

    print(f"   {len(config_files)} ")

    rows: List[EvalRow] = []
    result_dim_dir = os.path.join(result_base, "sensitivity", sequence, dimension)

    # seed
    for seed in SEEDS:
        print(f"\n  [Seed {seed}]")
        seed_result_dir = os.path.join(result_dim_dir, f"seed{seed}")
        ensure_dir(seed_result_dir)

        # seed
        seed_configs = [f for f in config_files if f"_seed{seed}.yaml" in f]

        for config_path in seed_configs:
            config_filename = os.path.basename(config_path)
            test_point = parse_test_point_from_filename(config_filename, dimension)
            if test_point is None:
                print(f"     : {config_filename}")
                continue

            # .yaml
            result_name = config_filename.replace(".yaml", "")
            result_dir = os.path.join(seed_result_dir, result_name)
            ensure_dir(result_dir)

            traj_path = find_trajectory_file(result_dir)

            # baseline shortcut
            is_baseline = False
            if dimension in ["focal", "distortion"]:
                is_baseline = abs(test_point - 1.0) < 0.01
            else:
                is_baseline = abs(test_point - 0.0) < 0.01

            if is_baseline and baseline_src:
                if not (traj_path and os.path.getsize(traj_path) > 100):
                    try_symlink_or_copy(baseline_src, os.path.join(result_dir, "trajectory.txt"))
                    print(f"     Baseline: {result_name}")
                else:
                    print(f"     Skip (exists): {result_name}")
            elif traj_path and os.path.getsize(traj_path) > 100:
                print(f"     Skip (exists): {result_name}")
            else:
                #
                bag_file = f"/dataset/CERBERUS/{sequence}.bag"
                if not os.path.exists(bag_file):
                    bag_file = f"/dataset/CERBERUS/{sequence}/{sequence}.bag"

                cmd = build_roslaunch_cmd(workspace, launch_file, config_path, bag_file, result_dir)
                print(f"     Run: {result_name}")
                ok = run_one(cmd, timeout_sec=600)
                if not ok:
                    print(f"     Failed: {result_name}")

        # seed
        print(f"\n     Seed {seed} ...")
        for config_path in seed_configs:
            config_filename = os.path.basename(config_path)
            test_point = parse_test_point_from_filename(config_filename, dimension)
            if test_point is None:
                continue

            result_name = config_filename.replace(".yaml", "")
            result_dir = os.path.join(seed_result_dir, result_name)
            traj_path = find_trajectory_file(result_dir)

            if not traj_path or os.path.getsize(traj_path) <= 100:
                continue

            #
            if gt_file_suffix == ".txt":
                gt_path = os.path.join(gt_root, f"{sequence}.txt")
            else:
                gt_path = os.path.join(gt_root, sequence, "gt_tum.txt")

            if not os.path.exists(gt_path):
                continue

            metrics = compute_coverage_metrics(gt_path, traj_path)

            #
            est_traj = load_tum_trajectory(traj_path)
            duration = est_traj[-1, 0] - est_traj[0, 0] if est_traj.size > 0 else 0.0

            # RMSENoneevo_ape
            rmse = metrics["rmse"]
            if rmse is None:
                rmse = evo_ape_rmse(gt_path, traj_path)

            rows.append(EvalRow(
                dimension=dimension,
                seed=seed,
                test_point=test_point,
                coverage_pct=metrics["coverage_pct"],
                status=metrics["status"],
                rmse=rmse,
                ate=metrics["ate"],
                duration=duration,
            ))

    return rows


def generate_summary(sequence: str, result_base: str, all_rows: List[EvalRow]) -> None:
    """CSV"""
    summary_dir = os.path.join(result_base, "sensitivity", sequence)
    ensure_dir(summary_dir)

    csv_path = os.path.join(summary_dir, "summary.csv")

    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "dimension", "seed", "test_point", "coverage_pct",
            "status", "rmse_m", "ate_m", "duration_s"
        ])

        for row in sorted(all_rows, key=lambda r: (r.dimension, r.seed, r.test_point)):
            writer.writerow([
                row.dimension,
                row.seed,
                row.test_point,
                row.coverage_pct,
                row.status,
                row.rmse if row.rmse is not None else "",
                row.ate if row.ate is not None else "",
                row.duration,
            ])

    print(f"\n{'='*60}")
    print(f" CSV: {csv_path}")
    print(f"{'='*60}")

    #
    print("\n:")
    print(f"{'':<15} {'Seed':<6} {'':<12} {'Coverage (%)':<15} {'RMSE (m)':<12} {'ATE (m)':<12} {'Status':<12}")
    print("-" * 90)

    for row in sorted(all_rows, key=lambda r: (r.dimension, r.seed, r.test_point)):
        rmse_str = f"{row.rmse:.4f}" if row.rmse is not None else "N/A"
        ate_str = f"{row.ate:.4f}" if row.ate is not None else "N/A"
        print(f"{row.dimension:<15} {row.seed:<6} {row.test_point:<12.2f} {row.coverage_pct:>13.2f}%  {rmse_str:<12} {ate_str:<12} {row.status:<12}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dimension", choices=DIMENSIONS + ["all"], default="all",
                    help="")
    ap.add_argument("--seq", type=str, default="seq1",
                    help=" seq1, seq2 ")
    args = ap.parse_args()

    sequence = args.seq
    config_dir, result_base, workspace, launch_file = resolve_runtime_paths()

    # GT
    if os.path.exists(f"/dataset/CERBERUS/gt_tum/{sequence}.txt"):
        gt_root = "/dataset/CERBERUS/gt_tum"
        gt_file_suffix = ".txt"
    elif os.path.exists(f"/dataset/CERBERUS/{sequence}/gt_tum.txt"):
        gt_root = "/dataset/CERBERUS"
        gt_file_suffix = "/gt_tum.txt"
    else:
        gt_root = "/ws/results/CERBERUS"
        gt_file_suffix = "/gt_tum.txt"

    print("=" * 60)
    print(f"SchurVINS CERBERUS  - {sequence}")
    print("=" * 60)
    print(f": {config_dir}")
    print(f": {result_base}")
    print(f":     {sequence}")
    print(f"Launch:   {launch_file}")
    print("=" * 60)

    if not os.path.exists(config_dir):
        print(f"ERROR: : {config_dir}")
        print(": python3 generate_sensitivity_configs.py")
        return

    if not os.path.exists(launch_file):
        print(f"ERROR: Launch: {launch_file}")
        return

    baseline_src = find_original_baseline_result(sequence)
    if baseline_src:
        print(f"Baseline: {baseline_src}")
    else:
        print(" Baseline0.0")

    #
    to_run = DIMENSIONS if args.dimension == "all" else [args.dimension]

    all_rows: List[EvalRow] = []

    for dimension in to_run:
        rows = run_experiments_for_dimension(
            dimension, sequence, config_dir, result_base, workspace,
            launch_file, gt_root, gt_file_suffix, baseline_src
        )
        all_rows.extend(rows)

    #
    if all_rows:
        generate_summary(sequence, result_base, all_rows)

    print("\n")


if __name__ == "__main__":
    main()
