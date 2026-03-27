# Clean Code Principles

General principles for all languages.

## Design

- Write simple, obvious code — a junior developer must understand it at first read.
- Fewer functions, types, and abstractions — add only when they clearly reduce complexity.
- Reuse existing code before adding new.
- Follow existing patterns in the codebase — consistency beats local perfection.
- Remove dead code immediately.

## Naming

- Names must reveal intent — a reader should understand purpose without reading the body.
- No single-letter names except loop counters (`i`, `j`, `k`).
- Classes/types: noun or noun phrase. Functions/methods: verb or verb phrase.
- Boolean variables/predicates: use `is`/`has`/`can`/`should` prefix.
- Do not encode types in names (`userList`, `strName`); let the type system do that.

## Functions

- A function must do exactly one thing at one level of abstraction.
- Prefer low number of parameters (0–3).
- Prefer to avoid boolean flag arguments — consider splitting into two well-named functions or using an enum.
- Do not use output parameters; return a value instead.
- Keep functions short; extract logic into well-named helpers.
- Command-Query Separation: a function that queries state should not change it.
- Tell, Don't Ask: instruct objects to perform behavior rather than querying their state to decide externally.

## Classes and Modules

- Single Responsibility Principle: a class should have one reason to change.
- Open/Closed Principle: open for extension, closed for modification.
- Dependency Inversion: depend on abstractions, not concretions; inject dependencies.
- Prefer composition over inheritance; inherit only for true "is-a" relationships.
- Keep classes small and cohesive; split when they grow.
- Law of Demeter: call only methods on direct collaborators, not on objects returned by them.
- Prefer immutable types and values; make things mutable only when necessary.
- YAGNI: do not add functionality until it is needed.

## Control Flow

- Fail fast: validate inputs at the start; use guard clauses and early returns.
- Avoid deep nesting — maximum 2–3 levels; invert conditions to return early.
- Replace magic numbers and strings with named constants or enums.
- KISS: choose the simplest solution that works; complexity is a cost.
- Principle of Least Surprise: code should behave the way a reader expects.

## Error Handling

- Never swallow exceptions silently; always handle or propagate.
- Preserve error context when re-throwing; do not lose the original cause.
- Use specific error/exception types, not generic catch-all types.
- Make failure modes explicit — errors are part of the interface.

## Avoiding Duplication

- DRY: every piece of knowledge must have a single, authoritative representation.
- Boy Scout Rule: leave code cleaner than you found it.
- Copy-pasting a block is a signal to extract a function.

## Comments

- Comments explain WHY, not WHAT; code should be self-explanatory.
- Do not restate the code in prose — prefer self-documenting names.
- Document non-obvious decisions, business rules, and known trade-offs.

## Performance

- Avoid N+1 query patterns: batch or preload related data.
- Avoid unnecessary allocations, intermediate collections, and repeated computation.
- Optimize for readability first; optimize for performance only where profiling shows a bottleneck.
