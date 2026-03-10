# Evaluation

This document describes the evaluation metrics, output file formats, and
result aggregation used in SubVIO-Stress-Bench.

---

## Metrics

The benchmark reports standard localization accuracy metrics alongside
failure-mode-specific indicators.

### Trajectory Accuracy

| Metric | Symbol | Description |
|---|---|---|
| Absolute Trajectory Error | ATE | Root-mean-square error after Umeyama alignment |
| Relative Pose Error (translation) | RPE_t | Mean translational drift per meter of travel |
| Relative Pose Error (rotation) | RPE_r | Mean rotational drift per meter of travel |

<!-- TODO: Verify metric definitions and alignment procedures against scripts -->

### Robustness Indicators

| Metric | Description |
|---|---|
| Failure rate | Fraction of sequences where the method diverges |
| Recovery time | Time to re-localize after a divergence event (if applicable) |
| Degradation slope | Rate of metric degradation as perturbation severity increases |

<!-- TODO: Add additional robustness metrics once confirmed -->

---

## Output File Format

Each run produces a per-sequence output file in `results/outputs/`:

```
results/outputs/
└── {method}/{perturbation}/{severity}/
    ├── trajectory.csv      # Estimated trajectory (timestamp, tx, ty, tz, qx, qy, qz, qw)
    ├── metrics.yaml        # Per-sequence metric values
    └── metadata.json       # Run metadata (config, timestamps, version)
```

<!-- TODO: Verify exact file names and formats against scripts -->

---

## Aggregated Summaries

The `make summarize` command collects per-run metrics and writes:

```
results/summaries/
├── summary_{perturbation}.csv   # Per-perturbation-level aggregated metrics
└── summary_all.csv              # Full cross-method, cross-perturbation table
```

---

## Tables and Figures

The `make figures` command generates:

```
results/tables/
├── main_table.csv           # Primary evaluation table
└── main_table.tex           # LaTeX version of the main table

results/figures/
├── degradation_curves.pdf   # Metric vs. perturbation severity curves
└── failure_rate_heatmap.pdf # Failure rate heatmap across methods and perturbations
```

<!-- TODO: Update file names once figure generation scripts are confirmed -->
