#!/usr/bin/env python3

import os
import shutil
import subprocess
import sys
from pathlib import Path


def resolve_rules_dir() -> Path:
    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if plugin_root:
        return Path(plugin_root) / "rules"
    plugin_dir = Path(__file__).resolve().parent.parent
    return plugin_dir / "rules"


def is_already_linked(target: Path, rules_dir: Path) -> bool:
    return target.is_symlink() and target.resolve() == rules_dir.resolve()


def warn_gitignore(project_dir: Path) -> None:
    try:
        subprocess.run(
            ["git", "-C", str(project_dir), "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return
    gitignore = project_dir / ".gitignore"
    if not gitignore.is_file() or ".claude/rules/nicecode" not in gitignore.read_text():
        print(
            "Warning: .claude/rules/nicecode/ is not in .gitignore. "
            "Add it to prevent committing user-specific symlinks."
        )


def create_symlink(target: Path, rules_dir: Path) -> None:
    is_real_dir = target.is_dir() and not target.is_symlink()
    needs_cleanup = target.exists() or target.is_symlink()

    if is_real_dir:
        shutil.rmtree(target)
    elif needs_cleanup:
        target.unlink()

    target.parent.mkdir(parents=True, exist_ok=True)
    target.symlink_to(rules_dir)


def main() -> None:
    quiet = "--quiet" in sys.argv
    rules_dir = resolve_rules_dir()
    project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))
    target = project_dir / ".claude" / "rules" / "nicecode"

    if quiet and not os.environ.get("CLAUDE_PLUGIN_ROOT"):
        return

    if not rules_dir.is_dir():
        print(f"Error: Rules directory not found at {rules_dir}", file=sys.stderr)
        sys.exit(1)

    if is_already_linked(target, rules_dir):
        if not quiet:
            print(f"Rules already linked to {rules_dir}")
    else:
        create_symlink(target, rules_dir)
        print(f"Linked {target} -> {rules_dir}")

    warn_gitignore(project_dir)


if __name__ == "__main__":
    main()
