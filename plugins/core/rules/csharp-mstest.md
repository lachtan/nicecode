---
paths:
  - "**/*Tests*/**/*.cs"
  - "**/*Test.cs"
  - "**/*Tests.cs"
managed-by: https://github.com/lachtan/nicecode
version: "1.1.0"
last-change: "2026-09-25 11:13:51"
---

# MSTest

Naming and build rules live in `csharp-code-style.md`. This file covers what makes a test worth keeping.

## Assertions

- Match the style already used in the test project — **FluentAssertions** (`.Should()`) or **MSTest Assert**. Never mix them in one project.
- If the project mixes both styles, or is brand new with no tests, ask which style to use.
- Do not name test helpers `Invoking` or `Awaiting` — collides with FluentAssertions extension methods. For lambda-to-delegate helpers use `AsAction` / `AsFunc`.

## A test must be able to fail

- **Never verify production code with production code.** Checking `Write` by calling `Parse`, or comparing against `Format(...)`, passes even when both are broken. Write expected values as literals, by hand.
- **Never derive the expected value from the formula under test.** `$"{time:o} {id}"` restates the implementation. A round-trip `Parse(Format(x)) == x` proves neither direction.
- **Do not read the limit from production code.** Write the boundary value as a literal, so that a changed limit fails the test.
- **Cover the failure branch.** I/O errors, cancellation and error handling are the most likely code to be wrong and the least likely to get a test.
- **Skip the trivial.** No tests for getters/setters, DTOs without logic, 1:1 mapping, or framework behaviour.
- **Never wait a fixed time for background work.** `Task.Delay` / `Thread.Sleep` makes the test slow when it passes and flaky when the machine is loaded — a red test then means nothing. Poll the condition with a timeout, or drive the work through an injected clock or signal.
- **Every test must pass alone, in any order and repeatedly.** No state shared between tests, no reliance on what another test left behind — with `[assembly: Parallelize]` the order is not even deterministic.

## A test must survive refactoring

- Refactoring internals without changing behaviour must leave the test untouched. If the test would need editing, it tests the implementation.
- Assert on the resulting behaviour, not on which collaborator got called. Reaching for `Verify()` usually means the assert is in the wrong place.
- Mock only at process boundaries — network, database, filesystem, clock, randomness. Five mocks in one test means the test sits at the wrong level; move it up to where the real objects work together.

## Parametrize instead of repeating

- Two or more tests differing only in input and expected output → `[DataRow]` / `[DynamicData]`.
- Add a `DisplayName` when the argument values alone do not convey what the case is about — the default name already lists them.
- Do not merge cases whose assertions differ. A parametrized test must contain no `if`.
