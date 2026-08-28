---
paths:
  - "**/*.cs"
managed-by: https://github.com/lachtan/nicecode
version: "1.0.0"
last-change: "2026-07-11 07:54:50"
---

# C# Code Style & Conventions

**Base style:** Follow [dotnet/runtime C# Coding Style](https://github.com/dotnet/runtime/blob/main/docs/coding-guidelines/coding-style.md) for all formatting, naming, and code organization conventions. This document only contains project-specific additions and modern C# patterns.

## C# version and formatting

- **C# 14.0** (LangVersion 14.0), .NET 9.0 as primary target
- Formatting defined in `.editorconfig`
- Use `var` wherever possible for local variables
- `nameof` instead of string literals for member names
- Always add an empty line between method declarations for readability
- In switch statements, add an empty line between case blocks for better readability
- Ensure that the final return statement of a method is on its own line
- Comments can be written in Czech language without diacritical marks

## Modern C# patterns

Prefer modern C# syntax over legacy patterns:

- Interpolated strings `$"Hello {name}"` instead of `string.Format("Hello {0}", name)`
- File-scoped namespaces instead of block-scoped
- Records/record structs instead of verbose DTOs
- Pattern matching instead of type checks with casts
- Collection expressions instead of explicit constructors
- Target-typed `new()` instead of redundant type names
- Expression-bodied members (`=>`) for single-expression methods and properties
- `using` declarations instead of `using` blocks
- Ranges and indices instead of `Substring`/`Skip`/`Take`
- Init-only setters for immutable properties
- Switch expressions over switch statements where appropriate
- Nullable reference types
- Null-conditional operators (`?.`, `?[]`) instead of explicit null checks (e.g., `scope?.Dispose()`)
- Primary constructors for `record` and `readonly record struct`
- `field` keyword for property backing fields (C# 14)
- Extension members (C# 14)
- `nameof` accessing instance members from static context (C# 14)
- Overloadable compound assignment operators (C# 14): `+=`, `-=`, `*=`, `/=`, `%=`, `&=`, `|=`, `^=`, `<<=`, `>>=`, `>>>=`
  Rules: must be `public`, non-static, return `void`, exactly one parameter.
  Example: `public void operator +=(Fraction other) => numerator += other.numerator;`
- Instance increment/decrement operators (C# 14): `++`, `--` can now be instance methods
  Rules: must be `public`, non-static, return `void`, no parameters.
  Example: `public void operator ++() => value++;`
- `params` with any collection type, not just arrays
- `ref readonly` parameters

## Naming conventions

- PascalCase for public members, methods, components
- camelCase for private fields and local variables
- Prefix `I` for interfaces (IUserService)
- Suffix `X` for extension classes (UserServiceX)
- Do not use underscore prefix `_` for field or variable names
- Use descriptive names; no single-letter names except loop counters (`i`, `j`, `k`); short or cryptic abbreviations are not acceptable

## Nullable Reference Types (NRT)

- Never add `#nullable disable` to new code.
- Enabled via property `<IsNrtEnabled>true</IsNrtEnabled>` (default for non-3rd party projects)
- Use `is null` / `is not null` instead of `== null` / `!= null`
- Trust the C# null annotations - don't add null checks when the type system says a value cannot be null
- Helpers: `RsjDebug.NotNull()`, `RsjRelease.NotNull()`, `.TryGet()`, `.GetValue()`
- For LINQ null filtering: `items.WhereNotNull()` instead of `.Where(i => i is not null)`

## Performance

- Avoid N+1 queries, unnecessary allocations, boxing
- Use `Span<T>` or `Memory<T>` for buffer operations
- Prefer efficient LINQ - avoid repeated enumeration
- Use `StringBuilder` for string concatenation in loops

## Error handling

- Always handle exceptions appropriately - no swallowed exceptions
- Preserve error context when re-throwing
- Use specific exception types over generic `Exception`

## Code design

- Use named arguments in object construction to keep property names explicit.
- Keep classes small and focused on a single responsibility. When a class grows too large, split it into smaller types.
- Write methods that do exactly one thing. Extract logic into well-named helper methods instead of writing long method bodies.
- Do not add comments that just restate what the code does. Only add comments to explain non-obvious logic or business decisions.
- Avoid deep nesting — max 2-3 levels. Use early returns and guard clauses to reduce indentation.
- Do not repeat logic — extract duplicated code into a shared method.
- Prefer composition over inheritance.
- Replace magic numbers and strings with named constants or enums.
- Names of methods, classes, and variables must reveal their intent clearly.

## Testing

- MSTest framework (assertion style: match existing project — see `csharp-mstest.md` Assertions section)
- Test projects: `[ProjectName].Tests.csproj`
- Naming pattern: `MethodName_Scenario_ExpectedBehavior`
- Do not use "Arrange", "Act", "Assert" comments
- **Always verify build before running tests** - run `dotnet build` first to ensure code compiles, then run `dotnet test`. Never use `--no-build` flag after code changes.

## Async patterns

- Suffix `Async` for async methods
- `ConfigureAwait(false)` in library code
- Never use `.Wait()`, `.Result` or `.GetAwaiter().GetResult()` in async code
- `Task.WhenAll()` for parallel execution
