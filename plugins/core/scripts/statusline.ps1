# 🖥️ pcmbl04 | 📁 C:\source\work\cat-deda | 🌿 mbl/sf-x4 | 💡 Opus 5 / high | 4% ░░░░░░░░░░ | ↓ 42k ↑ 374

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# U+FE0F is a variation selector — invisible, forces emoji rendering over the text glyph.
$COMPUTER_ICON = "🖥`u{FE0F}"
$FOLDER_ICON = '📁'
$BRANCH_ICON = '🌿'
$MODEL_ICON = '💡'
$TOKENS_IN_ICON = '↓'
$TOKENS_OUT_ICON = '↑'
$BAR_FILLED = '▓'
$BAR_EMPTY = '░'

$ESC = [char]27
$ANSI_RESET = "$ESC[0m"
$ANSI_RED = "$ESC[31m"
$ANSI_GREEN = "$ESC[32m"
$ANSI_YELLOW = "$ESC[33m"
$ANSI_ORANGE = "$ESC[38;5;208m"

$MODEL_COLOR = $ANSI_ORANGE
$EFFORT_COLOR = $ANSI_YELLOW

function Format-TokenCount([double]$Value) {
    if ($null -eq $Value) { return "0" }
    if ($Value -ge 1000000) {
        $num = ($Value / 1000000).ToString("F1", [cultureinfo]::InvariantCulture) -replace '\.0$', ''
        return "${num}M"
    }
    if ($Value -ge 1000) {
        $num = ($Value / 1000).ToString("F1", [cultureinfo]::InvariantCulture) -replace '\.0$', ''
        return "${num}k"
    }
    return "$([math]::Round($Value))"
}

function New-TokenCacheState {
    return [PSCustomObject]@{ offset = [long]0; total = 0; lastId = "" }
}

function Read-TokenCacheState([string]$CacheFile) {
    if (-not (Test-Path $CacheFile)) { return New-TokenCacheState }
    try {
        $cache = Get-Content -Raw $CacheFile | ConvertFrom-Json
        return [PSCustomObject]@{
            offset = [long]$cache.offset
            total  = [int]$cache.total
            lastId = "$($cache.lastId)"
        }
    }
    catch { return New-TokenCacheState }
}

function Save-TokenCacheState([string]$CacheFile, [PSCustomObject]$State) {
    [System.IO.Directory]::CreateDirectory((Split-Path $CacheFile)) | Out-Null
    $State | ConvertTo-Json -Compress | Set-Content -Path $CacheFile -Encoding UTF8
}

function Read-TranscriptTail([string]$TranscriptPath, [long]$Offset) {
    $stream = [System.IO.File]::Open($TranscriptPath, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::ReadWrite)
    try {
        $stream.Seek($Offset, [System.IO.SeekOrigin]::Begin) | Out-Null
        $reader = New-Object System.IO.StreamReader($stream, [System.Text.Encoding]::UTF8)
        return $reader.ReadToEnd()
    }
    finally {
        $stream.Dispose()
    }
}

function Add-OutputTokens([PSCustomObject]$State, [string]$Text) {
    $lastNewline = $Text.LastIndexOf("`n")
    if ($lastNewline -lt 0) { return $State }

    $completeText = $Text.Substring(0, $lastNewline + 1)
    $total = $State.total
    $lastId = $State.lastId

    foreach ($line in $completeText -split "`n") {
        if ($line -notlike '*"type":"assistant"*') { continue }
        try {
            $entry = $line | ConvertFrom-Json
            $outputTokens = $entry.message.usage.output_tokens
            $messageId = "$($entry.message.id)"
            if ($outputTokens -and $messageId -and $messageId -ne $lastId) {
                $total += $outputTokens
                $lastId = $messageId
            }
        }
        catch {}
    }

    return [PSCustomObject]@{
        offset = $State.offset + [System.Text.Encoding]::UTF8.GetByteCount($completeText)
        total  = $total
        lastId = $lastId
    }
}

function Get-CumulativeOutputTokens([string]$SessionId, [string]$TranscriptPath) {
    if (-not $TranscriptPath -or -not (Test-Path $TranscriptPath)) { return 0 }

    $cacheFile = Join-Path $HOME ".claude/session-env/$SessionId/statusline-out.json"
    $state = Read-TokenCacheState $cacheFile

    $fileLength = (Get-Item $TranscriptPath).Length
    if ($fileLength -lt $state.offset) { $state = New-TokenCacheState }
    if ($fileLength -le $state.offset) { return $state.total }

    $state = Add-OutputTokens $state (Read-TranscriptTail $TranscriptPath $state.offset)
    Save-TokenCacheState $cacheFile $state

    return $state.total
}

$data = $input | Out-String | ConvertFrom-Json

$cwd = $data.workspace.current_dir
if (-not $cwd) { $cwd = $data.cwd }

$hostName = "$env:COMPUTERNAME".ToLower()

$branch = git -C "$cwd" branch --show-current 2>$null

$modelName = $data.model.display_name -replace '\s*\(.*\)$', ''

$ctx = $data.context_window
$usedPct = 0
if ($ctx -and $null -ne $ctx.used_percentage) { $usedPct = [math]::Round($ctx.used_percentage) }
$totalInput = 0
if ($ctx -and $null -ne $ctx.total_input_tokens) { $totalInput = $ctx.total_input_tokens }
$totalOutput = Get-CumulativeOutputTokens -SessionId $data.session_id -TranscriptPath $data.transcript_path

$barWidth = 10
$filled = [math]::Min($barWidth, [math]::Floor($usedPct * $barWidth / 100))
$bar = ("$BAR_FILLED" * $filled) + ("$BAR_EMPTY" * ($barWidth - $filled))

if ($usedPct -ge 90) { $barColor = $ANSI_RED }
elseif ($usedPct -ge 70) { $barColor = $ANSI_YELLOW }
else { $barColor = $ANSI_GREEN }

$inFmt = Format-TokenCount $totalInput
$outFmt = Format-TokenCount $totalOutput
$effort = $data.effort.level

$segments = @("$COMPUTER_ICON $hostName", "$FOLDER_ICON $cwd")
if ($branch) { $segments += "$BRANCH_ICON $branch" }

$modelSegment = "$MODEL_ICON $MODEL_COLOR$modelName$ANSI_RESET"
if ($effort) { $modelSegment += " / $EFFORT_COLOR$effort$ANSI_RESET" }
$segments += $modelSegment

$segments += "$usedPct% $barColor$bar$ANSI_RESET"
$segments += "$TOKENS_IN_ICON $inFmt $TOKENS_OUT_ICON $outFmt"

Write-Host ($segments -join " | ")

