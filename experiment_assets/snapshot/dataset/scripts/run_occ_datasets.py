#!/usr/bin/env python3
"""
 R_occ G1G6
 masks  mask  R_occ
  R_occ  mask / s   s^2 s = sqrt(R_occ_target / R_occ_baseline)
 R_occ_baseline  3.35% mask
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

# %->
OCC_GROUPS = {
    3.35: "occ_p3.35",   # G1 Nominal
    10: "occ_p10",       # G2
    20: "occ_p20",       # G3
    30: "occ_p30",       # G4
    40: "occ_p40",       # G5
    50: "occ_p50",       # G6
    60: "occ_p60",
    70: "occ_p70",
    80: "occ_p80",
    90: "occ_p90",
}

R_OCC_BASELINE_PCT = 3.35  #  mask  R_occ (%)


def main():
    parser = argparse.ArgumentParser(
        description=" R_occ mask  RMSE/ Coverage "
    )
    parser.add_argument("--config", type=str, default="video_processing/config/processing_config.yaml")
    parser.add_argument("--occ", type=float, nargs="+", default=None,
                        help=" %%  3.35 10 20 30 40 50 60 70 80 90")
    parser.add_argument("--skip-bag", action="store_true", help=" bag")
    parser.add_argument("--dry-run", action="store_true", help=" scale ")
    args = parser.parse_args()

    occ_targets = args.occ if args.occ is not None else list(OCC_GROUPS.keys())
    occ_targets = sorted(set(occ_targets))

    cfg = load_config(args.config)
    base_dir = project_root
    dataset_cfg = cfg.get("dataset", {}) or {}

    bg_dir = dataset_cfg["input_images"]
    if not Path(bg_dir).is_absolute():
        bg_dir = str(base_dir / bg_dir)
    cam1_dir = dataset_cfg.get("input_images_cam1")
    if not cam1_dir:
        print("  dataset.input_images_cam1  composite")
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
    base_seq_name = (dataset_cfg.get("seq_name") or "seq1").strip()
    if "_occ" in base_seq_name or "_K" in base_seq_name:
        base_seq_name = "seq1"

    print("=" * 70)
    print("R_occ ")
    print("   R_occ = {:.2f}% (mask_scale=1.0)".format(R_OCC_BASELINE_PCT))
    print("  : {}".format(occ_targets))
    print("=" * 70)

    for occ_pct in occ_targets:
        # s^2 = R_occ_target / R_occ_baseline => s = sqrt(occ_pct / R_OCC_BASELINE_PCT)
        r_target = occ_pct / 100.0
        r_baseline = R_OCC_BASELINE_PCT / 100.0
        scale = math.sqrt(r_target / r_baseline) if r_baseline > 0 else 1.0
        seq_suffix = OCC_GROUPS.get(occ_pct) or "occ_p{}".format(occ_pct).replace(".", "_")
        seq_name = "{}_{}".format(base_seq_name, seq_suffix)

        print("\n--- {} ( R_occ = {:.2f}%) ---".format(seq_name, occ_pct))
        print("  mask_scale = {:.4f}".format(scale))

        if args.dry_run:
            continue

        composite_cfg = dict(dataset_cfg.get("composite", {}))
        composite_cfg["mask_scale"] = scale
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
                sys.executable,
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
    print(" R_occ ")
    print("   compute_occlusion_rate  R_occ mask_scale ")
    print("=" * 70)


if __name__ == "__main__":
    main()
