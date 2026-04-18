# Claude Code — seznam tools

Použitelné v `allowed-tools` frontmatteru slash commandů a v `permissions` v `settings.json`.

## Základní tools

| Tool | Popis | Scoping |
|---|---|---|
| `Read` | Čtení souborů | `Read(src/**)` |
| `Write` | Vytvoření / přepis souboru | `Write(docs/**)` |
| `Edit` | Cílené úpravy souboru | `Edit(src/**/*.ts)` |
| `Glob` | Hledání souborů podle vzoru | — |
| `Grep` | Hledání v obsahu | — |
| `Bash` | Spustí shell příkaz | `Bash(git diff:*)`, `Bash(npm run *)` |
| `WebFetch` | Stažení obsahu z URL | `WebFetch(domain:example.com)` |
| `WebSearch` | Webové vyhledávání | — |

## Ostatní tools

| Tool | Popis | Scoping |
|---|---|---|
| `Agent` | Spustí subagenta | `Agent(Explore)`, `Agent(custom-name)` |
| `SendMessage` | Zpráva teammate / pokračování subagenta | — |
| `AskUserQuestion` | Zeptá se uživatele (multiple-choice) | — |
| `TeamCreate` | Vytvoření agent týmu | — |
| `TeamDelete` | Zrušení agent týmu | — |
| `TodoWrite` | Session TODO checklist | — |
| `TaskCreate` | Vytvoření úkolu v task listu | — |
| `TaskGet` | Detail konkrétního úkolu | — |
| `TaskList` | Výpis všech úkolů | — |
| `TaskUpdate` | Změna statusu / závislostí / smazání úkolu | — |
| `TaskStop` | Zastavení běžícího background úkolu | — |
| `TaskOutput` | (Deprecated) Výstup z background úkolu | — |
| `CronCreate` | Naplánování opakovaného promptu | — |
| `CronDelete` | Zrušení naplánovaného úkolu | — |
| `CronList` | Výpis naplánovaných úkolů | — |
| `EnterPlanMode` | Přepnutí do plan mode | — |
| `ExitPlanMode` | Opuštění plan mode | — |
| `EnterWorktree` | Vytvoření git worktree a přepnutí do něj | — |
| `ExitWorktree` | Opuštění worktree a návrat | — |
| `Monitor` | Background příkaz s průběžným výstupem | `Monitor(…)` stejně jako Bash |
| `PowerShell` | Spuštění PowerShell příkazu | `PowerShell(npm run *)` |
| `NotebookEdit` | Úpravy Jupyter notebooku | `NotebookEdit(/path/*.ipynb)` |
| `LSP` | Code intelligence (LSP) | — |
| `Skill` | Spuštění skillu | `Skill(commit)`, `Skill(name *)` |
| `ToolSearch` | Lazy-load deferred tools | — |
| `ListMcpResourcesTool` | Seznam MCP zdrojů | — |
| `ReadMcpResourceTool` | Přečtení MCP zdroje podle URI | — |

## MCP tools

- `mcp__server` — všechny tools z daného serveru
- `mcp__server__*` — wildcard
- `mcp__server__tool_name` — konkrétní tool

## Cesty u Read / Edit / Write / NotebookEdit

- `/path` — od root projektu
- `path` nebo `./path` — od cwd
- `~/path` — od home
- `//path` — absolutní
- `*` — soubory v jednom adresáři
- `**` — rekurzivně

## Příklad `allowed-tools` ve frontmatteru

```yaml
allowed-tools:
  - Agent
  - Bash(git diff:*)
  - Bash(git log:*)
  - Read
  - Glob
  - Grep
```

## Zdroje

- [code.claude.com/docs — tools](https://code.claude.com/docs/en/tools)
- [code.claude.com/docs — permissions](https://code.claude.com/docs/en/permissions)
