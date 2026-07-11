---
paths:
  - "**/*.Tests.ps1"
managed-by: https://github.com/lachtan/nicecode
version: "1.0.0"
---

# Pester v5 Guidelines

Follow [powershell.md](./powershell.md) for general PowerShell conventions.

## Structure

- Use `*.Tests.ps1` naming pattern.
- Import tested functions via `BeforeAll { . $PSScriptRoot/FunctionName.ps1 }`.
- **No code outside Pester blocks** — all code must be inside `Describe`, `Context`, `It`, `BeforeAll`, etc. This is a v5 breaking change from v4.

## Scoping

- `BeforeAll` variables are available in child blocks as **read-only**. Do not reassign them in `It` blocks.
- `BeforeEach`, `It`, and `AfterEach` **share the same scope** — variables set in `BeforeEach` are directly accessible in `It`.
- Mocks are scoped to their containing block by default. A mock defined in a `Context` is not visible in a sibling `Context`.

## v5-Specific Features

- `-ForEach` works on `Describe`, `Context`, and `It` (not just `It`). `-TestCases` is a legacy alias for `-ForEach` on `It`.
- `Set-ItResult -Skipped -Because 'reason'` to skip at runtime (setup/teardown still run, unlike `-Skip` on the block).
- `Should.ErrorAction = 'Continue'` in `New-PesterConfiguration` to collect multiple assertion failures per test instead of stopping at the first.
- Configure runs via `New-PesterConfiguration` — do not pass individual parameters to `Invoke-Pester`. Key sections: `Run`, `Filter`, `Output`, `TestResult`, `CodeCoverage`, `Should`, `Debug`.
