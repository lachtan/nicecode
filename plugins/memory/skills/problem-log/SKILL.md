---
name: problem-log
description: >
  Use when a bug, config issue, or architectural decision has been identified
  or resolved. Also use before investigating any issue — check existing logs
  for prior solutions first. Maintains BUGS.md, GOTCHAS.md, and DECISIONS.md.
disable-model-invocation: false
user-invocable: true
---

# Problem Log

## File routing

All files live in `.claude/memory/`:

- `.claude/memory/BUGS.md` — reproducible errors, exceptions, wrong behavior
- `.claude/memory/GOTCHAS.md` — config quirks, env issues, non-obvious behavior, tooling traps
- `.claude/memory/DECISIONS.md` — approach or architecture decisions made to resolve a problem

## Lookup

Before investigating any bug or config issue, read `.claude/memory/BUGS.md` and
`.claude/memory/GOTCHAS.md` and check if a matching or similar entry exists. If
found, apply the known fix before trying anything else. Mention the match to the user.

## Entry format

One entry = max 4 lines:

```
## Short title · YYYY-MM-DD · [OPEN|RESOLVED|DECISION]
Cause: root cause or hypothesis (use "unknown" if unclear)
Fix/Decision: concrete steps, commands, or rationale
Prevention: what to check next time (omit if not applicable)
```

## Rules

- Create `.claude/memory/` if it does not exist yet
- Create the file with a `# Bug Log` / `# Gotcha Log` / `# Decision Log` header
  if it does not exist yet
- Add new entries at the top of the file (newest first)
- On resolution: update status in place, fill in Cause and Fix
- Keep each file under 80 entries — when exceeded, move all [RESOLVED] entries
  older than 90 days to `.claude/memory/archive/BUGS_archive.md` (same format, no deletions)
- Never delete entries, only change status or archive them
