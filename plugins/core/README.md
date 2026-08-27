# core

Core coding best practices — skills and rules for cleaner code.

## Review skills vs. the bundled ones

Claude Code ships its own review skills — `/code-review` (several finder angles plus a verify pass,
`--fix` to apply the findings, `--comment` to post them on a PR) and `/simplify` (applies the
cleanups straight away). Reach for those when you want the fixes applied for you.

`/deep-review` here is the read-only counterpart: it audits explicitly against
`rules/clean-code.md` and every applicable `CLAUDE.md`, and never touches a file — it reports,
you decide. Lighter read-only variants (`/quick-review`, `/preview-simplify`) live in the
[lab](../lab/README.md) plugin while their overlap with the bundled skills is still unproven.

## Scripts

- `install-rules.py` / `install-rules.ps1` — copy `rules/*.md` into
  `.claude/rules/plugins/nicecode/core/`, using each file's frontmatter
  `version` to skip already up-to-date files and overwrite stale ones. Require
  an explicit `--scope project` (into the current project) or `--scope user`
  (into the home directory, applies to every project) — run explicitly (see
  the `install-rules` skill) — there is no automatic trigger.
- `install-statusline.sh` — copies `statusline.sh`/`statusline.py`/`statusline.ps1`
  into `.claude/scripts/plugins/nicecode/core/` and sets `statusLine` in the
  matching `settings.json`, using a `version` marker in `statusline.sh` to skip
  up-to-date bundles and never overwriting a `statusLine` already set to
  something else. Same `--scope project`/`--scope user` convention (see the
  `install-statusline` skill) — bash + `jq` only, run explicitly.

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
- `python-uv.md` — always use `uv` for Python (never `pip`/`venv`/`pipx`).
- `csharp-code-style.md` — C# code style.
- `csharp-doc-style.md` — C# XML documentation style.
- `csharp-mstest.md` — C# unit testing with MSTest.
- `powershell.md` — PowerShell scripting conventions.
- `powershell-pester-5.md` — PowerShell testing with Pester 5.
- `rust.md` — Rust conventions.
- `markdown-style.md` — markdown style rules the auto-fixer cannot enforce.
- `nicecode-test.md` — `nicecode status` smoke-test command.

## Skills

- `best-practice` — do a task the idiomatic way from official docs, ignoring how the repo already does it.
- `chat` — answers a question without reading project files or invoking skills.
- `coding-discipline` — behavioral guidelines to reduce common LLM coding mistakes.
- `commit` — interactive git commit workflow with formatting rules.
- `deep-review` — multi-agent local code review with scope detection, parallel reviewers, and validation.
- `explain` — thorough analysis of a file or module: what it does, how it connects, how it can break.
- `install-rules` — installs/updates the versioned rule files into this project.
- `install-statusline` — installs/updates the statusline scripts and wires `statusLine` in settings.json.
- `ops-guide` — how to write a step-by-step procedure a human will run at a console.
- `search-first` — check whether something already exists (repo, dependencies, stdlib) before writing new code.
- `skill-authoring` — conventions for writing SKILL.md files so skills trigger reliably.
- `summary` — summarize the current conversation and save it to a markdown file.
