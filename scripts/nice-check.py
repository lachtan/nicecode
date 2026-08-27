#!/usr/bin/env python3
"""nice-check - audit this repo against its own rules.

Report only: prints every finding and exits 1 when any of them is an error, but
never changes a file. Run with `uv run scripts/nice-check.py`.

Stdlib only, and the frontmatter parser is hand-rolled on purpose: the tests run
under `uvx pytest`, an isolated environment where `import yaml` would fail.
"""

import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ERROR = "error"
WARNING = "warning"
SEVERITY_ORDER = {ERROR: 0, WARNING: 1}

MAX_LINE_LENGTH = 120
# Python is left to ruff so a long line is not reported twice; markdown and data files
# are left alone because MD013 is switched off in .markdownlint-cli2.yaml.
LINE_LENGTH_EXTENSIONS = (".ps1", ".sh")

REQUIRED_FLAGS = ("disable-model-invocation", "user-invocable")
MANAGED_KEYS = ("managed-by", "version")
BLOCK_SCALAR_STYLES = frozenset({">", ">-", ">+", "|", "|-", "|+"})

KEY_LINE = re.compile(r"^([A-Za-z][\w-]*):[ \t]*(.*)$")
LINK_TARGET = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
SCRIPT_TOKEN = re.compile(r"[^\s\"']+\.(?:py|sh|ps1)")
EXIT_ONE = re.compile(r"\bexit 1\b|\bsys\.exit\(1\)")
README_ITEM = re.compile(r"^- `(/?[\w.-]+)` +[-—]")
LAST_CHANGE = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")
# The \s+ also keeps this pattern from matching its own source line.
PLACEHOLDER = re.compile(r"Add your\s+description here")


@dataclass(frozen=True)
class Finding:
    severity: str
    check: str
    path: str
    line: int | None
    message: str


@dataclass(frozen=True)
class Repo:
    root: Path
    tracked: tuple[str, ...]
    eol: dict[str, str]  # tracked path -> worktree line ending ("lf", "crlf", "none", ...)


@dataclass(frozen=True)
class SkillRef:
    name: str
    plugin: str | None  # None for a repo-local skill living directly in .claude/skills/
    path: Path
    rel: str


@dataclass(frozen=True)
class FrontmatterValue:
    raw: str  # scalar as written, or the body of a block scalar / list
    style: str | None  # block scalar indicator, None for a plain scalar
    line: int


class FrontmatterError(Exception):
    pass


# -- loading -----------------------------------------------------------------


def git_lines(root: Path, *args: str) -> list[str]:
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=True)
    return result.stdout.splitlines()


def parse_eol(lines: list[str]) -> dict[str, str]:
    """`git ls-files --eol` prints `i/<eol> w/<eol> attr/<attr><tab><path>`.

    Parsed by column, never by substring: "crlf" contains "lf", so a `grep -v lf`
    filter silently drops exactly the files this check is looking for.
    """
    eols = {}
    for line in lines:
        attributes, _, path = line.partition("\t")
        fields = attributes.split()
        if path and len(fields) >= 2 and fields[1].startswith("w/"):
            eols[path] = fields[1].removeprefix("w/")
    return eols


def load_repo(root: Path) -> Repo:
    return Repo(root, tuple(git_lines(root, "ls-files")), parse_eol(git_lines(root, "ls-files", "--eol")))


def load_text(path: Path) -> tuple[str, str | None]:
    try:
        return path.read_text(encoding="utf-8"), None
    except (OSError, UnicodeDecodeError) as exc:
        return "", f"cannot read the file: {exc}"


def load_json(path: Path) -> tuple[Any, str | None]:
    text, error = load_text(path)
    if error:
        return None, error
    try:
        return json.loads(text), None
    except json.JSONDecodeError as exc:
        return None, f"invalid JSON: {exc}"


def relpath(repo: Repo, path: Path) -> str:
    return path.relative_to(repo.root).as_posix()


