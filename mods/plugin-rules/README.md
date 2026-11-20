# plugin-rules

Delivers the `rules/*.md` of installed plugins to Claude. Claude Code loads rules only from
`.claude/rules/` and `~/.claude/rules/`, never from a plugin, so without this mod a plugin's
rules had to be copied there by hand. With it, the rules always match the installed plugin
version and there is nothing to copy or update.

Requires Claude Code 2.1.328 or newer.

## Install

Claude Code only

```sh
claude plugin marketplace add lachtan/nicecode
claude plugin install plugin-rules@nicecode
```

To try local changes without installing, run `claude --plugin-dir mods/plugin-rules`.

## How the rules reach Claude

Each rule goes to Claude at most once per conversation, as a reminder that starts
`Contents of <path> (rules from the <plugin> plugin):`. This is how Claude Code itself
delivers a rule with `paths:`.

- A rule without `paths:` goes along with the first prompt, or with the first `Read`, `Edit`
  or `Write`.
- A rule with `paths:` goes along with the first `Read`, `Edit` or `Write` of a file one of its
  globs matches. The path is matched relative to the working directory.
- A subagent gets the rules on its own, with its first `Read`, `Edit` or `Write`.
- After a compaction or `/clear`, the rules are sent again.

A rule without frontmatter, or without `paths:` in it, applies to every file. Only a block list
under `paths:` is read:

```yaml
---
paths:
  - "**/*.sh"
---
```

A glob may use `**/`, `**`, `*`, `?` and `{a,b}`; every other character is literal.

A rule whose `paths:` cannot be read this way is skipped, rather than applied to the wrong files:
an inline list, a string, no item under the key, or a glob with an unclosed `{`. The debug log
(`claude --debug`) names each skipped rule.

Within a plugin the rules are sent in the order of their file names.

## Migrating from copied rules

Rules copied by the old `install-rules` skill would now reach Claude twice. Delete the copies:

```sh
rm -rf "$HOME/.claude/rules/plugins/nicecode"
rm -rf .claude/rules/plugins/nicecode   # in each project that had them
```

## Known trade-offs

- Reloading the mod (`/reload-plugins`, or **Apply** in `skill-toggle`) forgets what was sent,
  so each rule is sent once more. That costs a few kB of tokens.
- A subagent that never uses `Read`, `Edit` or `Write` gets no rules: there is no hook on a
  subagent's prompt.
- Only the files directly in `rules/` are read, not those in its subfolders.
- `NotebookEdit` triggers no rules, so a rule with `paths:` for `*.ipynb` is sent only when the
  notebook is read with `Read`.
- A plugin that is itself a mod (it has a hooks module) may register before this one, and its
  rules are then not seen. Keep rules in a plugin without a hooks module.
- Claude Code's own background agents (compaction, memory) also get rules when they read
  files. This is harmless.
