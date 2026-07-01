# ponytail

Anti-over-engineering layer — a lazy-senior-dev reflex that keeps Claude
reaching for the simplest solution that actually works. Type `/ponytail` for a
one-shot nudge, or `/ponytail on` to keep it on for the whole session.

Distilled from upstream [ponytail](https://github.com/DietrichGebert/ponytail),
adapted for Claude Code. The upstream skill injects its rules only once per
session, so as the context fills with diffs and tool output the rule loses
salience and the model drifts back to over-building. This plugin fixes that with
two layers of injection while the layer is on.

## How it works

The skill carries the full ruleset (`skills/ponytail/SKILL.md`). Typing
`/ponytail` — or the model auto-invoking it on a coding task — just runs that
ruleset **once**.

To make it persist, type `/ponytail on` (or `/ponytail anchor`). That writes a
per-session marker which drives two hooks, both powered by a single script
`skills/ponytail/ponytail.py`:

- **SessionStart hook** reloads the full ruleset on `startup`, `resume`,
  `clear`, and `compact` — but only while the marker is set — so the rules
  survive context compaction.
- **UserPromptSubmit hook** injects a short anchor (`skills/ponytail/anchor.txt`)
  before every prompt while the marker is set, keeping the rule at the
  recency-favored end of the context. It also writes the marker on `/ponytail on`
  and removes it on `stop ponytail` / `/ponytail off`.

## On-demand audit

`/ponytail-audit [path]` scans the whole repo (or the given path) for
over-engineering and hands back a ranked delete-list — one line per finding,
biggest cut first. It is report-only and runs **only** when you invoke it; it
never fires automatically while you code.

## Turning it off

`stop ponytail` or `/ponytail off` removes the session marker and reliably
silences the layer for the rest of the session; `/ponytail on` switches it back
on. To disable it entirely, regardless of session state:

- Installed plugin: `/plugin disable ponytail@nicecode` (or uninstall it).
- In this repo (self-apply): remove the `SessionStart` and `UserPromptSubmit`
  entries from `.claude/settings.json`.

## The ladder

The rules climb a ladder and stop at the first rung that holds: does it need to
exist (YAGNI) → reuse what's in the repo → standard library → native platform →
installed dependency → one line → minimum code that works. A non-negotiable
safety floor (input validation, error handling, security, accessibility) is
never simplified away.
