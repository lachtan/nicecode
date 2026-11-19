---
name: tests-review
description: >-
  Use when auditing tests that already exist — the user asks to review, check,
  go through or prune a test file or test project, questions whether the tests
  there are any good, or wants to know whether a test file is worth what it costs.
disable-model-invocation: false
user-invocable: true
managed-by: https://github.com/lachtan/nicecode
version: "1.0.0"
last-change: "2026-09-25 11:40:45"
---

# Reviewing existing tests

Criteria for a good test are in the `csharp-mstest.md` rule of the nicecode `core` plugin.
This skill is what to produce.

## Removing tests is the point

A review that only adds tests has failed. The usual outcome of an honest audit is **fewer
tests covering more behaviour**.

Before any verdict, find where else the behaviour is covered. A test whose behaviour is already
asserted one level up is `delete`, not `keep` — the higher test survives refactoring that the
lower one blocks. Grep the test project for the same collaborator and the same fixture values;
a duplicate usually shows up as the same magic constant in two files.

Two tests differing only in input already deserve `DataRow`. Do not praise a group of
near-identical tests for covering a boundary — merge them and keep the boundary.

## Output: one row per test

No prose. No "what's good" opening, no "minor points" closing — both are ways of filling a
review without deciding anything. Rank by severity, highest first.

| Test                                     | Verdict       | Why                                 |
| ---------------------------------------- | ------------- | ----------------------------------- |
| `Parse_RecordProducedByFormat`           | `delete`      | Round-trip proves neither direction |
| `Start_Fresh…` + `…AtMaxAge` + `…Older…` | `parametrize` | Same act, differs only in age       |

Verdicts: `keep` · `parametrize` · `merge` · `delete` · `rewrite` · `expand` · `raise-level`

Write the reasons in the user's language, one line each. A verdict without a concrete defect is
`keep` — do not pad the table.

## Then, separately

- **Untested behaviour** — only real branches with no coverage, named by branch. Not ideas for
  more tests.
- **Tests that promise more than they check** — the name or comment claims a guarantee the
  asserts do not deliver: a race the test cannot lose, a "writes are batched" claim verified
  only by the final value, a whole file that asserts after shutdown and so would pass with the
  signalling removed.

## Verify before you report

Where you can build and run: break the covered production line and check the test actually
fails. Sabotage a file only when `git status` reports it unmodified — otherwise you cannot tell
your damage from the user's work, so skip the check and say why. Restore with
`git checkout -- <path>`, then confirm with `git diff` on that file; an empty diff is part of the report.

A test that passes against broken code is `delete`, not `keep` — and now you have proof rather
than an opinion.

Say which findings you verified this way and which stayed unverified.

## Close with

One line, last: `N tests before → M after`, plus the count per verdict. If M is not lower than N,
one sentence saying why the audit did not reduce anything.
