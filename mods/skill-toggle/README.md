# skill-toggle

Turn off individual skills of installed plugins. All skills stay on until you turn one off.

Requires Claude Code 2.1.328 or newer.

## Run

```sh
claude --plugin-dir mods/skill-toggle
```

## Use

1. Run `/skill-toggle`. A pane lists every plugin skill.
2. Uncheck the skills you want off (`[x]` = on, `[ ]` = off).
3. Press **Apply (reload plugins)**. Unchecked skills no longer load, so Claude cannot see or run them.

Your choice applies to every project and is kept across sessions.

## Where the choice is stored

`~/.claude/plugins/store/skill-toggle_<id>.json`, key `disabled`:

```json
{ "disabled": ["core:commit", "lab:debug"] }
```

Each entry is `<plugin>:<skill>`. You can edit the list by hand; it takes effect after
`/reload-plugins` or in a new session. The `skills:<plugin>` keys in the same file only list every
skill of each plugin for the pane. An uninstalled plugin stays in the pane until you delete its
`skills:<plugin>` key (and its entries in `disabled`).

Running the mod a different way (`--plugin-dir` now, a marketplace install later) may use a
different file, so the choice may not carry over.
