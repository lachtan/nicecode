# NiceCode

Best practices for writing clean, readable, and simple code with Claude Code. Simplicity first.

## Languages

C#, PowerShell, Python, Bash, Rust

## Installation

```
/plugin marketplace add lachtan/nicecode
/plugin install core@nicecode
/plugin install mattpocock@nicecode
```

Per project:

```bash
claude plugin marketplace add lachtan/nicecode --scope=project
claude plugin install core@nicecode --scope=project
```

## Plugins

- [core](plugins/core/README.md) — coding best practices: agents, commands, hooks, rules, and skills.
- mattpocock-skills — skills from [mattpocock/skills](https://github.com/mattpocock/skills) (engineering + productivity).

## Rules

The plugin system does not load plugin rules automatically. A `SessionStart` hook creates a symlink so Claude Code picks them up as local project rules:

```
.claude/rules/plugins/nicecode/core  ->  <plugin-install-dir>/rules/
```

A `ConfigChange` hook handles the reverse: when the plugin is explicitly disabled in project settings, it removes the symlink.

**Known limitation:** When the plugin is uninstalled (not just disabled), the symlink becomes broken but is not actively cleaned up. Broken symlinks are harmless (Claude Code cannot load rules from a nonexistent target) but remain on disk until manually removed.

The symlink target is an absolute path specific to each machine. Add it to `.gitignore`:

```
.claude/rules/plugins/
```

## Troubleshooting

Set `NICECODE_DEBUG=1` to enable logging. The log is written to `$TMPDIR/install-rules.log`.

## Philosophy

The guiding principle is simplicity first, inspired by [Code Simplicity](https://www.amazon.com/dp/1449313892) by Max Kanat-Alexander: the most important property of software is simplicity, and complexity is the root cause of most bugs and maintenance cost.

## Documentation

- [Plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces)
- [Plugins](https://code.claude.com/docs/en/plugins)
