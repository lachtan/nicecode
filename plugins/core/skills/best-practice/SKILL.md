---
name: best-practice
description: >
  Do a task the idiomatic way from official docs and best practices, ignoring
  how the repo already does it.
disable-model-invocation: true
user-invocable: true
managed-by: https://github.com/lachtan/nicecode
version: "1.0.0"
last-change: "2026-07-11 10:06:11"
---

# Best practice (outside the repo)

For this task, do NOT search the existing repo/project for "how it's already done" —
it might be an experiment, a mistake, or a deliberate exception, and it's irrelevant here.

## Steps

1. Do not start by searching or grepping the repo/code/config for a pattern to copy.
2. Look up the official documentation for the technology/tool (WebSearch/WebFetch) and
   generally accepted best practices.
3. Follow the recommended/idiomatic approach from the documentation, not what's in the repo.
4. For concrete environment facts that can't be derived from documentation (hostname, paths,
   versions, credentials), ask the user directly. If the same approach/values already exist
   in the repo, offer them as an optional choice — don't adopt them automatically.
5. Only search the repo if it's necessary to actually complete the task (e.g. writing to a
   tracking file per the project's CLAUDE.md) — not to look for a pattern.
