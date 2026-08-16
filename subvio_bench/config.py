"""Configuration loading and validation."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Union

import yaml


class ConfigError(ValueError):
    """Raised when a benchmark configuration is invalid."""


def _expand(value: Any) -> Any:
    if isinstance(value, str):
        return os.path.expanduser(os.path.expandvars(value))
    if isinstance(value, list):
        return [_expand(item) for item in value]
    if isinstance(value, dict):
        return {key: _expand(item) for key, item in value.items()}
    return value


def load_config(path: Union[str, Path]) -> dict[str, Any]:
    config_path = Path(path).resolve()
    with config_path.open(encoding="utf-8") as stream:
        config = yaml.safe_load(stream)
    if not isinstance(config, dict):
        raise ConfigError("configuration root must be a mapping")
    config = _expand(config)
    config["_config_path"] = str(config_path)
    config["_config_dir"] = str(config_path.parent)
    validate_config(config)
    return config


def validate_config(config: dict[str, Any]) -> None:
    if config.get("schema_version") != 1:
        raise ConfigError("schema_version must be 1")
    workspace = config.get("workspace")
    if not isinstance(workspace, dict) or not workspace.get("output_root"):
        raise ConfigError("workspace.output_root is required")
    experiments = config.get("experiments")
    if not isinstance(experiments, list) or not experiments:
        raise ConfigError("experiments must be a non-empty list")
    seen: set[str] = set()
    for index, experiment in enumerate(experiments):
        prefix = f"experiments[{index}]"
        if not isinstance(experiment, dict):
            raise ConfigError(f"{prefix} must be a mapping")
        for field in ("id", "method", "sequence", "command", "trajectory"):
            if not experiment.get(field):
                raise ConfigError(f"{prefix}.{field} is required")
        experiment_id = str(experiment["id"])
        if experiment_id in seen:
            raise ConfigError(f"duplicate experiment id: {experiment_id}")
        seen.add(experiment_id)
        if not isinstance(experiment["command"], list):
            raise ConfigError(f"{prefix}.command must be an argument list, not a shell string")