def tracked_real_files(repo: Repo) -> list[str]:
    """Tracked paths that are ordinary files; the symlinks in .claude/ are directories."""
    return [rel for rel in repo.tracked if not (repo.root / rel).is_symlink() and (repo.root / rel).is_file()]


def plugin_dirs(repo: Repo) -> list[Path]:
    plugins = repo.root / "plugins"
    return sorted(p for p in plugins.iterdir() if p.is_dir()) if plugins.is_dir() else []


def real_skill_dirs(skills_dir: Path) -> list[Path]:
    if not skills_dir.is_dir():
        return []
    return [d for d in sorted(skills_dir.iterdir()) if d.is_dir() and not d.is_symlink() and (d / "SKILL.md").is_file()]


def discover_skills(repo: Repo) -> list[SkillRef]:
    skills = []
    for plugin_dir in plugin_dirs(repo):
        for skill_dir in real_skill_dirs(plugin_dir / "skills"):
            skills.append(make_skill_ref(repo, skill_dir, plugin_dir.name))
    for skill_dir in real_skill_dirs(repo.root / ".claude" / "skills"):
        skills.append(make_skill_ref(repo, skill_dir, None))
    return skills


def make_skill_ref(repo: Repo, skill_dir: Path, plugin: str | None) -> SkillRef:
    path = skill_dir / "SKILL.md"
    return SkillRef(skill_dir.name, plugin, path, relpath(repo, path))


# -- frontmatter -------------------------------------------------------------


