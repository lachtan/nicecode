---
name: craft-code
description: >-
  Use on any coding task — writing, refactoring, fixing, reviewing or designing code, an API
  or a module. Forces the simplest thing that works before you write, keeps interfaces simpler
  than implementations while you write, and checks the diff before you call it done. Triggers
  on add, implement, build, refactor, simplify, "is this over-engineered", a change that feels
  harder than it should, or a small fix that starts growing.
disable-model-invocation: false
user-invocable: true
managed-by: https://github.com/lachtan/nicecode
version: "1.1.0"
last-change: "2026-08-28 16:11:32"
---

# Craft Code

**Optimize for the cost of the next change, not this one.** Complexity is what makes future
changes expensive, and it arrives in small increments — hundreds of individually reasonable
decisions — so the standard is zero tolerance for small complexity, not vigilance about large.

Two standards, and **scope decides which one applies**. For code you _add_, the standard is
simplicity: the least that solves the stated problem. For structure you _change_, the standard
is design. "What is the smallest edit that works?" is how codebases rot: each minimal edit buys
one more special case, and the accumulation is invisible at the scale where the decisions get
made. When you are done, the code should look the way it would have if it had been designed
with this change in mind. Restructure only what the change actually touches; adjacent code you
were not asked about stays as it is, and restructuring goes in steps that leave the system
working — defects scale with the size of a diff.

**Scale the ceremony to the change.** All of this trades speed for care. A rename, a typo, a
one-line fix: climb the ladder, re-read the diff, stop. The full pass is for work that adds
behaviour or moves a boundary.

## Before you write

1. **Understand first.** Trace the real flow — the caller, the data, the failure. The ladder
   shortens the solution, never the reading. A fix targets the root cause, not the symptom:
   grep every caller of the function you are about to touch, because one guard in the shared
   function beats a guard in each caller.

2. **State the assumption you are acting on**, in one line. When two readings of the request
   would produce different work, ask instead of picking one silently.

3. **Turn the task into something checkable**, before you write the thing you will check.
   "Add validation" → a test for invalid inputs. "Fix the bug" → a test that reproduces it.
   "Refactor X" → tests green before and after. Weak criteria ("make it work") send you back to
   the user; strong ones let you loop on your own.

4. **Climb the ladder. Stop at the first rung that holds.**
   1. Does it need to exist at all? Speculative need → skip it, say so in one line.
   2. Is it already here? A helper, type, or pattern a few files over. Look before you write —
      re-implementing what already exists is the most common waste.
   3. Does the standard library do it?
   4. Does a native platform feature cover it? The language's async over a threading framework,
      a database constraint over application code.
   5. Does an already-installed dependency solve it? Never add a new one for what a few lines do.
   6. Can it be one line?
   7. Only then: the minimum code that works.

   Two rungs both hold → take the higher one and move on. Two options the same size → take the
   one that is correct on the edge cases; the point is writing less code, not picking the
   flimsier algorithm. This is a reflex, not a research project.

   Deletion over addition, boring over clever.

5. **Interface work only** — a new or changed public surface, a change spanning more than one
   file, or a new concept:
   - **Design twice.** Sketch two genuinely different approaches. Articulating why the second
     is worse is how you find out whether the first was good or merely first.
   - **Write the interface description before the body.** If you cannot describe it briefly and
     completely, fix the design, not the description.

   A rename, a bug fix, or a one-line change gets none of this.

## While you write

**Interfaces.** The gap between a simple interface and a complex implementation is the entire
value of a module — complexity hidden once, never paid again by callers. A module whose
interface costs about as much to learn as its body costs to read is not earning its existence.

- Structure by **knowledge**, not by steps. Ask what each unit _knows_ — a format, a policy, a
  protocol. Splitting read/transform/write means all three know the format.
- **Take the complexity yourself.** There are more callers than authors: compute the value
  instead of adding a knob, handle it instead of raising, default it instead of requiring it.
  Exporting a decision you are unsure about does not help — the caller knows less than you do.
- **Make the common case need no thought.** Effective complexity is the complexity of what
  people actually use.
