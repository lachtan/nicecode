---
name: install-rules
description: >
  Installs or updates the nicecode core plugin's rule files
  (coding conventions) into this project's .claude/rules directory, or into
  the user's home directory so they apply across every project.
  Use when the user asks to "install rules", "update rules", "sync rules",
  "refresh nicecode rules", or reports that rules aren't loading.
user-invocable: true
disable-model-invocation: false
managed-by: https://github.com/lachtan/nicecode
version: "1.2.0"
---

# Install Rules

Copies `core`'s rule files into `.claude/rules/plugins/nicecode/core/`, either
under the current project or under the user's home directory. Each rule file
carries a `version` in its frontmatter, so re-running this only overwrites
files where the plugin's version is newer than what's already installed —
files you've customized without a matching `version` are left untouched and
reported as skipped.

Rules the plugin no longer ships are deleted from the target directory, so a rule
retired upstream doesn't linger forever. Only files carrying nicecode's own
`managed-by` are removed — your own rules and rules from another source stay.

## Steps

1. Ask the user (`AskUserQuestion`) whether to install into this project only,
   or into their home directory to apply across every project. Always ask,
   even if the request sounds unambiguous.
2. Detect the OS.
3. Locate the script on disk — `${CLAUDE_PLUGIN_ROOT}` does not reliably
   expand here (known Claude Code limitation, same class of bug as
   [#9354](https://github.com/anthropics/claude-code/issues/9354)), so resolve
   the real path instead of using the literal variable in a command:
   - Check `echo $CLAUDE_PLUGIN_ROOT` (`echo $env:CLAUDE_PLUGIN_ROOT` on
     Windows). If non-empty and `<that>/scripts/install-rules.py` (or `.ps1`)
     exists, use it.
   - Otherwise, if you're working directly in the `nicecode` source repo, use
     `plugins/core/scripts/install-rules.py` / `.ps1` relative to the repo root.
   - Otherwise, search the installed plugin cache, e.g.
     `find ~/.claude/plugins/cache -path '*/core/*/scripts/install-rules.py' 2>/dev/null`
     (Windows: `Get-ChildItem -Recurse -Filter install-rules.ps1 ~/.claude/plugins/cache`).
   - If none of these find the script, tell the user and stop — do not guess a path.
4. Run the resolved script (its real, absolute path — not `${CLAUDE_PLUGIN_ROOT}`
   in the command) with the chosen `--scope`. `${CLAUDE_PROJECT_DIR}` has the
   same expansion problem as `${CLAUDE_PLUGIN_ROOT}` — for project scope, omit
   the positional project directory entirely and let the script default to
   the current directory (verify with the shell that you're actually inside
   the project first):
   - Project scope:
     - Linux/macOS: `python3 <resolved-path>/install-rules.py --scope project`
     - Windows: `pwsh -File <resolved-path>/install-rules.ps1 -Scope project`
   - User scope:
     - Linux/macOS: `python3 <resolved-path>/install-rules.py --scope user`
     - Windows: `pwsh -File <resolved-path>/install-rules.ps1 -Scope user`
5. Report the script's output to the user (installed / updated / removed / skipped
   counts and files). Call out removals explicitly — deleting a retired rule is
   destructive and the user should see which files went.
