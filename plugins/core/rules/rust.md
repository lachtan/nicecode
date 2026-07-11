---
paths:
  - "**/*.rs"
managed-by: https://github.com/lachtan/nicecode
version: "1.0.0"
---

# Rust Coding Conventions

Follow idiomatic Rust based on
[The Rust Book](https://doc.rust-lang.org/book/),
[Rust API Guidelines](https://rust-lang.github.io/api-guidelines/) and
[RFC 430 naming conventions](https://github.com/rust-lang/rfcs/blob/master/text/0430-finalizing-naming-conventions.md).

## STRICT: No Panicking Unwraps

**NEVER use in production code:**

- `unwrap()` — use `?`, `match`, `if let`, `.unwrap_or()` / `.unwrap_or_else()` / `.unwrap_or_default()`
- `expect()` — same alternatives as above
- `panic!()` — return `Result` or `Option` instead
- `unreachable!()` without proof — only when the compiler cannot see the invariant
- `todo!()` — not allowed in committed code

Always propagate errors with `?` or handle explicitly. Change `()` return types to `Result<(), E>` when needed.

**Exceptions:** allowed in `#[test]` functions, test helpers (`#[cfg(test)]`), and `main()`.

## Error Handling

- Use `Result<T, E>` for recoverable errors, `Option<T>` for optional values
- Create custom error types with `thiserror`, use `anyhow` in binaries
- Provide meaningful error messages and context
- Validate arguments and return appropriate errors
- Never use sentinel values (-1, null) — use `Option<T>` or `Result<T, E>` instead
- Use `Option`/`Result` transforms (`.map()`, `.and_then()`, `.unwrap_or()`) instead of `match`

## Ownership and Borrowing

- Prefer borrowing (`&T`) over cloning — use `clone()` only when ownership transfer is necessary
- Use `&str` over `String` for parameters when ownership isn't needed
- Prefer zero-copy operations to avoid unnecessary allocations
- Annotate lifetimes explicitly only when the compiler cannot infer them
- `Rc<T>` / `RefCell<T>` for single-threaded, `Arc<T>` / `Mutex<T>` / `RwLock<T>` for multi-threaded
- Prefer owned data over references in structs to simplify lifetime management
- Avoid self-referential structures — prefer indexing or `Pin` when absolutely necessary
- Prefer channels over `Arc<Mutex<T>>` for concurrency; keep lock scopes minimal
- Don't over-optimize prematurely — benchmark before avoiding allocations

## Code Style

- After every change run `cargo fmt`, `cargo clippy`, `cargo check`, `cargo test` — fix all issues before committing
- Keep functions under ~40 lines, files under ~400 lines
- Lines under 100 characters when possible

### Naming

- Follow RFC 430 conventions, use descriptive names
- Booleans: prefix with `is_`, `has_`, `can_`, `should_`
- Prefer positive conditions — `if has_items` over `if !is_empty`

### Imports

Order `use` statements separated by blank lines:

1. `std` / `core` / `alloc`
2. External crates
3. Local modules (`crate::`, `super::`, `self::`)

Never use glob imports (`use module::*`).

### File Organization

Top-to-bottom order:

1. Module documentation (`//!`)
2. `use` imports
3. Constants and type aliases
4. Structs, enums, and `impl` blocks
5. Public functions
6. Private helpers
7. `#[cfg(test)] mod tests`

### Comments

- Comment **why**, not **what** — prefer renaming or restructuring over adding a comment
- No commented-out code — git remembers

## Patterns to Follow

- Use modules (`mod`) and `pub` to encapsulate logic
- Structure async code with `async/await` and `tokio`
- Prefer enums over flags for type safety
- Use iterators over index-based loops — keep them lazy, avoid premature `collect()`
- Flatten nesting with `let ... else` and early `return`/`continue`
- Group related values into structs — use named structs over tuples with >2 elements
- Use type aliases for complex generics — `type UserMap = HashMap<UserId, Vec<Permission>>`
- Break long method chains (>3–4 steps) into named intermediate variables
- Declare variables close to their use
- Keep consistent abstraction level within a function
- Split binary (`main.rs`) and library (`lib.rs`) code
- Encode invariants into the type system — make invalid states unrepresentable
- Use functions, methods, and traits for common behavior; use marker traits for properties not expressible in signatures
- Use builder pattern for structs with many optional fields
- Use `Drop` for RAII resource cleanup
- Keep Cargo features additive — don't feature-gate public fields or trait methods
- Separate logical blocks with blank lines

## Patterns to Avoid

- No panics in library code — return `Result`
- No global mutable state — use dependency injection or thread-safe containers
- No deeply nested logic — refactor with functions or combinators
- No `unsafe` unless required and fully documented
- No wildcard `_ =>` in `match` on own enums — exhaustive matching catches new variants
- Avoid too many function parameters — group into a struct
- Don't mix setup/initialization with core logic in one function

## API Design

- Derive standard traits where appropriate: `Debug`, `Clone`, `Copy`, `Default`, `PartialEq`, `Eq`, `PartialOrd`, `Ord`, `Hash`
- Use standard conversions: `From`, `AsRef`, `AsMut`
- Implement `From` for infallible conversions (gives `Into` for free); use `TryFrom`/`TryInto` for fallible; use `Into` in trait bounds; avoid `as` casts
- Use newtypes for semantic meaning and to bypass the orphan rule
- Prefer specific types over `bool` parameters
- Functions with a clear receiver should be methods
- Structs should have private fields
- All public types must implement `Debug`
- Default to `pub(crate)` — minimize public API surface
- Prefer generics over `dyn Trait` unless heterogeneous collections or type erasure are needed
- Provide default implementations for trait methods when possible
- Re-export dependencies whose types appear in your public API
- Document all public APIs with `///` rustdoc including examples

## Testing

- Unit tests in `#[cfg(test)]` modules alongside the code
- Integration tests in `tests/` directory
- Document error conditions and safety considerations
- Doc examples should use `?`, never `unwrap()`

## Recommended Crates

| Purpose                    | Crate                         |
| -------------------------- | ----------------------------- |
| Error types (library)      | `thiserror`                   |
| Error propagation (binary) | `anyhow`                      |
| Serialization              | `serde` + format crates       |
| Async runtime              | `tokio`                       |
| Logging                    | `tracing` (prefer over `log`) |
| CLI parsing                | `clap` (derive)               |
| HTTP client                | `reqwest`                     |
| Date/time                  | `chrono` or `time`            |
| Regex                      | `regex`                       |
| Iterator extensions        | `itertools`                   |
| Random numbers             | `rand`                        |
| Byte manipulation          | `bytes`                       |
| Data parallelism           | `rayon`                       |
