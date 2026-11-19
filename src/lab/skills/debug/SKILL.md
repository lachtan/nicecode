---
name: debug
description: >-
  Use on a bug, test failure or unexpected behavior whose cause is not yet known —
  forces root-cause investigation before any fix. Triggers on a failing test, a stack
  trace, a flaky test, "why does this happen". Not for a cause already established.
disable-model-invocation: false
user-invocable: true
origin: https://github.com/obra/superpowers/tree/v6.3.0/skills/systematic-debugging
managed-by: https://github.com/lachtan/nicecode
version: "6.3.0"
last-change: "2026-08-28 09:28:03"
---

# Debugging

No fix before the cause is known. A change that makes the symptom go away without
naming the cause is a guess, and guessing costs more than the investigation would have.

## 1. Find the cause

- Read the whole error — stack trace, line numbers, error codes. The answer is often
  already in it.
- Reproduce it. Without a reliable trigger you have no way to know a fix worked; gather
  more data instead of guessing.
- Check what changed: `git log`, `git diff`, new dependencies, config, environment.
- Trace the bad value backward. Where the error surfaces is where it was *detected* —
  find the call that passed the bad value, then what passed it that, up to the origin.
- In a multi-component system (CI → build → sign, API → service → DB) do not guess
  which part fails. Log what enters and what leaves each boundary, run once, and read
  which boundary the data crosses wrong.
- If a similar path in this repo works, list every difference between it and the broken
  one. Do not dismiss any of them as "that can't matter".

Then say it out loud: "X happens because Y". If you cannot finish that sentence, you are
not done here.

## 2. One hypothesis at a time

The smallest change that tests the hypothesis, one variable. No second fix, no refactor,
no "while I'm here" cleanup bundled in — if it works you won't know which part did it.

## 3. Fix and prove it

- Write the failing test first and watch it fail. A test that has never failed proves
  nothing.
- Fix at the origin, not where the error surfaced. Add a guard at a second layer only
  where a different code path can reach the same state — not validation at every layer
  by default.
- Run the verification command and read its output. Never report success from
  expectation.

## 4. Three failed fixes = wrong premise

Count the attempts. After the third failed fix, stop — do not start a fourth. Three
fixes failing in three different places is not three bad hypotheses, it is one wrong
assumption underneath them: usually the design, or something you believe about the
system that is not true. Say so and settle it before touching more code.

## Flaky test = a race, not a slow machine

A test that passes sometimes is waiting on a guess. Replace `sleep` / `setTimeout` with
polling the condition the test actually cares about; a timeout is then the failure path,
not the wait. Keep a fixed delay only where the timing itself is under test (debounce,
throttle) and write down why.

## Red flags

| Thought | Reality |
|---|---|
| "Quick fix now, investigate later" | The first fix sets the pattern. There is no later. |
| "It's probably X, let me fix that" | "Probably" means step 1 got skipped. |
| "I'll change these two things and run the tests" | Then the result teaches you nothing. |
| "The issue is simple, it doesn't need this" | Simple bugs have causes too, and finding them is quick. |
| "Emergency, no time to investigate" | Guess-and-check is slower than investigating. Always. |
| "I'll skip the test, I checked it by hand" | Then nothing stops it coming back. |
| "One more attempt" (after 2+ failures) | Section 4. Stop. |
| "The reference is long, I'll adapt the pattern" | Partial understanding of a pattern guarantees a bug. |

Your partner saying "stop guessing", "is that not happening?", "will that show us?" or
"we're stuck?" means you are in the row above. Go back to step 1.

## When the cause is not in the code

Some failures really are environmental, timing-dependent or external. That is a
conclusion you reach after step 1, not a reason to skip it — and it is the wrong answer
roughly nineteen times out of twenty. When it is right: say what you ruled out, handle it
explicitly (retry, timeout, a clear error) and leave a log line behind for next time.
