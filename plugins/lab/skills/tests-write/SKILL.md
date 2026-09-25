---
name: tests-write
description: >-
  Use when adding tests to C# code that already exists — the user asks to
  "add tests", "write tests", "cover this with tests", or asks for test coverage
  of a class, method or module whose implementation is already written.
disable-model-invocation: false
user-invocable: true
managed-by: https://github.com/lachtan/nicecode
version: "1.0.0"
last-change: "2026-09-25 11:40:45"
---

# Writing tests for existing code

What makes an individual test good is in the `csharp-mstest.md` rule of the nicecode `core` plugin.
This skill is the order of work.

Writing *new* code instead? Use `superpowers:test-driven-development` if that skill is available —
a test written before the implementation cannot mirror it. If it is not, write the test first anyway:
contract, failing test, then the implementation; the rest of this skill does not apply.

## 1. Contract before implementation

Write down inputs, outputs, invariants and failure modes from the **public API, XML docs and
the request**. Do this before reading the method bodies.

If the implementation is already in context — the user pasted it, selected it, or you read it on
the way here — write the contract from the signature and the XML docs alone, and say in the report
that you did. The body is not a source for the contract at any point.

This step is the whole point. Starting from the body produces tests that restate it — they pass
on broken code and fail on correct refactoring. The contract is what the code *should* do; the
body is only what it currently does.

Now compare the contract against the body. **Every difference is a question for the user, not a
correction to the contract** — it is either a bug or an undocumented decision, and which one it is
is not yours to decide. Report it and carry on; only that one test waits for the answer.

Finally, pick the level: the highest one that is still fast and deterministic. Real collaborators
beat mocks.

## 2. Walk the checklist

Decide relevant / not relevant for each — out loud, briefly:

- empty input, `null`, single element
- boundaries: below the limit, **exactly on it**, above it
- duplicates, ordering, repeated calls (idempotence)
- numeric overflow, precision loss, division by zero
- cancellation, repeated start/stop, concurrent access
- dependency failure: I/O error, timeout, disconnect, error response
- time: midnight, DST, time zone, expiry
- encoding and culture: non-ASCII, multi-byte character split across reads

## 3. List before you write

Write the planned tests as a list first and strike the duplicates. Test count is a cost, not a
score — the target is the smallest set that covers the contract.

## 4. Sabotage what you wrote

Sabotage a file only when `git status` reports it unmodified — otherwise you cannot tell your
damage from the user's work, so skip the check and say why.

For each test, break the production code it covers — invert a condition, change a constant,
delete a line — and confirm the test fails. Restore with `git checkout -- <path>`, then confirm with
`git diff` on that file; an empty diff is part of the report.

A test that survives sabotage detects nothing. Delete it; do not weaken the sabotage until it
passes. Report which tests you sabotage-checked and which you could not.
