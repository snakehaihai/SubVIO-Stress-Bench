# results/

This directory stores outputs produced by local benchmark runs. Generated
trajectories, logs, summaries, tables, and figures are ignored by Git.

## Notes

- Datasets and experiment result data are not distributed in this repository.
- Each run writes to an isolated directory identified by its experiment ID.
- Keep method-native outputs in their upstream result directories.

## Log File Convention

```text
results/runs/<experiment-id>/run.log
```

## Output File Convention

```text
results/runs/<experiment-id>/
├── run.log
├── metadata.json
├── trajectory.txt
└── metrics.json
```

Generated qualitative plots are written under `results/figures/`.
