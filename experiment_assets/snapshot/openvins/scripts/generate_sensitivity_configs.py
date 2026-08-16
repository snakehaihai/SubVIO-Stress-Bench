#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
OpenVINS CERBERUS


sensitivity/
     acc_noise/         # 11  3seeds = 33
     gyro_noise/
     acc_bias/
     gyro_bias/
     rotation/
     translation/
     focal/
     principal/
     distortion/


- estimator_config.yaml (relative_config)
- kalibr_imu_chain.yaml (IMU)
- kalibr_imucam_chain.yaml ()
"""

from __future__ import annotations

import os
import json
import copy
from pathlib import Path
import numpy as np
import yaml
# numpyscipy
def rotvec_to_matrix(rotvec):
    """
    Rodrigues
    rotvec:  (3,)
    :  (3, 3)
    """
    angle = np.linalg.norm(rotvec)
    if angle < 1e-8:
        return np.eye(3)

    axis = rotvec / angle
    cos_a = np.cos(angle)
    sin_a = np.sin(angle)

    # Rodrigues
    K = np.array([
        [0, -axis[2], axis[1]],
        [axis[2], 0, -axis[0]],
        [-axis[1], axis[0], 0]
    ])

    R = np.eye(3) + sin_a * K + (1 - cos_a) * (K @ K)
    return R


# ==============  ==============
def generate_test_points():
    """"""

    # IMU: log 10^[-2, 2]
    imu_log_values = np.linspace(-2, 2, 11)
    imu_scales = (10 ** imu_log_values).tolist()

    # Tbc rotation:  [-2, +2]
    rotation_values = np.linspace(-2.0, 2.0, 11).tolist()

    # Tbc translation:  [-5, +5] cm
    translation_values = np.linspace(-5.0, 5.0, 11).tolist()

    # Focal: log 10^[-0.05, 0.05]
    focal_log_values = np.linspace(-0.05, 0.05, 11)
    focal_scales = (10 ** focal_log_values).tolist()

    # Principal:  [-50, +50] px
    principal_values = np.linspace(-50.0, 50.0, 11).tolist()

    # Distortion: log 10^[-0.3, 0.3]
    distortion_log_values = np.linspace(-0.3, 0.3, 11)
    distortion_scales = (10 ** distortion_log_values).tolist()

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


def resolve_paths() -> tuple[str, str, str]:
    """
    Return (output_dir, random_directions_path, base_config_dir).

    """
    #
    if os.path.exists("/ws/src/open_vins/config/CERBERUS"):
        output_dir = "/ws/src/open_vins/config/CERBERUS/sensitivity"
        base_config_dir = "/ws/src/open_vins/config/CERBERUS"
    #
    elif os.path.exists("/home/zyy/Algs/OpenVINS/src/open_vins/config/CERBERUS"):
        output_dir = "/home/zyy/Algs/OpenVINS/src/open_vins/config/CERBERUS/sensitivity"
        base_config_dir = "/home/zyy/Algs/OpenVINS/src/open_vins/config/CERBERUS"
    else:
        #
        output_dir = "/home/zyy/Algs/OpenVINS/src/open_vins/config/CERBERUS/sensitivity"
        base_config_dir = "/home/zyy/Algs/OpenVINS/src/open_vins/config/CERBERUS"

    # random_directions.json
    if os.path.exists("/home/zyy/Algs/summaries/sensitivity_experiment/random_directions.json"):
        random_directions_path = "/home/zyy/Algs/summaries/sensitivity_experiment/random_directions.json"
    elif os.path.exists("/ws/src/open_vins/config/CERBERUS/random_directions.json"):
        random_directions_path = "/ws/src/open_vins/config/CERBERUS/random_directions.json"
    elif os.path.exists("/ws/scripts/random_directions.json"):
        random_directions_path = "/ws/scripts/random_directions.json"
    else:
        random_directions_path = "/home/zyy/Algs/summaries/sensitivity_experiment/random_directions.json"

    return output_dir, random_directions_path, base_config_dir


def load_yaml_config(file_path: str) -> dict:
    """Load YAML config, ignoring optional '%YAML:1.0' header line."""
    with open(file_path, "r") as f:
        content = f.read()
    if content.startswith("%YAML"):
        lines = content.splitlines()
        content = "\n".join([ln for ln in lines if not ln.startswith("%YAML")])
    data = yaml.safe_load(content)
    if data is None:
        raise RuntimeError(f"Empty yaml: {file_path}")
    return data


def convert_to_python_types(obj):
    """numpyPython"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: convert_to_python_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_python_types(item) for item in obj]
    else:
        return obj


