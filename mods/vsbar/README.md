# vsbar

A status line for the Claude Code VS Code extension, which does not draw the `statusLine` from
`settings.json`. It shows the same facts as the core plugin's terminal statusline:

```text
vsbar plugin 🖥️ debian-dev | 🌿 master | 💡 Opus 5.5 / high / 1M | ↓ 13% / 134k | ↑ 11k
```

| Part | Meaning |
| --- | --- |
| `🖥️ debian-dev` | Host name, lower case. |
| `🌿 master` | Current git branch; left out outside a repository or on a detached HEAD. |
| `💡 Opus 5.5 / high / 1M` | Model, effort of the last request (left out until the first one), context window. |
| `↓ 13% / 134k` | Context used: share of the window and tokens. |
| `↑ 11k` | Output tokens of this session's main loop, subagents excluded; reset by `/clear`. |

Thousands are truncated (`11.6k` shows as `11k`), millions keep one decimal (`1.5M`).

Requires Claude Code 2.1.328 or newer.

## Install

Claude Code only; Codex does not run mods.

```sh
claude plugin marketplace add lachtan/nicecode
claude plugin install vsbar@nicecode
```

To try local changes without installing, run `claude --plugin-dir mods/vsbar`.

## Limits

- **VS Code only.** In a terminal the mod shows nothing, so the terminal keeps its own `statusLine`
  (see [Status line](../../README.md#status-line)).
- **No colors.** The mod pins the line with `ui.status`, which takes plain text; ANSI codes would show
  up escaped. A row that can be colored (`AbovePrompt`) is not drawn in VS Code.
- **The `vsbar plugin` label** in front of the line is drawn by Claude Code and cannot be hidden.
- **Model name** is derived from the model id (`claude-opus-5-5` → `Opus 5.5`); an id of another shape
  is shown as it is.
- **`↑` counts from the mod's start.** A resumed session starts again from 0, unlike the terminal
  statusline, which reads the whole transcript.

## How it works

`hooks/register.ts` wires five events to `hooks/status.ts`:

- `session.start`, `session.measure` (the context fill or the cost changed) and `turn.complete`
  redraw the line.
- `turn.step` remembers the effort level each main-loop request is sent at; the session API has
  no effort getter.
- `turn.complete` also adds the turn's output tokens; `session.end` with reason `clear` resets them.

Before drawing, the mod checks `session.surfaces()` for `vscode`; elsewhere it clears the line and
runs no command. Branch and host name come from `git branch --show-current` and `hostname`
(`COMPUTERNAME` on Windows). The effort and the output tokens live in the session's state
(`state`), so they survive a reload of the mod.
