# skill-toggle

Turn off individual skills of installed plugins. All skills stay on until you turn one off.

Requires Claude Code 2.1.328 or newer.

## Project and personal skills

This mod covers plugin skills only. To turn off a skill from `.claude/skills/` (project) or
`~/.claude/skills/` (personal), use Claude Code's own `/skills` menu: highlight the skill, press
`Space` until it shows `off`, then `Esc`. The choice is saved under `skillOverrides` in
`.claude/settings.local.json`, which stays out of git, so it applies only to you in that project:

```json
{ "skillOverrides": { "deploy": "off" } }
```

## Install

Claude Code only; Codex does not run mods.

```sh
claude plugin marketplace add lachtan/nicecode
claude plugin install skill-toggle@nicecode
```

To try local changes without installing, run `claude --plugin-dir mods/skill-toggle`.

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

A marketplace install and a `--plugin-dir` run may use different files, so the choice made in
one does not carry over to the other.
