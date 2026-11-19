---
name: skill-authoring
description: >-
  Use when creating a new SKILL.md, editing an existing skill, or reviewing skill frontmatter or
  description wording — covers trigger-phrased descriptions, frontmatter flags, body structure,
  and line-wrap conventions so skills trigger reliably and stay cheap once loaded into context.
disable-model-invocation: false
user-invocable: true
managed-by: https://github.com/lachtan/nicecode
version: "1.1.0"
last-change: "2026-08-27 08:38:23"
---

# Skill Authoring

Rules for writing SKILL.md files so skills trigger reliably and stay cheap once loaded into context.

## Description field

- Lead with the trigger condition, not a summary of what the skill does internally. `description` is
  matched against the current task to decide whether to load the skill — phrase it as
  "Use when X" / "Triggers on Y", with the key trigger case first.
- Combine a short "what it does" clause with the trigger condition — don't write either alone.
- Keep `description` (+ `when_to_use` if used) concise — combined hard limit is 1536 characters.
  Move caveats/examples to `when_to_use` instead of inflating `description`.
- Prefer concrete trigger phrases over abstract descriptions (e.g. "test failing", "bug report"
  rather than "helps with debugging").
- If `description` doesn't fit on one readable line (roughly >100 chars), wrap it with a YAML block
  scalar (`>-` folded or `|-` literal) instead of one long unbroken line — keeps the frontmatter
  readable and diffable.

## Frontmatter flags

- Always make an explicit decision for `disable-model-invocation` and `user-invocable` — never
  leave them unset by default without asking "should Claude auto-invoke this, and should the user
  be able to run it as `/name`?".
- `disable-model-invocation: true` — for workflows with side effects that must stay under explicit
  user control (deploy, commit, sending messages). Claude must not trigger these on its own
  judgement.
- `user-invocable: false` — for background knowledge the user never runs directly (conventions,
  reference material). Hides it from the `/` menu; Claude can still use it.
- Leaving both unset (both usable) is only correct when there's no side effect and no reason to hide
  the skill.
- Record `last-change: "YYYY-MM-DD HH:MM:SS"` (local time, in quotes — unquoted it parses as a YAML
  timestamp rather than a string) and rewrite it whenever you change the body. Bumping `version` or
  reformatting the markdown is not a change to what the skill says, so the stamp stays.
- Check whether other optional fields apply and add only the ones that do:
  `allowed-tools`/`disallowed-tools` (permission scoping), `argument-hint`/`arguments`
  (slash-command parameters), `model`/`effort` (override), `context: fork` + `agent` (isolated
  subagent run), `paths` (monorepo scoping).

## Body

- Every line stays in context for the rest of the session once the skill loads — write only what
  Claude wouldn't already know (project/domain specifics, gotchas, exact steps), not generic
  explanations.
- State what to do, not how or why it works internally.
- Structure over prose: numbered steps for procedures, a Gotchas list for surprising facts, a short
  When to use/Skip section for edge cases — avoid long paragraphs.
- Keep the whole SKILL.md under 500 lines; move detailed reference material to separate files the
  skill points to.
- Wrap prose lines at roughly 100 characters — long unwrapped lines are harder to review in diffs
  and editors without soft-wrap.

## Language

- Write skills in English by default — Claude Code's own skill docs and the wider ecosystem
  (Superpowers, agentskills.io) are English, and triggers/keywords match more reliably in English.
  Only write a skill in another language when the user explicitly asks for that language.
