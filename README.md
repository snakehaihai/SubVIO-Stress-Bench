# SubVIO-Stress-Bench

[![Paper](https://img.shields.io/badge/paper-IROS%202026%20draft-blue)]()
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue)](pyproject.toml)
[![Platform](https://img.shields.io/badge/platform-Ubuntu20.04%20%7C%20macOS-lightgrey)]()

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

The local implementation contributes 1,782 generated method-configuration files,
the exact configuration generators and runners, shared perturbation directions,
dataset-preparation scripts, a 1,458-row experiment manifest, and checksum-based
asset provenance.

---

## Benchmark Scope

SubVIO-Stress-Bench targets the intersection of two open problems in state estimation:

1. **Subterranean perception**: low-texture walls, poor lighting, confined geometries, and repeated structures.
2. **Sensor robustness**: systematic evaluation under controlled perturbations rather than cherry-picked scenarios.

The benchmark provides a standardized test harness to expose failure modes and quantify
degradation across a representative set of modern VIO algorithms.

The paper protocol uses four methods, nine one-at-a-time sensor dimensions,
11 levels, and three directional seeds. This produces 297 sensor configurations
per method. The dynamic benchmark contains 10 occlusion ratios and nine dynamic
factors for AirSLAM, OpenVINS, and ORB-SLAM3, producing 270 configurations.

---

## Supported Perturbation Types

<details>
<summary>Expand perturbation taxonomy</summary>

| Category | Perturbation | Description |
|---|---|---|
| Sensor Degradation | Accelerometer/gyroscope noise | Multiplicative noise-density scales from 0.01x to 100x |
| Sensor Degradation | Accelerometer/gyroscope bias model | Multiplicative bias random-walk scales from 0.01x to 100x |
| Miscalibration | Extrinsic rotation | Signed camera-IMU rotation offsets from -2 to +2 degrees |
| Miscalibration | Extrinsic translation | Signed camera-IMU translation offsets from -5 to +5 cm |
| Miscalibration | Intrinsic drift | Focal-length scale, principal-point offset, and distortion scale |
| Dynamic Occlusion | Partial occlusion | Centered masks covering 3.35% to 90% of the image |
| Dynamic Occlusion | Moving obstacles | Mask frame-rate factor `d = F_mask / F_dataset`, from 0.05 to 20 |

The exact numerical levels, units, seeds, and expected counts are defined in
[`configs/paper_protocol.yaml`](configs/paper_protocol.yaml). The local scripts
modify IMU bias random-walk parameters; the repository uses that precise term
instead of silently claiming deterministic bias injection.

</details>

---

## Evaluated Method Categories

| Category | Representative Methods |
|---|---|
| Filter-based | OpenVINS |
| Optimization-based (sliding window) | SchurVINS |
| Learning-based / Neural | AirSLAM learned feature front end |
| Hybrid | ORB-SLAM3 factor-graph pipeline; AirSLAM learned front end with geometric back end |

The categories describe the components emphasized in this study and are not
mutually exclusive. Reference revisions are listed in
[`configs/method_versions.yaml`](configs/method_versions.yaml).

---

## Repository Structure

```text
SubVIO-Stress-Bench/
├── README.md                  # This file
├── LICENSE                    # GNU GPL v3
├── CONTRIBUTING.md            # Contribution guidelines
├── CODE_OF_CONDUCT.md         # Community standards
├── CHANGELOG.md               # Version history
├── RELEASE_CHECKLIST.md       # Pre-release checklist
├── Makefile                   # Convenience commands
├── requirements.txt           # Python dependencies
├── pyproject.toml             # Installable Python package metadata
├── .gitignore                 # Ignored files
├── .gitattributes             # Git attributes
│
├── assets/                    # Static assets for documentation
│   └── benchmark_overview.svg # Benchmark overview figure
│
├── configs/                   # Protocol, adapters, paths, and self-test configs
├── experiment_assets/         # Local method configs/scripts and checksum manifest
├── subvio_bench/              # Runner, trajectory evaluation, and protocol library
├── scripts/                   # Benchmark entry points
├── tests/                     # Deterministic unit tests
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
└── tools/                     # Evaluation, plotting, and snapshot tools
    ├── README.md
    ├── plot_noise_trajectories.py
    ├── verify_experiment_assets.py
    └── experiment_metadata_template.json
```

---

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/snakehaihai/SubVIO-Stress-Bench.git
cd SubVIO-Stress-Bench

# 2. Set up the lightweight benchmark tools (no shared Conda environment)
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .

# 3. Verify the protocol and published local experiment assets
make validate-paper
make verify-assets
make check-language
make test
make self-test

# 4. Download the processed CERBERUS release (approximately 93.2 GB)
python -m pip install --upgrade huggingface_hub
hf download zhuyyyy/CERBERUS \
  --repo-type dataset \
  --revision d2a9b316f9f9dbf68a236eac8229a6acdef19ea5 \
  --local-dir data/cerberus

# 5. Configure workstation-specific paths
cp configs/local_paths.example.yaml configs/local_paths.yaml
# Edit configs/local_paths.yaml; this file is ignored by Git.
```

`make self-test` does not require ROS, Docker, a GPU, or the dataset. Real
method execution uses the native environment of each upstream algorithm.

---

## Environment Setup

<details>
<summary>Benchmark tools (recommended)</summary>

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

</details>

<details>
<summary>Evaluated methods</summary>

The original experiments did not use one shared Conda environment. Install the
published files from `experiment_assets/snapshot/` into matching algorithm
checkouts, then use each method's native ROS/Docker environment:

| Method | Runtime boundary |
|---|---|
| AirSLAM | ROS catkin workspace and the AirSLAM GPU container |
| ORB-SLAM3 | Native/CMake or the local ORB-SLAM3 container |
| OpenVINS | ROS and the OpenVINS container/workspace |
| SchurVINS | ROS and the SchurVINS container/workspace |

Run `make verify-assets` before installing the snapshot. Its manifest records
the source path and SHA-256 of every local configuration and script.

</details>

Requirements: Python 3.8 or later for repository tools; method-specific ROS,
compiler, CUDA, and Docker requirements follow their upstream projects.
See [docs/getting_started.md](docs/getting_started.md) for full environment notes.

---

## Data Preparation

SubVIO-Stress-Bench is built on the **CERBERUS DARPA Subterranean Challenge
Final Event dataset**.

1. **Original source.** Team CERBERUS publishes the original multi-robot Final
   Event recordings through the
   [official dataset repository](https://github.com/leggedrobotics/cerberus_darpa_subt_datasets)
   and the
   [ETH Research Collection archive](https://www.research-collection.ethz.ch/handle/20.500.11850/552248).
   The original release contains full ANYmal mission recordings, Alphasense
   stereo/IMU data, VLP16 LiDAR, calibration, and several trajectory products.
2. **Processed release used here.** The public
   [zhuyyyy/CERBERUS dataset](https://huggingface.co/datasets/zhuyyyy/CERBERUS)
   is a VIO-oriented derivative of the official release. It selects ANYmal 3,
   curates eight active-motion intervals (`seq0`-`seq7`, about 22
   minutes total), retains synchronized `cam0`/`cam1` monochrome images at 20
   Hz and IMU samples at 200 Hz, and supplies both folder and ROS1 bag forms.
3. **Ground truth and calibration.** The corresponding CompSLAM post-processed
   trajectory intervals are exported in TUM order under `groundtruth/`, and the
   camera intrinsics plus sensor extrinsics are retained under `calibration/`.
4. **Stress data.** Dynamic masks and frame-rate variants are generated locally
   by the scripts under `experiment_assets/snapshot/dataset/scripts/`; these
   derived stress variants are not silently treated as original CERBERUS data.

The processed release is approximately 93.2 GB and currently contains
`bag/seq0.bag`-`seq7.bag`, `folder/seq0`-`seq7` plus ZIP archives,
`groundtruth/seq0.txt`-`seq7.txt`, and calibration YAML files. Cite and respect
the terms of the original Team CERBERUS release when using the derivative.

See [docs/dataset_layout.md](docs/dataset_layout.md) for selective download
commands and the exact directory layout.

---

## Reproducing Results

```bash
# Inspect configured commands without starting ROS/Docker jobs
make dry-run CONFIG=configs/default.yaml

# Run enabled adapters after configuring each native method environment
make run-all CONFIG=configs/local.yaml

# Summarize newly generated benchmark runs
make summarize

# Generate generic benchmark figures
make figures

```

The qualitative trajectory-deformation figure is generated directly from TUM
ground truth and locally produced perturbed trajectories:

```bash
python tools/plot_noise_trajectories.py \
  --ground-truth /path/to/seq1.txt \
  --estimate "acc_noise_100x=/path/to/trajectory.txt" \
  --estimate "gyro_noise_39.81x=/path/to/trajectory.txt" \
  --output results/figures/noise_trajectories.png
```

The script associates timestamps, applies rigid SE(3) alignment, reports the
aligned RMSE in the legend, and plots the XY trajectory and height profile.

Full step-by-step instructions are in [docs/reproducing_results.md](docs/reproducing_results.md).

---

## Logging and Output Structure

All outputs follow the convention below:

```text
results/
├── logs/          # Per-run execution logs (one file per experiment)
├── outputs/       # Raw trajectory outputs and metric files
├── figures/       # Generated plots and visualization
├── summaries/     # Aggregated per-perturbation summaries
└── tables/        # Final evaluation tables in CSV / LaTeX
```

Every benchmark run additionally stores its resolved command, method,
sequence, perturbation, timestamps, return status, copied trajectory, and
evaluation metadata under `results/runs/<experiment-id>/`.

See [docs/evaluation.md](docs/evaluation.md) for metric definitions and
result file schemas.

---

## Citation

The VIO robustness manuscript is currently an anonymous IROS 2026 draft. Its
final authors, title metadata, and DOI must be inserted after acceptance; the
repository does not publish an invented citation.

For the original dataset, cite the Team CERBERUS dataset and associated work:

```bibtex
@article{tranzatto2024teamcerberus,
  title   = {Team CERBERUS Wins the DARPA Subterranean Challenge:
             Technical Overview and Lessons Learned},
  author  = {Tranzatto, Marco and others},
  journal = {Field Robotics},
  volume  = {4},
  pages   = {249--312},
  year    = {2024},
  doi     = {10.55417/fr.2024009}
}
```

---

## Acknowledgments

This work builds on the official Team CERBERUS Final Event data and the
open-source contributions of AirSLAM, OpenVINS, ORB-SLAM3, SchurVINS, evo,
ROS, and their dependencies. We thank the dataset providers and all evaluated
method authors. The processed Hugging Face release is a derived convenience
copy and does not replace acknowledgment of the original data creators.

---

## License

This project is licensed under the GNU General Public License v3.0.
See [LICENSE](LICENSE) for details. Evaluated methods and datasets retain their
independent upstream licenses and terms.
