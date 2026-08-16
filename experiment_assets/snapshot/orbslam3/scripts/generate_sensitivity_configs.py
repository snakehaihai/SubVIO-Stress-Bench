#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
ORB-SLAM3 CERBERUS


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
from scipy.spatial.transform import Rotation as R
import re


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


class ORB3ConfigParser:
    """ORB-SLAM3 OpenCV YAML"""

    def __init__(self, filepath):
        self.filepath = filepath
        self.raw_content = None
        self.params = {}
        self._load()

    def _load(self):
        """"""
        with open(self.filepath, 'r') as f:
            self.raw_content = f.read()
        self._parse_params()

    def _parse_params(self):
        """"""
        content = self.raw_content

        #
        simple_keys = [
            'IMU.NoiseGyro', 'IMU.NoiseAcc', 'IMU.GyroWalk', 'IMU.AccWalk',
            'Camera1.fx', 'Camera1.fy', 'Camera1.cx', 'Camera1.cy',
            'Camera1.k1', 'Camera1.k2', 'Camera1.k3', 'Camera1.k4',
            'Camera2.fx', 'Camera2.fy', 'Camera2.cx', 'Camera2.cy',
            'Camera2.k1', 'Camera2.k2', 'Camera2.k3', 'Camera2.k4',
        ]

        for key in simple_keys:
            pattern = r'^{}:\s*([\d.eE+-]+)'.format(re.escape(key))
            match = re.search(pattern, content, re.MULTILINE)
            if match:
                self.params[key] = float(match.group(1))

        # 4x4 (IMU.T_b_c1)
        self._parse_opencv_matrix('IMU.T_b_c1')
        self._parse_opencv_matrix('Stereo.T_c1_c2')

    def _parse_opencv_matrix(self, key):
        """OpenCV"""
        pattern = r'{}:\s*!!opencv-matrix\s*rows:\s*(\d+)\s*cols:\s*(\d+)\s*dt:\s*\w+\s*data:\s*\[([\d\s,.\-eE+]+)\]'.format(re.escape(key))
        match = re.search(pattern, self.raw_content, re.DOTALL)
        if match:
            rows = int(match.group(1))
            cols = int(match.group(2))
            data_str = match.group(3)
            data = [float(x.strip()) for x in data_str.split(',') if x.strip()]
            self.params[key] = np.array(data).reshape(rows, cols)

    def set_param(self, key, value):
        """"""
        self.params[key] = value

    def get_param(self, key):
        """"""
        return self.params.get(key)

    def save(self, output_path):
        """"""
        content = self.raw_content

        #
        simple_keys = [
            'IMU.NoiseGyro', 'IMU.NoiseAcc', 'IMU.GyroWalk', 'IMU.AccWalk',
            'Camera1.fx', 'Camera1.fy', 'Camera1.cx', 'Camera1.cy',
            'Camera1.k1', 'Camera1.k2', 'Camera1.k3', 'Camera1.k4',
            'Camera2.fx', 'Camera2.fy', 'Camera2.cx', 'Camera2.cy',
            'Camera2.k1', 'Camera2.k2', 'Camera2.k3', 'Camera2.k4',
        ]

        for key in simple_keys:
            if key in self.params:
                value = self.params[key]
                #
                if abs(value) < 0.01 or abs(value) >= 1000:
                    value_str = "{:.6e}".format(value)
                else:
                    value_str = "{:.12f}".format(value).rstrip('0').rstrip('.')

                pattern = r'^({}:\s*)[\d.eE+-]+'.format(re.escape(key))
                replacement = r'\g<1>{}'.format(value_str)
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

        # 4x4
        for key in ['IMU.T_b_c1', 'Stereo.T_c1_c2']:
            if key in self.params:
                content = self._replace_opencv_matrix(content, key, self.params[key])

        #
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w') as f:
            f.write(content)

    def _replace_opencv_matrix(self, content, key, matrix):
        """OpenCV"""
        data_list = matrix.flatten().tolist()

        data_lines = []
        for i in range(0, len(data_list), 4):
            row = data_list[i:i+4]
            row_str = ", ".join("{:.10f}".format(x) for x in row)
            if i + 4 < len(data_list):
                row_str += ","
            data_lines.append("         " + row_str)

        new_matrix = """{}: !!opencv-matrix
  rows: 4
  cols: 4
  dt: f
  data: [{}
{}
{}
{}]""".format(key, data_lines[0].strip(), data_lines[1], data_lines[2], data_lines[3])

        pattern = r'{}:\s*!!opencv-matrix\s*rows:\s*\d+\s*cols:\s*\d+\s*dt:\s*\w+\s*data:\s*\[[\d\s,.\-eE+]+\]'.format(re.escape(key))
        content = re.sub(pattern, new_matrix, content, flags=re.DOTALL)

        return content


