# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NiceCode is a Claude Code plugin marketplace. The guiding principle is **simplicity first**.

## Architecture

Marketplace (`.claude-plugin/marketplace.json`) → Plugins (`plugins/<name>/.claude-plugin/plugin.json`) → rules, skills, hooks.

Each plugin is a self-contained bundle: `core` (rules, skills and hooks), `lab`
(work in progress), `ponytail` (vendored), `rsj` (team skills) and `mattpocock` (vendored subset of mattpocock/skills).

## Development

Plugins are not wired into this repo's `.claude/`; test them by installing them from this marketplace. Skills are the main form; `core` ships one agent (`plan-reviewer`, spawned by `plan-loop`). Always edit source files in `plugins/<plugin>/`. `.claude/skills/nice-check/` is a repo-local skill with no plugin behind it.

### Hook conventions

- Hook scripts in `hooks/scripts/` receive JSON via stdin (`json.load(sys.stdin)` in Python).
- Exit code 2 = block the tool call, 0 = pass.
- Use `${CLAUDE_PLUGIN_ROOT}` for paths in `hooks.json` and `|` in the matcher to combine tools (e.g., `Edit|Write`).

### Frontmatter

`scripts/nice-check.py` (check B) enforces these on every `SKILL.md` and every `rules/*.md` under
`plugins/`. There is no exempt category: a taken-over file follows the same rules as an authored
one and records where it came from in `origin`.

- `managed-by` and `version` — on plugin skills, provenance bookkeeping only; on `rules/*.md`,
  `install-rules.py` actually reads them to decide whether to overwrite an installed copy.
- `last-change: "YYYY-MM-DD HH:MM:SS"` — local time, quoted (unquoted it parses as a YAML
  timestamp, not a string). Rewrite it when the body changes — what the file tells Claude to do.
  A frontmatter-only edit (version bump, a new flag) or a formatting sweep leaves it alone.
- `license` never appears in frontmatter — a licence lives in a `LICENSE` file or the plugin
  manifest, and `origin` is what credits the source.

On a `SKILL.md` additionally:

- `name` must match the skill's directory name.
- `disable-model-invocation` and `user-invocable` are always set explicitly.

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
