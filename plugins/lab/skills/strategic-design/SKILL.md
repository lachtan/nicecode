---
name: strategic-design
description: >-
  Design rules for keeping code cheap to change. Use when designing or writing a module,
  function or API, reviewing a diff, refactoring, naming things, or designing error handling.
  Also when a change feels harder than it should, a small fix starts growing, or you're
  tempted to add a wrapper layer or a config option.
disable-model-invocation: false
user-invocable: true
managed-by: https://github.com/lachtan/nicecode
version: "1.0.0"
---

# Strategic design

Distilled from Ousterhout, *A Philosophy of Software Design*, and Kanat-Alexander,
*Code Simplicity*.

**Optimize for the cost of the next change, not this one.** Implementation is
paid once; maintenance is paid on every future change, and systems live longer
than anyone expects. Complexity is what makes future changes expensive, and it
arrives in small increments — hundreds of individually reasonable decisions — so
the standard is zero tolerance for small complexity, not vigilance about large.

Counterpart: code nobody needs has no value however well designed. Don't write
it; delete it when it stops being used.

Full treatment — design twice, interface description before the body — when the
change adds or alters a public interface, spans more than one file, or introduces
a new concept. Otherwise: the red flags, and read your own diff. A rename doesn't
get a design review.

## Complexity

