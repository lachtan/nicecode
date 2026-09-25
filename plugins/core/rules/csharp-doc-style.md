---
paths:
  - "**/*.cs"
managed-by: https://github.com/lachtan/nicecode
version: "1.1.0"
last-change: "2026-09-25 11:13:51"
---

# C# Doc Comments

## When to write one

- Write a doc comment only when it says something the declaration does not. For a type, the
  declaration is its name and the members it exposes.
- Use `<param>`, `<typeparam>` and `<returns>` only for what the name and the type do not say:
  a unit, a valid range, what `null` means.
- Use `<exception>` for what the member itself throws, and state the condition, not just the fact
  that it throws. Document an exception thrown by a member it calls only where callers are likely
  to run into it.
- Use `<remarks>` only for a usage note that does not fit into the one-sentence summary: a
  required call order, a constraint the caller has to respect.
- Use `<inheritdoc/>` on an implementation of a documented interface, and add your own text
  only for the behaviour that differs.
- Say who disposes of what, and whether a member is safe to call concurrently, wherever the
  signature does not make it clear.

## Form

- Put all text inside block tags: `<summary>`, `<param>`, `<typeparam>`, `<returns>`,
  `<exception>`, `<remarks>`, `<example>`.
- Keep the text of each tag to one sentence and two lines at most. Only `<remarks>` and
  `<example>` may run longer.
- Do not use inline tags inside the text:
  - a type, member or parameter name in plain text, not `<see cref="..."/>` or
    `<paramref name="..."/>`
  - `true`, `false` and `null` in plain text, not `<see langword="..."/>`
  - no `<c>`
- Do not use `<seealso>`; name the related type in a sentence.
- Use `<example>` with a `<code>` block inside it where a usage example is clearer than a
  sentence.
