---
name: install-statusline
description: >-
  Installs or updates the nicecode core plugin's statusline scripts into this
  project's .claude/scripts directory (or the user's home directory) and wires
  the "statusLine" key in settings.json to point at it.
  Use when the user asks to "install statusline", "install the status line",
  "set up statusline", "sync statusline", or "update statusline".
user-invocable: true
disable-model-invocation: false
managed-by: https://github.com/lachtan/nicecode
version: "1.0.0"
last-change: "2026-07-11 11:41:33"
---

# Install Statusline

Copies `statusline.sh`/`statusline.py`/`statusline.ps1` into
`.claude/scripts/plugins/nicecode/core/`, either under the current project or
under the user's home directory, and sets `statusLine` in the matching
`settings.json` to run the installed `statusline.sh`. The three files are
versioned as one bundle (tracked via a `version` marker in `statusline.sh`),
so re-running this only overwrites them when the plugin's version is newer —
a target you've customized without a matching `managed-by`/`version` marker is
left untouched and reported as skipped. Likewise, if `statusLine` in
`settings.json` is already set to something else (e.g. your own personal
statusline), it is left alone and reported as skipped.

This is a plain bash script (`install-statusline.sh`, no PowerShell
counterpart) requiring `bash` and `jq` on PATH. On Windows this means running
it from git-bash or WSL — it does not run under plain `pwsh`. The installed
statusline itself is still cross-platform (its `statusline.sh` dispatcher
falls back to `pwsh` if `python3` isn't available).

## Steps

1. Ask the user (`AskUserQuestion`) whether to install into this project only,
   or into their home directory to apply across every project. Always ask,
   even if the request sounds unambiguous.
2. Locate the script on disk — `${CLAUDE_PLUGIN_ROOT}` does not reliably
   expand here (known Claude Code limitation, same class of bug as
   [#9354](https://github.com/anthropics/claude-code/issues/9354)), so resolve
   the real path instead of using the literal variable in a command:
   - Check `echo $CLAUDE_PLUGIN_ROOT`. If non-empty and
     `<that>/scripts/install-statusline.sh` exists, use it.
   - Otherwise, if you're working directly in the `nicecode` source repo, use
     `plugins/core/scripts/install-statusline.sh` relative to the repo root.
   - Otherwise, search the installed plugin cache, e.g.
     `find ~/.claude/plugins/cache -path '*/core/*/scripts/install-statusline.sh' 2>/dev/null`.
   - If none of these find the script, tell the user and stop — do not guess a path.
3. Confirm `bash` and `jq` are on PATH; if either is missing, tell the user
   and stop.
4. Run the resolved script (its real, absolute path — not
   `${CLAUDE_PLUGIN_ROOT}` in the command) with the chosen `--scope`.
   `${CLAUDE_PROJECT_DIR}` has the same expansion problem as
   `${CLAUDE_PLUGIN_ROOT}` — for project scope, omit the positional project
   directory entirely and let the script default to the current directory
   (verify with the shell that you're actually inside the project first):
   - Project scope: `bash <resolved-path>/install-statusline.sh --scope project`
   - User scope: `bash <resolved-path>/install-statusline.sh --scope user`
5. Report the script's output to the user (installed/updated/skipped for both
   the script files and the `statusLine` settings key). If the user's
   `settings.json` already has an unrelated `statusLine`, tell them so they
   can switch it manually if they want.
