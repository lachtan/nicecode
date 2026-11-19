#!/usr/bin/env python3
"""build - render the generated plugins/ tree and the marketplaces from src/.

src/ is the only place to edit. plugins/ and the marketplace files are generated and
committed, so the repo installs straight from git.

    uv run scripts/build.py          write the output, delete output files src/ no longer produces
    uv run scripts/build.py --check  write nothing; exit 1 and list every file that differs

Stdlib only, like nice-check: the tests run under `uvx pytest`.
"""

import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = "src"
OUTPUT_DIR = "plugins"
CATALOG = f"{SOURCE_DIR}/marketplace.json"
CLAUDE_MARKETPLACE = ".claude-plugin/marketplace.json"
# The neutral hook file sits in the plugin root, apart from the generated hooks/hooks.json.
NEUTRAL_HOOKS = "hooks.json"
OPTIONAL_PLUGIN_KEYS = ("repository", "license")
VERSION = re.compile(r"^\d+\.\d+\.\d+$")

EVENTS = {
    "before-tool": "PreToolUse",
    "after-tool": "PostToolUse",
    "session-start": "SessionStart",
    "prompt-submit": "UserPromptSubmit",
}
TOOL_EVENTS = frozenset({"before-tool", "after-tool"})
TOOLS = {"shell": "Bash", "edit": "Edit|Write"}
PLUGIN_ROOT = "{plugin_root}"


class BuildError(Exception):
    pass


@dataclass(frozen=True)
class OutputFile:
    content: bytes
    is_executable: bool


# -- input -------------------------------------------------------------------


def git_files(root: Path, directory: str) -> list[str]:
    """Tracked plus new files under directory, minus what .gitignore drops (__pycache__, caches)."""
    command = ["git", "-C", str(root), "ls-files", "-z", "--cached", "--others", "--exclude-standard", "--", directory]
    result = subprocess.run(command, capture_output=True, check=True)
    paths = {path for path in result.stdout.decode().split("\0") if path}
    # --cached still lists a tracked file that was deleted from the worktree.
    return sorted(path for path in paths if (root / path).is_file())


def load_catalog(root: Path) -> dict:
    catalog = json.loads((root / CATALOG).read_text(encoding="utf-8"))
    for plugin in catalog["plugins"]:
        version = plugin.get("version")
        if not isinstance(version, str) or not VERSION.match(version):
            raise BuildError(f"{CATALOG}: {plugin.get('name')}: version {version!r} is not a MAJOR.MINOR.PATCH string")
    return catalog


def source_plugin_files(root: Path) -> dict[str, list[str]]:
    """Plugin name -> its source files, as paths relative to the plugin directory."""
    plugins: dict[str, list[str]] = {}
    for path in git_files(root, SOURCE_DIR):
        parts = PurePosixPath(path).parts
        if len(parts) > 2:  # skips src/marketplace.json
            plugins.setdefault(parts[1], []).append("/".join(parts[2:]))
    return plugins


def check_catalog_matches_sources(catalog: dict, source_plugins: set[str]) -> None:
    listed = {plugin["name"] for plugin in catalog["plugins"]}
    if unlisted := sorted(source_plugins - listed):
        raise BuildError(f"plugins in {SOURCE_DIR}/ but not listed in {CATALOG}: {', '.join(unlisted)}")
    if missing := sorted(listed - source_plugins):
        raise BuildError(f"plugins listed in {CATALOG} but missing from {SOURCE_DIR}/: {', '.join(missing)}")


def is_shipped(path: str) -> bool:
    """Tests stay in src/; users never run them."""
    parts = PurePosixPath(path).parts
    return path != NEUTRAL_HOOKS and "tests" not in parts[:-1] and not re.fullmatch(r"test_.*\.py", parts[-1])


# -- rendering ---------------------------------------------------------------


def json_file(data: dict) -> OutputFile:
    return OutputFile((json.dumps(data, indent=2, ensure_ascii=False) + "\n").encode(), False)


def optional_keys(plugin: dict) -> dict:
    return {key: plugin[key] for key in OPTIONAL_PLUGIN_KEYS if key in plugin}


def claude_plugin_manifest(plugin: dict) -> dict:
    return {
        "name": plugin["name"],
        "description": plugin["description"],
        "author": plugin["author"],
        **optional_keys(plugin),
    }


def claude_marketplace(catalog: dict) -> dict:
    entries = [
        {
            "name": plugin["name"],
            "source": f"./{OUTPUT_DIR}/{plugin['name']}",
            "description": plugin["description"],
            "version": plugin["version"],
            **optional_keys(plugin),
        }
        for plugin in catalog["plugins"]
    ]
    return {
        "name": catalog["name"],
        "owner": catalog["owner"],
        "metadata": {"description": catalog["description"]},
        "plugins": entries,
    }


