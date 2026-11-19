# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NiceCode is a Claude Code plugin marketplace. The guiding principle is **simplicity first**.

## Architecture

Source (`src/`) → `scripts/build.py` → generated output: marketplace (`.claude-plugin/marketplace.json`)
→ plugins (`plugins/<name>/`) → rules, skills, hooks.

- `src/marketplace.json` — the catalog, the only place plugin metadata (name, description, version) lives.
- `src/<name>/` — the plugin's files; everything except tests and the neutral `hooks.json` is copied as is.
- `plugins/`, `.claude-plugin/` — generated and committed, so the repo installs straight from git.
  Never edit them by hand; `build.py --check` (run by `scripts/test.sh` and CI) fails when they drift.

Each plugin is a self-contained bundle: `core` (rules, skills and hooks), `lab`
(work in progress), `ponytail` (vendored), `rsj` (team skills) and `mattpocock` (vendored subset of mattpocock/skills).

## Development

Plugins are not wired into this repo's `.claude/`; test them by installing them from this marketplace. Skills are the main form; `core` ships one agent (`plan-reviewer`, spawned by `plan-loop`). Always edit source files in `src/<plugin>/`, then run `uv run scripts/build.py` and commit `src/` together with the output. `.claude/skills/nice-check/` is a repo-local skill with no plugin behind it.

### Hook conventions

- Hook scripts in `hooks/scripts/` receive JSON via stdin (`json.load(sys.stdin)` in Python).
- Exit code 2 = block the tool call, 0 = pass.
- Hooks are declared in the neutral `src/<plugin>/hooks.json`, which `build.py` translates into `plugins/<plugin>/hooks/hooks.json`:

  ```json
  {"hooks": [{"event": "before-tool", "tools": ["shell"], "command": "python3 {plugin_root}/hooks/scripts/check-uv.py"}]}
  ```

  - `event`: `before-tool` | `after-tool` | `session-start` | `prompt-submit`
    (→ `PreToolUse` | `PostToolUse` | `SessionStart` | `UserPromptSubmit`).
  - `tools`: `shell` (→ `Bash`) | `edit` (→ `Edit|Write`); required on `*-tool` events, forbidden on the others.
  - `{plugin_root}` becomes `${CLAUDE_PLUGIN_ROOT}`.

### Frontmatter

`scripts/nice-check.py` (check B) enforces these on every `SKILL.md` and every `rules/*.md` under
`src/`. There is no exempt category: a taken-over file follows the same rules as an authored
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

Bump `version` in `src/marketplace.json` on release, then rebuild.

### Tests

Always run tests via `uvx pytest`, never bare `pytest`.

Hook tests: `uvx pytest src/core/hooks/tests/`

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
