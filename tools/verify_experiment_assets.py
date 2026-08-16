#!/usr/bin/env python3
"""Verify the published experiment asset snapshot and its checksums."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path("experiment_assets/snapshot")
EXPECTED_FILES = {
    "airslam/configs/sensitivity": 297,
    "orbslam3/configs/sensitivity": 297,
    "openvins/configs/sensitivity": 891,
    "schurvins/configs/sensitivity": 297,
}


def main() -> int:
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="ascii"))
    failures = []
    for record in manifest["files"]:
        path = ROOT / record["path"]
        if not path.is_file():
            failures.append(f"missing: {record['path']}")
            continue
        data = path.read_bytes()
        if any(byte > 127 for byte in data):
            failures.append(f"non-ASCII content: {record['path']}")
        if path.suffix in {".yaml", ".yml"} and b"python/object" in data:
            failures.append(f"unsafe Python YAML tag: {record['path']}")
        if path.suffix == ".py":
            try:
                compile(data.decode("ascii"), str(path), "exec")
            except SyntaxError as error:
                failures.append(f"Python syntax error: {record['path']}: {error}")
        if path.suffix == ".sh":
            completed = subprocess.run(["bash", "-n", str(path)], capture_output=True, text=True)
            if completed.returncode:
                failures.append(f"shell syntax error: {record['path']}: {completed.stderr.strip()}")
        if hashlib.sha256(data).hexdigest() != record["snapshot_sha256"]:
            failures.append(f"checksum mismatch: {record['path']}")
    actual = sum(1 for path in ROOT.rglob("*") if path.is_file() and path.name != "manifest.json")
    if actual != manifest["file_count"]:
        failures.append(f"file count mismatch: {actual} != {manifest['file_count']}")
    for relative, expected in EXPECTED_FILES.items():
        count = sum(1 for path in (ROOT / relative).rglob("*") if path.is_file())
        if count != expected:
            failures.append(f"configuration count mismatch for {relative}: {count} != {expected}")
    if failures:
        print("\n".join(failures))
        return 1
    print(f"verified {actual} ASCII-only experiment asset files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
