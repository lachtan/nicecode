# Workaround for Claude Code bug on Windows
# https://github.com/anthropics/claude-code/issues/4928

$ProjectDir = Resolve-Path "$PSScriptRoot\..\.."

function DeleteNulFile($nulFile) {
    $path = "\\?\" + [System.IO.Path]::Combine($ProjectDir, $nulFile)
    if ([System.IO.File]::Exists($path)) {
        [System.IO.File]::Delete($path)
    }
}

DeleteNulFile "NUL"
DeleteNulFile "nul"