- Generalize the _shape_ of the interface, never the _set of capabilities_. Express today's
  requirement in the domain's basic operations; do not build for a requirement nobody stated.
  The test: does this change what the code can _do_, or only how it is _expressed_? Generality
  stops where you start writing glue to use your own interface.

**Signatures and names.**

- A unit does one thing at one level of abstraction. Policy sitting next to byte fiddling is
  what makes a body need a second reading.
- Few parameters — 0–3. No boolean flag arguments: split into two well-named functions, or take
  an enum. No output parameters; return a value. A function that queries state must not change it.
- Name what a thing _is_, not what type it holds. Types are noun phrases, functions are verb
  phrases, booleans read as predicates. A name broad enough to mean several things — `data`,
  `info`, `temp`, `manager`, `helper`, `process` — names nothing. No single-letter names outside
  a loop counter.
- Length is never a reason to split. Split when both halves can be understood and replaced on
  their own; merge when neither half reads without the other. Fewer lines is not less to hold in
  your head: longer but obvious beats terse but studied.

**Control flow.**

- Check preconditions at the top, then guard clauses and early returns; two or three levels of
  nesting is the ceiling — invert the condition and return.
- Named constants instead of magic numbers and strings.
- Prefer values that cannot change after construction; make something mutable only where the
  code has to mutate it.
- Compose rather than inherit. Inherit only for a true "is-a".
- Follow the patterns already in this codebase: consistency beats local perfection, and a better
  idea on its own does not justify breaking a convention. But consistency means similar things
  alike **and dissimilar things differently**.
- Inject a dependency where there is a real seam — something that gets swapped or faked in a
  test. An interface with one implementation and no seam is not a seam.

**Errors.** Every error condition is a branch someone has to handle, and handling code rarely
runs, so it rarely works. Four moves:

1. **Redefine** so it is not exceptional — "ensure it is gone" rather than "delete it"; clamp
   rather than reject; an empty thing rather than an absent one. Best whenever it applies.
2. **Handle it low**, so nothing above ever sees it.
3. **Let it propagate high**, so one handler covers many cases.
4. **Fail fast** on what nothing can recover from. The last resort, not the first.

Removing an error condition means changing what the operation _means_, never hiding that it
failed. If the caller could have recovered, or data would be lost, it surfaces. When it does
surface: specific types, never a silent swallow, and never lose the original cause.

**Comments.** The default is zero. A comment earns its place only as one of three things:

1. A **non-obvious why** — a decision a reader would otherwise "fix": a workaround for a
   foreign bug, a deliberate ordering, a measured trade-off. A ceiling the ladder chose on
   purpose belongs here, but only when the comment also names what lifts it.
2. An **invariant the code cannot state** — something the type system does not carry and the
   code silently depends on.
3. An **external authority** — a spec clause, a protocol rule, a ticket the code implements.

Everything else — how it works, what the next line does, a section header, a restated name,
a TODO — is not written.

Decide the addressee before writing a word. Reader is the _caller_ → the language's API
documentation form on the member, never an inline comment in the body. Reader is _whoever edits
this line_ → inline, directly above it. Contract facts belong to the API documentation and never
to the body: units, boundary inclusivity, what null or empty means, ownership and who releases
what, lifetime, thread-safety. A comment must hold for every use of the code — a reason true at
one call site belongs at that call site. Write each fact exactly once, and never re-add a comment
the user deleted. Comments already in the file are someone else's: fix one your change made
wrong, and leave the rest alone.

## Before you call it done

- **Run the check you defined up front.** Non-trivial logic — a branch, a loop, a parser, a
  money or security path — leaves **one** runnable check behind. Use the test framework the
  project already has; do not scaffold a new one, and add no fixtures unless asked. Trivial
  one-liners need none.
- Test at the interface you designed, not through it. A test that reaches into internals will
  fight every future restructuring — and behaviour you cannot reach through the interface at all
  means the interface is missing something.
- **Re-read your own diff.** It is what catches stale comments and leftovers. Every changed line
  should trace directly to the request.
