#!/usr/bin/env python3

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def resolve_rules_dir():
    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if plugin_root:
        return Path(plugin_root) / "rules"
    return (Path(__file__).resolve().parent.parent / "rules").resolve()


def resolve_target_dir():
    project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))
    return project_dir, project_dir / ".claude" / "rules" / "nicecode"


def is_plugin_enabled(project_dir):
    settings = project_dir / ".claude" / "settings.json"
    if not settings.is_file():
        return False
    return "core@nicecode" in settings.read_text()


def is_already_linked(target, rules_dir):
    return target.is_symlink() and target.resolve() == rules_dir.resolve()


def warn_gitignore(project_dir):
    try:
        subprocess.run(
            ["git", "-C", str(project_dir), "rev-parse", "--is-inside-work-tree"],
            capture_output=True, check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return
    gitignore = project_dir / ".gitignore"
    if not gitignore.is_file() or ".claude/rules/nicecode" not in gitignore.read_text():
        print("Warning: .claude/rules/nicecode/ is not in .gitignore. "
              "Add it to prevent committing user-specific symlinks.")


def create_symlink(target, rules_dir):
    if target.is_symlink() or target.is_dir():
        if target.is_dir() and not target.is_symlink():
            shutil.rmtree(target)
        else:
            target.unlink()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.symlink_to(rules_dir)


def main():
    quiet = "--quiet" in sys.argv
    rules_dir = resolve_rules_dir()
    project_dir, target = resolve_target_dir()

    if quiet and not is_plugin_enabled(project_dir):
        return

    if not rules_dir.is_dir():
        print(f"Error: Rules directory not found at {rules_dir}", file=sys.stderr)
        sys.exit(1)

    if is_already_linked(target, rules_dir):
        if not quiet:
            print(f"Rules already linked to {rules_dir}")
        warn_gitignore(project_dir)
        return

    create_symlink(target, rules_dir)
    print(f"Linked {target} -> {rules_dir}")
    warn_gitignore(project_dir)


if __name__ == "__main__":
    main()
