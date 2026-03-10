# results/

This directory stores all outputs produced by benchmark runs.
It is organized as follows:

```
results/
├── logs/        # Raw execution logs (one .log file per run)
├── outputs/     # Trajectory estimates and per-sequence metric files
├── figures/     # Generated plots and visualizations
├── summaries/   # Aggregated per-perturbation summaries
└── tables/      # Evaluation tables in CSV and LaTeX format
```

## Notes

- All subdirectories are included in `.gitignore` to prevent committing
  large generated files.
- Each subdirectory contains a `.gitkeep` file so the directory structure
  is tracked by git even when empty.
- Aggregate summaries and final tables intended for publication should be
  copied out of this directory and stored separately.

## Log File Convention

Each log file is named:

```
{method}__{perturbation}__{severity}__{sequence}__{timestamp}.log
```

## Output File Convention

```
results/outputs/{method}/{perturbation}/{severity}/
├── trajectory.csv     # Estimated poses
├── metrics.yaml       # Per-sequence metrics
└── metadata.json      # Run provenance
```

See [docs/evaluation.md](../docs/evaluation.md) for schema details.
