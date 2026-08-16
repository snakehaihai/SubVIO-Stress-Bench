#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ORB-SLAM3 CERBERUS


/ws/results/CERBERUS/sensitivity/seqN/
     acc_noise/
        seed0/
           acc_noise_0.0100x_seed0/  (trajectory_v0.txt, evo)
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

from __future__ import print_function, division, absolute_import

import argparse
import csv
import os
import re
import shutil
import subprocess
import time
try:
    from dataclasses import dataclass
except ImportError:
    # Python 2.7
    def dataclass(cls):
        return cls

import os
import numpy as np
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


def resolve_runtime_paths():
    """
    : config_dir, result_base, workspace, executable_path, vocab_path
    """
    # config dir
    if os.path.exists("sensitivity_experiments/configs/sensitivity"):
        config_dir = "sensitivity_experiments/configs/sensitivity"
    elif os.path.exists("/home/zyy/Algs/orb3/sensitivity_experiments/configs/sensitivity"):
        config_dir = "/home/zyy/Algs/orb3/sensitivity_experiments/configs/sensitivity"
    else:
        config_dir = "/home/zyy/Algs/orb3/sensitivity_experiments/configs/sensitivity"

    # results base
    if os.path.exists("/ws/results/CERBERUS"):
        result_base = "/ws/results/CERBERUS"
        workspace = "/ws"
    else:
        result_base = "/home/zyy/Algs/orb3/Results_orb3/CERBERUS"
        workspace = "/ws"

    #
    if os.path.exists("/ws/Examples/Stereo-Inertial/stereo_inertial_cerberus"):
        executable = "/ws/Examples/Stereo-Inertial/stereo_inertial_cerberus"
    elif os.path.exists("/home/zyy/Algs/orb3/Examples/Stereo-Inertial/stereo_inertial_cerberus"):
        executable = "/home/zyy/Algs/orb3/Examples/Stereo-Inertial/stereo_inertial_cerberus"
    else:
        executable = "/ws/Examples/Stereo-Inertial/stereo_inertial_cerberus"

    #
    if os.path.exists("/ws/Vocabulary/ORBvoc.txt"):
        vocab_path = "/ws/Vocabulary/ORBvoc.txt"
    elif os.path.exists("/home/zyy/Algs/orb3/Vocabulary/ORBvoc.txt"):
        vocab_path = "/home/zyy/Algs/orb3/Vocabulary/ORBvoc.txt"
    else:
        vocab_path = "/ws/Vocabulary/ORBvoc.txt"

    return config_dir, result_base, workspace, executable, vocab_path


def find_original_baseline_result(sequence):
    """baseline"""
    candidates = [
        "/ws/results/CERBERUS/Original/{}/trajectory_v0.txt".format(sequence),
        "/ws/results/CERBERUS/original/{}/trajectory_v0.txt".format(sequence),
        "/ws/results/CERBERUS/baseline/{}/trajectory_v0.txt".format(sequence),
        "/ws/results/CERBERUS/Baseline/{}/trajectory_v0.txt".format(sequence),
        "/ws/results/CERBERUS/stereo+imu/{}/trajectory_v0.txt".format(sequence),
        "/ws/results/CERBERUS/stereo+imu/{}/CameraTrajectory.txt".format(sequence),
        "/home/zyy/Algs/orb3/Results_orb3/CERBERUS/original/{}/trajectory_v0.txt".format(sequence),
    ]
    for p in candidates:
        if os.path.exists(p) and os.path.getsize(p) > 100:
            return p
    return None


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def try_symlink_or_copy(src, dst):
    """"""
    ensure_dir(os.path.dirname(dst))
    if os.path.exists(dst):
        return
    try:
        os.symlink(src, dst)
    except Exception:
        shutil.copy2(src, dst)


