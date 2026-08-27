# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NiceCode is a Claude Code plugin marketplace. The guiding principle is **simplicity first**.

## Architecture

Marketplace (`.claude-plugin/marketplace.json`) → Plugins (`plugins/<name>/.claude-plugin/plugin.json`) → rules, skills, hooks.

Each plugin is a self-contained bundle: `core` (rules, skills and hooks), `lab`
(work in progress), `ponytail` (vendored) and `mattpocock` (external source).

## Development

`.claude/` contains symlinks into `plugins/*/` — the repo points to itself so every local plugin's skills can be tested directly here. Skills are the only form still in use; `commands/` and `agents/` stay wired up for the sync script but no plugin ships them any more. Always edit source files in `plugins/<plugin>/`, never in `.claude/`. `scripts/sync-symlinks.py` keeps `.claude/{skills,commands,agents}/` in sync with what's under `plugins/*/`; a `PostToolUse` hook in `.claude/settings.json` runs it automatically after every `Write`, so a new/removed skill, command, or agent never needs a manual symlink. The one exception is `.claude/skills/nice-check/` — a real directory, not a symlink: a repo-local skill with no plugin behind it, so `sync-symlinks.py` reports it as `skipped` and leaves it alone.

### Hook conventions

- Hook scripts in `hooks/` receive JSON via stdin (`json.load(sys.stdin)` in Python).
- Exit code 2 = block the tool call, 0 = pass.
- Use `${CLAUDE_PLUGIN_ROOT}` for paths in `hooks.json` and `|` in the matcher to combine tools (e.g., `Edit|Write`).

### Skill frontmatter

`scripts/nice-check.py` (check B) enforces these on every authored `SKILL.md`:

- `name` must match the skill's directory name.
- `disable-model-invocation` and `user-invocable` are always set explicitly.
- `managed-by` and `version` on plugin skills — provenance bookkeeping only; no installer reads
  them, `install-rules.py` handles `rules/` alone.
- `last-change: "YYYY-MM-DD HH:MM:SS"` — local time, quoted (unquoted it parses as a YAML
  timestamp, not a string). Rewrite it when the body changes — what the skill tells Claude to do.
  A frontmatter-only edit (version bump, a new flag) or a formatting sweep leaves it alone.

A vendored skill (one carrying `license:`) is exempt from all of it — it belongs to its author.

### Versioning

Bump `version` in `.claude-plugin/marketplace.json` on release.

### Tests

Always run tests via `uvx pytest`, never bare `pytest`.

Hook tests: `uvx pytest plugins/core/hooks/tests/`

## Documentation

- When plugins change significantly (added, removed, renamed, or their structure changes), check `README.md` and update it to stay in sync with the code.
- [Plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces) — official docs for marketplace structure.
- [Plugins](https://code.claude.com/docs/en/plugins) — official docs for plugin creation.

## Git

- Do not add `Co-Authored-By` lines to commit messages.

## Claude Code

Talk to the user in Czech — chat, questions, plans and review reports.

Everything committed to the repo is in English: plugin and skill descriptions,
rules, READMEs, code, comments and commit messages. A file that gets committed
is English even when the conversation that produced it was Czech.