Two causes: **dependencies** (can't change this without changing that) and
**obscurity** (important information isn't apparent). Three symptoms:

- **Change amplification** — one idea, edits in many places.
- **Cognitive load** — how much you must know to change it safely. Fewer lines
  ≠ lower load; longer but obvious beats terse but studied.
- **Unknown unknowns** — not apparent what needs changing, or that anything
  does. Worst of the three: reading doesn't find it, bugs do.

Two calibrations: complexity is weighted by how often the code is touched, and
it is **judged by the reader** — if a reviewer says it isn't obvious, it isn't.

## Red flags

Recognizing bad design is easier than producing good design, so this is the
fastest tool available. One appearing means a better structure exists nearby.

| Flag | Symptom | Move |
| --- | --- | --- |
| Shallow module | Interface nearly as complex as implementation | Inline it, or grow it until it hides something |
| Information leakage | Same decision known in 2+ places | Merge them, or extract the knowledge — but only behind a real abstraction |
| Temporal decomposition | Structure follows execution order | Restructure by knowledge; order belongs in the caller |
| Overexposure | Common case forces learning rare features | Default the common case, move the rest aside |
| Pass-through method | Forwards to a near-identical signature | Expose the inner one, redistribute, or merge |
| Pass-through variable | Threaded through methods that don't use it | Shared object or context object; not a global |
| Repetition | Same non-trivial code recurring | Extract, or restructure so it exists once |
| Special-general mixture | Generic mechanism knows one specific caller | Push the specific code upward |
| Conjoined units | Neither half readable without the other | Merge, or move the boundary |
| Comment repeats code | Derivable from the line beside it | Say what's missing: units, why, what the term means |
| Impl leaks into interface docs | Callers told what only maintainers need | Move it inside; check what's now missing |
| Vague name | Broad enough to mean several things — `data`, `info`, `temp`, `manager`, `helper`, `process` | Name what it is; booleans read as predicates |
| Hard to name | No short precise name exists | The thing has no single purpose — usually it's two |
| Hard to describe | No short complete description exists | Fix the design, not the description |
| Non-obvious code | First reading gives wrong expectations | Reduce info needed → follow convention → name/comment |
| Unfixable complexity | Locally unsolvable | The fault is lower down; step back and fix that level |

Dispatchers and sibling implementations of one interface share signatures
legitimately — the first chooses, the second lets one lesson cover many. Decorators
are the usual source of illegitimate forwarding; prefer adding the behaviour to
the underlying thing.

Extract repetition only when both copies express the same *decision*, so a change
to the decision has to hit both. Code that merely looks alike today isn't
repetition. An extraction needing a boolean parameter to serve both callers is the
wrong extraction — that's two things wearing one name.

## Writing new code

1. **Make the interface much simpler than the implementation.** That gap is the
   entire value of a module — complexity hidden once, never paid by callers. A
   module whose interface costs about as much to learn as its body costs to read
   isn't earning its existence.
2. **Structure by knowledge, not by steps.** Ask what each module *knows* — a
   format, a policy, a protocol. Splitting read/transform/write means all three
   know the format.
3. **Design it twice.** Sketch two or three genuinely different approaches
   before anything expensive to reverse. Articulating why the alternative is
   worse is how you learn whether the first idea was good or merely first.
4. **Write the interface description before the body.** It's the only way to
   capture an abstraction, and it's the earliest warning: if you can't describe
   it briefly and completely, fix the design, not the description.
5. **Interface general, capabilities not.** Express today's functionality in the
   domain's basic operations — smaller and covers more. Don't implement
   capabilities nobody asked for; they won't match the requirement when it
   arrives and rot silently meanwhile.
6. **Take the complexity yourself.** More callers than authors. Compute the value
   instead of adding a knob; handle it instead of raising; default instead of
   requiring. Exporting a decision you're unsure about doesn't help — the caller
   knows less.
7. **Make the common case need no thought.** Effective complexity is the
   complexity of what people actually use.
8. **Remove error conditions and special cases.** Each is a branch someone must
   handle, and handling code rarely runs so it rarely works. Four moves:
   redefine so it isn't exceptional ("ensure it's gone" not "delete it"; clamp
   don't reject; empty thing not absent thing); handle it low so nobody above
   sees it; let it propagate high so one handler covers many; or fail fast on
   what nothing can recover from.
9. **Comment what the code can't say.** Units, boundary inclusivity, what null
   means, who releases it, invariants, why this exists, when it's called. Two
   useful levels — below the code for precision, above it for intent. Same level
   as the code is restatement.

## Changing existing code

"What's the smallest edit that works?" is how codebases rot — each minimal edit
adds one special case, and the accumulation is invisible at the scale where the
decisions get made. **Standard: when you're done, the code should look the way it
would have if designed with this change in mind.**

- Ask whether the current structure is still right *given* this change. If not,
  restructure first. Not improving the design means degrading it.
- Anchor redesign to a purpose: restructure so *this* feature or fix becomes
  easy, then do it. Keeps the new structure fitting a real use, and keeps things
  shipping — long pure-refactor stretches are their own failure.
- Keep steps small. Defects scale with diff size, so large restructurings go in
  a sequence that leaves the system working at each step.
- Test at the interface you designed, not through it. A test reaching into
  internals is information leakage under another name, and it will fight every
  future restructuring. If the behaviour can't be reached through the interface,
  the interface is missing something.
- Under real constraints the question isn't clean vs. dirty but: what's the
  cleanest option inside these constraints? Usually one costs days, not months.
- Keep comments near what they describe, don't duplicate them, and put
  explanations in the code rather than the commit message — nobody browses
  history.

**Evidence before fixing.** No speculative features, unconfirmed bug fixes, or
unmeasured optimization — all three guess at external reality. But complexity is
its own evidence: you don't need a bug report to justify simplifying code you
can see is confusing.

**Performance:** intuitions are unreliable even for experts. Measure, change,
measure; revert if it didn't help, since complexity buying nothing is pure loss.
Prefer a fundamental fix (cache, different algorithm). Otherwise design around
the critical path — one test up front catching all special cases, then the
common path runs unchecked. Simple usually is faster: fewer branches, fewer
layer crossings.

**Rewrites** fail by reintroducing as much complexity as they remove while the
old system still needs maintaining. Do it only with a real estimate from actually
attempting incremental redesign, plus capacity to run both at once. Otherwise
redesign in place.

## Limits

Every rule here produces the harm it prevents when taken too far.

- Hide what's unimportant; **when something is important, expose it.** An
  abstraction omitting what callers need is false — it looks simple and forces
  everyone to read the implementation anyway.
- Pull complexity down only when it relates to what the module already does and
  simplifies both callers and this interface. Absorbing callers' *concepts* is
  importing coupling.
- Removing an error condition means changing what the operation *means*, not
  hiding that it failed. Mask only what the lower layer genuinely resolves; if the
  caller could have recovered, or data would be lost, it surfaces.
- Generalize the *shape of the interface*, never the *set of capabilities* —
  expression is free, speculation isn't. Test: does this change what the code can
  do, or only how it's expressed? Generality stops where you start writing glue
  to use your own interface.
- Consistency means similar things alike **and dissimilar things differently**.
  But a better idea alone doesn't justify breaking an existing convention.
- Neither splitting nor merging is a default, and length is never a reason to
  split. Merge when things share knowledge or can't be understood apart. Judge a
  unit by whether it can be understood and replaced on its own: a long unit with
  one clean entry point is a good part; a short one that can't be read without its
  caller is worse than nothing, because it also added an interface.
- Design effort scales with lifetime — but code expected to last six months
  routinely lasts ten years.

## Before you call it done

Re-read your own diff — it catches stale comments and leftovers — and name the
flags it hits, or say "none". A flag you report and move past is a flag you
didn't fix; that's how the accumulation happens.
