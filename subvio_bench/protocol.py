"""Validation helpers for the paper protocol manifest."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Union

import yaml


class ProtocolError(ValueError):
    """Raised when the paper protocol is internally inconsistent."""


def load_protocol(path: Union[str, Path] = "configs/paper_protocol.yaml") -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as stream:
        protocol = yaml.safe_load(stream)
    validate_protocol(protocol)
    return protocol


def validate_protocol(protocol: dict[str, Any]) -> None:
    sensor = protocol["sensor_stress"]
    dimensions = sensor["dimensions"]
    if len(dimensions) != 9:
        raise ProtocolError("paper protocol requires nine sensor dimensions")
    if sensor["seeds"] != [0, 1, 2]:
        raise ProtocolError("paper protocol requires seeds 0, 1, and 2")
    for name, specification in dimensions.items():
        if len(specification["levels"]) != 11:
            raise ProtocolError(f"{name} must contain eleven levels")
    expected = len(dimensions) * 11 * len(sensor["seeds"])
    if sensor["expected_runs_per_method"] != expected:
        raise ProtocolError("sensor expected_runs_per_method is inconsistent")
    dynamic = protocol["dynamic_stress"]
    dynamic_expected = len(dynamic["methods"]) * len(dynamic["occlusion_percent"]) * len(dynamic["frame_rate_factor"])
    if dynamic["expected_runs_total"] != dynamic_expected:
        raise ProtocolError("dynamic expected_runs_total is inconsistent")
    evaluation = protocol["evaluation"]
    if evaluation["alignment"] != "SE3" or evaluation["correct_scale"]:
        raise ProtocolError("paper evaluation requires rigid SE(3), without scale correction")
