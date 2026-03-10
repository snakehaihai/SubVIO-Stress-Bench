# tools/

This directory contains utility and helper scripts for the benchmark.

## Contents

| Script | Description |
|---|---|
| `tree_summary.py` | Print a summary of the repository directory tree |
| `experiment_metadata_template.json` | Template for recording experiment metadata |

## Usage

```bash
# Print the repository tree
python tools/tree_summary.py

# or via Makefile:
make tree
```

## Planned Utilities

<!-- TODO: Add the following tools once benchmark scripts are finalized -->

| Script | Description |
|---|---|
| `summarize_results.py` | Aggregate per-run outputs into summary tables |
| `generate_figures.py` | Produce evaluation plots from aggregated results |
| `check_environment.py` | Verify that all dependencies are correctly installed |