def split_frontmatter(text: str) -> tuple[list[str], int]:
    """Returns the frontmatter lines and the 1-based line number of the first body line."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise FrontmatterError("file does not open with a --- frontmatter block")
    end = next((i for i, line in enumerate(lines[1:], 1) if line.strip() == "---"), None)
    if end is None:
        raise FrontmatterError("frontmatter block is never closed by ---")
    return lines[1:end], end + 2


def take_indented(lines: list[str], start: int) -> tuple[str, int]:
    index = start
    while index < len(lines) and (not lines[index].strip() or lines[index][:1] in (" ", "\t")):
        index += 1
    return "\n".join(line.strip() for line in lines[start:index] if line.strip()), index


def parse_frontmatter(text: str) -> dict[str, FrontmatterValue]:
    """Flat `key: value` frontmatter, plus block scalars and simple lists.

    Skill frontmatter has no nested mappings, so nothing deeper is supported.
    """
    lines, _ = split_frontmatter(text)
    values: dict[str, FrontmatterValue] = {}
    index = 0
    while index < len(lines):
        match = KEY_LINE.match(lines[index])
        line_number = index + 2
        index += 1
        if not match:
            continue
        key, value = match.group(1), match.group(2).strip()
        if value in BLOCK_SCALAR_STYLES:
            body, index = take_indented(lines, index)
            values[key] = FrontmatterValue(body, value, line_number)
        elif not value:
            body, index = take_indented(lines, index)
            values[key] = FrontmatterValue(body, None, line_number)
        else:
            values[key] = FrontmatterValue(value, None, line_number)
    return values


def unquote(raw: str) -> str:
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in "\"'":
        return raw[1:-1]
    return raw


# -- A. plugin manifests -----------------------------------------------------


def check_plugin_manifests(repo: Repo) -> list[Finding]:
    manifest_rel = ".claude-plugin/marketplace.json"
    manifest, error = load_json(repo.root / manifest_rel)
    if error:
        return [Finding(ERROR, "A", manifest_rel, None, error)]

    findings = []
    listed = set()
    for entry in manifest.get("plugins", []):
        listed.add(entry.get("name"))
        findings += check_manifest_entry(repo, manifest_rel, entry)
    for plugin_dir in plugin_dirs(repo):
        if plugin_dir.name not in listed:
            findings.append(Finding(ERROR, "A", manifest_rel, None, f"plugins/{plugin_dir.name} is not listed here"))
    return findings


def check_manifest_entry(repo: Repo, manifest_rel: str, entry: dict) -> list[Finding]:
    name = entry.get("name", "<unnamed>")
    source = entry.get("source")
    if not isinstance(source, str):
        return []  # an external source (an object): there is no local plugin.json to compare against
    plugin_rel = f"{source.removeprefix('./')}/.claude-plugin/plugin.json"
    plugin, error = load_json(repo.root / plugin_rel)
    if error:
        return [Finding(ERROR, "A", manifest_rel, None, f"{name}: {plugin_rel} - {error}")]
    if plugin.get("description") != entry.get("description"):
        return [Finding(ERROR, "A", plugin_rel, None, f"{name}: description differs from {manifest_rel}")]
    return []


# -- B. skill frontmatter ----------------------------------------------------


def check_skill_frontmatter(repo: Repo) -> list[Finding]:
    findings = []
    for skill in discover_skills(repo):
        text, error = load_text(skill.path)
        if error:
            findings.append(Finding(ERROR, "B", skill.rel, None, error))
            continue
        try:
            frontmatter = parse_frontmatter(text)
        except FrontmatterError as exc:
            findings.append(Finding(ERROR, "B", skill.rel, None, str(exc)))
            continue
        findings += frontmatter_findings(skill, frontmatter)
    return findings


def frontmatter_findings(skill: SkillRef, frontmatter: dict[str, FrontmatterValue]) -> list[Finding]:
    findings = []
    name = frontmatter.get("name")
    if name is None:
        findings.append(Finding(ERROR, "B", skill.rel, None, "frontmatter has no name"))
    elif unquote(name.raw) != skill.name:
        message = f"name {unquote(name.raw)!r} does not match the directory {skill.name!r}"
        findings.append(Finding(ERROR, "B", skill.rel, name.line, message))

    hint = frontmatter.get("argument-hint")
    if hint is not None and hint.style is None and hint.raw.startswith("["):
        message = "argument-hint parses as a YAML list, not a string; wrap the value in quotes"
        findings.append(Finding(WARNING, "B", skill.rel, hint.line, message))

    if "license" in frontmatter:
        return findings  # vendored skill: the rest is the upstream author's business
    return findings + authored_skill_findings(skill, frontmatter)


def authored_skill_findings(skill: SkillRef, frontmatter: dict[str, FrontmatterValue]) -> list[Finding]:
    findings = []
    description = frontmatter.get("description")
    if description is not None and description.style is not None and not description.style.endswith("-"):
        message = f"description uses `{description.style}`, which keeps a trailing newline; use `{description.style}-`"
        findings.append(Finding(WARNING, "B", skill.rel, description.line, message))

    for flag in REQUIRED_FLAGS:
        if flag not in frontmatter:
            findings.append(Finding(WARNING, "B", skill.rel, None, f"{flag} is not set explicitly"))

    findings += last_change_findings(skill, frontmatter.get("last-change"))

    if skill.plugin is None:
        return findings  # a repo-local skill has no installer, so nothing manages its version
    for key in MANAGED_KEYS:
        if key not in frontmatter:
            findings.append(Finding(WARNING, "B", skill.rel, None, f"{key} is missing"))
    return findings


def last_change_findings(skill: SkillRef, value: FrontmatterValue | None) -> list[Finding]:
    if value is None:
        return [Finding(WARNING, "B", skill.rel, None, "last-change is missing")]
    stamp = unquote(value.raw)
    if LAST_CHANGE.match(stamp):
        return []
    return [Finding(WARNING, "B", skill.rel, value.line, f"last-change {stamp!r} is not YYYY-MM-DD HH:MM:SS")]


# -- C. skill name collisions ------------------------------------------------


def check_skill_collisions(repo: Repo) -> list[Finding]:
    by_name: dict[str, list[SkillRef]] = {}
    for skill in discover_skills(repo):
        if skill.plugin is not None:
            by_name.setdefault(skill.name, []).append(skill)

    findings = []
    for name, skills in sorted(by_name.items()):
        if len(skills) > 1:
            others = ", ".join(skill.rel for skill in skills[1:])
            message = f"skill name {name!r} is also defined by {others}; sync-symlinks.py drops both and unlinks it"
            findings.append(Finding(ERROR, "C", skills[0].rel, None, message))
    return findings


# -- D. plugin README vs reality ---------------------------------------------


def mentions(text: str, name: str) -> bool:
    """Loose match: a plugin README may write a skill as `name`, /name or skills/name/."""
    return re.search(rf"(?<![\w-]){re.escape(name)}(?![\w-])", text) is not None


def check_plugin_readmes(repo: Repo) -> list[Finding]:
    findings = []
    for plugin_dir in plugin_dirs(repo):
        readme = plugin_dir / "README.md"
        rel = relpath(repo, readme)
        if not readme.is_file():
            findings.append(Finding(WARNING, "D", rel, None, "plugin has no README.md"))
            continue
        text, error = load_text(readme)
        if error:
            findings.append(Finding(ERROR, "D", rel, None, error))
            continue
        for name in plugin_item_names(plugin_dir):
            if not mentions(text, name):
                findings.append(Finding(WARNING, "D", rel, None, f"{name} is not mentioned in the README"))
        findings += readme_orphans(plugin_dir, rel, text)
    return findings


def plugin_item_names(plugin_dir: Path) -> list[str]:
    skills = [d.name for d in real_skill_dirs(plugin_dir / "skills")]
    return skills + [rule.stem for rule in sorted((plugin_dir / "rules").glob("*.md"))]


def readme_orphans(plugin_dir: Path, rel: str, text: str) -> list[Finding]:
    """A `- `x` - ...` bullet that names something the plugin does not actually contain."""
    known = set(plugin_item_names(plugin_dir))
    known |= {path.name for path in plugin_dir.rglob("*") if path.is_file()}

    findings = []
    for number, line in enumerate(text.splitlines(), 1):
        match = README_ITEM.match(line)
        if match and match.group(1).lstrip("/") not in known:
            message = f"README lists `{match.group(1)}`, which the plugin does not contain"
            findings.append(Finding(WARNING, "D", rel, number, message))
    return findings


# -- E. dead relative links --------------------------------------------------


def link_target(raw: str) -> str | None:
    parts = raw.split()
    target = parts[0].split("#", 1)[0] if parts else ""
    if not target or target.startswith(("http:", "https:", "mailto:")):
        return None
    return target


def link_candidates(repo: Repo, source_dir: Path, target: str, root_entries: set[str]) -> list[Path]:
    """Empty means the target is illustrative ([text](url), file.ts:42) rather than a repo path."""
    if target.startswith(("./", "../")):
        return [source_dir / target]
    if target.split("/")[0] in root_entries:
        return [repo.root / target, source_dir / target]
    return []


def check_markdown_links(repo: Repo) -> list[Finding]:
    root_entries = {rel.split("/")[0] for rel in repo.tracked}
    findings = []
    for rel in tracked_real_files(repo):
        if not rel.endswith(".md"):
            continue
        text, error = load_text(repo.root / rel)
        if error:
            findings.append(Finding(ERROR, "E", rel, None, error))
            continue
        findings += dead_links(repo, rel, text, root_entries)
    return findings


def dead_links(repo: Repo, rel: str, text: str, root_entries: set[str]) -> list[Finding]:
    source_dir = (repo.root / rel).parent
    findings = []
    for number, line in enumerate(text.splitlines(), 1):
        for match in LINK_TARGET.finditer(line):
            target = link_target(match.group(1))
            if target is None:
                continue
            candidates = link_candidates(repo, source_dir, target, root_entries)
            if candidates and not any(candidate.exists() for candidate in candidates):
                findings.append(Finding(ERROR, "E", rel, number, f"link target {target} does not exist"))
    return findings


# -- F. hook configuration ---------------------------------------------------


def hook_configs(repo: Repo) -> list[tuple[Path, Path]]:
    """(config file, root that ${CLAUDE_PLUGIN_ROOT} stands for)."""
    configs = [(plugin_dir / "hooks" / "hooks.json", plugin_dir) for plugin_dir in plugin_dirs(repo)]
    configs = [pair for pair in configs if pair[0].is_file()]
    settings = repo.root / ".claude" / "settings.json"
    if settings.is_file():
        configs.append((settings, repo.root))
    return configs


def check_hook_configs(repo: Repo) -> list[Finding]:
    findings = []
    for config, plugin_root in hook_configs(repo):
        rel = relpath(repo, config)
        data, error = load_json(config)
        if error:
            findings.append(Finding(ERROR, "F", rel, None, error))
            continue
        for event, blocks in sorted(data.get("hooks", {}).items()):
            findings += event_findings(repo, rel, event, blocks, plugin_root)
    return findings


def event_findings(repo: Repo, rel: str, event: str, blocks: list[dict], plugin_root: Path) -> list[Finding]:
    findings = []
    seen: set[str] = set()
    for block in blocks:
        matcher = block.get("matcher", "")
        if matcher in seen:
            message = f"{event}: matcher {matcher!r} is used twice; merge the blocks into one `hooks` list"
            findings.append(Finding(ERROR, "F", rel, None, message))
        seen.add(matcher)
        findings += missing_scripts(repo, rel, event, block, plugin_root)
    return findings


def missing_scripts(repo: Repo, rel: str, event: str, block: dict, plugin_root: Path) -> list[Finding]:
    findings = []
    for hook in block.get("hooks", []):
        for token in SCRIPT_TOKEN.findall(hook.get("command", "")):
            if not expand_hook_path(repo, token, plugin_root).exists():
                findings.append(Finding(ERROR, "F", rel, None, f"{event}: script {token} does not exist"))
    return findings


def expand_hook_path(repo: Repo, token: str, plugin_root: Path) -> Path:
    expanded = token.replace("${CLAUDE_PLUGIN_ROOT}", str(plugin_root))
    expanded = expanded.replace("${CLAUDE_PROJECT_DIR}", str(repo.root))
    path = Path(expanded)
    return path if path.is_absolute() else repo.root / path


# -- G. hook exit codes ------------------------------------------------------


def check_hook_exit_codes(repo: Repo) -> list[Finding]:
    findings = []
    for rel in tracked_real_files(repo):
        if not rel.startswith("plugins/") or "/hooks/" not in rel or "/tests/" in rel:
            continue
        text, error = load_text(repo.root / rel)
        if error:
            findings.append(Finding(ERROR, "G", rel, None, error))
            continue
        for number, line in enumerate(text.splitlines(), 1):
            if EXIT_ONE.search(line):
                message = "a hook may only exit 0 (pass) or 2 (block); see plugins/core/rules/bash.md"
                findings.append(Finding(ERROR, "G", rel, number, message))
    return findings


# -- H. references between skills --------------------------------------------


def references_skill(line: str, name: str) -> bool:
    escaped = re.escape(name)
    return re.search(rf"`{escaped}`\s+skill|(?<![\w/-])/{escaped}(?![\w-])", line) is not None


def check_skill_cross_references(repo: Repo) -> list[Finding]:
    skills = discover_skills(repo)
    names = sorted({skill.name for skill in skills})
    findings = []
    for skill in skills:
        text, error = load_text(skill.path)
        if error:
            continue  # already reported by check B
        findings += cross_references(skill, text, names)
    return findings


def cross_references(skill: SkillRef, text: str, names: list[str]) -> list[Finding]:
    try:
        frontmatter = parse_frontmatter(text)
        _, body_start = split_frontmatter(text)
    except FrontmatterError:
        return []  # already reported by check B
    if "license" in frontmatter:
        return []  # a vendored skill manages its own internal links

    findings = []
    body = text.splitlines()[body_start - 1 :]
    for offset, line in enumerate(body):
        for name in names:
            if name != skill.name and references_skill(line, name):
                message = f"mentions the {name!r} skill; skills must stay independent of each other"
                findings.append(Finding(WARNING, "H", skill.rel, body_start + offset, message))
    return findings


# -- I. text hygiene ---------------------------------------------------------


def check_text_hygiene(repo: Repo) -> list[Finding]:
    findings = [
        Finding(WARNING, "I", rel, None, "CRLF line endings; .editorconfig asks for lf")
        for rel, eol in sorted(repo.eol.items())
        if eol == "crlf"
    ]
    for rel in tracked_real_files(repo):
        text, error = load_text(repo.root / rel)
        if error:
            findings.append(Finding(ERROR, "I", rel, None, error))
            continue
        findings += file_hygiene(rel, text)
    return findings


def file_hygiene(rel: str, text: str) -> list[Finding]:
    lines = text.splitlines()
    findings = []
    if text and not text.endswith("\n"):
        findings.append(Finding(WARNING, "I", rel, len(lines), "file does not end with a newline"))
    # .editorconfig turns trim_trailing_whitespace off for *.md (line breaks are two spaces).
    trailing_matters = not rel.endswith(".md")
    length_matters = rel.endswith(LINE_LENGTH_EXTENSIONS)
    for number, line in enumerate(lines, 1):
        if trailing_matters and line != line.rstrip():
            findings.append(Finding(WARNING, "I", rel, number, "trailing whitespace"))
        if length_matters and len(line) > MAX_LINE_LENGTH:
            message = f"line is {len(line)} characters, over the {MAX_LINE_LENGTH} limit"
            findings.append(Finding(WARNING, "I", rel, number, message))
        findings += foreign_letters(rel, number, line)
        if PLACEHOLDER.search(line):
            findings.append(Finding(WARNING, "I", rel, number, "leftover generator placeholder"))
    return findings


def foreign_letters(rel: str, number: int, line: str) -> list[Finding]:
    """Non-ASCII *letters* only - dashes, arrows and math signs belong in English text."""
    found = sorted({char for char in line if ord(char) > 127 and char.isalpha()})
    if not found:
        return []
    return [Finding(WARNING, "I", rel, number, f"non-ASCII letters {''.join(found)}; the repo is written in English")]


# -- J. tracked files that do not belong ------------------------------------


def check_stray_tracked_files(repo: Repo) -> list[Finding]:
    return [
        Finding(WARNING, "J", rel, None, "plans are local scratch; .claude/plans/ must stay untracked")
        for rel in repo.tracked
        if rel.startswith(".claude/plans/")
    ]


# -- report ------------------------------------------------------------------

CHECKS = (
    check_plugin_manifests,
    check_skill_frontmatter,
    check_skill_collisions,
    check_plugin_readmes,
    check_markdown_links,
    check_hook_configs,
    check_hook_exit_codes,
    check_skill_cross_references,
    check_text_hygiene,
    check_stray_tracked_files,
)


def sort_key(finding: Finding) -> tuple:
    return (SEVERITY_ORDER[finding.severity], finding.check, finding.path, finding.line or 0)


def format_finding(finding: Finding) -> str:
    location = f"{finding.path}:{finding.line}" if finding.line else finding.path
    return f"{finding.severity:<7} [{finding.check}] {location}: {finding.message}"


def run_checks(repo: Repo) -> list[Finding]:
    return sorted((finding for check in CHECKS for finding in check(repo)), key=sort_key)


def main() -> int:
    findings = run_checks(load_repo(Path(__file__).resolve().parent.parent))
    if not findings:
        print("No findings.")
        return 0
    for finding in findings:
        print(format_finding(finding))
    errors = sum(finding.severity == ERROR for finding in findings)
    print(f"\n{len(findings)} findings: {errors} errors, {len(findings) - errors} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