def dump_yaml_config(data: dict, out_path: str) -> None:
    """Dump YAML config with header and correct indentation for OpenCV"""
    # numpyPython
    data_clean = convert_to_python_types(data)

    with open(out_path, "w") as f:
        f.write("%YAML:1.0\n\n")
        # yaml.dump
        yaml_str = yaml.dump(data_clean, default_flow_style=None, sort_keys=False, allow_unicode=True, indent=2, width=1000)

        # T_i_b:  T_imu_cam: 4
        lines = yaml_str.split('\n')
        fixed_lines = []
        in_list_context = False
        list_indent_level = 0

        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped:  #
                fixed_lines.append(line)
                continue

            #
            # 4OpenCV YAML
            list_keys = ['T_i_b:', 'T_imu_cam:', 'T_cam_imu:', 'Tw:', 'R_IMUtoGYRO:', 'Ta:', 'R_IMUtoACC:', 'Tg:']
            is_list_key = any(key in line for key in list_keys)

            if is_list_key:
                in_list_context = True
                list_indent_level = len(line) - len(line.lstrip())
                fixed_lines.append(line)
            elif in_list_context and stripped.startswith('- ['):
                # 4list_indent_level + 2
                # PyYAMLlist_indent_levellist_indent_level + 2
                fixed_lines.append(' ' * (list_indent_level + 2) + stripped)
            elif in_list_context and stripped and not stripped.startswith('-'):
                #
                in_list_context = False
                fixed_lines.append(line)
            else:
                fixed_lines.append(line)

        f.write('\n'.join(fixed_lines))


def load_random_directions(json_path: str) -> dict:
    """"""
    with open(json_path, "r") as f:
        return json.load(f)


def format_value_for_filename(value: float, dim_type: str) -> str:
    """"""
    if dim_type in ["acc_noise", "gyro_noise", "acc_bias", "gyro_bias", "focal", "distortion"]:
        return f"{value:.4f}x"
    elif dim_type == "rotation":
        return f"{value:+.2f}deg"
    elif dim_type == "translation":
        return f"{value:+.2f}cm"
    elif dim_type == "principal":
        return f"{value:+.1f}px"
    else:
        return f"{value:.4f}"


# ============== IMU ==============

def generate_acc_noise_configs(output_dir: str, base_config_dir: str, base_imu: dict, base_imucam: dict, base_estimator: dict) -> int:
    """"""
    orig_val = base_imu['imu0']['accelerometer_noise_density']
    count = 0

    for seed in SEEDS:
        for scale in TEST_POINTS["acc_noise"]:
            config_imu = copy.deepcopy(base_imu)
            config_imucam = copy.deepcopy(base_imucam)
            config_estimator = copy.deepcopy(base_estimator)

            config_imu['imu0']['accelerometer_noise_density'] = orig_val * scale

            val_str = format_value_for_filename(scale, "acc_noise")
            name = f"acc_noise_{val_str}_seed{seed}"

            dim_dir = os.path.join(output_dir, "acc_noise", name)
            Path(dim_dir).mkdir(parents=True, exist_ok=True)

            #
            dump_yaml_config(config_imu, os.path.join(dim_dir, "kalibr_imu_chain.yaml"))
            dump_yaml_config(config_imucam, os.path.join(dim_dir, "kalibr_imucam_chain.yaml"))

            # estimator_configestimator_config.yaml
            config_estimator['relative_config_imu'] = "kalibr_imu_chain.yaml"
            config_estimator['relative_config_imucam'] = "kalibr_imucam_chain.yaml"
            dump_yaml_config(config_estimator, os.path.join(dim_dir, "estimator_config.yaml"))

            count += 1

    return count


