# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NiceCode is a Claude Code plugin marketplace. The guiding principle is **simplicity first**.

## Architecture

Marketplace (`.claude-plugin/marketplace.json`) → Plugins (`plugins/<name>/.claude-plugin/plugin.json`) → rules, skills, hooks.

Each plugin is a self-contained bundle. Currently there is one plugin: `core`.

## Development

`.claude/` contains symlinks into `plugins/core/` — the repo points to itself so the plugin can be tested directly here. Always edit source files in `plugins/core/`, never in `.claude/`.

### Hook conventions

- Hook scripts in `hooks/` receive JSON via stdin (`json.load(sys.stdin)` in Python).
- Exit code 2 = block the tool call, 0 = pass.
- Use `${CLAUDE_PLUGIN_ROOT}` for paths in `hooks.json` and `|` in the matcher to combine tools (e.g., `Edit|Write`).

### Versioning

Bump `version` in `.claude-plugin/marketplace.json` on release.

### Tests

Always run tests via `uvx pytest`, never bare `pytest`.

Hook tests: `uvx pytest plugins/core/hooks/tests/`

## Documentation

- When plugins change significantly (added, removed, renamed, or their structure changes), check `README.md` and update it to stay in sync with the code.
- [Plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces) — official docs for marketplace structure.
- [Plugins](https://code.claude.com/docs/en/plugins) — official docs for plugin creation.

## Problem Logging

When you identify or resolve a bug, config issue, or make a significant
architectural decision, update the appropriate log file.
Before investigating any issue, check existing logs for prior solutions.
Format, file routing, and lookup rules: @.claude/skills/problem-log/SKILL.md

## Git

- Do not add `Co-Authored-By` lines to commit messages.
