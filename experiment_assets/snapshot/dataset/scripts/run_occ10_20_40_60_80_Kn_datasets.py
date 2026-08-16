#!/usr/bin/env python3
"""
 occ10 / occ20 / occ40 / occ60 / occ80  seq1_occn_Kn
 8  K0.05, 0.1, 0.2, 0.5, 2, 5, 10, 20 5*8=40
K = mask_hold_frames =  / K
 /media/zyy/Doremi/Datasets_minetunnel/CERBERUS_composite
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

DEFAULT_OCC_PCT = [10, 20, 40, 60, 80]
DEFAULT_K_LIST = [0.05, 0.1, 0.2, 0.5, 2, 5, 10, 20]
DEFAULT_OUTPUT_DIR = "/media/zyy/Doremi/Datasets_minetunnel/CERBERUS_composite"

R_OCC_BASELINE_PCT = 3.35


def _k_str(K):
    if K == int(K):
        return str(int(K))
    return f"{K:.4f}".rstrip("0").rstrip(".").rstrip(".")


def mask_scale_for_occ_pct(occ_pct):
    r_target = occ_pct / 100.0
    r_baseline = R_OCC_BASELINE_PCT / 100.0
    return math.sqrt(r_target / r_baseline) if r_baseline > 0 else 1.0


def main():
    parser = argparse.ArgumentParser(
        description="occ10/20/40/60/80  8  K 40 "
    )
    parser.add_argument("--config", type=str, default="video_processing/config/processing_config.yaml")
    parser.add_argument("--occ", type=float, nargs="+", default=DEFAULT_OCC_PCT,
                        help=" %%  10 20 40 60 80")
    parser.add_argument("--K", type=float, nargs="+", default=DEFAULT_K_LIST,
                        help="K  0.05 0.1 0.2 0.5 2 5 10 20")
    parser.add_argument("--output-dir", type=str, default=DEFAULT_OUTPUT_DIR,
                        help="")
    parser.add_argument("--skip-bag", action="store_true", help=" bag")
    parser.add_argument("--dry-run", action="store_true", help="")
    args = parser.parse_args()

    occ_list = sorted(set(args.occ))
    K_list = sorted(set(args.K))
    K_list = [max(0.05, float(K)) for K in K_list]
    out_dir = args.output_dir.rstrip("/")
    if not Path(out_dir).is_absolute():
        out_dir = str(project_root / out_dir)

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

    seq_root = Path(bg_dir).parent.parent
    imu_csv = dataset_cfg.get("imu_csv") or str(seq_root / "imu0" / "data.csv")

    Path(out_dir).mkdir(parents=True, exist_ok=True)

    total = len(occ_list) * len(K_list)
    print("=" * 70)
    print("seq1_occ10/20/40/60/80_Kn 5   8 K = {} ".format(total))
    print("  : {}".format(out_dir))
    print("  : {}%".format(occ_list))
    print("  K : {}".format(K_list))
    print("=" * 70)

    count = 0
    for occ_pct in occ_list:
        scale = mask_scale_for_occ_pct(occ_pct)
        base_name = "seq1_occ{}".format(int(occ_pct) if occ_pct == int(occ_pct) else occ_pct)
        for K in K_list:
            seq_name = "{}_K{}".format(base_name, _k_str(K))
            count += 1
            print("\n--- [{}/{}] {} (occ={}%, mask_scale={:.4f}, K={}) ---".format(
                count, total, seq_name, occ_pct, scale, K))

            if args.dry_run:
                continue

            composite_cfg = dict(dataset_cfg.get("composite", {}))
            composite_cfg["mask_scale"] = scale
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
    print("  {}  -> {}".format(total, out_dir))
    print("=" * 70)


if __name__ == "__main__":
    main()
