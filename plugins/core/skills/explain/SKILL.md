---
name: explain
description: Thoroughly examine and analyze a file or module — what it does, how it connects, and how it could break.
disable-model-invocation: true
user-invocable: true
---

Thoroughly examine and analyze: $ARGUMENTS

Explain:

- What this file/module does and why it exists
- How it connects to the rest of the codebase
- What I should know before I start modifying it
- What communication protocols it uses, if any
- 3 most likely ways someone could accidentally break it

DO NOT make any changes. Only study and explain.
