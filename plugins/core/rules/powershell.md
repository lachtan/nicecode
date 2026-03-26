---
paths:
  - "**/*.{ps1,psm1}"
---

# PowerShell Cmdlet Guidelines

## Naming

- Use only approved verbs (`Get-Verb` to list them).
- Use full cmdlet and parameter names in scripts — no aliases (`Where-Object` not `?`, `ForEach-Object` not `%`, `Get-ChildItem` not `ls`).

## Parameters

- Use standard parameter names (`Path`, `Name`, `Force`) and PascalCase.
- Use `[switch]` for boolean flags — never `[bool]` with `$true`/`$false`.
- Use `[ValidateSet()]`, `[ValidateNotNullOrEmpty()]` for constrained inputs.
- Use `ValueFromPipeline` / `ValueFromPipelineByPropertyName` for pipeline support.

## Output

- Return `[PSCustomObject]` — never formatted text or `Write-Host` for data.
- Stream one object at a time in the `process` block — avoid collecting into arrays.
- Action cmdlets: no output by default, add `-PassThru` switch when callers need the object back.

## Error Handling

- In advanced functions, use `$PSCmdlet.WriteError()` (non-terminating) and `$PSCmdlet.ThrowTerminatingError()` (terminating) — not `Write-Error` / `throw`.
- Construct proper `[System.Management.Automation.ErrorRecord]` with category, target, and exception.
- Use `[CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'High')]` for destructive operations; call `$PSCmdlet.ShouldProcess()` before making changes.

## Numeric Literals

- PowerShell natively supports binary multiplier suffixes: `1KB` → 1024, `1MB` → 1048576, `1GB`, `1TB`, `1PB`. Use them directly instead of manual multiplication.
- The `0B` (zero bytes) suffix does **not** work — there is no `B` multiplier. Use plain `0` instead.

## Style

- No `Read-Host` — accept all input via parameters for automation support.
- Include comment-based help (`.SYNOPSIS`, `.EXAMPLE`) for public functions.
