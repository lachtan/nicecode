---
managed-by: https://github.com/lachtan/nicecode
version: "1.0.0"
---

# Clean Code Principles

General principles for all languages.

## Naming

- Boolean variables/predicates: use `is`/`has`/`can`/`should` prefix.
- Do not encode types in names (`userList`, `strName`); let the type system do that.
- No single-letter names except loop counters (`i`, `j`, `k`).
- Classes/types: noun or noun phrase. Functions/methods: verb or verb phrase.
- Names must reveal intent — a reader should understand purpose without reading the body.

## Functions

- No boolean flag arguments — split into two well-named functions or use an enum.
- No output parameters; return a value instead.
- Prefer low number of parameters (0–3).
- A function that queries state must not change it (Command-Query Separation).
- A function must do exactly one thing at one level of abstraction.

## Design

- Prefer the simpler solution, always. Complexity is a cost even when it works.
- Write simple, obvious code — a junior developer must understand it at first read.
- Fewer abstractions — add only when they clearly reduce complexity.
- Reuse existing code before adding new.
- Follow existing patterns in the codebase — consistency beats local perfection.
- Remove dead code immediately.
- Prefer composition over inheritance; inherit only for true "is-a" relationships.
- Prefer immutable types and values; make things mutable only when necessary.
- Depend on abstractions, not concretions; inject dependencies.

## Control Flow

- Fail fast: validate inputs at the start; use guard clauses and early returns.
- Avoid deep nesting — maximum 2–3 levels; invert conditions to return early.
- Replace magic numbers and strings with named constants or enums.
- Code should behave the way a reader expects — avoid surprises.

## Error Handling

- Never swallow exceptions silently; always handle or propagate.
- Preserve error context when re-throwing; do not lose the original cause.
- Use specific error/exception types, not generic catch-all types.
- Make failure modes explicit — errors are part of the interface.

## Comments

- Use comments sparingly — each comment is a maintenance liability.
- Comments explain WHY, not WHAT; code should be self-explanatory.
- Document non-obvious decisions, business rules, and known trade-offs.

## Performance

- Avoid N+1 query patterns: batch or preload related data.
- Optimize for readability first; optimize for performance only where profiling shows a bottleneck.
