#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
SchurVINS CERBERUS -


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


- 11baseline
- 3seedsrandom_directions.json0,1,2
"""

from __future__ import annotations

import os
import json
import copy
from pathlib import Path
import numpy as np
import yaml
from scipy.spatial.transform import Rotation as R


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
    """Return (output_dir, random_directions_path, base_config_path)."""
    #  /home/zyy/Algs/schur/
    script_dir = os.path.dirname(os.path.abspath(__file__))

    #  -
    base_config_path = os.path.join(script_dir, "src/SchurVINS/svo_ros/param/calib/CERBERUS_stereo.yaml")
    output_dir = os.path.join(script_dir, "src/SchurVINS/svo_ros/param/calib/sensitivity")

    # schur
    if not os.path.exists(base_config_path):
        if os.path.exists("/ws/src/SchurVINS/svo_ros/param/calib/CERBERUS_stereo.yaml"):
            base_config_path = "/ws/src/SchurVINS/svo_ros/param/calib/CERBERUS_stereo.yaml"
            output_dir = "/ws/src/SchurVINS/svo_ros/param/calib/sensitivity"
        elif os.path.exists("/home/zyy/Algs/schur/src/SchurVINS/svo_ros/param/calib/CERBERUS_stereo.yaml"):
            base_config_path = "/home/zyy/Algs/schur/src/SchurVINS/svo_ros/param/calib/CERBERUS_stereo.yaml"
            output_dir = "/home/zyy/Algs/schur/src/SchurVINS/svo_ros/param/calib/sensitivity"

    # random_directions.json - summaries
    random_directions_path = None
    candidates = [
        "/home/zyy/Algs/summaries/random_directions.json",
        "/home/zyy/Algs/summaries/sensitivity_experiment/random_directions.json",
        os.path.join(script_dir, "../summaries/random_directions.json"),
        os.path.join(script_dir, "../summaries/sensitivity_experiment/random_directions.json"),
    ]
    for candidate in candidates:
        if os.path.exists(candidate):
            random_directions_path = candidate
            break

    if random_directions_path is None:
        #
        random_directions_path = "/home/zyy/Algs/summaries/random_directions.json"

    return output_dir, random_directions_path, base_config_path


def load_yaml_config(file_path: str) -> dict:
    """Load YAML config."""
    with open(file_path, "r") as f:
        data = yaml.safe_load(f)
    if data is None:
        raise RuntimeError(f"Empty yaml: {file_path}")
    return data


def dump_yaml_config(data: dict, out_path: str) -> None:
    """Save YAML config with proper formatting to match original style."""
    with open(out_path, "w") as f:
        # labelid
        f.write(f'label: "{data["label"]}"\n')
        f.write(f'id: {data["id"]}\n')
        f.write("cameras:\n")

        # cameras
        for cam_item in data["cameras"]:
            f.write("- camera:\n")
            camera = cam_item["camera"]
            f.write(f"    label: {camera['label']}\n")
            f.write(f"    id: {camera['id']}\n")
            f.write(f"    line-delay-nanoseconds: {camera['line-delay-nanoseconds']}\n")
            f.write(f"    image_height: {camera['image_height']}\n")
            f.write(f"    image_width: {camera['image_width']}\n")
            f.write(f"    type: {camera['type']}\n")
            f.write("    \n")

            # intrinsics
            f.write("    intrinsics:\n")
            f.write(f"      cols: {camera['intrinsics']['cols']}\n")
            f.write(f"      rows: {camera['intrinsics']['rows']}\n")
            f.write(f"      data: {camera['intrinsics']['data']}\n")

            # distortion
            f.write("    distortion:\n")
            f.write(f"      type: {camera['distortion']['type']}  \n")
            f.write("      parameters:\n")
            f.write(f"        cols: {camera['distortion']['parameters']['cols']}\n")
            f.write(f"        rows: {camera['distortion']['parameters']['rows']}\n")
            f.write(f"        data: {camera['distortion']['parameters']['data']}\n")

            # T_B_C
            f.write("  T_B_C:\n")
            tbc = cam_item["T_B_C"]
            f.write(f"    cols: {tbc['cols']}\n")
            f.write(f"    rows: {tbc['rows']}\n")
            # 4
            data_list = tbc['data']
            f.write("    data: [")
            for i in range(0, len(data_list), 4):
                row = data_list[i:i+4]
                if i == 0:
                    # 4
                    f.write(f"{row[0]}, {row[1]}, {row[2]}, {row[3]}")
                else:
                    # 412
                    f.write(f"\n           {row[0]}, {row[1]}, {row[2]}, {row[3]}")
                if i + 4 < len(data_list):
                    f.write(",")
            f.write("]\n")

        # imu_params
        f.write("\nimu_params:\n")
        imu = data["imu_params"]
        f.write(f"  delay_imu_cam: {imu['delay_imu_cam']}\n")
        f.write(f"  max_imu_delta_t: {imu['max_imu_delta_t']}\n")
        f.write(f"  acc_max: {imu['acc_max']}\n")
        f.write(f"  omega_max: {imu['omega_max']}\n")
        #  1.7e-04, 2.0e-03
        def format_scientific(val):
            """"""
            if abs(val) < 0.001:
                #  1.7e-04
                s = f"{val:.6e}"
                # 0 1.700000e-04 -> 1.7e-04
                if 'e' in s:
                    mantissa, exp = s.split('e')
                    mantissa = mantissa.rstrip('0').rstrip('.')
                    return f"{mantissa}e{exp}"
                return s
            else:
                return str(val)

        sigma_omega_c_str = format_scientific(imu['sigma_omega_c'])
        sigma_acc_c_str = format_scientific(imu['sigma_acc_c'])
        sigma_omega_bias_c_str = format_scientific(imu['sigma_omega_bias_c'])
        sigma_acc_bias_c_str = format_scientific(imu['sigma_acc_bias_c'])
        f.write(f"  sigma_omega_c: {sigma_omega_c_str}      #  (rad/s/Hz) = gyr_n\n")
        f.write(f"  sigma_acc_c: {sigma_acc_c_str}        #  (m/s/Hz) = acc_n\n")
        f.write(f"  sigma_omega_bias_c: {sigma_omega_bias_c_str}  #  (rad/s/Hz) = gyr_w\n")
        f.write(f"  sigma_acc_bias_c: {sigma_acc_bias_c_str}   #  (m/s/Hz) = acc_w\n")
        f.write(f"  sigma_integration: {imu['sigma_integration']}\n")
        f.write(f"  g: {imu['g']}\n")
        f.write(f"  imu_rate: {imu['imu_rate']}\n")

        # imu_initialization
        f.write("\nimu_initialization:\n")
        init = data["imu_initialization"]
        f.write(f"  velocity: {init['velocity']}\n")
        f.write(f"  omega_bias: {init['omega_bias']}\n")
        f.write(f"  acc_bias: {init['acc_bias']}\n")
        f.write(f"  velocity_sigma: {init['velocity_sigma']}\n")
        f.write(f"  omega_bias_sigma: {init['omega_bias_sigma']}\n")
        f.write(f"  acc_bias_sigma: {init['acc_bias_sigma']}\n")
        f.write("\n")


def load_random_directions(json_path: str) -> dict:
    """"""
    with open(json_path, "r") as f:
        data = json.load(f)
    return data


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


def parse_matrix_from_config(matrix_dict: dict) -> np.ndarray:
    """"""
    data = matrix_dict.get('data', [])
    rows = matrix_dict.get('rows', 4)
    cols = matrix_dict.get('cols', 4)
    return np.array(data).reshape(rows, cols)


def format_matrix_for_config(matrix: np.ndarray) -> dict:
    """"""
    return {
        'rows': matrix.shape[0],
        'cols': matrix.shape[1],
        'data': matrix.flatten().tolist()
    }


# ============== IMU ==============

def generate_acc_noise_configs(base: dict, output_dir: str) -> int:
    """"""
    orig_val = base['imu_params']['sigma_acc_c']
    count = 0

    for seed in SEEDS:
        for scale in TEST_POINTS["acc_noise"]:
            config = copy.deepcopy(base)
            config['imu_params']['sigma_acc_c'] = orig_val * scale

            val_str = format_value_for_filename(scale, "acc_noise")
            filename = f"schur_cerberus_acc_noise_{val_str}_seed{seed}.yaml"
            out_path = os.path.join(output_dir, "acc_noise", filename)
            Path(out_path).parent.mkdir(parents=True, exist_ok=True)
            dump_yaml_config(config, out_path)
            count += 1

    return count


def generate_gyro_noise_configs(base: dict, output_dir: str) -> int:
    """"""
    orig_val = base['imu_params']['sigma_omega_c']
    count = 0

    for seed in SEEDS:
        for scale in TEST_POINTS["gyro_noise"]:
            config = copy.deepcopy(base)
            config['imu_params']['sigma_omega_c'] = orig_val * scale

            val_str = format_value_for_filename(scale, "gyro_noise")
            filename = f"schur_cerberus_gyro_noise_{val_str}_seed{seed}.yaml"
            out_path = os.path.join(output_dir, "gyro_noise", filename)
            Path(out_path).parent.mkdir(parents=True, exist_ok=True)
            dump_yaml_config(config, out_path)
            count += 1

    return count


def generate_acc_bias_configs(base: dict, output_dir: str) -> int:
    """"""
    orig_val = base['imu_params']['sigma_acc_bias_c']
    count = 0

    for seed in SEEDS:
        for scale in TEST_POINTS["acc_bias"]:
            config = copy.deepcopy(base)
            config['imu_params']['sigma_acc_bias_c'] = orig_val * scale

            val_str = format_value_for_filename(scale, "acc_bias")
            filename = f"schur_cerberus_acc_bias_{val_str}_seed{seed}.yaml"
            out_path = os.path.join(output_dir, "acc_bias", filename)
            Path(out_path).parent.mkdir(parents=True, exist_ok=True)
            dump_yaml_config(config, out_path)
            count += 1

    return count


def generate_gyro_bias_configs(base: dict, output_dir: str) -> int:
    """"""
    orig_val = base['imu_params']['sigma_omega_bias_c']
    count = 0

    for seed in SEEDS:
        for scale in TEST_POINTS["gyro_bias"]:
            config = copy.deepcopy(base)
            config['imu_params']['sigma_omega_bias_c'] = orig_val * scale

            val_str = format_value_for_filename(scale, "gyro_bias")
            filename = f"schur_cerberus_gyro_bias_{val_str}_seed{seed}.yaml"
            out_path = os.path.join(output_dir, "gyro_bias", filename)
            Path(out_path).parent.mkdir(parents=True, exist_ok=True)
            dump_yaml_config(config, out_path)
            count += 1

    return count


# ============== Tbc ==============

def generate_rotation_configs(base: dict, output_dir: str, random_dirs: dict) -> int:
    """Tbccam0"""
    T_cam0_base = parse_matrix_from_config(base['cameras'][0]['T_B_C'])
    T_cam1_base = parse_matrix_from_config(base['cameras'][1]['T_B_C'])  #  cam1
    count = 0

    for seed in SEEDS:
        seed_str = str(seed)
        if seed_str not in random_dirs:
            print(f"   Warning: seed {seed} not found in random_directions.json")
            continue

        rotation_axis = np.array(random_dirs[seed_str]["rotation_axis"])
        rotation_axis = rotation_axis / np.linalg.norm(rotation_axis)

        for deg in TEST_POINTS["rotation"]:
            config = copy.deepcopy(base)

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

            #  cam0cam1
            config['cameras'][0]['T_B_C'] = format_matrix_for_config(T_new)
            config['cameras'][1]['T_B_C'] = format_matrix_for_config(T_cam1_base)  #

            val_str = format_value_for_filename(deg, "rotation")
            filename = f"schur_cerberus_rotation_{val_str}_seed{seed}.yaml"
            out_path = os.path.join(output_dir, "rotation", filename)
            Path(out_path).parent.mkdir(parents=True, exist_ok=True)
            dump_yaml_config(config, out_path)
            count += 1

    return count


def generate_translation_configs(base: dict, output_dir: str, random_dirs: dict) -> int:
    """Tbccam0"""
    T_cam0_base = parse_matrix_from_config(base['cameras'][0]['T_B_C'])
    T_cam1_base = parse_matrix_from_config(base['cameras'][1]['T_B_C'])  #  cam1
    count = 0

    for seed in SEEDS:
        seed_str = str(seed)
        if seed_str not in random_dirs:
            print(f"   Warning: seed {seed} not found in random_directions.json")
            continue

        translation_dir = np.array(random_dirs[seed_str]["translation_dir"])
        translation_dir = translation_dir / np.linalg.norm(translation_dir)

        for cm in TEST_POINTS["translation"]:
            config = copy.deepcopy(base)

            if abs(cm) < 1e-9:  # baseline
                T_new = T_cam0_base.copy()
            else:
                #  cm
                delta_m = cm / 100.0
                delta_t = translation_dir * delta_m

                T_new = T_cam0_base.copy()
                T_new[:3, 3] = T_cam0_base[:3, 3] + delta_t

            #  cam0cam1
            config['cameras'][0]['T_B_C'] = format_matrix_for_config(T_new)
            config['cameras'][1]['T_B_C'] = format_matrix_for_config(T_cam1_base)  #

            val_str = format_value_for_filename(cm, "translation")
            filename = f"schur_cerberus_translation_{val_str}_seed{seed}.yaml"
            out_path = os.path.join(output_dir, "translation", filename)
            Path(out_path).parent.mkdir(parents=True, exist_ok=True)
            dump_yaml_config(config, out_path)
            count += 1

    return count


# ============== Camera ==============

def generate_focal_configs(base: dict, output_dir: str) -> int:
    """"""
    #  - YAMLcameras[0]['camera']['intrinsics']
    fx0_base = base['cameras'][0]['camera']['intrinsics']['data'][0]
    fy0_base = base['cameras'][0]['camera']['intrinsics']['data'][1]
    fx1_base = base['cameras'][1]['camera']['intrinsics']['data'][0]
    fy1_base = base['cameras'][1]['camera']['intrinsics']['data'][1]

    count = 0

    for seed in SEEDS:
        for scale in TEST_POINTS["focal"]:
            config = copy.deepcopy(base)

            # fxfy
            config['cameras'][0]['camera']['intrinsics']['data'][0] = fx0_base * scale
            config['cameras'][0]['camera']['intrinsics']['data'][1] = fy0_base * scale
            config['cameras'][1]['camera']['intrinsics']['data'][0] = fx1_base * scale
            config['cameras'][1]['camera']['intrinsics']['data'][1] = fy1_base * scale

            val_str = format_value_for_filename(scale, "focal")
            filename = f"schur_cerberus_focal_{val_str}_seed{seed}.yaml"
            out_path = os.path.join(output_dir, "focal", filename)
            Path(out_path).parent.mkdir(parents=True, exist_ok=True)
            dump_yaml_config(config, out_path)
            count += 1

    return count


def generate_principal_configs(base: dict, output_dir: str, random_dirs: dict) -> int:
    """"""
    #  - YAMLcameras[0]['camera']['intrinsics']
    cx0_base = base['cameras'][0]['camera']['intrinsics']['data'][2]
    cy0_base = base['cameras'][0]['camera']['intrinsics']['data'][3]
    cx1_base = base['cameras'][1]['camera']['intrinsics']['data'][2]
    cy1_base = base['cameras'][1]['camera']['intrinsics']['data'][3]

    count = 0

    for seed in SEEDS:
        seed_str = str(seed)
        if seed_str not in random_dirs:
            print(f"   Warning: seed {seed} not found in random_directions.json")
            continue

        principal_dir = np.array(random_dirs[seed_str]["principal_dir"])
        principal_dir = principal_dir / np.linalg.norm(principal_dir)

        for px_offset in TEST_POINTS["principal"]:
            config = copy.deepcopy(base)

            if abs(px_offset) < 1e-9:  # baseline
                pass  #
            else:
                #
                delta_cx = principal_dir[0] * px_offset
                delta_cy = principal_dir[1] * px_offset

                config['cameras'][0]['camera']['intrinsics']['data'][2] = cx0_base + delta_cx
                config['cameras'][0]['camera']['intrinsics']['data'][3] = cy0_base + delta_cy
                config['cameras'][1]['camera']['intrinsics']['data'][2] = cx1_base + delta_cx
                config['cameras'][1]['camera']['intrinsics']['data'][3] = cy1_base + delta_cy

            val_str = format_value_for_filename(px_offset, "principal")
            filename = f"schur_cerberus_principal_{val_str}_seed{seed}.yaml"
            out_path = os.path.join(output_dir, "principal", filename)
            Path(out_path).parent.mkdir(parents=True, exist_ok=True)
            dump_yaml_config(config, out_path)
            count += 1

    return count


def generate_distortion_configs(base: dict, output_dir: str) -> int:
    """"""
    #  - YAMLcameras[0]['camera']['distortion']
    k0_base = base['cameras'][0]['camera']['distortion']['parameters']['data'].copy()
    k1_base = base['cameras'][1]['camera']['distortion']['parameters']['data'].copy()

    count = 0

    for seed in SEEDS:
        for scale in TEST_POINTS["distortion"]:
            config = copy.deepcopy(base)

            #
            for i in range(4):
                config['cameras'][0]['camera']['distortion']['parameters']['data'][i] = k0_base[i] * scale
                config['cameras'][1]['camera']['distortion']['parameters']['data'][i] = k1_base[i] * scale

            val_str = format_value_for_filename(scale, "distortion")
            filename = f"schur_cerberus_distortion_{val_str}_seed{seed}.yaml"
            out_path = os.path.join(output_dir, "distortion", filename)
            Path(out_path).parent.mkdir(parents=True, exist_ok=True)
            dump_yaml_config(config, out_path)
            count += 1

    return count


# ==============  ==============

def main() -> None:
    output_dir, random_directions_path, base_config_path = resolve_paths()

    print("=" * 70)
    print("SchurVINS CERBERUS ")
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
        print(f" Error: random_directions.json not found")
        print(f"  : {random_directions_path}")
        print("  :")
        print("    - /home/zyy/Algs/summaries/random_directions.json")
        print("    - /home/zyy/Algs/summaries/sensitivity_experiment/random_directions.json")
        print("   generate_random_directions.py ")
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
    print("\n :")
    print("   rotation/translationcam0cam1")
    print("   ")
    print("   /")


if __name__ == "__main__":
    main()