def build_run_cmd(executable, vocab_path, config_path, dataset_path, output_dir):
    """ORB-SLAM3"""
    ensure_dir(output_dir)
    times_file = os.path.join(dataset_path, "cam0", "data.csv")

    #
    if not os.path.isabs(config_path):
        config_path = os.path.abspath(config_path)

    #
    if not os.path.isabs(vocab_path):
        vocab_path = os.path.abspath(vocab_path)

    # LD_LIBRARY_PATHlibORB_SLAM3.so
    #
    possible_lib_paths = [
        "/ws/lib",
        "/ws/Thirdparty/DBoW2/lib",
        "/ws/Thirdparty/g2o/lib",
    ]
    exec_dir = os.path.dirname(executable)
    if exec_dir:
        possible_lib_paths.append(exec_dir)
        possible_lib_paths.append(os.path.join(exec_dir, "..", "lib"))

    #
    lib_paths = ":".join([p for p in possible_lib_paths if p and os.path.exists(p)])
    if not lib_paths:
        lib_paths = "/ws/lib"

    # vocabulary config_file sequence_folder times_file
    return (
        "cd {} && "
        "export LD_LIBRARY_PATH={}:$LD_LIBRARY_PATH && "
        "{} {} {} {} {} 2>&1; exit 0"
    ).format(output_dir, lib_paths, executable, vocab_path, config_path, dataset_path, times_file)


def run_one(cmd, timeout_sec=600):
    """"""
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
        return False


def load_tum_trajectory(file_path):
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


def find_trajectory_file(result_dir):
    """"""
    possible_names = [
        "trajectory_v0.txt",
        "CameraTrajectory.txt",
        "trajectory.txt",
        "KeyFrameTrajectory.txt"
    ]

    for name in possible_names:
        traj_path = os.path.join(result_dir, name)
        if os.path.exists(traj_path) and os.path.getsize(traj_path) > 100:
            return traj_path

    return None


def umeyama_alignment(src_points, dst_points):
    """UmeyamaSE3"""
    assert src_points.shape == dst_points.shape and src_points.shape[1] == 3
    assert src_points.shape[0] > 0

    n = src_points.shape[0]
    src_centroid = np.mean(src_points, axis=0)
    dst_centroid = np.mean(dst_points, axis=0)

    src_centered = src_points - src_centroid
    dst_centered = dst_points - dst_centroid

    H = np.dot(src_centered.T, dst_centered)
    U, S, Vt = np.linalg.svd(H)

    R = np.dot(Vt.T, U.T)

    if np.linalg.det(R) < 0:
        Vt[-1, :] *= -1
        R = np.dot(Vt.T, U.T)

    t = dst_centroid - np.dot(R, src_centroid)

    return R, t


def apply_se3_transform(points, R, t):
    """SE3"""
    return np.dot(R, points.T).T + t


def compute_coverage_metrics(gt_path, est_path, time_tolerance=0.05):
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
    gt_times = gt[:, 0].copy()
    est_times = est[:, 0].copy()

    # > 1e15GT< 1e10
    if np.max(est_times) > 1e15 and np.max(gt_times) < 1e10:
        est_times = est_times / 1e9
    # GTGT
    elif np.max(gt_times) > 1e15 and np.max(est_times) < 1e10:
        gt_times = gt_times / 1e9

    #
    matched_pairs = []
    for i, est_t in enumerate(est_times):
        gt_idx = np.argmin(np.abs(gt_times - est_t))
        if np.abs(gt_times[gt_idx] - est_t) < time_tolerance:
            matched_pairs.append((gt_idx, i))

    if len(matched_pairs) == 0:
        return {
            "coverage_pct": 0.0,
            "rmse": None,
            "ate": None,
            "status": "CRASHED",
        }

    # Coverage
    matched_times = [gt_times[gt_idx] for gt_idx, _ in matched_pairs]
    matched_duration = max(matched_times) - min(matched_times) if matched_times else 0.0
    gt_duration = gt_times[-1] - gt_times[0]
    coverage_pct = (matched_duration / gt_duration) * 100.0 if gt_duration > 0 else 0.0

    # Status
    time_diff = abs(est_times[-1] - gt_times[-1])
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


