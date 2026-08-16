# tools/

This directory contains benchmark utilities.

## Contents

| Script | Description |
|---|---|
| `tree_summary.py` | Print a compact repository tree |
| `evaluate_trajectory.py` | Evaluate one TUM estimate against ground truth |
| `summarize_results.py` | Aggregate standardized metric files |
| `generate_figures.py` | Plot standardized benchmark summaries |
| `plot_noise_trajectories.py` | Plot aligned ground truth and noise-affected trajectories |
| `generate_experiment_manifest.py` | Expand the protocol into expected run rows |
| `snapshot_experiment_assets.py` | Refresh the configuration and script snapshot |
| `verify_experiment_assets.py` | Verify snapshot counts, hashes, and ASCII-only content |
| `check_english_only.py` | Check that repository text contains no CJK characters |
| `experiment_metadata_template.json` | Metadata template for experiment runs |

## Usage

```bash
python tools/evaluate_trajectory.py ground_truth.txt estimate.txt
python tools/plot_noise_trajectories.py --help
make verify-assets
```

## Planned Utilities

Future tools should use portable command-line paths and include deterministic
tests.
