#!/usr/bin/env python3
"""
 bag
 =  / KK>1 K<1
 K=1,2,5,10 --K 0.5 0.2 0.1 0.05
"""

import argparse
import subprocess
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(Path(__file__).parent / "src"))

from composite_dataset import composite_stereo_seq_from_masks, load_config

DEFAULT_K_LIST = [1, 2, 5, 10]


def _k_str(K):
    if K == int(K):
        return str(int(K))
    return f"{K:.4f}".rstrip("0").rstrip(".")


def main():
    parser = argparse.ArgumentParser(description=" + bag")
    parser.add_argument("--config", type=str, default="video_processing/config/processing_config.yaml")
    parser.add_argument("--K", type=float, nargs="+", default=DEFAULT_K_LIST, help="K  1 2 5 10  0.5 0.2 0.1 0.05")
    parser.add_argument("--skip-bag", action="store_true", help=" bag")
    args = parser.parse_args()

    cfg = load_config(args.config)
    base_dir = project_root
    dataset_cfg = cfg.get("dataset", {}) or {}

    bg_dir = dataset_cfg["input_images"]
    if not Path(bg_dir).is_absolute():
        bg_dir = str(base_dir / bg_dir)
    cam1_dir = dataset_cfg.get("input_images_cam1")
    if not cam1_dir:
        cam1_dir = None
    elif not Path(cam1_dir).is_absolute():
        cam1_dir = str(base_dir / cam1_dir)
    masks_dir = dataset_cfg.get("masks_dir") or "video_processing/data/masks"
    if not Path(masks_dir).is_absolute():
        masks_dir = str(base_dir / masks_dir)
    out_dir = dataset_cfg["output_images"]
    if not Path(out_dir).is_absolute():
        out_dir = str(base_dir / out_dir)

    if not cam1_dir:
        print("  dataset.input_images_cam1  composite")
        sys.exit(1)

    cam0_path = Path(bg_dir)
    seq_root = cam0_path.parent.parent
    imu_csv = dataset_cfg.get("imu_csv") or str(seq_root / "imu0" / "data.csv")
    base_seq_name = (dataset_cfg.get("seq_name") or "seq1").strip()
    if "_K" in base_seq_name:
        base_seq_name = base_seq_name.split("_K")[0].strip("_") or "seq1"

    for K in args.K:
        K = float(K)
        K = max(0.05, K)
        seq_name = f"{base_seq_name}_K{_k_str(K)}"
        print("=" * 70)
        print(f": K={K} -> {seq_name} ( = /{K})")
        print("=" * 70)
        composite_cfg = dict(dataset_cfg.get("composite", {}))
        composite_cfg["mask_hold_frames"] = K
        composite_stereo_seq_from_masks(
            bg_dir,
            cam1_dir,
            imu_csv,
            masks_dir,
            out_dir,
            seq_name,
            composite_cfg,
            dataset_cfg.get("stereo"),
            None,
        )
        if not args.skip_bag:
            seq_dir = Path(out_dir) / seq_name
            bag_path = Path(out_dir) / f"{seq_name}.bag"
            if not seq_dir.is_absolute():
                seq_dir = base_dir / seq_dir
            if not bag_path.is_absolute():
                bag_path = base_dir / bag_path
            cmd = [
                "/usr/bin/python3",
                str(base_dir / "video_processing/tools/folder_to_bag.py"),
                "--seq-dir", str(seq_dir),
                "--bag", str(bag_path),
            ]
            try:
                env = None
                ros_setup = Path("/opt/ros/noetic/setup.bash")
                if ros_setup.exists():
                    #  source  shell  rosbag
                    run = subprocess.run(
                        ["bash", "-c", f"source {ros_setup} && {' '.join(cmd)}"],
                        cwd=str(base_dir),
                    )
                else:
                    run = subprocess.run(cmd, cwd=str(base_dir), env=env)
                if run.returncode != 0:
                    print(f" bag  {run.returncode} ROS  folder_to_bag")
            except Exception as e:
                print(f"  bag : {e} folder_to_bag")

    print("=" * 70)
    print(f" {len(args.K)} ")
    print("=" * 70)


if __name__ == "__main__":
    main()
