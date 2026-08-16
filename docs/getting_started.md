# Getting Started

This guide walks through installing the repository tools, checking the
published experiment assets, and preparing a workstation for real method runs.

---

## Prerequisites

- Linux (the original method runs used Ubuntu and ROS environments)
- Python 3.8 or later for the repository tools
- Git and Git LFS only if required by an upstream method checkout
- ROS, Docker, CUDA, and compilers as required by each evaluated method

The original experiments did not use a shared Conda environment. AirSLAM,
ORB-SLAM3, OpenVINS, and SchurVINS retain their native ROS, Docker, and build
boundaries.

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

Install each VIO method separately using its upstream instructions. Verify
`experiment_assets/manifest.json`, then copy the matching published
configurations and scripts into the corresponding upstream checkout.

### 3. Verify installation

```bash
make validate-paper
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

# Run enabled method adapters in their already prepared native environments
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
- See [Perturbations](perturbations.md) for the paper-derived parameter grid.
- See [Evaluation](evaluation.md) for metric definitions and output fields.
- See [Method Adapters](method_adapters.md) before enabling a real algorithm.
