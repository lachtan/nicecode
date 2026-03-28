---
name: debug
description: Systematic root-cause debugging — investigate before fixing. Use when asked to debug, fix a bug, or investigate an error.
user-invocable: true
---

Systematic debugging for: $ARGUMENTS

## Iron Law

No fixes without root cause investigation first. Fixing symptoms creates whack-a-mole debugging.

## Phase 1: Investigate

Gather context before forming any hypothesis.

1. **Collect symptoms** — read error messages, stack traces, reproduction steps. If context is missing, ask one question at a time.
2. **Read the code** — trace the code path from symptom back to potential causes.
3. **Check recent changes** — was this working before? A regression means the root cause is in the diff.
4. **Reproduce** — can you trigger the bug deterministically? If not, gather more evidence.

Output: **"Root cause hypothesis: ..."** — a specific, testable claim about what is wrong and why.

## Phase 2: Pattern Analysis

Check if the bug matches a known pattern:

| Pattern | Signature | Where to look |
|---------|-----------|---------------|
| Race condition | Intermittent, timing-dependent | Concurrent access to shared state |
| Nil/null propagation | NoMethodError, TypeError | Missing guards on optional values |
| State corruption | Inconsistent data, partial updates | Transactions, callbacks, hooks |
| Integration failure | Timeout, unexpected response | External API calls, service boundaries |
| Configuration drift | Works locally, fails elsewhere | Env vars, feature flags, DB state |
| Stale cache | Old data, fixes on cache clear | Redis, CDN, browser cache |

If the bug doesn't match known patterns, use WebSearch (sanitize queries first — strip hostnames, IPs, file paths, customer data).

## Phase 3: Hypothesis Testing

Before writing ANY fix, verify your hypothesis.

1. **Confirm** — add a temporary log/assertion at the suspected root cause. Run the reproduction. Does the evidence match?
2. **If wrong** — search for the error (sanitized), return to Phase 1. Do not guess.
3. **3-strike rule** — if 3 hypotheses fail, STOP. Ask the user:
   - Continue with a new hypothesis
   - Escalate for human review
   - Add logging and catch it next time

Red flags — slow down if you see:
- "Quick fix for now" — there is no "for now"
- Proposing a fix before tracing data flow — you're guessing
- Each fix reveals a new problem — wrong layer, not wrong code

## Phase 4: Fix

Once root cause is confirmed:

1. **Fix the root cause, not the symptom.** Smallest change that eliminates the problem.
2. **Minimal diff** — fewest files, fewest lines. Do not refactor adjacent code.
3. **Regression test** — must fail without the fix and pass with it.
4. **Run the full test suite.** No regressions allowed.
5. **If fix touches >5 files** — flag the blast radius and ask before proceeding.

## Phase 5: Verify and Report

Reproduce the original bug and confirm it's fixed. Run tests.

Output:

```
Symptom:         [what was observed]
Root cause:      [what was actually wrong]
Fix:             [what changed, with file:line references]
Evidence:        [test output proving fix works]
Regression test: [file:line of the new test]
```

## Rules

- 3+ failed fixes: stop and question the architecture
- Never apply a fix you cannot verify
- Never say "this should fix it" — prove it
- Fix touches >5 files: ask about blast radius first
