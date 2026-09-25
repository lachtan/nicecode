#!/usr/bin/env python3

from pathlib import Path

from hook_common import edited_file, run_check

FORMATTER = Path(__file__).parent / "format-powershell.ps1"


def main():
    path = edited_file((".ps1", ".psm1", ".psd1"))
    if path is None:
        return
    run_check(["pwsh", "-NoProfile", "-File", str(FORMATTER), path])


if __name__ == "__main__":
    main()
