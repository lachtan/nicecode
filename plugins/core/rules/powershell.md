---
paths:
  - "**/*.{ps1,psm1}"
managed-by: https://github.com/lachtan/nicecode
version: "1.0.0"
last-change: "2026-07-11 07:54:50"
---

# PowerShell Coding Guidelines

## Naming

- Use only approved verbs (`Get-Verb` to list them). Verb-Noun naming and approved verbs apply to public/exported functions; internal helpers are exempt.
- Distinguish similar verbs: `New` creates a resource / `Add` adds to a container, `Invoke` is synchronous / `Start` is async, `Get` retrieves objects / `Read` extracts from a resource, `Find` looks for an object / `Search` creates a reference. Use `Remove` — never `Delete`.
- Nouns must be singular: `Get-Process`, not `Get-Processes`.
- Use full cmdlet and parameter names in scripts — no aliases (`Where-Object` not `?`, `ForEach-Object` not `%`, `Get-ChildItem` not `ls`).
- Use explicit paths — `$PSScriptRoot` and `Join-Path` instead of relative `.` / `..` or `~`.

## Variables

- PascalCase for public variables; camelCase is acceptable for private/local variables.
- Use meaningful names — never `$a`, `$b`, `$c`.
- Plural for collections (`$users`), singular for a single element (`$user`).

## Parameters

- Use standard parameter names (`Path`, `Name`, `Force`) and PascalCase.
- Use `[switch]` for boolean flags — never `[bool]` with `$true`/`$false`.
- Use `[ValidateSet()]`, `[ValidateNotNullOrEmpty()]` for constrained inputs.
- Use `ValueFromPipeline` / `ValueFromPipelineByPropertyName` for pipeline support.
- Use `[OutputType([Type])]` on functions that return objects.
- Do not set default values for `[Parameter(Mandatory)]` parameters.
- Do not default `[switch]` to `$true`.

## Output

- Return `[PSCustomObject]` — never formatted text or `Write-Host` for data.
- Stream one object at a time in the `process` block — avoid collecting into arrays.
- Action cmdlets: no output by default, add `-PassThru` switch when callers need the object back.
- Do not use `Format-Table`/`Format-List` inside functions — they emit format objects, not data. Formatting is the caller's responsibility.

## Error Handling

- In advanced functions, use `$PSCmdlet.WriteError()` (non-terminating) and `$PSCmdlet.ThrowTerminatingError()` (terminating) — not `Write-Error` / `throw`. `throw` points error messages at the throw line, not the calling code; `ThrowTerminatingError` gives clean messages pointing to the caller.
- Construct proper `[System.Management.Automation.ErrorRecord]` with category, target, and exception.
- Use `-ErrorAction Stop` on cmdlet calls inside `try` blocks — non-terminating errors silently bypass `catch` without it.
- Copy `$_` to a named variable immediately in `catch` blocks — any subsequent command overwrites it.
- For .NET method calls, set `$ErrorActionPreference = 'Stop'` before the call (they do not respect `-ErrorAction`), then reset to `'Continue'`.
- Do not rely on `$?` for error detection — it is unreliable; use exceptions instead.
- Use `[CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'High')]` for destructive operations; call `$PSCmdlet.ShouldProcess()` before making changes.

## Null Handling

- Compare with `$null` on the left: `$null -eq $value`, not `$value -eq $null` — arrays filter instead of comparing when `$null` is on the right.
- `if ($value)` tests for non-`$null` AND non-zero AND non-empty-string AND non-empty-array — not just `$null`.
- Null-conditional (PS 7+): use `${var}?.Property` — the `${}` syntax is required because `?` can be part of variable names.

## Numeric Literals

- PowerShell natively supports binary multiplier suffixes: `1KB` → 1024, `1MB` → 1048576, `1GB`, `1TB`, `1PB`. Use them directly instead of manual multiplication.
- The `0B` (zero bytes) suffix does **not** work — there is no `B` multiplier. Use plain `0` instead.

## Functions

- Do not use `return` to emit output — place objects on their own line. `return` implies single value and exit, which is misleading in pipeline-oriented code.
- Each function should return one type of object — mixed types break the table/list formatter (first object's type determines display format).
- Use the `clean {}` block (PS 7.3+) for resource cleanup — it runs even on Ctrl+C and pipeline stops, unlike `finally`.

## Formatting

- One True Brace Style (OTBS): opening brace at end of line, closing brace at beginning of line.
- 4 spaces per indent level, never tabs.
- Use splatting for long commands instead of backtick line continuation — backticks are fragile (invisible trailing whitespace breaks them).
- Single quotes for constant strings, double quotes only when interpolation is needed.
- Suppress output with `$null = Command` (fastest), not `| Out-Null` (slowest due to pipeline overhead).
- Spaces around operators, after commas, inside `$()` and `{}`.
- No semicolons as line terminators or in hashtable declarations.

## Style

- No `Read-Host` — accept all input via parameters for automation support.
- Include comment-based help (`.SYNOPSIS`, `.EXAMPLE`) for public functions.
- Comments should explain *why*, not *what* — well-named PowerShell code is self-documenting for "what."
- Use `#requires -version X.Y` in scripts and `PowerShellVersion` in module manifests to document the minimum required version.

## Performance

- `foreach` statement is faster than `ForEach-Object` cmdlet (no pipeline marshaling overhead).
- For large files, stream via pipeline or .NET `StreamReader` — do not load entire files into memory with `Get-Content`.
