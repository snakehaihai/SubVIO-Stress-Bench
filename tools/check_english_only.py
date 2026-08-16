#!/usr/bin/env python3
"""Reject CJK characters from publishable repository text files."""

from __future__ import annotations

import os
from pathlib import Path


SKIP_DIRS = {".git", ".venv", "__pycache__"}


def is_cjk(character: str) -> bool:
    codepoint = ord(character)
    return (
        0x3400 <= codepoint <= 0x4DBF
        or 0x4E00 <= codepoint <= 0x9FFF
        or 0xF900 <= codepoint <= 0xFAFF
        or 0x20000 <= codepoint <= 0x2FA1F
    )


def main() -> int:
    failures = []
    for root, directories, files in os.walk("."):
        directories[:] = [name for name in directories if name not in SKIP_DIRS]
        for name in files:
            path = Path(root) / name
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            for line_number, line in enumerate(text.splitlines(), 1):
                if any(is_cjk(character) for character in line):
                    failures.append(f"{path}:{line_number}")
    if failures:
        print("CJK text found:\n" + "\n".join(failures))
        return 1
    print("repository text is CJK-free")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
