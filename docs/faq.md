# FAQ

Frequently asked questions about SubVIO-Stress-Bench.

---

## General

**What is SubVIO-Stress-Bench?**

SubVIO-Stress-Bench is a benchmark for evaluating the robustness of
visual-inertial odometry (VIO) methods in subterranean environments under
controlled sensor perturbations. See the [README](../README.md) for an overview.

---

**Which VIO methods are evaluated?**

<!-- TODO: List specific evaluated methods once confirmed from paper -->

The benchmark evaluates a representative selection of VIO paradigms including
filter-based, optimization-based, and learning-based approaches.
Refer to the paper for the complete list.

---

**Which dataset is used?**

The benchmark is built on the **CERBERUS** dataset, which provides challenging
sequences from underground environments.
See [Dataset Layout](dataset_layout.md) for setup instructions.

---

## Installation

**The Conda environment creation fails. What should I do?**

Try creating the environment step by step:

```bash
conda create -n subvio-bench python=3.9
conda activate subvio-bench
pip install -r requirements.txt
```

If specific packages fail, check the error message and install them individually.

---

**Can I use pip instead of Conda?**

Yes. See [Getting Started](getting_started.md) for pip-based setup instructions.

---

## Running the Benchmark

**Where do I configure the dataset path?**

Update the `dataset.root` entry in the relevant YAML file under `configs/`.
See [Dataset Layout](dataset_layout.md) for details.

---

**A method crashes or diverges on a sequence. Is this expected?**

Yes. Divergence and failure under perturbations is a primary quantity being
measured by this benchmark. Failures are recorded in the output metrics and
contribute to the failure rate statistic.

---

**How long does a full benchmark run take?**

<!-- TODO: Add expected runtime once confirmed -->

Runtime depends on the number of methods, sequences, and perturbation levels.
Refer to the paper or contact the maintainers for indicative figures.

---

## Results

**The numbers I obtain differ slightly from the paper. Why?**

Minor numerical differences can arise from hardware, operating system, and
library version differences. Large discrepancies may indicate a configuration
error; check the run logs in `results/logs/`.

---

**How do I add a new method to the benchmark?**

<!-- TODO: Document the method integration interface once scripts are finalized -->

See [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines.
Open an issue or pull request describing the method you would like to add.

---

## Contact

Open an issue on GitHub for bug reports, questions, or feature requests.
