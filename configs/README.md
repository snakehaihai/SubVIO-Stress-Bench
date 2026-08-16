# configs/

This directory stores the paper protocol, benchmark adapter configurations,
method revision records, and a portable local-path template.

## Structure

```text
configs/
├── README.md                 # This file
├── default.yaml              # Disabled real-method adapter examples
├── self_test.yaml            # Portable deterministic smoke test
├── paper_protocol.yaml       # Paper-derived experiment and metric contract
├── method_versions.yaml      # Reference upstream revisions
└── local_paths.example.yaml  # Template for ignored workstation paths
```

The 1,782 generated method configurations are stored under
`experiment_assets/snapshot/`, where their checksums and provenance are tracked
by `experiment_assets/manifest.json`.

## Usage

Validate and inspect a configuration before enabling real commands:

```bash
cp configs/default.yaml configs/local.yaml
python -c "from subvio_bench.config import load_config; load_config('configs/local.yaml')"
python scripts/run_all.py --config configs/local.yaml --include-disabled --dry-run
python scripts/run_all.py --config configs/local.yaml
```

Use `configs/local_paths.yaml`, copied from the example, for workstation paths.
Local configuration files are ignored by Git.

## Format

The benchmark runner schema is version 1:

```yaml
schema_version: 1
workspace:
  output_root: results/runs
experiments:
  - id: unique-run-id
    enabled: false
    method: AirSLAM
    sequence: seq1
    command: [bash, /path/to/run.sh]
    trajectory: /path/to/estimated_tum.txt
    ground_truth: /path/to/ground_truth_tum.txt
    timeout_s: 3600
    perturbation:
      dimension: acc_noise
      level: 1.0
      seed: 0
```

`id`, `method`, `sequence`, `command`, and `trajectory` are required for each
experiment. IDs must be unique. Optional fields include `ground_truth`, `cwd`,
`env`, `timeout_s`, `enabled`, and `perturbation`. Environment variables such
as `${HOME}` are expanded at load time; absolute local paths must not be
committed.
