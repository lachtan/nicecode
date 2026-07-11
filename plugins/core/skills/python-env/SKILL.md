---
name: python-env
description: >
  Use when installing Python packages, creating virtual environments,
  managing Python dependencies, or setting up Python projects.
  Triggers on: pip, pip3, python -m pip, python -m venv, pipx, easy_install,
  "add dependency", "install package", "set up Python project".
disable-model-invocation: false
user-invocable: false
managed-by: https://github.com/lachtan/nicecode
version: "1.0.0"
---

# uv-tool

## Overview

**Always use `uv` for all Python package and environment operations.** Never use `pip`, `pip3`, `python -m pip`, `python -m venv`, `pipx`, or `easy_install`.

## Forbidden Commands

Any of these in your command means you are violating this rule:

- `pip install`
- `pip3 install`
- `python -m pip`
- `python -m venv`
- `python -m ensurepip`
- `pipx`
- `easy_install`
- `pip freeze`
- `pip uninstall`
- `pip list`

## When to Use Which Command

| Situation                                               | Command                              |
| ------------------------------------------------------- | ------------------------------------ |
| Add a project dependency (recorded in `pyproject.toml`) | `uv add X`                           |
| Install ad-hoc package in venv (not recorded)           | `uv pip install X`                   |
| Install all project dependencies from `pyproject.toml`  | `uv sync`                            |
| Install from `requirements.txt`                         | `uv pip install -r requirements.txt` |
| Create a virtual environment                            | `uv venv`                            |
| Run a CLI tool without installing                       | `uvx X` (or `uv tool run X`)         |
| Install a CLI tool globally                             | `uv tool install X`                  |
| List installed packages                                 | `uv pip list`                        |
| Freeze installed packages                               | `uv pip freeze`                      |
| Uninstall a package                                     | `uv pip uninstall X`                 |

**Key distinction:** `uv add` writes to `pyproject.toml` — use it for project dependencies. `uv pip install` only installs into the venv — use it for temporary/ad-hoc needs.

## Quick Migration Reference

| Instead of                        | Use                                                     |
| --------------------------------- | ------------------------------------------------------- |
| `pip install X`                   | `uv add X` (project dep) or `uv pip install X` (ad-hoc) |
| `pip install -r requirements.txt` | `uv pip install -r requirements.txt`                    |
| `pip install -e .`                | `uv sync`                                               |
| `pip freeze`                      | `uv pip freeze`                                         |
| `pip list`                        | `uv pip list`                                           |
| `pip uninstall X`                 | `uv pip uninstall X`                                    |
| `python -m venv .venv`            | `uv venv`                                               |
| `pipx install X`                  | `uv tool install X`                                     |
| `pipx run X`                      | `uvx X`                                                 |

## Red Flags — STOP and Fix

If you are about to type any of these, STOP:

- `pip` anywhere in a shell command
- `python -m pip`
- `python -m venv`
- `pipx`
- `easy_install`
- Creating a `requirements.txt` by hand instead of using `uv add`

## Common Excuses

| Excuse                           | Reality                                                 |
| -------------------------------- | ------------------------------------------------------- |
| "pip is simpler for one package" | `uv pip install X` is the same number of words. Use it. |
| "The docs say pip install"       | Translate to uv equivalent. Always.                     |
| "I need a venv first"            | `uv venv` creates one. Then `uv pip install`.           |
| "uv doesn't support this flag"   | It almost certainly does. Check `uv --help`.            |
| "It's just a quick test"         | Rules don't have exceptions for "quick".                |
