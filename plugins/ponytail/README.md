# ponytail

Anti-over-engineering layer — an opt-in lazy-senior-dev reflex that keeps
Claude reaching for the simplest solution that actually works. Type `/ponytail`
to switch it on for the session.

Distilled from upstream [ponytail](https://github.com/DietrichGebert/ponytail),
adapted for Claude Code. The upstream skill injects its rules only once per
session, so as the context fills with diffs and tool output the rule loses
salience and the model drifts back to over-building. This plugin fixes that with
two layers of injection.

## How it works

Type `/ponytail` in any prompt to activate the layer for the rest of the
session. A per-session marker then drives two hooks:

- **SessionStart hook** reloads the full ruleset `skills/ponytail/SKILL.md` on
  `startup`, `resume`, `clear`, and `compact` — but only while the session is
  active — so the rules survive context compaction.
- **UserPromptSubmit hook** injects a short anchor (`skills/ponytail/anchor.txt`)
  before every prompt while active, keeping the rule at the recency-favored end
  of the context.
- The skill is also discoverable by subagents and invocable as `/ponytail`.

## On-demand audit

`/ponytail-audit [path]` scans the whole repo (or the given path) for
over-engineering and hands back a ranked delete-list — one line per finding,
biggest cut first. It is report-only and runs **only** when you invoke it; it
never fires automatically while you code.

## Turning it off

`stop ponytail` / `normal mode` removes the session marker and reliably silences
the layer for the rest of the session; `/ponytail` switches it back on. (Use
those exact phrases — they are the on/off gestures the hook recognizes.) To
disable it entirely, regardless of session state:

- Installed plugin: `/plugin disable ponytail@nicecode` (or uninstall it).
- In this repo (self-apply): remove the `SessionStart` and `UserPromptSubmit`
  entries from `.claude/settings.json`.

## The ladder

The rules climb a ladder and stop at the first rung that holds: does it need to
exist (YAGNI) → reuse what's in the repo → standard library → native platform →
installed dependency → one line → minimum code that works. A non-negotiable
safety floor (input validation, error handling, security, accessibility) is
never simplified away.
