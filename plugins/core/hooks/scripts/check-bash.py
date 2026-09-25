#!/usr/bin/env python3

from hook_common import edited_file, run_check


def main():
    path = edited_file((".sh",))
    if path is None:
        return
    run_check(["shellcheck", path])


if __name__ == "__main__":
    main()
