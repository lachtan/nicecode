---
name: plan-loop
description: >-
  Use only when the user explicitly asks to run the plan review loop on an implementation plan —
  a fresh plan-reviewer subagent reviews it, you revise the plan, repeat until nothing is left to
  fix or 3 rounds pass. Never run it unprompted after writing a plan.
argument-hint: "[plan.md]"
user-invocable: true
disable-model-invocation: false
allowed-tools:
  - Agent
  - Read
  - Edit
  - Grep
  - Glob
  - WebSearch
  - WebFetch
  - AskUserQuestion
  - ExitPlanMode
managed-by: https://github.com/lachtan/nicecode
version: "1.0.0"
last-change: "2026-09-25 11:13:51"
---

# Plan review loop

You are the plan author. A fresh `plan-reviewer` subagent reviews the plan each round, you triage
its findings and revise the plan. You hold the state between rounds; every reviewer starts from
scratch.

Write everything the user sees in the user's language. Labels and table headers below are English;
translate them.

## Procedure

1. **Resolve the input.** The argument is a path to a plan file. With no argument, use the plan file
   of the current plan mode session if there is one; otherwise ask the user. Never guess and never
   search for candidate plans.
2. **Run round N** (N = 1, 2, 3). Spawn a new `plan-reviewer` subagent in the foreground — never
   resume an earlier one. Its prompt contains:
   - the absolute plan path,
   - the report language (the user's language),
   - from round 2 on, the cumulative rejected list: every finding rejected in any earlier round,
     each with its round and ID, the finding quoted verbatim, and your rejection reason.
3. **Exit early** when the reviewer reports the plan is already implemented or is a backlog. Pass
   its report to the user and stop.
4. **Triage** every Blocking and `Fill in` finding as one of:
   - **accepted** — edit the plan to resolve it.
   - **rejected** — give a one-sentence reason. Before rejecting a missing-anchor finding, check the
     anchor yourself with `Glob`/`Grep`. Always reject a finding that contradicts an explicit user
     requirement, and say so in the reason.
   - **user decision** — a choice only the user can make. Ask with `AskUserQuestion`, then apply the
     answer to the plan.

   Edit only the plan file.
5. **Print the round table:** `ID | severity | decision | reason / what changed`. Notes are in
   it too, with an empty decision.
6. **Decide whether to continue:**
   - **CONVERGED** — the reviewer returned no Blocking and no `Fill in` finding. Stop.
   - **STALEMATE** — every Blocking and `Fill in` finding of the round re-raises an already rejected
     finding, and you reject each one again. Stop.
   - **NOT CONVERGED** — round 3 is done and neither of the above holds. Stop.
   - Otherwise start the next round.
7. **Print the final report:**
   - status and number of rounds,
   - every accepted and rejected finding across all rounds, with reasons,
   - open disagreements and unresolved `Fill in` findings,
   - for NOT CONVERGED, that the round 3 edits were not reviewed.

   Leave open disagreements to the user — do not settle them yourself.
8. **Plan mode.** Never switch the permission mode. If the session is in plan mode, finish by
   presenting the revised plan with `ExitPlanMode`.

## Gotchas

- Keep the reviewer fresh every round even though resuming would be cheaper — a resumed reviewer
  defends its earlier verdict instead of judging the revised plan.
- In plan mode only the session's plan file is editable. If the resolved plan is a different
  file, say so and stop; the user has to leave plan mode and run the loop again.
