# Getting Started

This guide walks through setting up the environment and running the benchmark
for the first time.

---

## Prerequisites

- Linux or macOS (tested on Ubuntu 20.04+)
- Python 3.8 or later
- Conda (recommended) or pip

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/snakehaihai/SubVIO-Stress-Bench.git
cd SubVIO-Stress-Bench
```

### 2. Create the environment

**With Conda (recommended):**

```bash
conda env create -f environment.yml
conda activate subvio-bench
```

**With pip:**

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Verify installation

```bash
python --version
# TODO: add a lightweight self-test command, e.g.:
# python -c "import numpy, pandas, matplotlib; print('OK')"
```

---

## Data Preparation

See [Dataset Layout](dataset_layout.md) for the full data directory structure.

1. Download the CERBERUS dataset sequences.
   <!-- TODO: add official download link -->
2. Place the sequences under `data/cerberus/` (or update the path in `configs/`).

---

## Running the Benchmark

```bash
# Run with default settings
make run

# Run all perturbation experiments
make run-all

# See all available commands
make help
```

<!-- TODO: Add more detail once the run scripts and configs are confirmed -->

---

## Next Steps

- See [Reproducing Results](reproducing_results.md) to replicate paper experiments.
- See [Perturbations](perturbations.md) for details on the perturbation framework.
- See [Evaluation](evaluation.md) for metric definitions.
