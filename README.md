# NiceCode

A collection of best practices for multiple programming languages.
The primary goal is to provide skills, rules, commands, and hooks that help Claude agents write cleaner, more readable, and simpler code.
Simplicity first.

## Languages

- C#
- F#
- Rust
- Python
- Bash

## Installation

```text
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
To install them into your project, run:

```
/install-rules
```

This creates a symlink from `.claude/rules/nicecode/` to the plugin's `rules/` directory.
After a plugin update, a `SessionStart` hook automatically re-creates the symlink to the new version.

Since the symlink points to an absolute path specific to each user, add it to `.gitignore`:

```text
.claude/rules/nicecode/
```

The plugin warns you automatically if this entry is missing.

To remove the symlink:

```
/uninstall-rules
```

## Documentation

- [Create and distribute a plugin marketplace](https://code.claude.com/docs/en/plugin-marketplaces)
- [Create plugins](https://code.claude.com/docs/en/plugins)
