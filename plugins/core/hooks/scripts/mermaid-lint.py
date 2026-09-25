#!/usr/bin/env python3

from hook_common import edited_file, run_check


def main():
    path = edited_file((".md",))
    if path is None:
        return
    run_check(["npx", "--yes", "md-mermaid-lint", path])


if __name__ == "__main__":
    main()
