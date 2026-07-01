# PostToolUse hook: validates Mermaid diagrams in markdown files after Edit/Write
# Runs @mermaid-lint/cli (mermaid-lint) — syntax check only, no browser

$data = $input | Out-String | ConvertFrom-Json

$filePath = $data.tool_input.file_path
if (-not $filePath -or -not $filePath.EndsWith('.md')) {
    exit 0
}

if (-not (Get-Command mermaid-lint -ErrorAction SilentlyContinue)) {
    Write-Warning "mermaid-lint not found — Mermaid validation skipped. Install with: npm install -g @mermaid-lint/cli"
    exit 1
}

mermaid-lint $filePath