def resolve_paths() -> tuple[str, str, str]:
    """Return (base_config_path, output_dir, random_directions_path)."""
    #
    if os.path.exists("Examples/Stereo-Inertial/CERBERUS.yaml"):
        base_config = "Examples/Stereo-Inertial/CERBERUS.yaml"
        output_dir = "sensitivity_experiments/configs/sensitivity"
    elif os.path.exists("/home/zyy/Algs/orb3/Examples/Stereo-Inertial/CERBERUS.yaml"):
        base_config = "/home/zyy/Algs/orb3/Examples/Stereo-Inertial/CERBERUS.yaml"
        output_dir = "/home/zyy/Algs/orb3/sensitivity_experiments/configs/sensitivity"
    else:
        base_config = "/home/zyy/Algs/orb3/Examples/Stereo-Inertial/CERBERUS.yaml"
        output_dir = "/home/zyy/Algs/orb3/sensitivity_experiments/configs/sensitivity"

    # random_directions.json
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

def generate_acc_noise_configs(base_parser: ORB3ConfigParser, output_dir: str) -> int:
    """"""
    orig_val = base_parser.get_param('IMU.NoiseAcc')
    if orig_val is None:
        orig_val = 2.0e-03
    count = 0

    for seed in SEEDS:
        for scale in TEST_POINTS["acc_noise"]:
            config = ORB3ConfigParser(base_parser.filepath)
            config.set_param('IMU.NoiseAcc', orig_val * scale)

            val_str = format_value_for_filename(scale, "acc_noise")
            filename = f"orb3_cerberus_acc_noise_{val_str}_seed{seed}.yaml"
            out_path = os.path.join(output_dir, "acc_noise", filename)
            Path(out_path).parent.mkdir(parents=True, exist_ok=True)
            config.save(out_path)
            count += 1

    return count


def generate_gyro_noise_configs(base_parser: ORB3ConfigParser, output_dir: str) -> int:
    """"""
    orig_val = base_parser.get_param('IMU.NoiseGyro')
    if orig_val is None:
        orig_val = 1.7e-04
    count = 0

    for seed in SEEDS:
        for scale in TEST_POINTS["gyro_noise"]:
            config = ORB3ConfigParser(base_parser.filepath)
            config.set_param('IMU.NoiseGyro', orig_val * scale)

            val_str = format_value_for_filename(scale, "gyro_noise")
            filename = f"orb3_cerberus_gyro_noise_{val_str}_seed{seed}.yaml"
            out_path = os.path.join(output_dir, "gyro_noise", filename)
            Path(out_path).parent.mkdir(parents=True, exist_ok=True)
            config.save(out_path)
            count += 1

    return count


def generate_acc_bias_configs(base_parser: ORB3ConfigParser, output_dir: str) -> int:
    """"""
    orig_val = base_parser.get_param('IMU.AccWalk')
    if orig_val is None:
        orig_val = 3.0e-03
    count = 0

    for seed in SEEDS:
        for scale in TEST_POINTS["acc_bias"]:
            config = ORB3ConfigParser(base_parser.filepath)
            config.set_param('IMU.AccWalk', orig_val * scale)

            val_str = format_value_for_filename(scale, "acc_bias")
            filename = f"orb3_cerberus_acc_bias_{val_str}_seed{seed}.yaml"
            out_path = os.path.join(output_dir, "acc_bias", filename)
            Path(out_path).parent.mkdir(parents=True, exist_ok=True)
            config.save(out_path)
            count += 1

    return count


def generate_gyro_bias_configs(base_parser: ORB3ConfigParser, output_dir: str) -> int:
    """"""
    orig_val = base_parser.get_param('IMU.GyroWalk')
    if orig_val is None:
        orig_val = 1.9393e-05
    count = 0

    for seed in SEEDS:
        for scale in TEST_POINTS["gyro_bias"]:
            config = ORB3ConfigParser(base_parser.filepath)
            config.set_param('IMU.GyroWalk', orig_val * scale)

            val_str = format_value_for_filename(scale, "gyro_bias")
            filename = f"orb3_cerberus_gyro_bias_{val_str}_seed{seed}.yaml"
            out_path = os.path.join(output_dir, "gyro_bias", filename)
            Path(out_path).parent.mkdir(parents=True, exist_ok=True)
            config.save(out_path)
            count += 1

    return count


