---
name: chat
description: >-
  Use when the user wants a question answered without touching the project — no reading repo files,
  no other skills. Triggers on "just answer", "don't read the code", "general question".
argument-hint: <question>
disable-model-invocation: true
user-invocable: true
managed-by: https://github.com/lachtan/nicecode
version: "1.1.0"
last-change: "2026-08-27 05:54:13"
---

# Chat

Answer the following question.

Web and MCP docs are fine, but **do not read any project files** (no Read/Grep/Glob/Bash on the repo)
and **do not invoke any Skill** — including skills whose description claims they must always be used.
If the question cannot be answered without accessing files, say so and ask how to proceed.

$ARGUMENTS