def generate_gyro_noise_configs(output_dir: str, base_config_dir: str, base_imu: dict, base_imucam: dict, base_estimator: dict) -> int:
    """"""
    orig_val = base_imu['imu0']['gyroscope_noise_density']
    count = 0

    for seed in SEEDS:
        for scale in TEST_POINTS["gyro_noise"]:
            config_imu = copy.deepcopy(base_imu)
            config_imucam = copy.deepcopy(base_imucam)
            config_estimator = copy.deepcopy(base_estimator)

            config_imu['imu0']['gyroscope_noise_density'] = orig_val * scale

            val_str = format_value_for_filename(scale, "gyro_noise")
            name = f"gyro_noise_{val_str}_seed{seed}"

            dim_dir = os.path.join(output_dir, "gyro_noise", name)
            Path(dim_dir).mkdir(parents=True, exist_ok=True)

            dump_yaml_config(config_imu, os.path.join(dim_dir, "kalibr_imu_chain.yaml"))
            dump_yaml_config(config_imucam, os.path.join(dim_dir, "kalibr_imucam_chain.yaml"))

            config_estimator['relative_config_imu'] = "kalibr_imu_chain.yaml"
            config_estimator['relative_config_imucam'] = "kalibr_imucam_chain.yaml"
            dump_yaml_config(config_estimator, os.path.join(dim_dir, "estimator_config.yaml"))

            count += 1

    return count


def generate_acc_bias_configs(output_dir: str, base_config_dir: str, base_imu: dict, base_imucam: dict, base_estimator: dict) -> int:
    """"""
    orig_val = base_imu['imu0']['accelerometer_random_walk']
    count = 0

    for seed in SEEDS:
        for scale in TEST_POINTS["acc_bias"]:
            config_imu = copy.deepcopy(base_imu)
            config_imucam = copy.deepcopy(base_imucam)
            config_estimator = copy.deepcopy(base_estimator)

            config_imu['imu0']['accelerometer_random_walk'] = orig_val * scale

            val_str = format_value_for_filename(scale, "acc_bias")
            name = f"acc_bias_{val_str}_seed{seed}"

            dim_dir = os.path.join(output_dir, "acc_bias", name)
            Path(dim_dir).mkdir(parents=True, exist_ok=True)

            dump_yaml_config(config_imu, os.path.join(dim_dir, "kalibr_imu_chain.yaml"))
            dump_yaml_config(config_imucam, os.path.join(dim_dir, "kalibr_imucam_chain.yaml"))

            config_estimator['relative_config_imu'] = "kalibr_imu_chain.yaml"
            config_estimator['relative_config_imucam'] = "kalibr_imucam_chain.yaml"
            dump_yaml_config(config_estimator, os.path.join(dim_dir, "estimator_config.yaml"))

            count += 1

    return count


def generate_gyro_bias_configs(output_dir: str, base_config_dir: str, base_imu: dict, base_imucam: dict, base_estimator: dict) -> int:
    """"""
    orig_val = base_imu['imu0']['gyroscope_random_walk']
    count = 0

    for seed in SEEDS:
        for scale in TEST_POINTS["gyro_bias"]:
            config_imu = copy.deepcopy(base_imu)
            config_imucam = copy.deepcopy(base_imucam)
            config_estimator = copy.deepcopy(base_estimator)

            config_imu['imu0']['gyroscope_random_walk'] = orig_val * scale

            val_str = format_value_for_filename(scale, "gyro_bias")
            name = f"gyro_bias_{val_str}_seed{seed}"

            dim_dir = os.path.join(output_dir, "gyro_bias", name)
            Path(dim_dir).mkdir(parents=True, exist_ok=True)

            dump_yaml_config(config_imu, os.path.join(dim_dir, "kalibr_imu_chain.yaml"))
            dump_yaml_config(config_imucam, os.path.join(dim_dir, "kalibr_imucam_chain.yaml"))

            config_estimator['relative_config_imu'] = "kalibr_imu_chain.yaml"
            config_estimator['relative_config_imucam'] = "kalibr_imucam_chain.yaml"
            dump_yaml_config(config_estimator, os.path.join(dim_dir, "estimator_config.yaml"))

            count += 1

    return count


# ============== Tbc ==============

