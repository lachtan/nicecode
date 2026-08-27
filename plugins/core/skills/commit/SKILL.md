---
name: commit
description: Use when committing changes to git — provides commit message formatting rules and an interactive commit workflow.
disable-model-invocation: false
user-invocable: true
managed-by: https://github.com/lachtan/nicecode
version: "1.0.0"
---

# Git Commit

Commit message formatting rules and an interactive commit workflow.

## Formatting Rules

- **Language:** Choose based on context of existing commits. If unclear, ask the user.
- **Subject line:** first line, max ~100 characters. Concisely describes the essence of the change — choose whether to emphasize *what* changed or *why*, depending on context.
- **Body:** separated from the subject by a blank line, optional. Keep it brief and to the point — only what is not obvious from the diff. Avoid unnecessarily long descriptions.
- **Free format:** do not use prefixes like `feat:`, `docs:`, `refactor:`.
- **No co-authorship:** do not add a `Co-Authored-By: ...` line to commit messages unless the user explicitly requests it.

## Workflow

1. Run `git status` — check the state of the working tree and staging area.
2. If there are unstaged or untracked changes, ask the user whether to add them to staging (`git add .`).
3. If there are no staged changes, inform the user and stop.
4. Show the diff of staged changes for context.
5. Based on the diff, propose a commit message following the formatting rules above.
6. Show the proposed commit message to the user for approval.
7. After approval, run `git commit`.
