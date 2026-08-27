# PostToolUse hook: auto-format PowerShell files after Edit/Write using PSScriptAnalyzer

$data = $input | Out-String | ConvertFrom-Json

$filePath = $data.tool_input.file_path
if (-not $filePath -or $filePath -notmatch '\.(ps1|psm1|psd1)$') {
    exit 0
}

if (-not (Get-Module -ListAvailable -Name PSScriptAnalyzer)) {
    Write-Warning ("PSScriptAnalyzer not found — PowerShell format check was skipped. " +
        "Install with: Install-Module PSScriptAnalyzer -Scope CurrentUser")
    exit 0
}

$original = Get-Content -Path $filePath -Raw
$formatted = Invoke-Formatter -ScriptDefinition $original

if ($formatted -ne $original) {
    Set-Content -Path $filePath -Value $formatted
}
