# Experiment asset snapshot

This directory is the portable, data-free snapshot of the local experiment
implementation. It contains code and configuration files only.

The snapshot contains:

- all generated 9 x 11 x 3 sensitivity configurations for AirSLAM,
  ORB-SLAM3, OpenVINS, and SchurVINS;
- the shared random perturbation directions;
- the base CERBERUS calibration/settings files used by the generators;
- the local configuration generators and sensitivity runners;
- the dynamic occlusion/frame-rate dataset scripts and method launch wrappers.

`snapshot/manifest.json` records the local source path, source SHA-256, snapshot
SHA-256, file size, and whether ASCII sanitization changed the file. The
sanitization removes non-ASCII comments and terminal messages so the published
repository contains no Chinese text. Numerical YAML values and executable
control flow are retained. Source and snapshot hashes can differ because of
that text-only sanitization.

Thirty local AirSLAM principal-point configurations contained Python-specific
NumPy scalar YAML tags. The snapshot normalizes those scalars to portable plain
floats, and its copy of the generator explicitly casts new principal-point
values to `float`. The original algorithm checkout is left untouched. OpenCV
matrix tags used by ORB-SLAM3 are retained because they are required by its
settings loader.

Refresh from the workstation only after reviewing local changes:

```bash
python3 tools/snapshot_experiment_assets.py --replace
python3 tools/verify_experiment_assets.py
```

These files are method-specific overrides and must be placed into the matching
algorithm checkout paths documented by the manifest. They do not vendor the
algorithm implementations, ROS, Docker images, model weights, or CERBERUS data.
Upstream method and dataset licenses remain applicable.
See [third-party provenance](THIRD_PARTY.md) before redistribution.
