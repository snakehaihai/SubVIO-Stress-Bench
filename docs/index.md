# SubVIO-Stress-Bench Documentation

Welcome to the documentation for **SubVIO-Stress-Bench**, a failure-centric
stress-test benchmark for visual-inertial odometry (VIO) in subterranean environments.

---

## Contents

| Document | Description |
|---|---|
| [Getting Started](getting_started.md) | Environment setup and first run |
| [Reproducing Results](reproducing_results.md) | Step-by-step reproduction guide |
| [Dataset Layout](dataset_layout.md) | Expected data directory structure |
| [Perturbations](perturbations.md) | Description of all perturbation types |
| [Evaluation](evaluation.md) | Metrics, output formats, and result schemas |
| [FAQ](faq.md) | Frequently asked questions |
| [Method adapters](method_adapters.md) | Integrating external VIO runtimes |

---

## Overview

SubVIO-Stress-Bench provides a controlled experimental framework for studying
how VIO methods respond to degraded sensing conditions in subterranean environments.
The benchmark is grounded in the CERBERUS dataset and applies structured
perturbations to expose and characterize algorithmic failure modes.

For a quick introduction, see [Getting Started](getting_started.md).
For full reproduction instructions, see [Reproducing Results](reproducing_results.md).
