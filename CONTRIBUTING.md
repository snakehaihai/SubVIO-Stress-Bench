# Contributing to SubVIO-Stress-Bench

Thank you for your interest in contributing to SubVIO-Stress-Bench.
This document provides guidelines for submitting bug reports, feature requests,
and code contributions.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Submitting Pull Requests](#submitting-pull-requests)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Commit Messages](#commit-messages)

---

## Code of Conduct

All contributors are expected to adhere to the [Code of Conduct](CODE_OF_CONDUCT.md).
Please read it before participating.

---

## How to Contribute

### Reporting Bugs

Before opening a new issue, please search existing issues to avoid duplicates.

When filing a bug report, include:

- A clear and descriptive title.
- Steps to reproduce the issue.
- Expected versus observed behavior.
- Environment details (OS, Python version, relevant package versions).
- Relevant log output or error messages.

Use the **Bug Report** issue template when available.

### Suggesting Enhancements

Feature requests and benchmark extensions are welcome.
Please open an issue with:

- A clear description of the proposed change.
- Motivation and use case.
- Any relevant references (papers, datasets, implementations).

### Submitting Pull Requests

1. Fork the repository and create a feature branch from `main`.
2. Make changes that are focused, minimal, and well-documented.
3. Ensure existing scripts and data files are not modified unless the change
   is clearly documented and backward compatible.
4. Add or update relevant documentation in `docs/` when appropriate.
5. Open a pull request against `main` with a clear description of the change.

---

## Development Setup

```bash
git clone https://github.com/snakehaihai/SubVIO-Stress-Bench.git
cd SubVIO-Stress-Bench
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

---

## Coding Standards

- Follow [PEP 8](https://peps.python.org/pep-0008/) for Python code.
- Use descriptive variable and function names.
- Include docstrings for all public functions and classes.
- Keep functions focused and short.
- Do not commit large binary files or dataset files.

---

## Commit Messages

Use clear, imperative commit messages:

```
Add perturbation config for temporal offset
Fix metric computation for degenerate trajectories
Update dataset_layout.md with new sequence names
```

Avoid vague messages such as `fix`, `update`, or `WIP`.
