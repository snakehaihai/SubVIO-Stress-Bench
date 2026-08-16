#!/usr/bin/env python3
"""
 occ3030%  seq1_occ30_Kn  8
K = mask_hold_frames =  / KK=0.1  10
 K = 0.05, 0.1, 0.2, 0.5, 2, 5, 10, 20
"""

import argparse
import math
import subprocess
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(Path(__file__).parent / "src"))

from composite_dataset import composite_stereo_seq_from_masks, load_config

#  occ30  K
DEFAULT_K_LIST = [0.05, 0.1, 0.2, 0.5, 2, 5, 10, 20]

R_OCC_BASELINE_PCT = 3.35
OCC30_PCT = 30.0
# occ30  mask_scale
MASK_SCALE_OCC30 = math.sqrt(OCC30_PCT / 100.0 / (R_OCC_BASELINE_PCT / 100.0))


def _k_str(K):
    if K == int(K):
        return str(int(K))
    return f"{K:.4f}".rstrip("0").rstrip(".").rstrip(".")


def main():
    parser = argparse.ArgumentParser(
        description=" occ30  seq1_occ30_KnK=0.05,0.1,0.2,0.5,2,5,10,20"
    )
    parser.add_argument("--config", type=str, default="video_processing/config/processing_config.yaml")
    parser.add_argument("--K", type=float, nargs="+", default=DEFAULT_K_LIST,
                        help="K  0.05 0.1 0.2 0.5 2 5 10 20")
    parser.add_argument("--skip-bag", action="store_true", help=" bag")
    parser.add_argument("--dry-run", action="store_true", help="")
    args = parser.parse_args()

    K_list = sorted(set(args.K))
    K_list = [max(0.05, float(K)) for K in K_list]

    cfg = load_config(args.config)
    base_dir = project_root
    dataset_cfg = cfg.get("dataset", {}) or {}

    bg_dir = dataset_cfg["input_images"]
    if not Path(bg_dir).is_absolute():
        bg_dir = str(base_dir / bg_dir)
    cam1_dir = dataset_cfg.get("input_images_cam1")
    if not cam1_dir:
        print("  dataset.input_images_cam1")
        sys.exit(1)
    if not Path(cam1_dir).is_absolute():
        cam1_dir = str(base_dir / cam1_dir)
    masks_dir = dataset_cfg.get("masks_dir") or "video_processing/data/masks"
    if not Path(masks_dir).is_absolute():
        masks_dir = str(base_dir / masks_dir)
    out_dir = dataset_cfg["output_images"]
    if not Path(out_dir).is_absolute():
        out_dir = str(base_dir / out_dir)

    seq_root = Path(bg_dir).parent.parent
    imu_csv = dataset_cfg.get("imu_csv") or str(seq_root / "imu0" / "data.csv")

    print("=" * 70)
    print("seq1_occ30_Kn =occ30=K=/K")
    print("  mask_scale = {:.4f} ( 30% )".format(MASK_SCALE_OCC30))
    print("  K : {}".format(K_list))
    print("=" * 70)

    for K in K_list:
        seq_name = "seq1_occ30_K{}".format(_k_str(K))
        print("\n--- {} (K={},  = /{}) ---".format(seq_name, K, K))

        if args.dry_run:
            continue

        composite_cfg = dict(dataset_cfg.get("composite", {}))
        composite_cfg["mask_scale"] = MASK_SCALE_OCC30
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
            seq_path = Path(out_dir) / seq_name
            bag_path = Path(out_dir) / "{}.bag".format(seq_name)
            if not seq_path.is_absolute():
                seq_path = base_dir / seq_path
            if not bag_path.is_absolute():
                bag_path = base_dir / bag_path
            cmd = [
                "/usr/bin/python3",
                str(base_dir / "video_processing/tools/folder_to_bag.py"),
                "--seq-dir", str(seq_path),
                "--bag", str(bag_path),
            ]
            try:
                ros_setup = Path("/opt/ros/noetic/setup.bash")
                if ros_setup.exists():
                    run = subprocess.run(
                        ["bash", "-c", "source {} && {}".format(ros_setup, " ".join(cmd))],
                        cwd=str(base_dir),
                    )
                else:
                    run = subprocess.run(cmd, cwd=str(base_dir))
                if run.returncode != 0:
                    print(" bag  {} folder_to_bag".format(run.returncode))
            except Exception as e:
                print("  bag : {}".format(e))

    print("\n" + "=" * 70)
    print(" seq1_occ30_Kn  {} ".format(len(K_list)))
    print("=" * 70)


if __name__ == "__main__":
    main()
