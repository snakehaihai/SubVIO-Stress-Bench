# Perturbations

The unified taxonomy reflects the published method configurations. It does not
imply that every method implements every dimension.

| Canonical type | Configuration examples | Interpretation |
|---|---|---|
| `image_degradation` | `K0.05` ... `K20` | prepared visual degradation level |
| `occlusion` | `occ_p30`, `occ30` | prepared partial image occlusion percentage |
| `composite` | `occ50_K0.1` | two or more simultaneous perturbations |
| `focal` | `intrinsic_focal`, `focal_*x` | focal-length scale/error |
| `principal` | `intrinsic_principal`, pixel offsets | principal-point error |
| `distortion` | `distort_all`, `distortion_*x` | distortion-model error |
| `translation` | `T`, `tbc_tx/ty/tz` | camera–IMU translation error |
| `rotation` | `R`, `tbc_roll/pitch/yaw` | camera–IMU rotation error |
| `acc_noise`, `gyro_noise` | `imu_acc`, `imu_gyro` | IMU measurement noise |
| `acc_bias`, `gyro_bias` | sensitivity config names | IMU bias-model error |

The numeric `severity` is meaningful only within its perturbation type. Do not
compare `K`, degrees, pixels, percentages, and noise multipliers as if they
shared a scale. Composite runs should preserve their component list.

Perturbations are prepared by the published method and dataset scripts. The
benchmark records their configuration identity with each run.
