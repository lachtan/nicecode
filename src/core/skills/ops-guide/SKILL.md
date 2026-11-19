---
name: ops-guide
description: >-
  Use when writing or shortening a step-by-step procedure a human will run at a console —
  install guide, upgrade or migration runbook, one-off operational fix.
argument-hint: "[topic, or path to an existing guide]"
disable-model-invocation: false
user-invocable: true
managed-by: https://github.com/lachtan/nicecode
version: "1.0.0"
last-change: "2026-08-27 05:55:11"
---

# Writing an ops guide

**Decide the reader first.** A procedure an agent executes can be verbose — a machine reads all of
it and skips nothing. A procedure a **human** executes must be short: the fewest commands that do
the job, comments only where the command isn't self-explanatory. If the reader isn't obvious from
the request, ask.

**Check for a predecessor.** Where earlier runbooks, notes or a `scripts/` directory already cover
part of the job, extend them and reuse their names — a parallel document that restates them is
worse than no document. Writing from scratch is the normal case; don't hunt for what isn't there.

## Rules

1. Assume every command in the document gets typed. Cut what the reader would skip.
2. A verification command earns its place when the step **can fail silently** — exits 0, but you
   can't tell whether it worked. Put one check where it matters, not a gate after every step, and
   write it as a comment next to the command, not as a "done when" section under the stage.
3. Don't pre-solve failures that haven't happened, and don't open with a risk inventory. One
   preventive line — a snapshot, a backup, a dry run — only where failure is both likely and
   expensive. Everything else gets a one-line *symptom → fix* next to the step, when it happens.
4. Look for the existing command before inventing a mechanism. A design that adds state somebody
   has to clean up later is almost certainly the wrong one.
5. Keep kilometre-long code out of the guide — a wall of SQL or Ruby buries the steps around it.
   A long run of plain install commands is fine; that's still just steps. Move a block to a script
   when it gets rerun, repeats across stages, or is too long to read in place — it costs a
   copy-to-host step, so a one-off block with nowhere better to live stays inline. When it does move
   out, the guide keeps its name and one sentence of what it does.
6. Comment only what the command doesn't say. Never restate a command in prose.
7. Split documents by topic, never by level of detail. Two versions of one procedure drift apart.
8. Uncertainty is one inline comment, not a paragraph of analysis.
9. Stay inside the assignment. Hardening, monitoring and "while we're in there" go on a separate
   list, not into the procedure.
10. Write the guide in the reader's language, whatever the language of this skill.

## What the commands don't say

Add only the ones that apply, one line each — never a paragraph.

- Which host and which user the commands run as — once at the top when it never changes,
  in the stage heading where it does.
- What the reader must have in hand before starting: console access, a passphrase,
  a maintenance window.
- Where the service goes down, if it does.
- Where the last way back is, and what it is — a snapshot to restore, a dump to reload.

## Budget

Aim for ~30 lines per stage and ~150 for the whole guide, code blocks included. It's a smell test,
not a limit — but when you cross it, cut prose. Don't split the guide into a second document.

## Red flags

| Thought                                         | Reality                                                    |
| ----------------------------------------------- | ---------------------------------------------------------- |
| "One more verification step, to be safe"        | Only if the step can fail silently.                        |
| "Better mention this risk"                      | Only if it's likely *and* expensive. Otherwise it's noise. |
| "The reader might not follow this"              | Trust them. Cut the explanation.                           |
| "I'll write a short version too"                | Two versions drift apart. Write one.                       |
| "I'm not sure, so let me explain the trade-off" | One comment: `# not sure this helps`.                      |
| "This is a related improvement"                 | Not in this document.                                      |
| "I'll document what each flag does"             | The man page already did.                                  |
| "They'll want the whole command list"           | They'll skip half of it. Cut those.                        |
| "This block belongs inline"                     | If it buries the steps around it, it goes to a script.     |
| "I'll build a small mechanism for this"         | Find the existing command first.                           |
