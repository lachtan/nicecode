#!/usr/bin/env python3

import re
import json
import os
import sys
from pathlib import Path
from typing import NoReturn

PLUGIN_NAME = "nicecode"


def exit_with_error(message: str) -> NoReturn:
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(1)


def validate_dir(path: Path, name: str) -> None:
    if not path.is_dir():
        exit_with_error(f"{name} directory does not exist: {path}")


def resolve_env_dir(var_name: str) -> Path:
    value = os.environ.get(var_name)
    if not value:
        exit_with_error(f"{var_name} environment variable is not set.")
    directory = Path(value).resolve()
    validate_dir(directory, var_name)
    return directory


def is_plugin_enabled_in_project(project_dir: Path) -> bool:
    config_file = project_dir / ".claude" / "config.json"
    if not config_file.is_file():
        return False
    try:
        config = json.loads(config_file.read_text())
    except (json.JSONDecodeError, OSError):
        return False
    enabled_plugins = config.get("enabledPlugins", {})
    return any(plugin.endswith(f"@{PLUGIN_NAME}") and enabled for plugin, enabled in enabled_plugins.items())


def is_rules_in_gitignore(project_dir: Path) -> bool:
    gitignore = project_dir / ".gitignore"
    return gitignore.is_file() and bool(
        re.search(rf"^\.claude/rules/{PLUGIN_NAME}\b", gitignore.read_text(), re.MULTILINE)
    )


def link_rules(plugin_rules_dir: Path, project_rules_dir: Path) -> None:
    if project_rules_dir.is_symlink() and project_rules_dir.resolve() == plugin_rules_dir:
        return
    if project_rules_dir.is_symlink():
        project_rules_dir.unlink()
    project_rules_dir.parent.mkdir(parents=True, exist_ok=True)
    project_rules_dir.symlink_to(plugin_rules_dir)


def main() -> None:
    plugin_root = resolve_env_dir("CLAUDE_PLUGIN_ROOT")
    project_dir = resolve_env_dir("CLAUDE_PROJECT_DIR")

    if is_rules_in_gitignore(project_dir) or not is_plugin_enabled_in_project(project_dir):
        return

    project_rules_dir = project_dir / ".claude" / "rules" / PLUGIN_NAME
    if project_rules_dir.is_dir() and not project_rules_dir.is_symlink():
        return

    plugin_rules_dir = plugin_root / "rules"
    validate_dir(plugin_rules_dir, "Plugin rules")

    link_rules(plugin_rules_dir, project_rules_dir)


if __name__ == "__main__":
    main()
