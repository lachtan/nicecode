# NiceCode

A collection of best practices for multiple programming languages.
The primary goal is to provide skills, rules, and hooks that help Claude agents write cleaner, more readable, and simpler code.
Simplicity first.

## Languages

- C#
- F#
- Rust
- Python
- Bash

## Installation

```
/plugin marketplace add lachtan/nicecode
/plugin install core@nicecode
```

Per project:

```bash
claude plugin marketplace add lachtan/nicecode --scope=project
claude plugin install core@nicecode --scope=project
```

## Rules

The plugin includes coding rules (clean code, C# style, PowerShell, testing, etc.) that the plugin system does not load on its own.
To work around this, a `SessionStart` hook checks whether the plugin is enabled in the project and automatically creates a symlink.
When the plugin is disabled, the hook removes the symlink.

```text
.claude/rules/plugins/nicecode/core  →  <plugin-install-dir>/rules/
```

This makes Claude Code pick up the rules as if they were local project rules.

Since the symlink target is an absolute path specific to each machine, add it to `.gitignore`:

```text
.claude/rules/plugins/
```

## Documentation

- [Create and distribute a plugin marketplace](https://code.claude.com/docs/en/plugin-marketplaces)
- [Create plugins](https://code.claude.com/docs/en/plugins)
