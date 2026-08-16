# Reproducing Results

This guide describes how to run the published configurations and generate the
qualitative trajectory-deformation figure from locally produced trajectories.

---

## Overview

The repository provides the experiment protocol, method-specific
configurations, perturbation scripts, benchmark runner, trajectory evaluator,
and plotting utility. Datasets, algorithm installations, model weights, and
experiment outputs are not included.

---

## Step 1: Data Preparation

Download the processed CERBERUS release and configure local paths as described
in [Dataset Layout](dataset_layout.md):

```bash
cp configs/local_paths.example.yaml configs/local_paths.yaml
```

---

## Step 2: Perturbation Application

Verify the published configuration and script snapshot:

```bash
make verify-assets
make validate-paper
```

Install the required files from `experiment_assets/snapshot/` into matching
method checkouts. Generate perturbed folders or ROS bags with the dataset tools
under `experiment_assets/snapshot/dataset/scripts/`.

---

## Step 3: Running Evaluations

Configure enabled method adapters and inspect their commands before execution:

```bash
make dry-run CONFIG=configs/local.yaml
make run-all CONFIG=configs/local.yaml
```

Each method runs in its own upstream ROS, Docker, CUDA, or native build
environment. The benchmark runner records logs, status, and the configured TUM
trajectory output for each experiment.

---

## Step 4: Aggregating Results

The trajectory-deformation figure is drawn directly from a TUM ground-truth
trajectory and one or more locally generated perturbed trajectories:

```bash
python tools/plot_noise_trajectories.py \
  --ground-truth /path/to/groundtruth/seq1.txt \
  --estimate "acc_noise_100x=/path/to/acc_noise_trajectory.txt" \
  --estimate "gyro_noise_39.81x=/path/to/gyro_noise_trajectory.txt" \
  --estimate "focal_1.12x=/path/to/focal_trajectory.txt" \
  --output results/figures/noise_trajectories.png
```

Each `--estimate` argument uses `LABEL=PATH` and may be repeated. The tool:

1. loads the first eight TUM columns;
2. associates estimate and ground-truth timestamps within 0.02 seconds;
3. applies rigid SE(3) Umeyama alignment without scale correction;
4. computes translational RMSE on associated poses;
5. plots the aligned XY trajectories and distance-versus-height profiles.

No experiment result table is required by this plotting command.

---

## Expected Outputs

The command writes the requested PNG file under `results/figures/`. Generated
figures and trajectories remain ignored by Git.

---

## Notes on Reproducibility

- Record the dataset revision, method commit, configuration filename, seed,
  and trajectory filename for each plotted curve.
- Use the same ground truth and timestamp tolerance for every method.
- Do not enable Sim(3) scale correction for metric stereo-inertial results.
- Keep datasets and generated experiment outputs outside the repository.
