[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$COMPUTER_ICON = [char]::ConvertFromUtf32(0x1F5A5) + [char]0xFE0F
$FOLDER_ICON = [char]::ConvertFromUtf32(0x1F4C1)
$BRANCH_ICON = [char]::ConvertFromUtf32(0x1F33F)
$EFFORT_ICON = [char]::ConvertFromUtf32(0x1F4A1)
$BAR_FILLED = [char]0x2593
$BAR_EMPTY = [char]0x2591

function Format-TokenCount {
    param([double]$Value)
    if ($null -eq $Value) { return "0" }
    if ($Value -ge 1000000) {
        $num = ("{0:N1}" -f ($Value / 1000000)) -replace '\.0$', ''
        return "${num}M"
    }
    if ($Value -ge 1000) {
        $num = ("{0:N1}" -f ($Value / 1000)) -replace '\.0$', ''
        return "${num}k"
    }
    return "$([math]::Round($Value))"
}

function Get-CumulativeOutputTokens {
    param([string]$SessionId, [string]$TranscriptPath)

    # Cumulative output-token count for the session, computed incrementally.
    # The cache holds the already-processed transcript offset, the running total,
    # and the last counted message.id (lines of one API response are contiguous,
    # so this single id is enough to dedup across a read boundary). Dedup is
    # required because one response spans several transcript lines with the same
    # output_tokens.
    if (-not $TranscriptPath -or -not (Test-Path $TranscriptPath)) { return 0 }

    $cacheDir = Join-Path $HOME ".claude/session-env/$SessionId"
    $cacheFile = Join-Path $cacheDir "statusline-out.json"

    $offset = [long]0
    $total = 0
    $lastId = ""
    if (Test-Path $cacheFile) {
        try {
            $cache = Get-Content -Raw $cacheFile | ConvertFrom-Json
            $offset = [long]$cache.offset
            $total = [int]$cache.total
            $lastId = "$($cache.lastId)"
        }
        catch {}
    }

    $fileLength = (Get-Item $TranscriptPath).Length
    if ($fileLength -lt $offset) {
        # New or truncated session — start from zero.
        $offset = [long]0
        $total = 0
        $lastId = ""
    }

    if ($fileLength -gt $offset) {
        $stream = [System.IO.File]::Open($TranscriptPath, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::ReadWrite)
        try {
            $stream.Seek($offset, [System.IO.SeekOrigin]::Begin) | Out-Null
            $reader = New-Object System.IO.StreamReader($stream, [System.Text.Encoding]::UTF8)
            $newText = $reader.ReadToEnd()
        }
        finally {
            $stream.Dispose()
        }

        # Process only complete lines; leave a partially written last line for next time.
        $lastNewline = $newText.LastIndexOf("`n")
        if ($lastNewline -ge 0) {
            $completeText = $newText.Substring(0, $lastNewline + 1)
            $offset += [System.Text.Encoding]::UTF8.GetByteCount($completeText)

            foreach ($line in $completeText -split "`n") {
                if ($line -notlike '*"type":"assistant"*') { continue }
                try {
                    $entry = $line | ConvertFrom-Json
                    $ot = $entry.message.usage.output_tokens
                    $id = "$($entry.message.id)"
                    if ($ot -and $id -and $id -ne $lastId) {
                        $total += $ot
                        $lastId = $id
                    }
                }
                catch {}
            }
        }

        [System.IO.Directory]::CreateDirectory($cacheDir) | Out-Null
        [PSCustomObject]@{ offset = $offset; total = $total; lastId = $lastId } |
            ConvertTo-Json -Compress | Set-Content -Path $cacheFile -Encoding UTF8
    }

    return $total
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
$contextSize = 0
if ($ctx -and $ctx.context_window_size) { $contextSize = $ctx.context_window_size }
$totalInput = 0
if ($ctx -and $null -ne $ctx.total_input_tokens) { $totalInput = $ctx.total_input_tokens }
$totalOutput = Get-CumulativeOutputTokens -SessionId $data.session_id -TranscriptPath $data.transcript_path

$barWidth = 10
$filled = [math]::Min($barWidth, [math]::Floor($usedPct * $barWidth / 100))
$bar = ("$BAR_FILLED" * $filled) + ("$BAR_EMPTY" * ($barWidth - $filled))

$ESC = [char]27
$RESET = "$ESC[0m"
if ($usedPct -ge 90) { $barColor = "$ESC[31m" }
elseif ($usedPct -ge 70) { $barColor = "$ESC[33m" }
else { $barColor = "$ESC[32m" }

$inFmt = Format-TokenCount $totalInput
$outFmt = Format-TokenCount $totalOutput
$sizeFmt = Format-TokenCount $contextSize
$effort = $data.effort.level

$segments = @("$COMPUTER_ICON $hostName", "$FOLDER_ICON $cwd")
if ($branch) { $segments += "$BRANCH_ICON $branch" }
$segments += "$modelName $sizeFmt"
if ($effort) { $segments += "$EFFORT_ICON $effort" }
$segments += "$usedPct% $barColor$bar$RESET"
$segments += "$([char]0x2193) $inFmt $([char]0x2191) $outFmt"

Write-Host ($segments -join " | ")

