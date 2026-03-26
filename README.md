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

The plugin includes coding rules (clean code, C# style, PowerShell, testing, etc.) that are not loaded automatically by the plugin system.
A `SessionStart` hook automatically creates a symlink from `.claude/rules/nicecode/` to the plugin's `rules/` directory when the plugin is enabled in the project.

To manually install or reinstall rules, run `/install-rules`. To remove them, run `/uninstall-rules`.

Since the symlink points to an absolute path specific to each user, add it to `.gitignore`:

```text
.claude/rules/nicecode/
```

The plugin warns you automatically if this entry is missing.

## Documentation

- [Create and distribute a plugin marketplace](https://code.claude.com/docs/en/plugin-marketplaces)
- [Create plugins](https://code.claude.com/docs/en/plugins)
