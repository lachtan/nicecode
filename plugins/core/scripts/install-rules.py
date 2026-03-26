#!/usr/bin/env python3

import json
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import NoReturn

MARKETPLACE = "nicecode"
PLUGIN = "core"
FULL_PLUGIN_NAME = f"{PLUGIN}@{MARKETPLACE}"
RULES_SUBDIR = Path("plugins") / MARKETPLACE / PLUGIN
DEBUG = bool(os.environ.get("NICECODE_DEBUG"))
LOG_FILE = Path(tempfile.gettempdir()) / "install-rules.log" if DEBUG else None


def log(message: str) -> None:
    if not DEBUG:
        return
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    line = f"{stamp} {message}"
    print(line, file=sys.stderr)
    assert LOG_FILE is not None
    with LOG_FILE.open("a") as file:
        file.write(f"{line}\n")


def exit_with_error(message: str) -> NoReturn:
    log(f"Error: {message}")
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
    log(f"{var_name}={directory}")
    return directory


def is_plugin_enabled_in_project(project_dir: Path) -> bool:
    config_file = project_dir / ".claude" / "settings.json"
    if not config_file.is_file():
        log(f"Config not found: {config_file}")
        return False
    try:
        config = json.loads(config_file.read_text())
    except (json.JSONDecodeError, OSError):
        log(f"Config parse error: {config_file}")
        return False
    enabled_plugins = config.get("enabledPlugins", {})
    plugin_enabled = any(plugin == FULL_PLUGIN_NAME and enabled for plugin, enabled in enabled_plugins.items())
    log(f"Plugin enabled: {plugin_enabled}")
    return plugin_enabled


def link_rules(plugin_rules_dir: Path, project_rules_dir: Path) -> None:
    log(f"Linking {plugin_rules_dir} -> {project_rules_dir}")
    if project_rules_dir.is_symlink() and project_rules_dir.resolve() == plugin_rules_dir:
        log("Already linked, skipping")
        return
    if project_rules_dir.is_symlink():
        log(f"Wrong symlink target {project_rules_dir.resolve()}, replacing")
        project_rules_dir.unlink()
    project_rules_dir.parent.mkdir(parents=True, exist_ok=True)
    project_rules_dir.symlink_to(plugin_rules_dir)
    log(f"Linked {plugin_rules_dir} -> {project_rules_dir}")


def main() -> None:
    plugin_root = resolve_env_dir("CLAUDE_PLUGIN_ROOT")
    project_dir = resolve_env_dir("CLAUDE_PROJECT_DIR")

    if not is_plugin_enabled_in_project(project_dir):
        log("Skipped: plugin not enabled")
        return

    project_rules_dir = project_dir / ".claude" / "rules" / RULES_SUBDIR
    if project_rules_dir.is_dir() and not project_rules_dir.is_symlink():
        log(f"Skipped: {project_rules_dir} is a real directory")
        return

    plugin_rules_dir = plugin_root / "rules"
    validate_dir(plugin_rules_dir, "Plugin rules")

    link_rules(plugin_rules_dir, project_rules_dir)


if __name__ == "__main__":
    main()
