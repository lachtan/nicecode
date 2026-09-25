# Formats one PowerShell file in place with PSScriptAnalyzer; called by format-powershell.py

param([string]$Path)

# PSScriptAnalyzer is optional; without it the file is left as is.
if (-not (Get-Module -ListAvailable -Name PSScriptAnalyzer)) {
    exit 0
}

$original = Get-Content -Path $Path -Raw
$formatted = Invoke-Formatter -ScriptDefinition $original

if ($formatted -ne $original) {
    Set-Content -Path $Path -Value $formatted
}