def generate_rotation_configs(output_dir: str, base_config_dir: str, base_imu: dict, base_imucam: dict, base_estimator: dict, random_dirs: dict) -> int:
    """Tbc"""
    count = 0

    # T_imu_cam
    T_cam0_base = np.array(base_imucam['cam0']['T_imu_cam'])
    T_cam1_base = np.array(base_imucam['cam1']['T_imu_cam'])

    for seed in SEEDS:
        seed_str = str(seed)
        if seed_str not in random_dirs:
            print(f"   Warning: seed {seed} not found in random_directions.json")
            continue

        rotation_axis = np.array(random_dirs[seed_str]["rotation_axis"])
        rotation_axis = rotation_axis / np.linalg.norm(rotation_axis)

        for deg in TEST_POINTS["rotation"]:
            config_imu = copy.deepcopy(base_imu)
            config_imucam = copy.deepcopy(base_imucam)
            config_estimator = copy.deepcopy(base_estimator)

            if abs(deg) < 1e-9:  # baseline
                T_cam0_new = T_cam0_base.copy()
                T_cam1_new = T_cam1_base.copy()
            else:
                #  deg
                rotvec = rotation_axis * np.deg2rad(deg)
                delta_R = rotvec_to_matrix(rotvec)

                #
                R_cam0_orig = T_cam0_base[:3, :3]
                t_cam0_orig = T_cam0_base[:3, 3]
                R_cam0_new = delta_R @ R_cam0_orig
                U, _, Vt = np.linalg.svd(R_cam0_new)
                R_cam0_new = U @ Vt

                R_cam1_orig = T_cam1_base[:3, :3]
                t_cam1_orig = T_cam1_base[:3, 3]
                R_cam1_new = delta_R @ R_cam1_orig
                U, _, Vt = np.linalg.svd(R_cam1_new)
                R_cam1_new = U @ Vt

                T_cam0_new = np.eye(4)
                T_cam0_new[:3, :3] = R_cam0_new
                T_cam0_new[:3, 3] = t_cam0_orig

                T_cam1_new = np.eye(4)
                T_cam1_new[:3, :3] = R_cam1_new
                T_cam1_new[:3, 3] = t_cam1_orig

            config_imucam['cam0']['T_imu_cam'] = T_cam0_new.tolist()
            config_imucam['cam1']['T_imu_cam'] = T_cam1_new.tolist()

            val_str = format_value_for_filename(deg, "rotation")
            name = f"rotation_{val_str}_seed{seed}"

            dim_dir = os.path.join(output_dir, "rotation", name)
            Path(dim_dir).mkdir(parents=True, exist_ok=True)

            dump_yaml_config(config_imu, os.path.join(dim_dir, "kalibr_imu_chain.yaml"))
            dump_yaml_config(config_imucam, os.path.join(dim_dir, "kalibr_imucam_chain.yaml"))

            config_estimator['relative_config_imu'] = "kalibr_imu_chain.yaml"
            config_estimator['relative_config_imucam'] = "kalibr_imucam_chain.yaml"
            dump_yaml_config(config_estimator, os.path.join(dim_dir, "estimator_config.yaml"))

            count += 1

    return count


def generate_translation_configs(output_dir: str, base_config_dir: str, base_imu: dict, base_imucam: dict, base_estimator: dict, random_dirs: dict) -> int:
    """Tbc"""
    count = 0

    T_cam0_base = np.array(base_imucam['cam0']['T_imu_cam'])
    T_cam1_base = np.array(base_imucam['cam1']['T_imu_cam'])

    for seed in SEEDS:
        seed_str = str(seed)
        if seed_str not in random_dirs:
            print(f"   Warning: seed {seed} not found in random_directions.json")
            continue

        translation_dir = np.array(random_dirs[seed_str]["translation_dir"])
        translation_dir = translation_dir / np.linalg.norm(translation_dir)

        for cm in TEST_POINTS["translation"]:
            config_imu = copy.deepcopy(base_imu)
            config_imucam = copy.deepcopy(base_imucam)
            config_estimator = copy.deepcopy(base_estimator)

            if abs(cm) < 1e-9:  # baseline
                T_cam0_new = T_cam0_base.copy()
                T_cam1_new = T_cam1_base.copy()
            else:
                #  cm
                delta_m = cm / 100.0
                delta_t = translation_dir * delta_m

                T_cam0_new = T_cam0_base.copy()
                T_cam0_new[:3, 3] = T_cam0_base[:3, 3] + delta_t

                T_cam1_new = T_cam1_base.copy()
                T_cam1_new[:3, 3] = T_cam1_base[:3, 3] + delta_t

            config_imucam['cam0']['T_imu_cam'] = T_cam0_new.tolist()
            config_imucam['cam1']['T_imu_cam'] = T_cam1_new.tolist()

            val_str = format_value_for_filename(cm, "translation")
            name = f"translation_{val_str}_seed{seed}"

            dim_dir = os.path.join(output_dir, "translation", name)
            Path(dim_dir).mkdir(parents=True, exist_ok=True)

            dump_yaml_config(config_imu, os.path.join(dim_dir, "kalibr_imu_chain.yaml"))
            dump_yaml_config(config_imucam, os.path.join(dim_dir, "kalibr_imucam_chain.yaml"))

            config_estimator['relative_config_imu'] = "kalibr_imu_chain.yaml"
            config_estimator['relative_config_imucam'] = "kalibr_imucam_chain.yaml"
            dump_yaml_config(config_estimator, os.path.join(dim_dir, "estimator_config.yaml"))

            count += 1

    return count


