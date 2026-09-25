---
paths:
  - "**/*.cs"
  - "**/*.xml"
  - "**/*.py"
  - "**/*.ps1"
  - "**/*.psm1"
  - "**/*.sh"
  - "**/*.sql"
managed-by: https://github.com/lachtan/nicecode
version: "1.1.0"
last-change: "2026-09-25 11:13:51"
---

# Comments

Besides the code itself, a source file holds two kinds of text. Decide which one you are writing
before you write a word:

- **Documentation** is for people who use the code from outside. It describes the contract: what
  the code produces, what the caller must and must not do, its preconditions and postconditions.
  Write it in the form the language provides for it (XML doc, docstring, comment-based help).
  Documentation does not need one of the reasons below; describing the contract is its job — and
  where the declaration already states the contract, there is nothing left to describe. It still
  follows "One source of truth" and stays short.
- **A comment** is for the person who edits this exact code. It sits directly above the line it
  concerns. The default is no comment at all. A comment is an exception that has to earn its
  place: if you cannot name which of the reasons below it falls under, do not write it.

A contract fact never goes into a comment inside the implementation. A configuration file or a
one-off script has no contract and therefore no documentation, only comments.

## The only reasons to write a comment

1. **A non-obvious WHY.** A decision that looks like a mistake, so a reader might undo it — for
   example a workaround for a bug in someone else's code, a deliberate ordering, or a trade-off
   backed by a measurement. Write down the constraint that forced the decision. Explain how the
   workaround works only when the reader could not work it out from the code.
2. **An invariant the code cannot state.** A required ordering, a format, a range, a precondition
   that nothing in the code expresses and everything silently depends on.
3. **An external authority.** A spec clause, a protocol rule, or a ticket the code implements.

None of these is a reason:

- how the code works, or what the next line does
- who calls this code
- what the code used to do, or what was tried and dropped (see below)
- a restatement of a name
- a TODO

The one exception: in a long file with no structure of its own, such as a configuration file,
header comments that help the reader navigate are allowed.

## What was tried and dropped is not a comment

A variant that was tried and dropped gets no comment, whether it was dropped in an earlier
revision, in a previous session, or in the conversation that produced this code. The reader never
saw that variant and cannot check the claim. Write the constraint that ruled the variant out, not
the variant: "this loop must stay allocation-free", never "a List was tried here first".

## The line below already says it

A statement that reads on its own gets no comment above it: a raised error carries its own type
and message, a call carries the name of what it calls, a guard carries its condition. If the line
does not read on its own, fix the name or extract the value into a named one. Do not explain it in
a comment.

## A comment must hold for every use of the code

Write only what is true everywhere this code is used, now and later. A reason that holds for one
use (one scenario, one exchange, one pipeline) belongs with that use, not inside the shared code
it calls. Test: "In another context, would this sentence still be true?" If not, move it to that
context, or restate it as an invariant.

## One source of truth

Write each fact exactly once. If it is in the documentation, do not repeat it inside the code; if
it is inside the code, do not repeat it where the code is used. Point to it in whatever way the
file allows, or say nothing.

## Comments you did not write

Comments already in the file belong to their author. Do not delete or rewrite one just because it
matches none of the reasons above. If your change makes it wrong, fix it. If it merely looks
wrong, tell the user instead of removing it silently. Never re-add a comment the user has deleted.

## Before finishing an edit

Re-read every comment you added. Delete the ones nothing above allows. Lead each
surviving comment with its main point and cut everything the point does not need.
