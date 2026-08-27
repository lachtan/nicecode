---
name: search-first
description: >-
  Use before writing new code for a feature, utility, parser, validator, client, or integration —
  check whether it already exists in this repo, in current dependencies, or in the standard library.
  Triggers on add, implement, build, create, integrate, "search first", "check what we have",
  "is there a library for this". Not for bug fixes, refactors, renames, or tests of existing code.
disable-model-invocation: false
user-invocable: true
origin: https://github.com/affaan-m/ECC/blob/main/skills/search-first/SKILL.md
managed-by: https://github.com/lachtan/nicecode
version: "1.0.0"
---

# Search First

Reuse beats writing new. Search internal before external, cap the whole search at ~3 minutes
of tool calls.

## Steps

1. **Search this repo** for the concept by name and its synonyms — for *rate limiting* also
   `throttle`, `quota`, `limiter`, `bucket`. Scan directory names for a module that would own it.
2. **Read the dependency manifest.** A package already in the project solves it for free.
3. **If you found a fit, stop** — propose reusing or extending it and skip step 4.
4. **Look outside**, in this order: standard library → docs of a framework already in use →
   mature, actively maintained package in the project's registry. Blog posts and tutorials
   are not a primary source.

## Report before writing code

One line, then proceed:

`Search first: <what exists, or "nothing relevant"> → <reuse X | extend X | add Y | write new>`

## Skip when

- The task is a bug fix, refactor, rename, formatting, or a test for existing code.
- The answer is an obvious standard-library one-liner.
- A new dependency would replace under ~30 lines of straightforward code.