# ============== Camera ==============

def generate_focal_configs(output_dir: str, base_config_dir: str, base_imu: dict, base_imucam: dict, base_estimator: dict) -> int:
    """"""
    count = 0

    for seed in SEEDS:
        for scale in TEST_POINTS["focal"]:
            config_imu = copy.deepcopy(base_imu)
            config_imucam = copy.deepcopy(base_imucam)
            config_estimator = copy.deepcopy(base_estimator)

            # fxfy
            config_imucam['cam0']['intrinsics'][0] = base_imucam['cam0']['intrinsics'][0] * scale
            config_imucam['cam0']['intrinsics'][1] = base_imucam['cam0']['intrinsics'][1] * scale
            config_imucam['cam1']['intrinsics'][0] = base_imucam['cam1']['intrinsics'][0] * scale
            config_imucam['cam1']['intrinsics'][1] = base_imucam['cam1']['intrinsics'][1] * scale

            val_str = format_value_for_filename(scale, "focal")
            name = f"focal_{val_str}_seed{seed}"

            dim_dir = os.path.join(output_dir, "focal", name)
            Path(dim_dir).mkdir(parents=True, exist_ok=True)

            dump_yaml_config(config_imu, os.path.join(dim_dir, "kalibr_imu_chain.yaml"))
            dump_yaml_config(config_imucam, os.path.join(dim_dir, "kalibr_imucam_chain.yaml"))

            config_estimator['relative_config_imu'] = "kalibr_imu_chain.yaml"
            config_estimator['relative_config_imucam'] = "kalibr_imucam_chain.yaml"
            dump_yaml_config(config_estimator, os.path.join(dim_dir, "estimator_config.yaml"))

            count += 1

    return count


def generate_principal_configs(output_dir: str, base_config_dir: str, base_imu: dict, base_imucam: dict, base_estimator: dict, random_dirs: dict) -> int:
    """"""
    count = 0

    for seed in SEEDS:
        seed_str = str(seed)
        if seed_str not in random_dirs:
            print(f"   Warning: seed {seed} not found in random_directions.json")
            continue

        principal_dir = np.array(random_dirs[seed_str]["principal_dir"])
        principal_dir = principal_dir / np.linalg.norm(principal_dir)

        for px_offset in TEST_POINTS["principal"]:
            config_imu = copy.deepcopy(base_imu)
            config_imucam = copy.deepcopy(base_imucam)
            config_estimator = copy.deepcopy(base_estimator)

            if abs(px_offset) < 1e-9:  # baseline
                pass  #
            else:
                #
                delta_cx = principal_dir[0] * px_offset
                delta_cy = principal_dir[1] * px_offset

                config_imucam['cam0']['intrinsics'][2] = base_imucam['cam0']['intrinsics'][2] + delta_cx
                config_imucam['cam0']['intrinsics'][3] = base_imucam['cam0']['intrinsics'][3] + delta_cy
                config_imucam['cam1']['intrinsics'][2] = base_imucam['cam1']['intrinsics'][2] + delta_cx
                config_imucam['cam1']['intrinsics'][3] = base_imucam['cam1']['intrinsics'][3] + delta_cy

            val_str = format_value_for_filename(px_offset, "principal")
            name = f"principal_{val_str}_seed{seed}"

            dim_dir = os.path.join(output_dir, "principal", name)
            Path(dim_dir).mkdir(parents=True, exist_ok=True)

            dump_yaml_config(config_imu, os.path.join(dim_dir, "kalibr_imu_chain.yaml"))
            dump_yaml_config(config_imucam, os.path.join(dim_dir, "kalibr_imucam_chain.yaml"))

            config_estimator['relative_config_imu'] = "kalibr_imu_chain.yaml"
            config_estimator['relative_config_imucam'] = "kalibr_imucam_chain.yaml"
            dump_yaml_config(config_estimator, os.path.join(dim_dir, "estimator_config.yaml"))

            count += 1

    return count