def evo_ape_rmse(gt_path, est_path):
    """evo_apeRMSE"""
    cmd = "evo_ape tum {} {} -as --no_warnings".format(gt_path, est_path)
    # Python 3.6  stdout/stderr  capture_output
    try:
        r = subprocess.run(
            cmd, shell=True, executable="/bin/bash",
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            universal_newlines=True
        )
    except TypeError:
        # Python 2.7
        r = subprocess.Popen(
            cmd, shell=True, executable="/bin/bash",
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = r.communicate()
        r.returncode = r.returncode if hasattr(r, 'returncode') else 0
        r.stdout = stdout.decode('utf-8') if isinstance(stdout, bytes) else stdout
        r.stderr = stderr.decode('utf-8') if isinstance(stderr, bytes) else stderr

    if r.returncode != 0:
        return None
    m = re.search(r"\brmse\s+([0-9]*\.?[0-9]+)", r.stdout, flags=re.IGNORECASE)
    if not m:
        return None
    try:
        return float(m.group(1))
    except Exception:
        return None


def parse_test_point_from_filename(filename, dimension):
    """"""
    patterns = {
        "acc_noise": r"_([0-9]+\.?[0-9]*)x_",
        "gyro_noise": r"_([0-9]+\.?[0-9]*)x_",
        "acc_bias": r"_([0-9]+\.?[0-9]*)x_",
        "gyro_bias": r"_([0-9]+\.?[0-9]*)x_",
        "rotation": r"_([\+\-]?[0-9]+\.?[0-9]*)deg_",
        "translation": r"_([\+\-]?[0-9]+\.?[0-9]*)cm_",
        "focal": r"_([0-9]+\.?[0-9]*)x_",
        "principal": r"_([\+\-]?[0-9]+\.?[0-9]*)px_",
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


class EvalRow(object):
    def __init__(self, dimension, seed, test_point, coverage_pct, status, rmse, ate, duration):
        self.dimension = dimension
        self.seed = seed
        self.test_point = test_point
        self.coverage_pct = coverage_pct
        self.status = status
        self.rmse = rmse
        self.ate = ate
        self.duration = duration


def run_experiments_for_dimension(
    dimension,
    sequence,
    config_dir,
    result_base,
    executable,
    vocab_path,
    gt_root,
    gt_file_suffix,
    baseline_src,
    eval_only=False,
):
    """"""
    print("\n{}".format("="*60))
    print(": {}".format(dimension))
    print("{}".format("="*60))

    dimension_config_dir = os.path.join(config_dir, dimension)
    if not os.path.exists(dimension_config_dir):
        print("   : {}".format(dimension_config_dir))
        return []

    #
    config_files = sorted(glob.glob(os.path.join(dimension_config_dir, "*.yaml")))
    if not config_files:
        print("   ")
        return []

    print("   {} ".format(len(config_files)))

    rows = []
    result_dim_dir = os.path.join(result_base, "sensitivity", sequence, dimension)

    # seed
    for seed in SEEDS:
        print("\n  [Seed {}]".format(seed))
        seed_result_dir = os.path.join(result_dim_dir, "seed{}".format(seed))
        ensure_dir(seed_result_dir)

        # seed
        seed_configs = [f for f in config_files if "_seed{}.yaml".format(seed) in f]

        for config_path in seed_configs:
            config_filename = os.path.basename(config_path)
            test_point = parse_test_point_from_filename(config_filename, dimension)
            if test_point is None:
                print("     : {}".format(config_filename))
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
                is_baseline = abs(test_point - 0.0) < 0.01 or abs(test_point - 1.0) < 0.01  # IMU1.0baseline

            if is_baseline and baseline_src:
                if not traj_path:
                    # baseline
                    baseline_traj = baseline_src
                    if os.path.exists(baseline_traj):
                        # result_dir
                        traj_dst = os.path.join(result_dir, os.path.basename(baseline_traj))
                        try_symlink_or_copy(baseline_traj, traj_dst)
                        print("     Baseline: {}".format(result_name))
                    else:
                        print("     Baseline: {}".format(baseline_traj))
                else:
                    print("     Skip (exists): {}".format(result_name))
            elif traj_path:
                print("     Skip (exists): {}".format(result_name))
            else:
                #
                if eval_only:
                    print("     Skip (eval-only mode, no trajectory): {}".format(result_name))
                else:
                    #
                    dataset_path = "/dataset/CERBERUS/{}".format(sequence)
                    #
                    abs_config_path = os.path.abspath(config_path) if not os.path.isabs(config_path) else config_path
                    cmd = build_run_cmd(executable, vocab_path, abs_config_path, dataset_path, result_dir)
                    print("     Run: {} (config: {})".format(result_name, abs_config_path))
                    ok = run_one(cmd, timeout_sec=600)
                    if not ok:
                        print("     Failed: {}".format(result_name))

        # seed
        print("\n     Seed {} ...".format(seed))
        for config_path in seed_configs:
            config_filename = os.path.basename(config_path)
            test_point = parse_test_point_from_filename(config_filename, dimension)
            if test_point is None:
                continue

            result_name = config_filename.replace(".yaml", "")
            result_dir = os.path.join(seed_result_dir, result_name)
            traj_path = find_trajectory_file(result_dir)

            if not traj_path:
                continue

            #
            if gt_file_suffix == ".txt":
                gt_path = os.path.join(gt_root, "{}.txt".format(sequence))
            else:
                gt_path = os.path.join(gt_root, sequence, "gt_tum.txt")

            if not os.path.exists(gt_path):
                continue

            metrics = compute_coverage_metrics(gt_path, traj_path)

            #
            est_traj = load_tum_trajectory(traj_path)
            if est_traj.size > 0:
                est_times = est_traj[:, 0]
                #  > 1e15
                if np.max(est_times) > 1e15:
                    #
                    duration = (est_times[-1] - est_times[0]) / 1e9
                else:
                    duration = est_times[-1] - est_times[0]
            else:
                duration = 0.0

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


def generate_summary(sequence, result_base, all_rows):
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

    print("\n{}".format("="*60))
    print(" CSV: {}".format(csv_path))
    print("{}".format("="*60))

    #
    print("\n:")
    print("{:<15} {:<6} {:<12} {:<15} {:<12} {:<12} {:<12}".format(
        "", "Seed", "", "Coverage (%)", "RMSE (m)", "ATE (m)", "Status"))
    print("-" * 90)

    for row in sorted(all_rows, key=lambda r: (r.dimension, r.seed, r.test_point)):
        rmse_str = "{:.4f}".format(row.rmse) if row.rmse is not None else "N/A"
        ate_str = "{:.4f}".format(row.ate) if row.ate is not None else "N/A"
        print("{:<15} {:<6} {:<12.2f} {:>13.2f}%  {:<12} {:<12} {:<12}".format(
            row.dimension, row.seed, row.test_point, row.coverage_pct, rmse_str, ate_str, row.status))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dimension", choices=DIMENSIONS + ["all"], default="all",
                    help="")
    ap.add_argument("--seq", type=str, default="seq1",
                    help=" seq1, seq2 ")
    ap.add_argument("--eval-only", action="store_true",
                    help="")
    args = ap.parse_args()

    sequence = args.seq
    config_dir, result_base, workspace, executable, vocab_path = resolve_runtime_paths()

    # GT
    if os.path.exists("/dataset/CERBERUS/gt_tum/{}.txt".format(sequence)):
        gt_root = "/dataset/CERBERUS/gt_tum"
        gt_file_suffix = ".txt"
    elif os.path.exists("/dataset/CERBERUS/{}/gt_tum.txt".format(sequence)):
        gt_root = "/dataset/CERBERUS"
        gt_file_suffix = "/gt_tum.txt"
    else:
        gt_root = "/ws/results/CERBERUS"
        gt_file_suffix = "/gt_tum.txt"

    print("=" * 60)
    print("ORB-SLAM3 CERBERUS  - {}".format(sequence))
    print("=" * 60)
    print(": {}".format(config_dir))
    print(": {}".format(result_base))
    print(":     {}".format(sequence))
    print(": {}".format(executable))
    print(":   {}".format(vocab_path))
    print("=" * 60)

    if not os.path.exists(config_dir):
        print("ERROR: : {}".format(config_dir))
        print(": python3 generate_sensitivity_configs.py")
        return

    if not os.path.exists(executable):
        print("ERROR: : {}".format(executable))
        print("ORB-SLAM3")
        return

    if not os.path.exists(vocab_path):
        print("ERROR: : {}".format(vocab_path))
        return

    baseline_src = find_original_baseline_result(sequence)
    if baseline_src:
        print("Baseline: {}".format(baseline_src))
    else:
        print(" Baselinebaseline")

    #
    to_run = DIMENSIONS if args.dimension == "all" else [args.dimension]

    all_rows = []

    for dimension in to_run:
        rows = run_experiments_for_dimension(
            dimension, sequence, config_dir, result_base, executable,
            vocab_path, gt_root, gt_file_suffix, baseline_src,
            eval_only=args.eval_only
        )
        all_rows.extend(rows)

    #
    if all_rows:
        generate_summary(sequence, result_base, all_rows)

    print("\n")


if __name__ == "__main__":
    main()
