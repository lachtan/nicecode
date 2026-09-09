---
paths:
  - "**/*.cs"
  - "**/*.xml"
  - "**/*.py"
  - "**/*.ps1"
  - "**/*.psm1"
  - "**/*.sh"
  - "**/*.sql"
  - "**/*.rs"
managed-by: https://github.com/lachtan/nicecode
version: "1.0.0"
last-change: "2026-08-28 14:47:48"
---

# Comments

The default is zero comments. A comment is an exception that must earn its place: if you cannot
name which licence below it falls under, delete it.

These rules govern the comments you write. Comments already in the file are the author's: do not
delete or rewrite one just because it maps to no licence — if a change makes it wrong, fix it; if
it looks wrong, raise it in review instead of removing it silently.

The licence gate governs comments in the body. What belongs on the member as API documentation is
governed by the language's doc-style rule.

## The only licences to write a comment

1. **Non-obvious WHY** — a decision a reader would otherwise "fix": a workaround for a foreign
   bug, a deliberate ordering, a measured trade-off. State the constraint; describe the mechanics
   only when the mechanics are what a reader cannot reconstruct.
2. **An invariant the code cannot state** — something the type system does not carry and the code
   silently depends on.
3. **An external authority** — a spec clause, protocol rule, or ticket the code implements.

Everything else — how it works, what the next line does, section headers, restating a name,
TODOs — is not written.

## Decide the addressee before writing a word

- Reader is the **caller** → the language's API documentation form on the member, where it has one
  (XML doc comments, docstrings, comment-based help). Never an inline comment in the body.
- Reader is **whoever edits this exact code** → an inline comment directly above the line it
  concerns.

Contract facts — what may be returned, what the caller must do, thread-safety, ownership,
lifetime — belong to the API documentation, never inside the body.

## A comment must hold for every use of the code

Write only what is true for every caller, present and future. A reason valid for one call site
(one scenario, one exchange, one pipeline) belongs at that call site, not inside the reusable
component. Test: "If this code were used in a different module, is the sentence still true?"
If not, move it to the caller, or restate it as an invariant.

## One source of truth

A fact is written exactly once. If it is in the API documentation, do not restate it in the body;
if it is in the body, do not restate it at the call site. Cross-reference it in whatever way the
language allows, or say nothing.

Never re-add a comment the user has deleted.

## Before finishing an edit

Re-read every comment you added and delete the ones you cannot map to a licence above. Lead each
surviving comment with its main point; keep it as short as full coverage of the logic allows.
