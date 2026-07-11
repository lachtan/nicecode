#!/usr/bin/env python3

import os
import sys
from pathlib import Path

CATEGORIES = ("skills", "commands", "agents")


def discover_skill_items(plugin_dir: Path) -> dict[str, Path]:
    skills_dir = plugin_dir / "skills"
    if not skills_dir.is_dir():
        return {}
    return {
        item.name: item
        for item in sorted(skills_dir.iterdir())
        if item.is_dir() and (item / "SKILL.md").is_file()
    }


def discover_file_items(plugin_dir: Path, category: str) -> dict[str, Path]:
    category_dir = plugin_dir / category
    if not category_dir.is_dir():
        return {}
    return {item.name: item for item in sorted(category_dir.glob("*.md"))}


def discover_category_items(plugins_dir: Path, category: str) -> dict[str, Path]:
    expected: dict[str, Path] = {}
    conflicted: set[str] = set()

    for plugin_dir in sorted(p for p in plugins_dir.iterdir() if p.is_dir()):
        items = discover_skill_items(plugin_dir) if category == "skills" else discover_file_items(plugin_dir, category)
        for name, source in items.items():
            if name in conflicted:
                continue
            if name in expected and expected[name] != source:
                print(
                    f"warning: {category}/{name} is defined by both {expected[name]} and {source}, skipping",
                    file=sys.stderr,
                )
                del expected[name]
                conflicted.add(name)
                continue
            expected[name] = source

    return expected


def relative_symlink_target(source: Path, link_path: Path) -> str:
    return os.path.relpath(source, start=link_path.parent)


def ensure_real_directory(path: Path) -> None:
    if path.is_symlink():
        path.unlink()
    path.mkdir(parents=True, exist_ok=True)


def remove_stale_entries(target_dir: Path, category: str, expected: dict[str, Path]) -> list[str]:
    reports = []
    stale_names = sorted(entry.name for entry in target_dir.iterdir() if entry.name not in expected)

    for name in stale_names:
        entry = target_dir / name
        if entry.is_symlink():
            entry.unlink()
            reports.append(f"removed {category}/{name} (source no longer exists)")
        else:
            reports.append(f"skipped {category}/{name}: not a symlink, leaving alone")

    return reports


def sync_expected_entries(target_dir: Path, category: str, expected: dict[str, Path]) -> list[str]:
    reports = []

    for name in sorted(expected):
        source = expected[name]
        link_path = target_dir / name
        desired_target = relative_symlink_target(source, link_path)

        if link_path.is_symlink():
            if os.readlink(link_path) == desired_target:
                reports.append(f"up to date {category}/{name}")
            else:
                link_path.unlink()
                link_path.symlink_to(desired_target, target_is_directory=source.is_dir())
                reports.append(f"updated {category}/{name}")
        elif link_path.exists():
            reports.append(f"skipped {category}/{name}: exists and is not a symlink, leaving alone")
        else:
            link_path.symlink_to(desired_target, target_is_directory=source.is_dir())
            reports.append(f"created {category}/{name}")

    return reports


def sync_category(plugins_dir: Path, claude_dir: Path, category: str) -> list[str]:
    expected = discover_category_items(plugins_dir, category)
    target_dir = claude_dir / category
    ensure_real_directory(target_dir)

    return remove_stale_entries(target_dir, category, expected) + sync_expected_entries(target_dir, category, expected)


def sync_all(plugins_dir: Path, claude_dir: Path) -> list[str]:
    return [line for category in CATEGORIES for line in sync_category(plugins_dir, claude_dir, category)]


def summarize(reports: list[str]) -> str:
    created = sum(line.startswith("created ") for line in reports)
    updated = sum(line.startswith("updated ") for line in reports)
    removed = sum(line.startswith("removed ") for line in reports)
    skipped = sum(line.startswith("skipped ") or line.startswith("up to date ") for line in reports)
    return f"{created} created, {updated} updated, {removed} removed, {skipped} skipped/up to date"


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    reports = sync_all(repo_root / "plugins", repo_root / ".claude")
    for line in reports:
        print(line)
    print(f"\n{summarize(reports)}")


if __name__ == "__main__":
    main()