# ============== Tbc ==============

def generate_rotation_configs(base_parser: ORB3ConfigParser, output_dir: str, random_dirs: dict) -> int:
    """Tbc"""
    base_T = base_parser.get_param('IMU.T_b_c1')
    if base_T is None:
        print("   Warning:  IMU.T_b_c1")
        return 0

    count = 0

    for seed in SEEDS:
        seed_str = str(seed)
        if seed_str not in random_dirs:
            print(f"   Warning: seed {seed} not found in random_directions.json")
            continue

        rotation_axis = np.array(random_dirs[seed_str]["rotation_axis"])
        rotation_axis = rotation_axis / np.linalg.norm(rotation_axis)

        for deg in TEST_POINTS["rotation"]:
            config = ORB3ConfigParser(base_parser.filepath)

            if abs(deg) < 1e-9:  # baseline
                T_new = base_T.copy()
            else:
                #  deg
                delta_R = R.from_rotvec(rotation_axis * np.deg2rad(deg)).as_matrix()
                R_orig = base_T[:3, :3]
                t_orig = base_T[:3, 3]
                R_new = delta_R @ R_orig

                #
                U, _, Vt = np.linalg.svd(R_new)
                R_new = U @ Vt

                T_new = np.eye(4)
                T_new[:3, :3] = R_new
                T_new[:3, 3] = t_orig

            config.set_param('IMU.T_b_c1', T_new)

            val_str = format_value_for_filename(deg, "rotation")
            filename = f"orb3_cerberus_rotation_{val_str}_seed{seed}.yaml"
            out_path = os.path.join(output_dir, "rotation", filename)
            Path(out_path).parent.mkdir(parents=True, exist_ok=True)
            config.save(out_path)
            count += 1

    return count


def generate_translation_configs(base_parser: ORB3ConfigParser, output_dir: str, random_dirs: dict) -> int:
    """Tbc"""
    base_T = base_parser.get_param('IMU.T_b_c1')
    if base_T is None:
        print("   Warning:  IMU.T_b_c1")
        return 0

    count = 0

    for seed in SEEDS:
        seed_str = str(seed)
        if seed_str not in random_dirs:
            print(f"   Warning: seed {seed} not found in random_directions.json")
            continue

        translation_dir = np.array(random_dirs[seed_str]["translation_dir"])
        translation_dir = translation_dir / np.linalg.norm(translation_dir)

        for cm in TEST_POINTS["translation"]:
            config = ORB3ConfigParser(base_parser.filepath)

            if abs(cm) < 1e-9:  # baseline
                T_new = base_T.copy()
            else:
                #  cm
                delta_m = cm / 100.0
                delta_t = translation_dir * delta_m

                T_new = base_T.copy()
                T_new[:3, 3] = base_T[:3, 3] + delta_t

            config.set_param('IMU.T_b_c1', T_new)

            val_str = format_value_for_filename(cm, "translation")
            filename = f"orb3_cerberus_translation_{val_str}_seed{seed}.yaml"
            out_path = os.path.join(output_dir, "translation", filename)
            Path(out_path).parent.mkdir(parents=True, exist_ok=True)
            config.save(out_path)
            count += 1

    return count


# ============== Camera ==============

def generate_focal_configs(base_parser: ORB3ConfigParser, output_dir: str) -> int:
    """"""
    fx0_base = base_parser.get_param('Camera1.fx')
    fy0_base = base_parser.get_param('Camera1.fy')
    fx1_base = base_parser.get_param('Camera2.fx')
    fy1_base = base_parser.get_param('Camera2.fy')

    count = 0

    for seed in SEEDS:
        for scale in TEST_POINTS["focal"]:
            config = ORB3ConfigParser(base_parser.filepath)

            # fxfy
            config.set_param('Camera1.fx', fx0_base * scale)
            config.set_param('Camera1.fy', fy0_base * scale)
            config.set_param('Camera2.fx', fx1_base * scale)
            config.set_param('Camera2.fy', fy1_base * scale)

            val_str = format_value_for_filename(scale, "focal")
            filename = f"orb3_cerberus_focal_{val_str}_seed{seed}.yaml"
            out_path = os.path.join(output_dir, "focal", filename)
            Path(out_path).parent.mkdir(parents=True, exist_ok=True)
            config.save(out_path)
            count += 1

    return count


