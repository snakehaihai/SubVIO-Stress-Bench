# Getting Started

This guide walks through installing the repository tools, checking the
published experiment assets, and preparing a workstation for real method runs.

---

## Prerequisites

- Ubuntu Linux
- Python 3.8 or later for the repository tools
- Git and Git LFS only if required by an upstream method checkout
- Docker Engine
- NVIDIA driver and NVIDIA Container Toolkit for AirSLAM GPU execution

The experiments did not use a shared Conda environment. AirSLAM, ORB-SLAM3,
OpenVINS, and SchurVINS were isolated in separate Docker environments so that
their ROS and system-library requirements do not conflict.

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/snakehaihai/SubVIO-Stress-Bench.git
cd SubVIO-Stress-Bench
```

### 2. Create the environment

Create a lightweight virtual environment for the benchmark utilities:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

Install each VIO method separately using the container guidance below. Verify
`experiment_assets/snapshot/manifest.json`, then copy the matching published
configurations and scripts into the corresponding upstream checkout.

### 3. Prepare algorithm containers

The benchmark does not distribute Docker images and does not depend on the
original workstation's image IDs, container names, or absolute paths. Use one
image per algorithm and reproduce the dependency boundary described by its
upstream project.

| Method | Recommended container configuration | Upstream instructions |
|---|---|---|
| AirSLAM | Use the official `xukuanhit/air_slam:v4` image or build an equivalent Ubuntu 20.04/ROS Noetic image with CUDA 12.1 and TensorRT 8.6.1.6. Start it with the NVIDIA runtime and mount the AirSLAM checkout and dataset. | [AirSLAM](https://github.com/sair-lab/AirSLAM#-test-environment) |
| OpenVINS | Build the upstream `Dockerfile_ros1_20_04`, mount a catkin workspace at `/catkin_ws`, mount the dataset separately, then build OpenVINS inside the container. | [OpenVINS Docker guide](https://docs.openvins.com/dev-docker.html) |
| ORB-SLAM3 | Build a dedicated Ubuntu 18.04 image with C++11, Pangolin, OpenCV >= 3.0, Eigen >= 3.1, and ROS Melodic when using the included ROS wrappers. Run upstream `build.sh` inside the image. | [ORB-SLAM3](https://github.com/UZ-SLAMLab/ORB_SLAM3#2-prerequisites) |
| SchurVINS | Build an Ubuntu 18.04/ROS Melodic catkin image with `python-catkin-tools`, `python-vcstool`, OpenCV, yaml-cpp, BLAS, LAPACK, SuiteSparse, and the dependencies imported from `dependencies.yaml`. | [SchurVINS](https://github.com/bytedance/SchurVINS#2-prerequisites) |

Install [Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/).
For AirSLAM, also install the
[NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
and verify GPU access with `docker run --gpus all`.

A typical container must expose three host resources:

```text
algorithm checkout  -> method workspace inside the container
CERBERUS dataset    -> read-only dataset path inside the container
results directory   -> writable trajectory/log output path
```

Container names and internal mount points are implementation choices. Adjust
`cwd`, `command`, `trajectory`, and `ground_truth` in the benchmark adapter to
match your layout. The published files under `experiment_assets/snapshot/`
contain the method-specific configurations and launch wrappers used by the
benchmark; they do not contain machine-specific Docker images.

### 4. Verify installation

```bash
make validate-protocol
make verify-assets
make check-language
make test
make self-test
```

`make self-test` runs deterministic mock trajectories and does not require the
CERBERUS data, ROS, Docker, CUDA, or an evaluated method.

---

## Data Preparation

See [Dataset Layout](dataset_layout.md) for provenance and the exact layout.

1. Download the processed VIO-oriented release from
   [zhuyyyy/CERBERUS](https://huggingface.co/datasets/zhuyyyy/CERBERUS).
2. Copy `configs/local_paths.example.yaml` to `configs/local_paths.yaml` and
   edit only workstation-specific paths. The copied file is ignored by Git.
3. Keep the base release separate from locally generated masks, perturbed
   folders, and perturbed bags.

---

## Running the Benchmark

```bash
# Inspect every resolved command before execution
make dry-run CONFIG=configs/local.yaml

# Run enabled method adapters in their prepared containers
make run-all CONFIG=configs/local.yaml

# Aggregate newly evaluated trajectories
make summarize
make figures

# See all available commands
make help
```

`run-all` is an orchestrator, not a universal environment installer. A method
crash is retained as a failed run with its log and metadata; it is never
converted into an artificial RMSE value.

---

## Next Steps

- See [Reproducing Results](reproducing_results.md) for the full workflow and
  crash-aware aggregation policy.
- See [Perturbations](perturbations.md) for the benchmark parameter grid.
- See [Evaluation](evaluation.md) for metric definitions and output fields.
- See [Method Adapters](method_adapters.md) before enabling a real algorithm.
