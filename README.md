# SubVIO-Stress-Bench

[![Paper](https://img.shields.io/badge/paper-TODO-blue)]()
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue)]()
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS-lightgrey)]()

**SubVIO-Stress-Bench** is a failure-centric stress-test benchmark for visual-inertial odometry (VIO)
in subterranean environments.
It evaluates robustness under sensor degradation, miscalibration, and dynamic occlusion
across representative VIO paradigms on the CERBERUS dataset.

---

## Highlights

- Systematic evaluation of VIO methods under realistic failure modes encountered in subterranean environments.
- Controlled perturbation framework covering three orthogonal degradation axes: sensor degradation, miscalibration, and dynamic occlusion.
- Evaluation across diverse VIO paradigms including filter-based, optimization-based, and learning-based approaches.
- Built on the CERBERUS dataset, providing challenging real-world underground sequences.
- Reproducible experimental pipeline with structured logging and result aggregation.

---

## Benchmark Scope

SubVIO-Stress-Bench targets the intersection of two open problems in state estimation:

1. **Subterranean perception**: low-texture walls, poor lighting, confined geometries, and repeated structures.
2. **Sensor robustness**: systematic evaluation under controlled perturbations rather than cherry-picked scenarios.

The benchmark provides a standardized test harness to expose failure modes and quantify
degradation across a representative set of modern VIO algorithms.

---

## Supported Perturbation Types

<details>
<summary>Expand perturbation taxonomy</summary>

| Category | Perturbation | Description |
|---|---|---|
| Sensor Degradation | Noise injection | Additive Gaussian noise on IMU measurements |
| Sensor Degradation | Image degradation | Blur, reduced exposure, sensor saturation |
| Miscalibration | Extrinsic offset | Translational and rotational bias in camera-IMU extrinsics |
| Miscalibration | Temporal offset | Time-stamp desynchronization between camera and IMU |
| Miscalibration | Intrinsic drift | Focal length and distortion coefficient perturbation |
| Dynamic Occlusion | Moving obstacles | Dynamic foreground agents blocking visual features |
| Dynamic Occlusion | Partial occlusion | Region-of-interest masking simulating partial blockage |

<!-- TODO: Verify and expand this table against actual perturbation implementations in the codebase -->

</details>

---

## Evaluated Method Categories

<!-- TODO: List the specific VIO methods evaluated once confirmed from paper -->

| Category | Representative Methods |
|---|---|
| Filter-based | TODO |
| Optimization-based (sliding window) | TODO |
| Learning-based / Neural | TODO |
| Hybrid | TODO |

---

## Repository Structure

```
SubVIO-Stress-Bench/
├── README.md                  # This file
├── LICENSE                    # GNU GPL v3
├── CONTRIBUTING.md            # Contribution guidelines
├── CODE_OF_CONDUCT.md         # Community standards
├── CHANGELOG.md               # Version history
├── RELEASE_CHECKLIST.md       # Pre-release checklist
├── Makefile                   # Convenience commands
├── requirements.txt           # Python dependencies
├── environment.yml            # Conda environment specification
├── .gitignore                 # Ignored files
├── .gitattributes             # Git attributes
│
├── assets/                    # Static assets for documentation
│   ├── banner.png             # [placeholder] Repository banner
│   └── benchmark_overview.png # [placeholder] Benchmark overview figure
│
├── configs/                   # Experiment configuration files
│   └── README.md
│
├── docs/                      # Extended documentation
│   ├── index.md
│   ├── getting_started.md
│   ├── reproducing_results.md
│   ├── dataset_layout.md
│   ├── perturbations.md
│   ├── evaluation.md
│   └── faq.md
│
├── examples/                  # Minimal runnable examples
│   └── README.md
│
├── results/                   # Structured result storage
│   ├── logs/                  # Raw execution logs
│   ├── outputs/               # Processed outputs
│   ├── figures/               # Generated figures
│   ├── summaries/             # Human-readable summaries
│   └── tables/                # Evaluation tables (CSV / LaTeX)
│
└── tools/                     # Utility and helper scripts
    ├── README.md
    ├── tree_summary.py        # Auto-generate repository tree
    └── experiment_metadata_template.json
```

---

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/snakehaihai/SubVIO-Stress-Bench.git
cd SubVIO-Stress-Bench

# 2. Set up the environment
conda env create -f environment.yml
conda activate subvio-bench
# or: pip install -r requirements.txt

# 3. Prepare data (see docs/dataset_layout.md)
# TODO: add data preparation command

# 4. Run a benchmark evaluation
# TODO: add run command
make run   # see Makefile for available targets
```

---

## Environment Setup

<details>
<summary>Conda (recommended)</summary>

```bash
conda env create -f environment.yml
conda activate subvio-bench
```

</details>

<details>
<summary>pip</summary>

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

</details>

Requirements: Python 3.8 or later, Linux or macOS.
See [docs/getting_started.md](docs/getting_started.md) for full environment notes.

---

## Data Preparation

SubVIO-Stress-Bench is built on the **CERBERUS** dataset.

1. Download the CERBERUS sequences from the official source (TODO: add link).
2. Place data under a directory of your choice, e.g. `data/cerberus/`.
3. Update the dataset path in your config file (see `configs/`).

See [docs/dataset_layout.md](docs/dataset_layout.md) for the expected directory layout.

---

## Reproducing Results

```bash
# Run all perturbation experiments
make run-all

# Summarize results
make summarize

# Generate tables and figures
make figures
```

Full step-by-step instructions are in [docs/reproducing_results.md](docs/reproducing_results.md).

---

## Logging and Output Structure

All outputs follow the convention below:

```
results/
├── logs/        # Per-run execution logs (one file per experiment)
├── outputs/     # Raw trajectory outputs and metric files
├── figures/     # Generated plots and visualization
├── summaries/   # Aggregated per-perturbation summaries
└── tables/      # Final evaluation tables in CSV and LaTeX
```

See [docs/evaluation.md](docs/evaluation.md) for metric definitions and
result file schemas.

---

## Citation

If you use SubVIO-Stress-Bench in your research, please cite:

```bibtex
@article{TODO2025subviobench,
  title   = {SubVIO-Stress-Bench: A Failure-Centric Stress-Test Benchmark
             for Visual-Inertial Odometry in Subterranean Environments},
  author  = {TODO},
  journal = {TODO},
  year    = {2025},
  note    = {TODO: update when published}
}
```

---

## Acknowledgments

<!-- TODO: Add funding acknowledgments, dataset providers, and any third-party method authors -->

This work builds on the CERBERUS dataset and the broader VIO community's
open-source contributions. We thank the authors of all evaluated methods.

---

## License

This project is licensed under the GNU General Public License v3.0.
See [LICENSE](LICENSE) for details.
