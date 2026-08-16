"""Run configured VIO experiments and record reproducibility metadata."""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from .config import ConfigError, load_config
from .evaluation import evaluate


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _selected(experiment: dict[str, Any], methods: set[str], ids: set[str], include_disabled: bool) -> bool:
    if not include_disabled and not experiment.get("enabled", True):
        return False
    if methods and experiment["method"] not in methods:
        return False
    if ids and experiment["id"] not in ids:
        return False
    return True


def run_experiment(config: dict[str, Any], experiment: dict[str, Any], dry_run: bool, overwrite: bool) -> dict[str, Any]:
    root = Path(config["workspace"]["output_root"]).resolve()
    run_dir = root / "runs" / experiment["id"]
    run_dir.mkdir(parents=True, exist_ok=True)
    command = [str(part) for part in experiment["command"]]
    cwd = Path(experiment.get("cwd", config["_config_dir"])).resolve()
    trajectory_source = Path(experiment["trajectory"]).resolve()
    gt_source = Path(experiment["ground_truth"]).resolve() if experiment.get("ground_truth") else None
    metadata = {
        "schema_version": 1,
        "experiment": {key: value for key, value in experiment.items() if key != "env"},
        "command": command,
        "cwd": str(cwd),
        "config": config["_config_path"],
        "host": platform.node(),
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "started_at": datetime.now(timezone.utc).isoformat(),
        "status": "dry-run" if dry_run else "running",
    }
    _write_json(run_dir / "metadata.json", metadata)
    if dry_run:
        print(f"[dry-run] {experiment['id']}: {' '.join(command)}")
        return metadata
    target_trajectory = run_dir / "trajectory.txt"
    if target_trajectory.exists() and not overwrite:
        metadata["status"] = "skipped-existing"
        _write_json(run_dir / "metadata.json", metadata)
        print(f"[skip] {experiment['id']}: {target_trajectory} exists")
        return metadata
    environment = os.environ.copy()
    environment.update({str(key): str(value) for key, value in experiment.get("env", {}).items()})
    started = time.monotonic()
    try:
        with (run_dir / "run.log").open("w", encoding="utf-8") as log:
            completed = subprocess.run(
                command,
                cwd=cwd,
                env=environment,
                stdout=log,
                stderr=subprocess.STDOUT,
                timeout=experiment.get("timeout_s"),
                check=False,
            )
        metadata["return_code"] = completed.returncode
    except subprocess.TimeoutExpired as exc:
        metadata["status"] = "failed"
        metadata["error"] = f"command timed out after {exc.timeout} seconds"
        metadata["return_code"] = None
    except OSError as exc:
        metadata["status"] = "failed"
        metadata["error"] = str(exc)
        metadata["return_code"] = None
    metadata["duration_s"] = round(time.monotonic() - started, 3)
    if metadata["status"] == "failed":
        pass
    elif completed.returncode != 0:
        metadata["status"] = "failed"
    elif not trajectory_source.is_file():
        metadata["status"] = "missing-trajectory"
    else:
        shutil.copy2(trajectory_source, target_trajectory)
        metadata["status"] = "completed"
        if gt_source:
            try:
                metrics = evaluate(
                    gt_source,
                    target_trajectory,
                    float(config.get("evaluation", {}).get("max_timestamp_difference_s", 0.02)),
                    bool(config.get("evaluation", {}).get("correct_scale", False)),
                    float(config.get("evaluation", {}).get("drift_penalty_m_per_s", 0.025)),
                )
                metrics.update({
                    "experiment_id": experiment["id"],
                    "method": experiment["method"],
                    "sequence": experiment["sequence"],
                    "perturbation": experiment.get("perturbation", {"type": "none", "severity": 0}),
                })
                _write_json(run_dir / "metrics.json", metrics)
            except (OSError, ValueError) as exc:
                metadata["status"] = "evaluation-failed"
                metadata["error"] = str(exc)
    metadata["finished_at"] = datetime.now(timezone.utc).isoformat()
    _write_json(run_dir / "metadata.json", metadata)
    print(f"[{metadata['status']}] {experiment['id']}")
    return metadata


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/default.yaml")
    parser.add_argument("--method", action="append", default=[])
    parser.add_argument("--experiment", action="append", default=[])
    parser.add_argument("--include-disabled", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        config = load_config(args.config)
    except (OSError, ConfigError) as exc:
        print(f"configuration error: {exc}", file=sys.stderr)
        return 2
    methods, ids = set(args.method), set(args.experiment)
    experiments = [
        item for item in config["experiments"]
        if _selected(item, methods, ids, args.include_disabled)
    ]
    if not experiments:
        print("no experiments selected", file=sys.stderr)
        return 2
    outcomes = [run_experiment(config, item, args.dry_run, args.overwrite) for item in experiments]
    failures = {"failed", "missing-trajectory", "evaluation-failed"}
    return 1 if any(item["status"] in failures for item in outcomes) else 0


if __name__ == "__main__":
    raise SystemExit(main())
