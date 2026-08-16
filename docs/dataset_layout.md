# Dataset Layout

SubVIO-Stress-Bench uses a VIO-oriented derivative of the Team CERBERUS DARPA
Subterranean Challenge Final Event dataset. Dataset files remain external to
this Git repository.

---

## Obtaining the Dataset

The original multi-robot mission data is published by Team CERBERUS through
the [official dataset repository](https://github.com/leggedrobotics/cerberus_darpa_subt_datasets)
and the [ETH Research Collection](https://www.research-collection.ethz.ch/handle/20.500.11850/552248).
It is the authoritative source for the full mission recordings, calibration,
LiDAR data, and original trajectory products.

The experiments in this repository use the processed public release at
[zhuyyyy/CERBERUS](https://huggingface.co/datasets/zhuyyyy/CERBERUS). It selects
ANYmal 3 and curates eight active-motion intervals (`seq0`-`seq7`,
about 22 minutes in total). It retains synchronized monochrome stereo frames
at 20 Hz, IMU samples at 200 Hz, the corresponding CompSLAM post-processed
ground-truth slices in TUM format, and camera/sensor calibration. Both folder
and ROS1 bag representations are provided.

Download the pinned dataset revision with the official Hugging Face CLI:

```bash
python -m pip install --upgrade huggingface_hub
hf download zhuyyyy/CERBERUS \
  --repo-type dataset \
  --revision d2a9b316f9f9dbf68a236eac8229a6acdef19ea5 \
  --local-dir data/cerberus
```

The complete processed release is approximately 93.2 GB. Use `--include` with
the CLI when only bags, folders, ground truth, or calibration are needed.

---

## Expected Directory Structure

```text
data/
└── cerberus/
    ├── bag/
    │   ├── seq0.bag
    │   └── ... seq7.bag
    ├── folder/
    │   ├── seq0/
    │   │   ├── cam0/data/
    │   │   ├── cam1/data/
    │   │   └── imu0/data.csv
    │   ├── ... seq7/
    │   └── seq0.zip ... seq7.zip
    ├── groundtruth/
    │   ├── seq0.txt
    │   └── ... seq7.txt
    └── calibration/
        ├── intrinsics/
        └── extrinsics/
```

AirSLAM and ORB-SLAM3 scripts generally consume the folder representation.
OpenVINS and SchurVINS generally consume ROS bags. These are two encodings of
the same selected intervals, not two independent datasets.

---

## Configuration

Copy the portable template and edit local paths:

```bash
cp configs/local_paths.example.yaml configs/local_paths.yaml
```

```yaml
# configs/local_paths.yaml (example; ignored by Git)
dataset_root: ${HOME}/Datasets/DARPA-CERBERUS
ground_truth: ${HOME}/Datasets/DARPA-CERBERUS/anymal_3/gt_tum/seq1.txt
```

Method adapters may point to different folder/bag roots while sharing the same
logical sequence identifier. Do not commit absolute paths.

---

## Notes

- Ground truth is evaluation-only and is never supplied to a VIO estimator.
- Ground-truth rows use `timestamp tx ty tz qx qy qz qw`.
- The processed Hugging Face release is a derivative convenience copy; cite
  the original Team CERBERUS work as well as the processed release.
- Dynamic masks, occlusion ratios, frame-rate variants, and other stress data
  are generated locally by `experiment_assets/snapshot/dataset/scripts/` and
  are not represented as unmodified CERBERUS recordings.
- Keep generated stress variants outside the base dataset directory.
