#!/usr/bin/env python3

import argparse
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

RULES_SUBDIR = Path(".claude") / "rules" / "plugins" / "nicecode" / "core"
FRONTMATTER_DELIMITER = "---"
MANAGED_BY = "https://github.com/lachtan/nicecode"


@dataclass(order=True, frozen=True)
class Version:
    major: int
    minor: int
    patch: int

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


def extract_frontmatter(text: str) -> list[str] | None:
    lines = text.splitlines()
    if not lines or lines[0] != FRONTMATTER_DELIMITER:
        return None
    for index, line in enumerate(lines[1:], start=1):
        if line == FRONTMATTER_DELIMITER:
            return lines[1:index]
    return None


def frontmatter_value(frontmatter_lines: list[str], key: str) -> str | None:
    prefix = f"{key}:"
    for line in frontmatter_lines:
        if line.startswith(prefix):
            return line.removeprefix(prefix).strip().strip("\"'")
    return None


def parse_version(frontmatter_lines: list[str]) -> Version | None:
    raw_value = frontmatter_value(frontmatter_lines, "version")
    if raw_value is None:
        return None
    major, minor, patch = raw_value.split(".")
    return Version(int(major), int(minor), int(patch))


def format_version(version: Version | None) -> str:
    return str(version) if version is not None else "unknown"


def install_rule(source_file: Path, target_dir: Path) -> str:
    source_frontmatter = extract_frontmatter(source_file.read_text()) or []
    source_version = parse_version(source_frontmatter)
    target_file = target_dir / source_file.name

    if not target_file.exists():
        shutil.copy2(source_file, target_file)
        return f"installed {source_file.name} ({format_version(source_version)})"

    target_frontmatter = extract_frontmatter(target_file.read_text())
    if target_frontmatter is None or frontmatter_value(target_frontmatter, "managed-by") != MANAGED_BY:
        return f"skipped {source_file.name}: not managed by this repo, not overwriting"

    target_version = parse_version(target_frontmatter)
    if target_version is None or (source_version is not None and source_version > target_version):
        shutil.copy2(source_file, target_file)
        return f"updated {source_file.name}: {format_version(target_version)} -> {format_version(source_version)}"

    return f"up to date {source_file.name} ({format_version(target_version)})"


def replace_stale_symlink(target_dir: Path) -> None:
    if target_dir.is_symlink():
        target_dir.unlink()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("project_dir", nargs="?", help="Project directory (only used with --scope project; defaults to cwd)")
    parser.add_argument("--scope", choices=["project", "user"], required=True, help="Install into the project's .claude/rules or the user's home directory")
    return parser.parse_args()


def resolve_base_dir(args: argparse.Namespace) -> Path:
    if args.scope == "user":
        return Path.home()
    return Path(args.project_dir).resolve() if args.project_dir else Path.cwd()


def main() -> None:
    args = parse_args()
    plugin_rules_dir = Path(__file__).resolve().parent.parent / "rules"
    target_dir = resolve_base_dir(args) / RULES_SUBDIR

    if not plugin_rules_dir.is_dir():
        print(f"Error: plugin rules directory not found: {plugin_rules_dir}", file=sys.stderr)
        sys.exit(1)

    replace_stale_symlink(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    results = [install_rule(source_file, target_dir) for source_file in sorted(plugin_rules_dir.glob("*.md"))]
    for result in results:
        print(result)

    installed = sum(result.startswith("installed ") for result in results)
    updated = sum(result.startswith("updated ") for result in results)
    skipped = sum(result.startswith("skipped ") or result.startswith("up to date ") for result in results)
    print(f"\n{installed} installed, {updated} updated, {skipped} skipped")


if __name__ == "__main__":
    main()
