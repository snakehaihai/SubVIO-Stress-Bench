# configs/

This directory stores experiment configuration files in YAML format.

## Structure

```
configs/
├── README.md              # This file
├── default.yaml           # Default benchmark configuration (TODO)
└── perturbations/         # Per-perturbation configuration files (TODO)
    ├── imu_noise.yaml
    ├── image_blur.yaml
    ├── extrinsic_offset.yaml
    ├── temporal_offset.yaml
    └── ...
```

## Usage

Specify a configuration file when running the benchmark:

```bash
# TODO: update with actual run command
python scripts/run_benchmark.py --config configs/default.yaml
```

## Format

Each configuration file follows this general structure:

```yaml
dataset:
  root: /path/to/data/cerberus
  sequences:
    - sequence_01

perturbation:
  type: none  # or: imu_noise, image_blur, extrinsic_offset, temporal_offset, ...
  # perturbation-specific parameters follow

methods:
  - name: TODO
    # method-specific parameters

evaluation:
  metrics:
    - ATE
    - RPE_t
    - RPE_r
```

<!-- TODO: Add actual configuration files once benchmark scripts are finalized -->
