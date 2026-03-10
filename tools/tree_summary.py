#!/usr/bin/env python3
"""
tree_summary.py
---------------
Print a summary of the SubVIO-Stress-Bench repository directory tree,
excluding common generated artifacts and hidden directories.
"""

import os
import sys


EXCLUDE_DIRS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    "venv",
    ".venv",
    "env",
    ".env",
    "node_modules",
    ".conda",
    ".eggs",
    "dist",
    "build",
    "*.egg-info",
}

EXCLUDE_FILES = {
    ".DS_Store",
    "Thumbs.db",
    "*.pyc",
    "*.pyo",
}


def _should_exclude(name: str) -> bool:
    for pattern in EXCLUDE_DIRS:
        if pattern.startswith("*"):
            if name.endswith(pattern[1:]):
                return True
        elif name == pattern:
            return True
    return False


def print_tree(root: str, prefix: str = "", max_depth: int = 4, depth: int = 0) -> None:
    if depth > max_depth:
        return

    try:
        entries = sorted(os.listdir(root))
    except PermissionError:
        return

    entries = [e for e in entries if not _should_exclude(e)]

    for i, entry in enumerate(entries):
        path = os.path.join(root, entry)
        connector = "└── " if i == len(entries) - 1 else "├── "
        print(f"{prefix}{connector}{entry}")

        if os.path.isdir(path):
            extension = "    " if i == len(entries) - 1 else "│   "
            print_tree(path, prefix + extension, max_depth, depth + 1)


def main() -> None:
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    repo_name = os.path.basename(repo_root)
    print(repo_name + "/")
    print_tree(repo_root)


if __name__ == "__main__":
    main()
