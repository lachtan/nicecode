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
| [matt](plugins/matt/README.md) | `grill-me` and `research`, vendored from [mattpocock/skills](https://github.com/mattpocock/skills). |
| [ponytail](plugins/ponytail/README.md) | Anti-over-engineering reflex, toggled with `/ponytail`. |
| [rsj](plugins/rsj/README.md) | Announce actions before running them; never take a question as approval. |
| [skill-toggle](mods/skill-toggle/README.md) | Claude Code only: turn off chosen skills of installed plugins with `/skill-toggle`. |
| [plugin-rules](mods/plugin-rules/README.md) | Claude Code only: deliver the rules of installed plugins to Claude — install it with `core`. |
| [vsbar](mods/vsbar/README.md) | Claude Code only: a status line for the VS Code extension. |

## Install

### Claude Code

```bash
claude plugin marketplace add lachtan/nicecode
claude plugin install core@nicecode
claude plugin install plugin-rules@nicecode
```

Claude Code does not load a plugin's rules; the `plugin-rules` mod delivers them. Install the
other plugins the same way (`lab@nicecode`, …). Inside a session, the same commands work as
`/plugin marketplace add` and `/plugin install`.

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
skills and hooks, but not the rules, the `plan-reviewer` agent or the `skill-toggle`,
`plugin-rules` and `vsbar` mods.

## Status line

Claude Code does not register a plugin's status line, so it is installed on request. Ask
Claude **"install statusline"**: it copies the scripts into
`.claude/scripts/plugins/nicecode/core/` and points `statusLine` in `settings.json` at them.
Needs `bash` and `jq`.

Claude asks for a scope first: `project` installs into the current project, `user` into
`~/.claude/` so it applies everywhere.

Updating is the same request again. A newer statusline version overwrites what is installed,
while a `statusLine` you set to something else is left alone.

The VS Code extension does not draw `statusLine`; install the [vsbar](mods/vsbar/README.md) mod
there instead.

For the `project` scope, gitignore the copies — the installer regenerates them:

```gitignore
.claude/scripts/plugins/
```

Without Claude, from a clone of this repo:

```bash
bash plugins/core/scripts/install-statusline.sh --scope user
```

With the `project` scope, the target defaults to the current directory; pass another one as
a positional argument.

## Migrating from copied rules

Before `core` 2.0.0 its rules were copied by the `install-rules` skill. With `plugin-rules`
installed those copies would reach Claude twice, so delete them:

```bash
rm -rf "$HOME/.claude/rules/plugins/nicecode"
rm -rf .claude/rules/plugins/nicecode   # in each project that had them
```

## Contributing

Plugin sources live in `src/`; `plugins/` is generated from them. See [CLAUDE.md](CLAUDE.md).
