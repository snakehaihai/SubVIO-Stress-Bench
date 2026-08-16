# Evaluation

This document defines the implemented trajectory metrics, standardized run
outputs, and crash-aware aggregation rules.

---

## Metrics

Ground truth and estimates use TUM order:

```text
timestamp tx ty tz qx qy qz qw
```

Comments and extra columns are accepted. Clearly nanosecond-scale timestamps
are converted to seconds. The evaluator associates nearest timestamps within
the configured tolerance and then applies Umeyama alignment.

### Trajectory Accuracy

| Metric | Output field | Definition |
|---|---|---|
| Absolute pose error | `ape_translation_rmse_m` | Translational RMSE after rigid SE(3) alignment |
| Relative pose error | `rpe_translation_rmse_m` | Translational RMSE between adjacent associated pose increments |
| Distance coverage | `distance_coverage` | Reference path distance between first and last tracked poses divided by full reference path distance |
| Penalized APE | `penalized_ape_rmse_m` | APE with untracked prefix/tail samples penalized at the configured rate |

Rigid alignment is the default because the evaluated stereo VIO systems are
metric-scale. `--correct-scale` enables Sim(3) only for a separately justified
monocular analysis. The paper states a 0.025 m/s prefix/tail penalty but does
not specify the discrete integration convention; this repository records its
deterministic nearest-boundary interpretation in each metric output.

### Robustness Indicators

| Indicator | Definition |
|---|---|
| Run status | Success, non-zero exit, timeout, missing trajectory, or evaluation failure |
| Success count | Number of numeric measured trajectories in an aggregate cell |
| Crash count | Number of explicit failed process records in an aggregate cell |
| Missing count | Number of expected protocol records without a source measurement |
| Partial aggregate | A sensor cell with fewer than three successful directional seeds |

Rotational APE/RPE, recovery time, degradation slope, and uncertainty
calibration are not currently produced and must not be inferred from the
implemented translational fields.

---

## Output File Format

Each standardized run is isolated under its experiment ID:

```text
results/runs/<experiment-id>/
├── run.log
├── metadata.json
├── trajectory.txt
└── metrics.json
```

`metadata.json` records the resolved command, method, sequence, perturbation,
timestamps, return code, status, and configured input/output paths.
`metrics.json` records association parameters, matched/reference/estimate pose
counts, the alignment transform, trajectory metrics, and coverage convention.

---

## Aggregated Summaries

```bash
python tools/summarize_results.py --results-dir results
```

The summarizer collects standardized `metrics.json` files produced by enabled
benchmark runs.

---

## Tables and Figures

`tools/generate_figures.py` plots standardized summary metrics.
`tools/plot_noise_trajectories.py` plots aligned ground-truth and perturbed TUM
trajectories as described in [Reproducing Results](reproducing_results.md).
