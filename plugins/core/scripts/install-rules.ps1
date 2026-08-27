param(
    [Parameter(Mandatory)]
    [ValidateSet("project", "user")]
    [string]$Scope,

    [string]$ProjectDir = (Get-Location).Path
)

$ErrorActionPreference = "Stop"

$FrontmatterDelimiter = "---"
$ManagedBy = "https://github.com/lachtan/nicecode"

$PluginRulesDir = Join-Path (Split-Path -Parent $PSScriptRoot) "rules"
$BaseDir = if ($Scope -eq "user") { $HOME } else { (Resolve-Path $ProjectDir).Path }
$TargetDir = Join-Path $BaseDir ".claude/rules/plugins/nicecode/core"

if (-not (Test-Path $PluginRulesDir -PathType Container)) {
    Write-Error "Plugin rules directory not found: $PluginRulesDir"
    exit 1
}

function Get-FrontmatterLines {
    param([string]$Path)

    $lines = Get-Content -Path $Path
    if ($lines.Count -eq 0 -or $lines[0] -ne $FrontmatterDelimiter) {
        return $null
    }
    for ($index = 1; $index -lt $lines.Count; $index++) {
        if ($lines[$index] -eq $FrontmatterDelimiter) {
            if ($index -eq 1) {
                return @()
            }
            return $lines[1..($index - 1)]
        }
    }
    return $null
}

function Get-FrontmatterValue {
    param(
        [string[]]$FrontmatterLines,
        [string]$Key
    )

    $prefix = "$($Key):"
    foreach ($line in $FrontmatterLines) {
        if ($line.StartsWith($prefix)) {
            return $line.Substring($prefix.Length).Trim().Trim('"''')
        }
    }
    return $null
}

function Get-RuleVersion {
    param([string[]]$FrontmatterLines)

    $rawValue = Get-FrontmatterValue -FrontmatterLines $FrontmatterLines -Key "version"
    if ($null -eq $rawValue) {
        return $null
    }
    return [version]$rawValue
}

function Install-Rule {
    param(
        [System.IO.FileInfo]$SourceFile,
        [string]$TargetDir
    )

    $sourceFrontmatter = Get-FrontmatterLines -Path $SourceFile.FullName
    $sourceVersion = Get-RuleVersion -FrontmatterLines $sourceFrontmatter
    $targetFile = Join-Path $TargetDir $SourceFile.Name

    if (-not (Test-Path $targetFile)) {
        Copy-Item -Path $SourceFile.FullName -Destination $targetFile
        return "installed $($SourceFile.Name) ($sourceVersion)"
    }

    $targetFrontmatter = Get-FrontmatterLines -Path $targetFile
    $targetManagedBy = if ($null -eq $targetFrontmatter) { $null } else { Get-FrontmatterValue -FrontmatterLines $targetFrontmatter -Key "managed-by" }

    if ($targetManagedBy -ne $ManagedBy) {
        return "skipped $($SourceFile.Name): not managed by this repo, not overwriting"
    }

    $targetVersion = Get-RuleVersion -FrontmatterLines $targetFrontmatter

    if ($null -eq $targetVersion -or ($sourceVersion -and ($sourceVersion -gt $targetVersion))) {
        Copy-Item -Path $SourceFile.FullName -Destination $targetFile -Force
        return "updated $($SourceFile.Name): $targetVersion -> $sourceVersion"
    }

    return "up to date $($SourceFile.Name) ($targetVersion)"
}

function Remove-OrphanedRule {
    param([System.IO.FileInfo]$TargetFile)

    # Deletes a rule this repo installed that the plugin no longer ships. $null = left alone.
    $frontmatter = Get-FrontmatterLines -Path $TargetFile.FullName
    $managedBy = if ($null -eq $frontmatter) { $null } else { Get-FrontmatterValue -FrontmatterLines $frontmatter -Key "managed-by" }

    if ($managedBy -ne $ManagedBy) {
        return $null
    }

    Remove-Item -Path $TargetFile.FullName -Force
    return "removed $($TargetFile.Name): no longer in plugin"
}

$existingTarget = Get-Item -Path $TargetDir -Force -ErrorAction SilentlyContinue
if ($existingTarget -and $existingTarget.LinkType) {
    Remove-Item -Path $TargetDir -Force
}

New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null

$sourceFiles = Get-ChildItem -Path $PluginRulesDir -Filter "*.md" | Sort-Object Name

$results = @($sourceFiles | ForEach-Object { Install-Rule -SourceFile $_ -TargetDir $TargetDir })

$sourceNames = @($sourceFiles | ForEach-Object { $_.Name })
$results += @(
    Get-ChildItem -Path $TargetDir -Filter "*.md" |
        Sort-Object Name |
        Where-Object { $sourceNames -notcontains $_.Name } |
        ForEach-Object { Remove-OrphanedRule -TargetFile $_ } |
        Where-Object { $null -ne $_ }
)

$results | ForEach-Object { Write-Output $_ }

$installed = ($results | Where-Object { $_.StartsWith("installed ") }).Count
$updated = ($results | Where-Object { $_.StartsWith("updated ") }).Count
$removed = ($results | Where-Object { $_.StartsWith("removed ") }).Count
$skipped = ($results | Where-Object { $_.StartsWith("skipped ") -or $_.StartsWith("up to date ") }).Count

Write-Output ""
Write-Output "$installed installed, $updated updated, $removed removed, $skipped skipped"
