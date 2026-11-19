# Formats one PowerShell file in place with PSScriptAnalyzer; called by check-edited-file.py

param([string]$Path)

$ErrorActionPreference = 'Stop'

if (-not (Get-Module -ListAvailable -Name PSScriptAnalyzer)) {
    exit 0
}

$original = Get-Content -Path $Path -Raw
$formatted = Invoke-Formatter -ScriptDefinition $original

if ($formatted -ne $original) {
    Set-Content -Path $Path -Value $formatted
}
