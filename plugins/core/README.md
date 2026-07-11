# core

Core coding best practices — skills and rules for cleaner code.

## Agents

- `quick-reviewer` — reviews code for quality and best practices.
- `preview-simplifier` — simplifies and refines code for clarity, consistency, and maintainability while preserving functionality.

## Commands

- `/quick-review` — delegates to the `quick-reviewer` agent.
- `/preview-simplify` — delegates to the `preview-simplifier` agent.
- `/deep-review` — multi-agent local code review with scope detection, parallel reviewers, and validation.

## Scripts

- `install-rules.py` / `install-rules.ps1` — copy `rules/*.md` into
  `.claude/rules/plugins/nicecode/core/`, using each file's frontmatter
  `version` to skip already up-to-date files and overwrite stale ones. Require
  an explicit `--scope project` (into the current project) or `--scope user`
  (into the home directory, applies to every project) — run explicitly (see
  the `install-rules` skill) — there is no automatic trigger.

## Hooks

- `PreToolUse` (Bash) → `check-uv.py` — guards against running Python tooling without `uv`.
- `PostToolUse` (Edit/Write) → `format-python.sh` — auto-formats Python files.
- `PostToolUse` (Edit/Write) → `format-powershell.ps1` — auto-formats PowerShell files.
- `PostToolUse` (Edit/Write) → `fix-markdown.ps1` — auto-fixes markdown formatting.
- `PostToolUse` (Edit/Write) → `mermaid-lint.ps1` — lints Mermaid diagrams in markdown.
- `PostToolUse` (Edit/Write) → `check-bash.sh` — validates bash scripts.
- `PostToolUse` (Edit/Write/Bash) → `remove-nul.ps1` — strips null bytes from output.

## Rules

- `clean-code.md` — cross-language clean-code principles (naming, functions, design, error handling).
- `bash.md` — Bash scripting conventions.
- `python.md` — Python conventions.
- `csharp-code-style.md` — C# code style.
- `csharp-doc-style.md` — C# XML documentation style.
- `csharp-mstest.md` — C# unit testing with MSTest.
- `powershell.md` — PowerShell scripting conventions.
- `powershell-pester-5.md` — PowerShell testing with Pester 5.
- `rust.md` — Rust conventions.
- `ansible.md` — Ansible playbook conventions.
- `markdown-style.md` — markdown style rules the auto-fixer cannot enforce.
- `hooks.md` — conventions for writing Claude Code hooks.
- `nicecode-test.md` — `nicecode status` smoke-test command.

## Skills

- `coding-discipline` — behavioral guidelines to reduce common LLM coding mistakes.
- `commit` — interactive git commit workflow with formatting rules.
- `explain` — thorough analysis of a file or module: what it does, how it connects, how it can break.
- `install-rules` — installs/updates the versioned rule files into this project.
- `nofiles` — constrain Claude to answer without opening any additional files.
- `python-env` — Python environment and dependency management via `uv`.
- `skillify` — capture the current session's repeatable process into a reusable skill.
- `summary` — summarize the current conversation and save it to a markdown file.
