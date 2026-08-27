# PostToolUse hook: validate Mermaid diagrams in markdown files

$data = $input | Out-String | ConvertFrom-Json
$filePath = $data.tool_input.file_path

if (-not $filePath -or -not $filePath.EndsWith('.md')) {
    exit 0
}

if (-not (Get-Command npx -ErrorAction SilentlyContinue)) {
    Write-Warning "npx not found — Mermaid diagram lint check was skipped. Install with: npm install -g npx"
    exit 1
}

npx --yes md-mermaid-lint $filePath
