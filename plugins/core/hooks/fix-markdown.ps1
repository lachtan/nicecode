# PostToolUse hook: auto-fix and lint markdown files after Edit/Write
# Runs markdownlint-cli2 --fix to auto-format, reports remaining issues

$data = $input | Out-String | ConvertFrom-Json

$filePath = $data.tool_input.file_path
if (-not $filePath -or -not $filePath.EndsWith('.md')) {
    exit 0
}

if (-not (Get-Command markdownlint-cli2 -ErrorAction SilentlyContinue)) {
    Write-Warning ("markdownlint-cli2 not found — markdown lint check was skipped. " +
        "Install with: npm install -g markdownlint-cli2")
    exit 0
}

# Auto-fix what can be fixed, report remaining issues (non-zero exit if any remain)
markdownlint-cli2 --fix $filePath
