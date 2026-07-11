---
description: Answer a question without reading project files or invoking skills
argument-hint: <question>
managed-by: https://github.com/lachtan/nicecode
version: "1.0.0"
---

Answer the following question.
Web and MCP docs are fine, but **do not read any project files** (no Read/Grep/Glob/Bash on the repo)
and **do not invoke any Skill** — including skills whose description claims they must always be used.
If the question cannot be answered without accessing files, say so and ask how to proceed.

$ARGUMENTS
