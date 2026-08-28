---
description: "Python coding conventions"
paths:
  - "**/*.py"
managed-by: https://github.com/lachtan/nicecode
version: "1.0.0"
last-change: "2026-07-11 07:54:50"
---

# Python Coding Conventions

## Core Principles

- **Readability first** — code must be easily readable and understandable at a glance
- **Simplicity** — prefer the simplest solution that solves the problem; avoid unnecessary abstractions and cleverness
- **Clean Code** — meaningful names, small focused functions, single responsibility, no duplication (DRY), clear intent

## Style

- Follow PEP 8; max line length **120 characters**
- 4-space indentation
- Blank lines to separate functions, classes, and logical blocks
- Use f-strings for string formatting; do not use `%` or `.format()`

## Naming

- Variables and functions: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`

## Types and Annotations

- Use Python 3.12+ built-in generics: `list[str]`, `dict[str, int]`, `tuple[int, ...]`
- Use `X | Y` instead of `Union[X, Y]`, `str | None` instead of `Optional[str]`
- Do not import from `typing` unless truly necessary (e.g., `Protocol`, `TypeVar`)
- All public functions and methods must have type hints

## Docstrings and Comments

- Add a docstring or comment only when it explains **intent** not obvious from the code or signature
- First line: short imperative summary; omit parameter/return docs if self-explanatory
- Prefer clear naming over explanatory comments; never restate what the code does

## Functions

- Break complex functions into smaller ones
- Handle edge cases explicitly; prefer specific exceptions over bare `except`

## Error Handling

- Never silently swallow exceptions
- Do not unnecessarily wrap exceptions in other exception types

## Imports

- Module-level; avoid inside functions unless necessary (e.g., circular imports, heavy optional deps)
- Group: stdlib → third-party → local

## Paths

- Prefer `pathlib.Path` over `os.path`
