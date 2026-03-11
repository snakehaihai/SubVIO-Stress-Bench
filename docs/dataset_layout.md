# Dataset Layout

SubVIO-Stress-Bench uses the **CERBERUS** dataset.
This document describes the expected directory structure for the dataset.

---

## Obtaining the Dataset

<!-- TODO: add official CERBERUS download link and any access instructions -->

Download the CERBERUS sequences from the official source and place them under
a local `data/` directory (or configure a custom path in `configs/`).

---

## Expected Directory Structure

```
data/
└── cerberus/
    ├── sequence_01/
    │   ├── cam0/
    │   │   └── data/           # Image frames
    │   ├── imu0/
    │   │   └── data.csv        # IMU measurements
    │   └── ground_truth/
    │       └── data.csv        # Reference trajectory
    ├── sequence_02/
    │   └── ...
    └── ...
```

<!-- TODO: Verify exact directory and file names against the actual CERBERUS
     dataset format once confirmed -->

---

## Configuration

Update the dataset root path in the relevant configuration file:

```yaml
# configs/default.yaml  (example)
dataset:
  root: /path/to/data/cerberus
  sequences:
    - sequence_01
    - sequence_02
```

---

## Notes

- Ground-truth trajectories are used only for evaluation; they are not fed
  to the VIO methods.
- Perturbed versions of the data are generated on-the-fly or cached in a
  separate directory (see [Reproducing Results](reproducing_results.md)).
