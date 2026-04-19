# Claude Code — tool list

Usable in the `allowed-tools` frontmatter of slash commands and in `permissions` in `settings.json`.

## Core tools

| Tool | Description | Scoping |
|---|---|---|
| `Read` | Read files | `Read(src/**)` |
| `Write` | Create / overwrite file | `Write(docs/**)` |
| `Edit` | Targeted file edits | `Edit(src/**/*.ts)` |
| `Glob` | Find files by pattern | — |
| `Grep` | Search file contents | — |
| `Bash` | Run a shell command | `Bash(git diff:*)`, `Bash(npm run *)` |
| `WebFetch` | Fetch content from a URL | `WebFetch(domain:example.com)` |
| `WebSearch` | Web search | — |

## Other tools

| Tool | Description | Scoping |
|---|---|---|
| `Agent` | Run a subagent | `Agent(Explore)`, `Agent(custom-name)` |
| `SendMessage` | Message a teammate / resume a subagent | — |
| `AskUserQuestion` | Ask the user (multiple-choice) | — |
| `TeamCreate` | Create an agent team | — |
| `TeamDelete` | Delete an agent team | — |
| `TodoWrite` | Session TODO checklist | — |
| `TaskCreate` | Create a task in the task list | — |
| `TaskGet` | Get details of a specific task | — |
| `TaskList` | List all tasks | — |
| `TaskUpdate` | Change status / dependencies / delete a task | — |
| `TaskStop` | Stop a running background task | — |
| `TaskOutput` | (Deprecated) Output from a background task | — |
| `CronCreate` | Schedule a recurring prompt | — |
| `CronDelete` | Remove a scheduled task | — |
| `CronList` | List scheduled tasks | — |
| `EnterPlanMode` | Enter plan mode | — |
| `ExitPlanMode` | Leave plan mode | — |
| `EnterWorktree` | Create a git worktree and switch to it | — |
| `ExitWorktree` | Leave the worktree and return | — |
| `Monitor` | Background command with streaming output | `Monitor(…)` same as Bash |
| `PowerShell` | Run a PowerShell command | `PowerShell(npm run *)` |
| `NotebookEdit` | Edit a Jupyter notebook | `NotebookEdit(/path/*.ipynb)` |
| `LSP` | Code intelligence (LSP) | — |
| `Skill` | Run a skill | `Skill(commit)`, `Skill(name *)` |
| `ToolSearch` | Lazy-load deferred tools | — |
| `ListMcpResourcesTool` | List MCP resources | — |
| `ReadMcpResourceTool` | Read an MCP resource by URI | — |

## MCP tools

- `mcp__server` — all tools from the given server
- `mcp__server__*` — wildcard
- `mcp__server__tool_name` — a specific tool

## Paths for Read / Edit / Write / NotebookEdit

- `/path` — from the project root
- `path` or `./path` — from the cwd
- `~/path` — from home
- `//path` — absolute
- `*` — files in a single directory
- `**` — recursive

## Example `allowed-tools` in frontmatter

```yaml
allowed-tools:
  - Agent
  - Bash(git diff:*)
  - Bash(git log:*)
  - Read
  - Glob
  - Grep
```

## Sources

- [code.claude.com/docs — tools](https://code.claude.com/docs/en/tools)
- [code.claude.com/docs — permissions](https://code.claude.com/docs/en/permissions)
