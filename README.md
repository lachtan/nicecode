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

```
/plugin marketplace add lachtan/nicecode
/plugin install core@nicecode
```

## Rules

The plugin includes coding rules (clean code, C# style, PowerShell, testing, etc.) that are not loaded automatically by the plugin system.
To install them into your project, run:

```
/install-rules
```

This copies all rules into `.claude/rules/nicecode/` in your project directory.
Existing rules are overwritten on re-install.

To remove all installed rules:

```
/uninstall-rules
```

## Documentation

- [Create and distribute a plugin marketplace](https://code.claude.com/docs/en/plugin-marketplaces)
- [Create plugins](https://code.claude.com/docs/en/plugins)