def hook_matcher(hook: dict) -> str | None:
    event, tools = hook["event"], hook.get("tools")
    if event not in TOOL_EVENTS:
        if tools is not None:
            raise BuildError(f"event {event!r} takes no tools")
        return None
    if not tools:
        raise BuildError(f"event {event!r} needs tools")
    unknown = [tool for tool in tools if tool not in TOOLS]
    if unknown:
        raise BuildError(f"unknown tools {unknown}; known: {sorted(TOOLS)}")
    return "|".join(TOOLS[tool] for tool in tools)


def translate_hooks(neutral: dict) -> dict:
    """Neutral hooks -> the hooks.json that Claude Code and Codex both read.

    Entries with the same event and matcher share one matcher group, commands in source
    order, so no matcher repeats within an event (nice-check F).
    """
    groups: dict[str, dict[str | None, list[str]]] = {}
    for hook in neutral["hooks"]:
        if hook.get("event") not in EVENTS:
            raise BuildError(f"unknown event {hook.get('event')!r}; known: {sorted(EVENTS)}")
        command = hook["command"].replace(PLUGIN_ROOT, "${CLAUDE_PLUGIN_ROOT}")
        groups.setdefault(EVENTS[hook["event"]], {}).setdefault(hook_matcher(hook), []).append(command)

    hooks = {}
    for event, matchers in groups.items():
        hooks[event] = [
            {
                **({"matcher": matcher} if matcher is not None else {}),
                "hooks": [{"type": "command", "command": command} for command in commands],
            }
            for matcher, commands in matchers.items()
        ]
    return {"hooks": hooks}


def render_plugin(root: Path, plugin: dict, files: list[str]) -> dict[str, OutputFile]:
    name = plugin["name"]
    source, output = root / SOURCE_DIR / name, f"{OUTPUT_DIR}/{name}"
    rendered = {}
    for path in files:
        if is_shipped(path):
            file = source / path
            rendered[f"{output}/{path}"] = OutputFile(file.read_bytes(), file.stat().st_mode & 0o111 != 0)
    rendered[f"{output}/.claude-plugin/plugin.json"] = json_file(claude_plugin_manifest(plugin))
    if NEUTRAL_HOOKS in files:
        neutral = json.loads((source / NEUTRAL_HOOKS).read_text(encoding="utf-8"))
        try:
            rendered[f"{output}/hooks/hooks.json"] = json_file(translate_hooks(neutral))
        except BuildError as exc:
            raise BuildError(f"{SOURCE_DIR}/{name}/{NEUTRAL_HOOKS}: {exc}") from exc
    return rendered


def render(root: Path) -> dict[str, OutputFile]:
    """Every generated file, keyed by its path relative to root."""
    catalog = load_catalog(root)
    sources = source_plugin_files(root)
    check_catalog_matches_sources(catalog, set(sources))
    rendered = {CLAUDE_MARKETPLACE: json_file(claude_marketplace(catalog))}
    for plugin in catalog["plugins"]:
        rendered |= render_plugin(root, plugin, sources[plugin["name"]])
    return rendered


# -- output ------------------------------------------------------------------


def is_up_to_date(path: Path, expected: OutputFile) -> bool:
    if not path.is_file():
        return False
    return path.read_bytes() == expected.content and (path.stat().st_mode & 0o111 != 0) == expected.is_executable


def stale_files(root: Path, rendered: dict[str, OutputFile]) -> list[str]:
    """Output files on disk that src/ no longer produces."""
    return [path for path in git_files(root, OUTPUT_DIR) if path not in rendered]


def differences(root: Path, rendered: dict[str, OutputFile]) -> list[str]:
    changed = [path for path, file in rendered.items() if not is_up_to_date(root / path, file)]
    return sorted(changed + stale_files(root, rendered))


def write(root: Path, rendered: dict[str, OutputFile]) -> None:
    for path in stale_files(root, rendered):
        (root / path).unlink()
        remove_empty_parents(root, root / path)
    for path, file in rendered.items():
        target = root / path
        if is_up_to_date(target, file):
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(file.content)
        target.chmod(0o755 if file.is_executable else 0o644)


def remove_empty_parents(root: Path, path: Path) -> None:
    directory = path.parent
    while directory != root and not any(directory.iterdir()):
        directory.rmdir()
        directory = directory.parent


def main(argv: list[str], root: Path = ROOT) -> int:
    try:
        rendered = render(root)
    except BuildError as exc:
        print(f"build: {exc}", file=sys.stderr)
        return 1
    if "--check" not in argv:
        write(root, rendered)
        return 0
    changed = differences(root, rendered)
    for path in changed:
        print(f"out of date: {path}")
    if changed:
        print("Run `uv run scripts/build.py` and commit the result.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
