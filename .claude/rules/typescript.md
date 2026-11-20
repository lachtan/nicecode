---
paths:
  - "**/*.ts"
  - "**/*.tsx"
---

# TypeScript

Readability for a human comes first.

## Names

- No single-letter names, not even when an API's docs use them: `event`, not `e`; `engine`, not `$`.

## Structure

- Small files with one responsibility each; split by what the code is about, not by size.
- The entry file only wires: one line per event or command, each pointing to a named function in another module.
- Actions are named module-level functions taking their dependencies as parameters, not closures defined
  inside another function. An inline arrow is allowed only as a thin callback wrapper:
  `onPress: () => toggleSkill(engine, skill)`.

## Expressions

- Prefer plain `for` loops that push to an array over nested `.map()` inside expressions.
- Name intermediate values; never combine a ternary, a template and a call in one expression.
- Mark a promise you deliberately do not await with `void`.

## Types

- Type data from outside the code (store values, JSON, files a user can hand-edit) as `unknown` and narrow it
  with `typeof` / `Array.isArray` / type guards; never cast it to the expected shape.
- Use `as` only after a check has proven the value; tests may cast fakes with `as unknown as`.

## No JSX

- Do not use JSX. Call element constructors as plain functions: `Box({ flexDirection: "column", children: rows })`.
- Use `.tsx` only for a file that really contains JSX; otherwise `.ts`.

## Comments

- Every file starts with a `/** ... */` header saying what the file does.
- JSDoc on an export only when its name does not say enough: what `undefined` means, a value format
  (`` /** `<plugin>:<skill>`. */ ``), a side effect. Comments explain why, never what.

## Style

- Double quotes, semicolons, 2-space indent, max 120 columns.
- `interface` for object shapes; `type` for unions and aliases.

## Claude Code mods

- Import sibling files without an extension (`from "./skills"`); `claude plugin validate` rejects `.ts` extensions.
