---
name: plan-review
description: >-
  Use when reviewing an implementation plan (a `.md` file) before implementation starts —
  to judge whether it can be implemented without guessing.
argument-hint: "[plan.md]"
user-invocable: true
disable-model-invocation: true
managed-by: https://github.com/lachtan/nicecode
version: "1.0.0"
---

# Implementation plan review

Answer one question about the plan: **can it be implemented without guessing?**

You judge whether the plan is *complete*, not whether the design is *good*. Architecture critique,
alternative approaches and code quality are out of scope.

**Write the report in the language the user speaks in this conversation.** If that is not yet clear,
match the language of the plan file. Translate the severity labels and the verdict too — this file is
in English, the output follows the user.

## Procedure

1. **Resolve the input.** The argument is a path to a plan file. With no argument, ask the user for the
   path. Never guess and never search for candidate plans.
2. **Read the whole plan** in one `Read`. Contradictions between sections are invisible otherwise.
3. **Verify the anchors.** List every file path and every named symbol (class, method, constant,
   config key) the plan claims already exists. Check paths with `Glob` and symbol names with `Grep`.
   - Do **not** `Read` whole source files, and do not judge whether the proposed change is correct.
   - Skip anchors the plan introduces as new.
   - One `Grep` per symbol is enough. If a name is generic, scope the search with `glob` or `path`.
   - **A single miss is not proof of absence.** Pass repo-root-absolute paths, and before reporting a
     missing anchor retry with a second form (`Glob **/Name.cs`, or `Grep` for the bare name with no
     `path` filter). Report it only if it misses both times.
   - Beware over-broad `Grep`: a common identifier matches hundreds of files and proves nothing. Anchor
     the pattern (`class Name`, `Name(`) and scope it with `path`.
4. **Check whether the plan is already implemented.** If the symbols the plan wants to *create* exist
   while the ones it wants to *change* are gone, the code has moved past the plan. Stop the review,
   report exactly that with the evidence, and note whether the result matches what the plan proposed.
   Do not emit a wall of missing-anchor findings — a superseded plan is not a defective plan.
5. **Walk the checklist** below, category by category.
6. **Print the report** in the format below and end with the verdict.

Some documents handed in as plans are backlogs, not plans. Treat one as a backlog only when **all
three** hold: no single deliverable, no verification section, and the text says the items are optional
or to be picked as needed. Then say so once, list the items whose *shape* is undecided (an unresolved
either/or is a defect even in a backlog), and skip the rest of the checklist. If any of the three fails,
it is a plan — review it.

## Checklist

Each category carries a boundary — what is *not* a finding. Respect it. A skill that cries wolf on a
good plan stops being used.

Plans may be written in any language. Match the *meaning* below, not English keywords.

1. **Deferred decisions** — always blocking. Any phrase that hands a decision to implementation time:
   "we'll solve this while implementing", "we'll see", "as needed", "something like", "we'll tune it
   later", "TBD", "to be determined".
   *Not a finding:* an explicit out-of-scope section listing what the plan deliberately excludes. That
   is the opposite of a deferred decision.
2. **Missing anchors** — the plan names a file, class or method that `Glob`/`Grep` does not find, or
   finds under a different name.
   *Not a finding:* anything the plan itself creates.
3. **Unverifiable verification** — no section with concrete commands, or a gate stated in prose ("test
   that it works") without saying what exactly must pass.
   *Not a finding:* a manual step explicitly left to the user.
4. **Internal contradictions** — prose says one thing, a code sample or another section says another
   (text says `private`, the sample is `public`). Includes the design section contradicting the test
   section.
5. **Silently dropped scope** — the request (or the plan's context section) asks for A, B, C; the plan
   covers A and B, never mentions C, and C is not listed as excluded.
6. **Unconsidered impact** — public surface changes but callers are not mentioned; behaviour changes
   but configuration, tests or docstrings are not; C# files change but `/fix-projects` is missing.
7. **Missing failure paths** — only the happy path is described. What about I/O failure, timeout, empty
   input, concurrency.
   *Not a finding:* a failure that cannot occur on the changed path.
8. **Unacknowledged decisions** — the plan states a value or choice it invented (a limit, retry count,
   name, format) as if it were a given, with no sentence saying it is a decision and why.
9. **Unverified assumptions** — the plan rests on a claim about foreign code, a library or a protocol
   that it never checks. If the claim is false, part of the plan collapses with it.
10. **Speculative scope** — an abstraction, layer, generality or extension point the request did not
    ask for. See [clean-code.md](../../rules/clean-code.md) ("Prefer the simpler solution").
11. **Order and divisibility** — steps depend on each other in the wrong order, or the plan cannot be
    done in parts that each leave the build and tests green.
    *Not a finding:* a small plan that is naturally a single step.
12. **Project rules** — the plan proposes something the repository forbids. Read the `CLAUDE.md` on the
    path of the affected files and the matching `.claude/rules/*.md`; typical breaches are the wrong
    comment language, tests placed outside the project that owns them, and a branch name off the
    required pattern.

### Signal filter

Report only what changes the outcome of the implementation. Never report wording, structure or "this
could be phrased better" — the plan is not the deliverable.

If you are not certain a finding is real, phrase it as a question instead of an assertion.

## Severity and verdict

Pick severity by asking *what happens if the implementer ignores this?*

- **Blocking** — they will have to guess, or they will build on something that does not exist.
- **Fill in** — the implementation will run, but the result will differ from what was intended.
- **Note** — a detail, changes nothing.

The verdict is binary, so that it forces an action:

- one or more blocking findings → *send back for rework*
- otherwise → *ready to implement*, listing what should still be filled in

The superseded case from step 4 is an early exit, not a third grade — state that the plan is already
implemented, give the evidence, and stop.

## Report format

Findings grouped by severity, blocking first. Three lines each:

- **where** — the plan section, plus `[path:line](path#Lline)` for anchors
- **what** — one sentence naming the gap; for a deferred decision, quote the plan verbatim
- **how to fill it** — a concrete proposed wording or decision, not just criticism

Quotes from the plan are copied verbatim — never corrected, never translated, even when the report is
written in another language.

Close with one line of counts per severity, then the verdict. With no findings, say the plan is ready to
implement and state that all twelve checklist categories were walked — naming only some of them
understates what was checked.