- Delete every comment you added that you cannot place under one of the three licences above.
- Remove the imports, variables and functions **your** change orphaned — and only those.
  Pre-existing dead code: name it, do not delete it.
- Name the red flags the diff hits, or say "none". A flag you report and move past is a flag you
  did not fix, and that is how the accumulation happens.

Close with one line. Drop a field that has nothing to report; never let it grow past one line.

```
craft: skipped <what> (add when <condition>) · verified by <check> · flags: <none | names>
```

## Red flags

Recognizing bad design is easier than producing good design, so this is the fastest tool
available: one flag appearing means a better structure exists nearby. Two calibrations — weigh
a flag by how often that code gets touched, and remember it is **judged by the reader**. If a
reviewer says it is not obvious, it is not obvious.

| Flag                           | Symptom                                           | Move                                                           |
| ------------------------------ | ------------------------------------------------- | -------------------------------------------------------------- |
| Shallow module                 | Interface nearly as complex as the implementation | Inline it, or grow it until it hides something                 |
| Information leakage            | The same decision known in 2+ places              | Merge them, or extract the knowledge behind a real abstraction |
| Temporal decomposition         | Structure follows execution order                 | Restructure by knowledge; order belongs in the caller          |
| Overexposure                   | Common case forces learning rare features         | Default the common case, move the rest aside                   |
| Pass-through method            | Forwards to a near-identical signature            | Expose the inner one, redistribute, or merge                   |
| Pass-through variable          | Threaded through methods that never use it        | Shared or context object; not a global                         |
| Repetition                     | The same non-trivial code recurring               | Extract, or restructure so it exists once                      |
| Special-general mixture        | Generic mechanism knows one specific caller       | Push the specific code upward                                  |
| Conjoined units                | Neither half is readable without the other        | Merge, or move the boundary                                    |
| Comment repeats code           | Derivable from the line beside it                 | Say what is missing: units, why, what the term means           |
| Impl leaks into interface docs | Callers told what only maintainers need           | Move it inside; check what is now missing                      |
| Vague name                     | Broad enough to mean several things               | Name what it is; booleans read as predicates                   |
| Hard to name                   | No short precise name exists                      | The thing has no single purpose — usually it is two            |
| Hard to describe               | No short complete description exists              | Fix the design, not the description                            |
| Non-obvious code               | First reading gives wrong expectations            | Reduce info needed → follow convention → name or comment       |
| Unfixable complexity           | Locally unsolvable                                | The fault is lower down; step back and fix that level          |

Legitimate exceptions: dispatchers and sibling implementations of one interface share signatures
on purpose. Decorators are the usual source of the illegitimate kind — prefer adding the
behaviour to the underlying thing. Extract repetition only when both copies express the same
_decision_ — code that merely looks alike today is not repetition, and an extraction that needs
a boolean parameter to serve both callers is two things wearing one name.

## Limits

Every rule above produces the harm it prevents when taken too far.

- Hide what is unimportant, but when something is important, **expose it**. An abstraction that
  omits what callers need is false: it looks simple and forces everyone to read the body anyway.
- Pull complexity down only when it relates to what the unit already does. Absorbing a caller's
  _concepts_ is importing coupling, not hiding it.
- Neither splitting nor merging is a default. A long unit with one clean entry point is a good
  part; a short one that cannot be read without its caller is worse than nothing, because it
  also added an interface.

**Evidence before fixing.** No speculative features, no unconfirmed bug fixes, no unmeasured
optimization — all three guess at external reality. Complexity is its own evidence, though: you
do not need a bug report to justify simplifying code you can see is confusing. For performance,
measure, change, measure, and revert if it did not help — complexity that buys nothing is loss.
Prefer a fundamental fix, a cache or a better algorithm, over shaving the path you already have.
A pattern that is wrong by construction — an N+1 query, work repeated inside a loop — needs no
measurement; batch or preload it.

## Never simplify away

Input validation at trust boundaries. Error handling that prevents data loss. Security measures.
Accessibility basics. Anything the user explicitly asked for.

When the user wants the full version, build it — no re-arguing.
