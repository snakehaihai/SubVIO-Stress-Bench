# Reproducing Results

This document describes how to reproduce the benchmark results reported in the paper.

---

## Overview

The reproduction pipeline consists of four stages:

1. **Data preparation**: Download and organize the CERBERUS dataset.
2. **Perturbation application**: Apply controlled perturbations to sensor data.
3. **Method evaluation**: Run each VIO method on perturbed sequences.
4. **Result aggregation**: Collect metrics, generate tables, and produce figures.

---

## Step 1: Data Preparation

See [Dataset Layout](dataset_layout.md) for the expected directory structure.

```bash
# TODO: add data download / preparation command
```

---

## Step 2: Perturbation Application

<!-- TODO: describe how perturbations are applied to the raw data -->

Perturbation configurations are stored in `configs/`.
Each configuration specifies the perturbation type, magnitude, and affected sequences.

```bash
# TODO: add perturbation application command
```

---

## Step 3: Running Evaluations

```bash
make run-all
```

This will iterate over all method--perturbation combinations defined in the
experiment configuration and write outputs to `results/outputs/`.

<!-- TODO: Describe the structure of individual run commands once scripts are confirmed -->

---

## Step 4: Aggregating Results

```bash
make summarize  # produces results/summaries/
make figures    # produces results/figures/ and results/tables/
```

---

## Expected Outputs

After a full run, you should find:

```
results/
├── logs/         # One log file per experiment run
├── outputs/      # Raw trajectory estimates and per-sequence metrics
├── summaries/    # Aggregated per-perturbation-level summaries
├── figures/      # PNG / PDF plots
└── tables/       # CSV and LaTeX tables
```

<!-- TODO: Add representative output snippets or table previews once confirmed -->

---

## Notes on Reproducibility

- All random seeds used in experiments are fixed in the configuration files.
- Results may vary slightly depending on hardware and software versions.
- See [FAQ](faq.md) for troubleshooting common issues.
