---
name: grill-me
description: |
  Interview the user relentlessly about a plan or design until reaching shared understanding,
  resolving each branch of the decision tree. Use when user wants to stress-test a plan, get
  grilled on their design, or mentions "grill me".
disable-model-invocation: false
user-invocable: true
origin: https://github.com/mattpocock/skills/blob/main/skills/productivity/grill-me/SKILL.md
---

Interview me relentlessly about every aspect of this plan until we reach a shared understanding.
Walk down each branch of the design tree, resolving dependencies between decisions one-by-one.
For each question, provide your recommended answer.

Ask the questions one at a time.

If a question can be answered by exploring the codebase, explore the codebase instead.
Dispatch a subagent for non-trivial exploration.

Before asking, name the assumption your question would resolve.

Stop when you can write a one-paragraph implementation sketch with zero hand-waving
and no decision deferred to "we'll figure that out later."
