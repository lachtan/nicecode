---
managed-by: https://github.com/lachtan/nicecode
version: "1.0.0"
last-change: "2026-07-14 05:18:46"
---

# Python — use uv

Always use `uv` for Python. Never `pip`, `pip3`, `python -m pip`,
`python -m venv`, `pipx`, or `easy_install`.

For project dependencies use `uv add` (records them in `pyproject.toml`),
not `uv pip install` (venv-only, unrecorded).
