---
name: nice-check
description: >-
  Use when checking this repo against its own rules before a merge or release, or when
  auditing what needs fixing — plugin manifests, skill and rule frontmatter, README sync,
  dead links, hook exit codes and text hygiene. Report only, changes nothing.
disable-model-invocation: true
user-invocable: true
last-change: "2026-08-28 09:29:19"
---

# nice-check

Audit this repo against the rules it sets for itself. Report only — fixing is a separate request.

## Steps

1. Run the checker:

   ```bash
   uv run scripts/nice-check.py
   ```

   It prints one line per finding (`error`/`warning`, check letter, `path:line`, message) and
   exits 1 when any finding is an error. Checks A–J cover plugin manifests, the frontmatter of
   skills and rule files, skill-name collisions, plugin README sync, dead relative links, hook
   configuration, hook exit codes, references between skills, text hygiene and stray tracked files.

2. Run the tools that already own the rest — do not reimplement these in the script:

   ```bash
   uvx pytest -q
   uvx ruff format --check .
   python3 scripts/sync-symlinks.py     # expect no "warning:" and 0 created/updated/removed
   npx --yes markdownlint-cli2 "**/*.md"
   ```

3. Report the findings grouped by severity, errors first. For each one give
   `[path:line](path#Lline)`, what is wrong, and the concrete fix. Close with a one-line summary.
   When everything is clean, print exactly `No findings.`

4. Change nothing. Report only.

## Gotchas

- `sync-symlinks.py` always prints `skipped skills/nice-check: not a symlink, leaving alone` —
  this skill is repo-local and has no plugin behind it. Expected output, not a finding.
- `uv run` is needed only for a consistent interpreter; the script is stdlib-only.