def generate_principal_configs(base_parser: ORB3ConfigParser, output_dir: str, random_dirs: dict) -> int:
    """"""
    cx0_base = base_parser.get_param('Camera1.cx')
    cy0_base = base_parser.get_param('Camera1.cy')
    cx1_base = base_parser.get_param('Camera2.cx')
    cy1_base = base_parser.get_param('Camera2.cy')

    count = 0

    for seed in SEEDS:
        seed_str = str(seed)
        if seed_str not in random_dirs:
            print(f"   Warning: seed {seed} not found in random_directions.json")
            continue

        principal_dir = np.array(random_dirs[seed_str]["principal_dir"])
        principal_dir = principal_dir / np.linalg.norm(principal_dir)

        for px_offset in TEST_POINTS["principal"]:
            config = ORB3ConfigParser(base_parser.filepath)

            if abs(px_offset) < 1e-9:  # baseline
                pass  #
            else:
                #
                delta_cx = principal_dir[0] * px_offset
                delta_cy = principal_dir[1] * px_offset

                config.set_param('Camera1.cx', cx0_base + delta_cx)
                config.set_param('Camera1.cy', cy0_base + delta_cy)
                config.set_param('Camera2.cx', cx1_base + delta_cx)
                config.set_param('Camera2.cy', cy1_base + delta_cy)

            val_str = format_value_for_filename(px_offset, "principal")
            filename = f"orb3_cerberus_principal_{val_str}_seed{seed}.yaml"
            out_path = os.path.join(output_dir, "principal", filename)
            Path(out_path).parent.mkdir(parents=True, exist_ok=True)
            config.save(out_path)
            count += 1

    return count


def generate_distortion_configs(base_parser: ORB3ConfigParser, output_dir: str) -> int:
    """"""
    k0_base = [
        base_parser.get_param('Camera1.k1'),
        base_parser.get_param('Camera1.k2'),
        base_parser.get_param('Camera1.k3'),
        base_parser.get_param('Camera1.k4'),
    ]
    k1_base = [
        base_parser.get_param('Camera2.k1'),
        base_parser.get_param('Camera2.k2'),
        base_parser.get_param('Camera2.k3'),
        base_parser.get_param('Camera2.k4'),
    ]

    count = 0

    for seed in SEEDS:
        for scale in TEST_POINTS["distortion"]:
            config = ORB3ConfigParser(base_parser.filepath)

            #
            for i, k_name in enumerate(['k1', 'k2', 'k3', 'k4']):
                config.set_param(f'Camera1.{k_name}', k0_base[i] * scale)
                config.set_param(f'Camera2.{k_name}', k1_base[i] * scale)

            val_str = format_value_for_filename(scale, "distortion")
            filename = f"orb3_cerberus_distortion_{val_str}_seed{seed}.yaml"
            out_path = os.path.join(output_dir, "distortion", filename)
            Path(out_path).parent.mkdir(parents=True, exist_ok=True)
            config.save(out_path)
            count += 1

    return count


# ==============  ==============

def main() -> None:
    base_config_path, output_dir, random_directions_path = resolve_paths()

    print("=" * 70)
    print("ORB-SLAM3 CERBERUS ")
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
    if not os.path.exists(base_config_path):
        print(f" Error: : {base_config_path}")
        return

    base_parser = ORB3ConfigParser(base_config_path)

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
        ("acc_noise", lambda: generate_acc_noise_configs(base_parser, output_dir)),
        ("gyro_noise", lambda: generate_gyro_noise_configs(base_parser, output_dir)),
        ("acc_bias", lambda: generate_acc_bias_configs(base_parser, output_dir)),
        ("gyro_bias", lambda: generate_gyro_bias_configs(base_parser, output_dir)),
        ("rotation", lambda: generate_rotation_configs(base_parser, output_dir, random_dirs)),
        ("translation", lambda: generate_translation_configs(base_parser, output_dir, random_dirs)),
        ("focal", lambda: generate_focal_configs(base_parser, output_dir)),
        ("principal", lambda: generate_principal_configs(base_parser, output_dir, random_dirs)),
        ("distortion", lambda: generate_distortion_configs(base_parser, output_dir)),
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
