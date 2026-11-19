# NiceCode

A plugin marketplace for Claude Code and Codex: rules, skills and hooks for clean, readable,
simple code in C#, PowerShell, Python, Bash and Rust.

The guiding principle is simplicity first, after
[Code Simplicity](https://www.amazon.com/dp/1449313892) by Max Kanat-Alexander: complexity is
the root cause of most bugs and maintenance cost.

## Plugins

| Plugin | What it gives you |
| --- | --- |
| [core](plugins/core/README.md) | Coding rules, skills and hooks — start here. |
| [lab](plugins/lab/README.md) | Experimental skills before they move to `core`. |
| [mattpocock](plugins/mattpocock/README.md) | `grill-me` and `research`, vendored from [mattpocock/skills](https://github.com/mattpocock/skills). |
| [ponytail](plugins/ponytail/README.md) | Anti-over-engineering reflex, toggled with `/ponytail`. |
| [rsj](plugins/rsj/README.md) | Announce actions before running them; never take a question as approval. |

## Install

### Claude Code

```bash
claude plugin marketplace add lachtan/nicecode
claude plugin install core@nicecode
```

Install the other plugins the same way (`lab@nicecode`, …). Inside a session, the same
commands work as `/plugin marketplace add` and `/plugin install`.

Both commands take `--scope`:

| Scope | Applies to | Stored in |
| --- | --- | --- |
| `user` (default) | you, in every project | `~/.claude/settings.json` |
| `project` | every collaborator of the repo | `.claude/settings.json` (committed) |
| `local` | you, in this repo only | `.claude/settings.local.json` (gitignored) |

### Codex

```bash
codex plugin marketplace add lachtan/nicecode
codex plugin add core@nicecode
```

Or pick the plugins from `/plugins` inside [Codex](https://developers.openai.com/codex/plugins).
Codex asks you to trust plugin hooks before they run; review them under `/hooks`. It gets the
skills and hooks, but not the rules or the `plan-reviewer` agent.

## Rules and status line

Installing `core` gives you its skills and hooks. Claude Code does not load a plugin's rules
or register its status line, so those two are installed on request. Ask Claude:

- **"install rules"** — copies the rule files into `.claude/rules/plugins/nicecode/core/`.
- **"install statusline"** — copies the scripts into `.claude/scripts/plugins/nicecode/core/`
  and points `statusLine` in `settings.json` at them. Needs `bash` and `jq`.

Claude asks for a scope first: `project` installs into the current project, `user` into
`~/.claude/` so it applies everywhere.

Updating is the same request again. Files are versioned: a newer plugin version overwrites
the installed copy, while rule files you wrote yourself and a `statusLine` you set to
something else are left alone.

For the `project` scope, gitignore the copies — the installer regenerates them:

```gitignore
.claude/rules/plugins/
.claude/scripts/plugins/
```

### Without Claude

From a clone of this repo:

```bash
python3 plugins/core/scripts/install-rules.py --scope user
pwsh -File plugins/core/scripts/install-rules.ps1 -Scope user
bash plugins/core/scripts/install-statusline.sh --scope user
```

With the `project` scope, the target defaults to the current directory; pass another one as
a positional argument (`-ProjectDir` in PowerShell).

## Contributing

Plugin sources live in `src/`; `plugins/` is generated from them. See [CLAUDE.md](CLAUDE.md).