def generate_distortion_configs(output_dir: str, base_config_dir: str, base_imu: dict, base_imucam: dict, base_estimator: dict) -> int:
    """"""
    count = 0

    for seed in SEEDS:
        for scale in TEST_POINTS["distortion"]:
            config_imu = copy.deepcopy(base_imu)
            config_imucam = copy.deepcopy(base_imucam)
            config_estimator = copy.deepcopy(base_estimator)

            #
            for i in range(len(config_imucam['cam0']['distortion_coeffs'])):
                config_imucam['cam0']['distortion_coeffs'][i] = base_imucam['cam0']['distortion_coeffs'][i] * scale
                config_imucam['cam1']['distortion_coeffs'][i] = base_imucam['cam1']['distortion_coeffs'][i] * scale

            val_str = format_value_for_filename(scale, "distortion")
            name = f"distortion_{val_str}_seed{seed}"

            dim_dir = os.path.join(output_dir, "distortion", name)
            Path(dim_dir).mkdir(parents=True, exist_ok=True)

            dump_yaml_config(config_imu, os.path.join(dim_dir, "kalibr_imu_chain.yaml"))
            dump_yaml_config(config_imucam, os.path.join(dim_dir, "kalibr_imucam_chain.yaml"))

            config_estimator['relative_config_imu'] = "kalibr_imu_chain.yaml"
            config_estimator['relative_config_imucam'] = "kalibr_imucam_chain.yaml"
            dump_yaml_config(config_estimator, os.path.join(dim_dir, "estimator_config.yaml"))

            count += 1

    return count


# ==============  ==============

def main() -> None:
    output_dir, random_directions_path, base_config_dir = resolve_paths()

    print("=" * 70)
    print("OpenVINS CERBERUS ")
    print("=" * 70)
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
    base_imu_path = os.path.join(base_config_dir, "kalibr_imu_chain.yaml")
    base_imucam_path = os.path.join(base_config_dir, "kalibr_imucam_chain.yaml")
    base_estimator_path = os.path.join(base_config_dir, "estimator_config.yaml")

    if not os.path.exists(base_imu_path):
        print(f" Error: : {base_imu_path}")
        return
    if not os.path.exists(base_imucam_path):
        print(f" Error: : {base_imucam_path}")
        return
    if not os.path.exists(base_estimator_path):
        print(f" Error: : {base_estimator_path}")
        return

    base_imu = load_yaml_config(base_imu_path)
    base_imucam = load_yaml_config(base_imucam_path)
    base_estimator = load_yaml_config(base_estimator_path)

    print(" ")

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
        ("acc_noise", lambda: generate_acc_noise_configs(output_dir, base_config_dir, base_imu, base_imucam, base_estimator)),
        ("gyro_noise", lambda: generate_gyro_noise_configs(output_dir, base_config_dir, base_imu, base_imucam, base_estimator)),
        ("acc_bias", lambda: generate_acc_bias_configs(output_dir, base_config_dir, base_imu, base_imucam, base_estimator)),
        ("gyro_bias", lambda: generate_gyro_bias_configs(output_dir, base_config_dir, base_imu, base_imucam, base_estimator)),
        ("rotation", lambda: generate_rotation_configs(output_dir, base_config_dir, base_imu, base_imucam, base_estimator, random_dirs)),
        ("translation", lambda: generate_translation_configs(output_dir, base_config_dir, base_imu, base_imucam, base_estimator, random_dirs)),
        ("focal", lambda: generate_focal_configs(output_dir, base_config_dir, base_imu, base_imucam, base_estimator)),
        ("principal", lambda: generate_principal_configs(output_dir, base_config_dir, base_imu, base_imucam, base_estimator, random_dirs)),
        ("distortion", lambda: generate_distortion_configs(output_dir, base_config_dir, base_imu, base_imucam, base_estimator)),
    ]

    for i, (name, gen_func) in enumerate(generators, 1):
        print(f"\n[{i}/9]  {name} ...")
        count = gen_func()
        print(f"    {count} 3")
        total_count += count

    print("\n" + "=" * 70)
    print(" ")
    print("=" * 70)
    print(f"\n: {total_count} ")
    print(f"  : estimator_config.yaml, kalibr_imu_chain.yaml, kalibr_imucam_chain.yaml")
    print(f"  : {total_count * 3} ")
    print(f"  9  11  3seeds = {9 * 11 * 3} ")
    print(f"\n: {output_dir}")


if __name__ == "__main__":
    main()
