---
name: deep-review
description: >-
  Use when reviewing changed code in depth — a multi-agent local review with scope detection,
  parallel reviewers and a validation pass, auditing against clean-code rules and every
  applicable CLAUDE.md. Read-only: reports findings, never edits a file.
argument-hint: "[staged|branch|last|A..B|paths] [focus]"
disable-model-invocation: true
user-invocable: true
allowed-tools:
  - Agent
  - Bash(git diff:*)
  - Bash(git log:*)
  - Read
  - Glob
  - Grep
origin: https://github.com/anthropics/claude-code/blob/main/plugins/code-review/commands/code-review.md
managed-by: https://github.com/lachtan/nicecode
version: "1.2.0"
---

Perform a thorough local code review of the user's changes described in `$ARGUMENTS`.

**Agent assumptions (apply to all subagents you launch):**
- All tools are functional and will work without error. Do not test tools or make exploratory calls. Make sure this is clear to every subagent that is launched.
- Only call a tool if it is required to complete the task. Every tool call should have a clear purpose.

Follow these steps precisely:

1. **Pre-flight (haiku).** Launch a haiku agent to determine the review scope from `$ARGUMENTS` and collect the diff.

   Scope detection — `$ARGUMENTS` may contain a scope token in any position. Detection order: keywords `staged` / `branch` / `last` → range with `..` (e.g. `HEAD~3..HEAD`) → existing file paths → remaining text is a focus area. When no scope is given, default to staged changes if any exist, otherwise the full branch diff versus the base branch.

   The agent must run the appropriate `git diff` and `git log --oneline`, then return:
   - The resolved scope (one of: staged, branch, last, range, paths).
   - The raw diff.
   - Commit messages in the scope.
   - The focus area (if any).
   - A verdict: `meaningful` or `skip`. Mark `skip` when the diff is empty or contains only whitespace, formatting, or pure comment-reflow changes.

   If the verdict is `skip`, output `No meaningful changes to review.` and stop.

2. **CLAUDE.md index (haiku).** Launch a haiku agent to produce the list of `CLAUDE.md` file paths (not contents) relevant to the changed files. Include:
   - The repository root `CLAUDE.md`, if it exists.
   - Every `CLAUDE.md` found in any directory containing a changed file, or in any parent directory above it.

   Return only file paths.

3. **Summary (sonnet).** Launch a sonnet agent to read the diff and commit messages from step 1 and return a 2–4 sentence summary of the author's intent. This summary is shared context for step 4.

4. **Parallel review (4 agents in parallel).** Launch four agents at once, independently. Each receives: the diff from step 1, the list of CLAUDE.md paths from step 2, the summary from step 3, the focus area (if any), and the HIGH SIGNAL filter below. Each returns a list of issues where each issue is `{description, reason, file, line, severity}` with severity in `Critical` / `Important` / `Minor`.

   - **Agents 1 + 2 — CLAUDE.md compliance (sonnet, parallel).** Read `${CLAUDE_PLUGIN_ROOT}/rules/clean-code.md` and every `CLAUDE.md` returned by step 2. Audit the diff for violations. **Scoping rule:** when evaluating a given file, consider only `CLAUDE.md` files that share the file's path or sit in a parent directory — never unrelated branches of the tree.
   - **Agent 3 — diff-only bug scan (opus).** Read only the diff. Flag significant bugs visible from the diff itself. Do not read surrounding context. Do not flag anything you cannot validate from the diff alone.
   - **Agent 4 — contextual bug scan (opus).** May read surrounding files. Focus on security issues (injection, hardcoded secrets, unvalidated input, path traversal, auth flaws), correctness (logic errors, race conditions, null handling, off-by-one, unhandled edge cases), and error handling (swallowed exceptions, lost context, missing propagation) within the changed code.

   **HIGH SIGNAL filter — mandatory for all four agents.**

   Flag only issues where:
   - The code will fail to compile or parse (syntax errors, type errors, missing imports, unresolved references).
   - The code will definitely produce wrong results regardless of inputs (clear logic errors).
   - Clear, unambiguous CLAUDE.md or clean-code.md violations where you can quote the exact rule being broken.

   Do NOT flag:
   - Code style or general quality concerns.
   - Potential issues that depend on specific inputs or state ("could fail if…").
   - Subjective suggestions or improvements.
   - Pre-existing issues outside the diff.
   - Pedantic nitpicks a senior engineer would not flag.
   - Issues mentioned in CLAUDE.md but explicitly silenced in the code (e.g., via a lint-ignore comment).

   If you are not certain an issue is real, do not flag it. False positives erode trust.

5. **Validation (parallel).** For each issue returned by any agent in step 4, launch a validation subagent in parallel. Use **opus** for bug/logic issues, **sonnet** for CLAUDE.md/clean-code violations. The validator receives: the issue description, the summary from step 3, and the diff. Its sole job is to confirm with high confidence that the issue is real. For example, for "variable not defined," verify in the code that the variable is in fact undefined in the relevant scope. For a CLAUDE.md violation, verify that the cited rule is in-scope for the file and is actually broken. Return `{validated: true|false, reason}`.

6. **Filter.** Drop every issue where `validated` is false.

7. **Deduplicate.** Agents 1+2 and agents 3+4 often report the same issue. Merge duplicates into a single entry. When merging, keep the most specific description and the highest severity.

8. **Output.** Print findings grouped by severity (Critical first, then Important, then Minor). For each finding:
   - A file/line link in the form `[path/to/file.ext:42](path/to/file.ext#L42)`.
   - What the issue is and why it matters — quote the specific rule for CLAUDE.md/clean-code violations.
   - A concrete fix: code, or a clear instruction — not just criticism.

   End with a one-line summary of total findings by severity. If no findings survive, print exactly: `No issues found. Checked for bugs and CLAUDE.md compliance.`
