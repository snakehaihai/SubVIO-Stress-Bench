# Perturbations

This document describes the perturbation framework used in SubVIO-Stress-Bench.

---

## Overview

The benchmark applies structured perturbations along three orthogonal axes
to stress-test VIO methods under conditions representative of real subterranean
deployments.

---

## Perturbation Categories

### 1. Sensor Degradation

Perturbations that reduce the quality or availability of raw sensor data.

| Perturbation | Description | Parameters |
|---|---|---|
| IMU noise injection | Additive Gaussian noise on accelerometer and gyroscope readings | sigma_acc, sigma_gyro |
| Image blur | Gaussian blur applied to camera frames | kernel_size |
| Reduced exposure | Brightness reduction simulating low-light conditions | scale_factor |

<!-- TODO: Verify exact parameter names and ranges against scripts -->

---

### 2. Miscalibration

Perturbations that introduce errors in the assumed sensor calibration.

| Perturbation | Description | Parameters |
|---|---|---|
| Extrinsic translation offset | Bias in the camera-IMU translation estimate | delta_t (m) |
| Extrinsic rotation offset | Bias in the camera-IMU rotation estimate | delta_R (deg) |
| Temporal offset | Desynchronization between camera and IMU timestamps | delta_tau (ms) |
| Intrinsic perturbation | Perturbation of focal length and distortion coefficients | TODO |

<!-- TODO: Verify exact parameter names and ranges against scripts -->

---

### 3. Dynamic Occlusion

Perturbations that introduce moving or static foreground interference.

| Perturbation | Description | Parameters |
|---|---|---|
| Moving obstacle | Dynamic foreground agent occluding features | size, velocity |
| Region masking | Fixed rectangular mask blocking image regions | mask_fraction |

<!-- TODO: Verify exact parameter names and ranges against scripts -->

---

## Perturbation Configurations

Perturbation settings are specified in YAML configuration files under `configs/`.
Each file defines the perturbation type, severity levels, and the sequences
to which the perturbation is applied.

Example structure:

```yaml
perturbation:
  type: imu_noise
  levels:
    - sigma_acc: 0.01
      sigma_gyro: 0.001
    - sigma_acc: 0.05
      sigma_gyro: 0.005
sequences:
  - sequence_01
  - sequence_02
```

<!-- TODO: Replace with actual config examples once finalized -->
