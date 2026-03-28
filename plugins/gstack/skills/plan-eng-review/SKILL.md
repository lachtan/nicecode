---
name: plan-eng-review
description: Engineering plan review — lock architecture, tests, edge cases, and performance before implementation.
user-invocable: true
disable-model-invocation: true
---

Engineering review of the current plan. $ARGUMENTS

Review the plan thoroughly before any code changes. For every issue, explain tradeoffs, give an opinionated recommendation, and ask for input.

## Engineering Preferences

- **DRY** — flag repetition aggressively
- **Well-tested** — non-negotiable; too many tests beats too few
- **Engineered enough** — not hacky, not over-abstracted
- **Edge cases** — handle more, not fewer
- **Explicit over clever**
- **Minimal diff** — fewest new abstractions and files touched

## Step 0: Scope Challenge

Before reviewing, answer:

1. **What already exists?** What existing code solves each sub-problem? Can we reuse instead of rebuild?
2. **Minimum viable change?** What is the smallest set of changes for the goal? Flag scope creep.
3. **Complexity smell:** >8 files or >2 new classes/services → challenge whether a simpler approach exists.
4. **Best practices check:** For each new pattern or infrastructure, does the framework have a built-in? Known pitfalls? (Use WebSearch if needed.)

If complexity check triggers, recommend scope reduction. Once user decides, commit fully — don't re-argue later.

## Review Sections

Work through one at a time. Ask about each issue individually.

### 1. Architecture

- System design and component boundaries
- Dependency graph and coupling
- Data flow and bottlenecks
- Scaling and single points of failure
- Security (auth, data access, API boundaries)
- For each new codepath: one realistic production failure scenario

### 2. Code Quality

- Module structure and organization
- DRY violations
- Error handling and missing edge cases
- Technical debt hotspots
- Over-engineered vs under-engineered areas

### 3. Tests

Trace every codepath in the plan:

1. For each entry point, follow data through every branch, error path, and function call.
2. Map user flows and interaction edge cases (double-click, navigate away, stale data, slow connection).
3. Check each branch against existing tests.
4. Produce an ASCII coverage diagram:

```
[+] src/services/billing.ts
    ├── processPayment()
    │   ├── [TESTED]  Happy path + card declined — billing.test.ts:42
    │   └── [GAP]     Network timeout — NO TEST
    └── refundPayment()
        ├── [TESTED]  Full refund — billing.test.ts:89
        └── [GAP]     Partial refund — smoke test only

COVERAGE: 3/5 paths (60%)
GAPS: 2 paths need tests
```

For each gap: specify test file, what to assert, whether unit or E2E.

**Regression rule:** if the diff breaks existing behavior and no test covers it → critical, no skipping.

### 4. Performance

- N+1 queries and DB access patterns
- Memory usage concerns
- Caching opportunities
- Slow or high-complexity code paths

## Required Outputs

- **NOT in scope** — work considered and explicitly deferred, with rationale
- **What already exists** — existing code/flows that solve sub-problems
- **Failure modes** — for each new codepath, how it could fail in production. No test AND no error handling AND silent failure → critical gap
- **Completion summary** — issues found per section, gaps identified, scope decisions

## Rules

- One issue = one question — never batch
- Describe problems with file/line references
- For each option: effort, risk, maintenance burden in one line
- If a section has no issues, say so and move on
- If an issue has an obvious fix with no alternatives, state it and move on
