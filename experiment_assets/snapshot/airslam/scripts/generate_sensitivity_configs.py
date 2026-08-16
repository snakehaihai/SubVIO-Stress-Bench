#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
CERBERUS





 IMU       acc_noise      (log)        10^[-2,2]    11 log
           gyro_noise     (log)        10^[-2,2]    11 log
           acc_bias       (log)        10^[-2,2]    11 log
           gyro_bias      (log)        10^[-2,2]    11 log

 Tbc       rotation       +   [-2, +2]    11
           translation    +   [-5, +5]cm   11

 Camera    focal         fx,fy(log)    10^[0.05]   11 log
           principal      +   [-50,+50]px  11
           distortion    k1-k4(log)    10^[0.3]    11 log

"""

from __future__ import annotations

import os
import json
import copy  #
from pathlib import Path
import yaml
import numpy as np
from scipy.spatial.transform import Rotation as R


# ============== ==============

def generate_test_points():
    """"""

    # IMU: log 10^[-2, 2]
    imu_log_values = np.linspace(-2, 2, 11)
    imu_scales = (10 ** imu_log_values).tolist()
    # [0.01, 0.025, 0.063, 0.158, 0.398, 1.0, 2.51, 6.31, 15.85, 39.81, 100.0]

    # Tbc rotation:  [-2, +2]
    rotation_values = np.linspace(-2.0, 2.0, 11).tolist()
    # [-2.0, -1.6, -1.2, -0.8, -0.4, 0.0, 0.4, 0.8, 1.2, 1.6, 2.0]

    # Tbc translation:  [-5, +5] cm
    translation_values = np.linspace(-5.0, 5.0, 11).tolist()
    # [-5.0, -4.0, -3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0]

    # Focal: log 10^[-0.05, 0.05]
    focal_log_values = np.linspace(-0.05, 0.05, 11)
    focal_scales = (10 ** focal_log_values).tolist()
    # [0.891, 0.912, 0.933, 0.955, 0.977, 1.0, 1.023, 1.047, 1.072, 1.096, 1.122]

    # Principal:  [-50, +50] px
    principal_values = np.linspace(-50.0, 50.0, 11).tolist()
    # [-50, -40, -30, -20, -10, 0, 10, 20, 30, 40, 50]

    # Distortion: log 10^[-0.3, 0.3]
    distortion_log_values = np.linspace(-0.3, 0.3, 11)
    distortion_scales = (10 ** distortion_log_values).tolist()
    # [0.501, 0.575, 0.661, 0.759, 0.871, 1.0, 1.148, 1.318, 1.514, 1.738, 1.995]

    return {
        "acc_noise": imu_scales,
        "gyro_noise": imu_scales,
        "acc_bias": imu_scales,
        "gyro_bias": imu_scales,
        "rotation": rotation_values,
        "translation": translation_values,
        "focal": focal_scales,
        "principal": principal_values,
        "distortion": distortion_scales,
    }

TEST_POINTS = generate_test_points()

# seeds
SEEDS = [0, 1, 2]


def load_yaml_config(file_path: str) -> dict:
    """Load YAML, ignoring optional '%YAML:1.0' header line."""
    with open(file_path, "r") as f:
        content = f.read()
    if content.startswith("%YAML"):
        lines = content.splitlines()
        content = "\n".join([ln for ln in lines if not ln.startswith("%YAML")])
    data = yaml.safe_load(content)
    if data is None:
        raise RuntimeError(f"Empty yaml: {file_path}")
    return data


def dump_yaml_with_header(data: dict, out_path: str) -> None:
    with open(out_path, "w") as f:
        f.write("%YAML:1.0\n\n")
        yaml.dump(data, f, default_flow_style=None, sort_keys=False, allow_unicode=True)


def resolve_paths() -> tuple[str, str, str]:
    """Return (base_config_path, output_dir, random_directions_path)."""
    if os.path.exists("/airslam/configs/camera/cerberus.yaml"):
        base_config = "/airslam/configs/camera/cerberus.yaml"
        output_dir = "/airslam/configs/camera/sensitivity"
    elif os.path.exists("/ws/src/airslam/configs/camera/cerberus.yaml"):
        base_config = "/ws/src/airslam/configs/camera/cerberus.yaml"
        output_dir = "/ws/src/airslam/configs/camera/sensitivity"
    elif os.path.exists("configs/camera/cerberus.yaml"):
        base_config = "configs/camera/cerberus.yaml"
        output_dir = "configs/camera/sensitivity"
    else:
        base_config = "/home/zyy/Algs/AirSLAM/src/airslam/configs/camera/cerberus.yaml"
        output_dir = "/home/zyy/Algs/AirSLAM/src/airslam/configs/camera/sensitivity"

    if os.path.exists("/home/zyy/Algs/summaries/sensitivity_experiment/random_directions.json"):
        random_directions_path = "/home/zyy/Algs/summaries/sensitivity_experiment/random_directions.json"
    elif os.path.exists("summaries/sensitivity_experiment/random_directions.json"):
        random_directions_path = "summaries/sensitivity_experiment/random_directions.json"
    else:
        random_directions_path = "/home/zyy/Algs/summaries/sensitivity_experiment/random_directions.json"

    return base_config, output_dir, random_directions_path


def load_random_directions(json_path: str) -> dict:
    """"""
    with open(json_path, "r") as f:
        data = json.load(f)
    return data


def format_value_for_filename(value: float, dim_type: str) -> str:
    """"""
    if dim_type in ["acc_noise", "gyro_noise", "acc_bias", "gyro_bias", "focal", "distortion"]:
        #
        return f"{value:.4f}x"
    elif dim_type == "rotation":
        #
        return f"{value:+.2f}deg"
    elif dim_type == "translation":
        #
        return f"{value:+.2f}cm"
    elif dim_type == "principal":
        #
        return f"{value:+.1f}px"
    else:
        return f"{value:.4f}"


# ============== IMU ==============

def generate_acc_noise_configs(base: dict, output_dir: str) -> int:
    """"""
    orig_val = base.get("accelerometer_noise_density", 2.0e-03)
    count = 0

    for seed in SEEDS:
        for scale in TEST_POINTS["acc_noise"]:
            data = copy.deepcopy(base)  #
            data["accelerometer_noise_density"] = orig_val * scale

            val_str = format_value_for_filename(scale, "acc_noise")
            filename = f"acc_noise_{val_str}_seed{seed}.yaml"
            out_path = os.path.join(output_dir, "acc_noise", filename)
            Path(out_path).parent.mkdir(parents=True, exist_ok=True)
            dump_yaml_with_header(data, out_path)
            count += 1

    return count


def generate_gyro_noise_configs(base: dict, output_dir: str) -> int:
    """"""
    orig_val = base.get("gyroscope_noise_density", 1.7e-04)
    count = 0

    for seed in SEEDS:
        for scale in TEST_POINTS["gyro_noise"]:
            data = copy.deepcopy(base)  #
            data["gyroscope_noise_density"] = orig_val * scale

            val_str = format_value_for_filename(scale, "gyro_noise")
            filename = f"gyro_noise_{val_str}_seed{seed}.yaml"
            out_path = os.path.join(output_dir, "gyro_noise", filename)
            Path(out_path).parent.mkdir(parents=True, exist_ok=True)
            dump_yaml_with_header(data, out_path)
            count += 1

    return count


def generate_acc_bias_configs(base: dict, output_dir: str) -> int:
    """"""
    orig_val = base.get("accelerometer_random_walk", 3.0e-03)
    count = 0

    for seed in SEEDS:
        for scale in TEST_POINTS["acc_bias"]:
            data = copy.deepcopy(base)  #
            data["accelerometer_random_walk"] = orig_val * scale

            val_str = format_value_for_filename(scale, "acc_bias")
            filename = f"acc_bias_{val_str}_seed{seed}.yaml"
            out_path = os.path.join(output_dir, "acc_bias", filename)
            Path(out_path).parent.mkdir(parents=True, exist_ok=True)
            dump_yaml_with_header(data, out_path)
            count += 1

    return count


def generate_gyro_bias_configs(base: dict, output_dir: str) -> int:
    """"""
    orig_val = base.get("gyroscope_random_walk", 1.9393e-05)
    count = 0

    for seed in SEEDS:
        for scale in TEST_POINTS["gyro_bias"]:
            data = copy.deepcopy(base)  #
            data["gyroscope_random_walk"] = orig_val * scale

            val_str = format_value_for_filename(scale, "gyro_bias")
            filename = f"gyro_bias_{val_str}_seed{seed}.yaml"
            out_path = os.path.join(output_dir, "gyro_bias", filename)
            Path(out_path).parent.mkdir(parents=True, exist_ok=True)
            dump_yaml_with_header(data, out_path)
            count += 1

    return count


# ============== Tbc +  ==============

def generate_rotation_configs(base: dict, output_dir: str, random_dirs: dict) -> int:
    """Tbc


    -
    -
    - 0baseline
    """
    T_cam0_base = np.array(base['cam0']['T'])
    count = 0

    for seed in SEEDS:
        seed_str = str(seed)
        if seed_str not in random_dirs:
            print(f"   Warning: seed {seed} not found in random_directions.json")
            continue

        rotation_axis = np.array(random_dirs[seed_str]["rotation_axis"])
        rotation_axis = rotation_axis / np.linalg.norm(rotation_axis)

        for deg in TEST_POINTS["rotation"]:
            data = copy.deepcopy(base)  #

            if abs(deg) < 1e-9:  # baseline
                T_new = T_cam0_base.copy()
            else:
                #  deg
                delta_R = R.from_rotvec(rotation_axis * np.deg2rad(deg)).as_matrix()
                R_orig = T_cam0_base[:3, :3]
                t_orig = T_cam0_base[:3, 3]
                R_new = delta_R @ R_orig

                #
                U, _, Vt = np.linalg.svd(R_new)
                R_new = U @ Vt

                T_new = np.eye(4)
                T_new[:3, :3] = R_new
                T_new[:3, 3] = t_orig

            data['cam0']['T'] = T_new.tolist()

            val_str = format_value_for_filename(deg, "rotation")
            filename = f"rotation_{val_str}_seed{seed}.yaml"
            out_path = os.path.join(output_dir, "rotation", filename)
            Path(out_path).parent.mkdir(parents=True, exist_ok=True)
            dump_yaml_with_header(data, out_path)
            count += 1

    return count


def generate_translation_configs(base: dict, output_dir: str, random_dirs: dict) -> int:
    """Tbc


    -
    -
    - 0baseline
    """
    T_cam0_base = np.array(base['cam0']['T'])
    count = 0

    for seed in SEEDS:
        seed_str = str(seed)
        if seed_str not in random_dirs:
            print(f"   Warning: seed {seed} not found in random_directions.json")
            continue

        translation_dir = np.array(random_dirs[seed_str]["translation_dir"])
        translation_dir = translation_dir / np.linalg.norm(translation_dir)

        for cm in TEST_POINTS["translation"]:
            data = copy.deepcopy(base)  #

            if abs(cm) < 1e-9:  # baseline
                T_new = T_cam0_base.copy()
            else:
                #  cm
                delta_m = cm / 100.0
                delta_t = translation_dir * delta_m

                T_new = T_cam0_base.copy()
                T_new[:3, 3] = T_cam0_base[:3, 3] + delta_t

            data['cam0']['T'] = T_new.tolist()

            val_str = format_value_for_filename(cm, "translation")
            filename = f"translation_{val_str}_seed{seed}.yaml"
            out_path = os.path.join(output_dir, "translation", filename)
            Path(out_path).parent.mkdir(parents=True, exist_ok=True)
            dump_yaml_with_header(data, out_path)
            count += 1

    return count


# ============== Camera ==============

def generate_focal_configs(base: dict, output_dir: str) -> int:
    """

    fxfyscale
    """
    #
    fx0_base = base['cam0']['intrinsics'][0]
    fy0_base = base['cam0']['intrinsics'][1]
    fx1_base = base['cam1']['intrinsics'][0]
    fy1_base = base['cam1']['intrinsics'][1]

    count = 0

    for seed in SEEDS:
        for scale in TEST_POINTS["focal"]:
            data = copy.deepcopy(base)  #

            # fxfy
            data['cam0']['intrinsics'][0] = fx0_base * scale
            data['cam0']['intrinsics'][1] = fy0_base * scale
            data['cam1']['intrinsics'][0] = fx1_base * scale
            data['cam1']['intrinsics'][1] = fy1_base * scale

            val_str = format_value_for_filename(scale, "focal")
            filename = f"focal_{val_str}_seed{seed}.yaml"
            out_path = os.path.join(output_dir, "focal", filename)
            Path(out_path).parent.mkdir(parents=True, exist_ok=True)
            dump_yaml_with_header(data, out_path)
            count += 1

    return count


def generate_principal_configs(base: dict, output_dir: str, random_dirs: dict) -> int:
    """

    2D
    """
    #
    cx0_base = base['cam0']['intrinsics'][2]
    cy0_base = base['cam0']['intrinsics'][3]
    cx1_base = base['cam1']['intrinsics'][2]
    cy1_base = base['cam1']['intrinsics'][3]

    count = 0

    for seed in SEEDS:
        seed_str = str(seed)
        if seed_str not in random_dirs:
            print(f"   Warning: seed {seed} not found in random_directions.json")
            continue

        principal_dir = np.array(random_dirs[seed_str]["principal_dir"])
        principal_dir = principal_dir / np.linalg.norm(principal_dir)

        for px_offset in TEST_POINTS["principal"]:
            data = copy.deepcopy(base)  #

            if abs(px_offset) < 1e-9:  # baseline
                pass  #
            else:
                #
                delta_cx = principal_dir[0] * px_offset
                delta_cy = principal_dir[1] * px_offset

                data['cam0']['intrinsics'][2] = float(cx0_base + delta_cx)
                data['cam0']['intrinsics'][3] = float(cy0_base + delta_cy)
                data['cam1']['intrinsics'][2] = float(cx1_base + delta_cx)
                data['cam1']['intrinsics'][3] = float(cy1_base + delta_cy)

            val_str = format_value_for_filename(px_offset, "principal")
            filename = f"principal_{val_str}_seed{seed}.yaml"
            out_path = os.path.join(output_dir, "principal", filename)
            Path(out_path).parent.mkdir(parents=True, exist_ok=True)
            dump_yaml_with_header(data, out_path)
            count += 1

    return count


def generate_distortion_configs(base: dict, output_dir: str) -> int:
    """

    k1-k4scale
    """
    #
    k0_base = base['cam0']['distortion_coeffs'].copy()
    k1_base = base['cam1']['distortion_coeffs'].copy()

    count = 0

    for seed in SEEDS:
        for scale in TEST_POINTS["distortion"]:
            data = copy.deepcopy(base)  #

            #
            for i in range(4):
                data['cam0']['distortion_coeffs'][i] = k0_base[i] * scale
                data['cam1']['distortion_coeffs'][i] = k1_base[i] * scale

            val_str = format_value_for_filename(scale, "distortion")
            filename = f"distortion_{val_str}_seed{seed}.yaml"
            out_path = os.path.join(output_dir, "distortion", filename)
            Path(out_path).parent.mkdir(parents=True, exist_ok=True)
            dump_yaml_with_header(data, out_path)
            count += 1

    return count


# ==============  ==============

def main() -> None:
    base_config_path, output_dir, random_directions_path = resolve_paths()

    print("=" * 70)
    print("CERBERUS  v2")
    print("=" * 70)
    print(f": {base_config_path}")
    print(f": {output_dir}")
    print(f": {random_directions_path}")
    print("=" * 70)

    #
    print("\n :")
    print("-" * 70)
    for dim, values in TEST_POINTS.items():
        if dim in ["acc_noise", "gyro_noise", "acc_bias", "gyro_bias"]:
            print(f"  {dim}: {[f'{v:.3f}' for v in values]}")
        else:
            print(f"  {dim}: {[f'{v:+.2f}' if v != 0 else '0.00' for v in values]}")
    print("-" * 70)

    #
    base = load_yaml_config(base_config_path)

    #
    if not os.path.exists(random_directions_path):
        print(f" Error: random_directions.json not found at {random_directions_path}")
        print("   generate_random_directions.py")
        return

    random_dirs = load_random_directions(random_directions_path)
    print(f" : {len(random_dirs)} seeds")

    #
    print("\n...")
    print("-" * 70)

    total_count = 0

    generators = [
        ("acc_noise", lambda: generate_acc_noise_configs(base, output_dir)),
        ("gyro_noise", lambda: generate_gyro_noise_configs(base, output_dir)),
        ("acc_bias", lambda: generate_acc_bias_configs(base, output_dir)),
        ("gyro_bias", lambda: generate_gyro_bias_configs(base, output_dir)),
        ("rotation", lambda: generate_rotation_configs(base, output_dir, random_dirs)),
        ("translation", lambda: generate_translation_configs(base, output_dir, random_dirs)),
        ("focal", lambda: generate_focal_configs(base, output_dir)),
        ("principal", lambda: generate_principal_configs(base, output_dir, random_dirs)),
        ("distortion", lambda: generate_distortion_configs(base, output_dir)),
    ]

    for i, (name, gen_func) in enumerate(generators, 1):
        print(f"\n[{i}/9]  {name} ...")
        count = gen_func()
        print(f"    {count} ")
        total_count += count

    print("\n" + "=" * 70)
    print(" ")
    print("=" * 70)
    print(f"\n: {total_count} ")
    print(f"  9  11  3seeds = {9 * 11 * 3} ")
    print(f"\n: {output_dir}")


if __name__ == "__main__":
    main()
