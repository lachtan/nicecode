---
name: distill
description: Import or update gstack skills into this plugin. Clones the gstack repo, lists available skills, and distills selected ones.
user-invocable: true
disable-model-invocation: true
---

Import or update gstack skills. $ARGUMENTS

## Step 1: Clone source

Clone `https://github.com/garrytan/gstack` into a temp directory. Remove it when done.

## Step 2: Discover and select

List all skills from the cloned repo (directories containing `SKILL.md` or `SKILL.md.tmpl`). For each, show:

- Skill name
- One-line description (from frontmatter)
- **[exists]** if already present in `plugins/gstack/skills/<name>/`
- **[new]** if not

Ask the user which skills to distill. Pre-select those marked **[exists]** as the default update set.

## Step 3: Distill each skill

For each selected skill, read the `.tmpl` file (preferred) or `SKILL.md` from the cloned repo. Then write a distilled `SKILL.md` into `plugins/gstack/skills/<name>/`.

Use existing distilled skills as reference for tone and format. Read 1-2 existing files in `plugins/gstack/skills/` before starting.

### Frontmatter

```yaml
---
name: <skill-name>
description: <one-line description of what the skill does>
user-invocable: true
# add disable-model-invocation: true for interactive/review skills
---
```

### What to keep

- The core methodology, workflow phases, and decision frameworks
- Tables, checklists, and structured formats that encode real knowledge
- Concrete examples and pushback patterns
- Rules and constraints that define the skill's behavior

### What to strip

Everything injected by the `{{PREAMBLE}}` template and other gstack infrastructure:

- **Preamble bash block** — session tracking, update checks, analytics JSONL
- **Telemetry** — opt-in dialogs, duration logging, remote binary calls
- **Voice/persona** — Garry Tan persona, YC references, "golden age", writing rules
- **Lake intro** — "Boil the Lake" essay, completeness principle tables
- **Proactive prompt** — config dialogs for auto-suggesting skills
- **Upgrade check** — version detection, auto-upgrade flow
- **Contributor mode** — internal bug reporting
- **Completion status protocol** — formalized DONE/BLOCKED protocol
- **AskUserQuestion format** — 4-point formatting prescription
- **Review dashboard** — JSONL persistence, review readiness tables
- **Plan Status Footer** — review report tables for plan files
- **Codex/cross-model** — second opinion, adversarial review, subagent dispatch
- **Design binary** — mockup generation, comparison boards, serve commands
- **YC pitch** — founder discovery, tiered closing plea, `ycombinator.com/apply`
- **All bash code blocks** — remove every fenced bash block and any inline shell commands
- **All gstack binary references** — `$B`, `$D`, `gstack-config`, `gstack-slug`, etc.
- **All `~/.gstack/` state file operations**

### Distillation rules

- Target 60-120 lines per skill. The originals are 500-1300 lines — aim for 10-15x compression.
- Write in Claude Code style: concise, direct, no filler.
- No emoji.
- Preserve the skill's unique value — the methodology, not the machinery.
- If the original skill references other gstack skills (e.g., "run /qa next"), remove those references.
- Keep WebSearch instructions where they add genuine value (research, landscape awareness).

## Step 4: Verify

After writing all skills, show a summary table: skill name, original line count, distilled line count, status (new/updated).

## Step 5: Clean up

Remove the cloned temp directory.
