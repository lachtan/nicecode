---
name: handoff
description: >-
  Use when the user asks for a handoff or is about to /clear, compact or restart —
  formats this session's context as a copy-pasteable brief for a fresh session.
disable-model-invocation: false
user-invocable: true
managed-by: https://github.com/lachtan/nicecode
version: "1.0.0"
last-change: "2026-09-11 12:48:38"
---

# Handoff

Render this session's context as one fenced markdown block, ready to copy
into a fresh session. The reader has the repo but no conversation history,
so write only what the repo does not show: decisions and their reasons,
what was ruled out and why, constraints the user set, what is left.
No chronology, no code, no narrative. Omit empty sections. Mark anything
you are not sure about with `(unverified)`.

```markdown
# Handoff: <task in one line>

## Current state

## Constraints

## Decisions

## Ruled out

## Next step

## Done when
```
