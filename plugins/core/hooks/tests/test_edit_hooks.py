#!/usr/bin/env python3

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).parent.parent / "scripts"

# Fake tools are shell scripts, which Windows cannot run from PATH.
pytestmark = pytest.mark.skipif(sys.platform == "win32", reason="fake tools are shell scripts")

# (hook script, tool it runs, a file it handles)
HOOKS = [
    ("format-python.py", "ruff", "a.py"),
    ("check-bash.py", "shellcheck", "a.sh"),
    ("fix-markdown.py", "markdownlint-cli2", "a.md"),
    ("mermaid-lint.py", "npx", "a.md"),
    ("format-powershell.py", "pwsh", "a.PS1"),
]


def run_hook(script: str, stdin: str, path_dir: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script)],
        input=stdin,
        capture_output=True,
        text=True,
        env={**os.environ, "PATH": str(path_dir)},
    )


def edit_input(file_path: str) -> str:
    return json.dumps({"tool_input": {"file_path": file_path}})


def fake_tool(directory: Path, name: str, exit_code: int, output: str = "") -> None:
    tool = directory / name
    tool.write_text(f"#!/bin/sh\necho '{output}'\nexit {exit_code}\n")
    tool.chmod(0o755)


@pytest.mark.parametrize("script, tool, file_path", HOOKS)
def test_other_extension_is_ignored(tmp_path, script, tool, file_path):
    fake_tool(tmp_path, tool, 1, "should not run")
    result = run_hook(script, edit_input("a.txt"), tmp_path)
    assert result.returncode == 0
    assert result.stdout == ""


@pytest.mark.parametrize("script, tool, file_path", HOOKS)
def test_missing_tool_is_skipped_silently(tmp_path, script, tool, file_path):
    result = run_hook(script, edit_input(file_path), tmp_path)
    assert result.returncode == 0
    assert result.stdout == ""
    assert result.stderr == ""


@pytest.mark.parametrize("script, tool, file_path", HOOKS)
def test_clean_file_reports_nothing(tmp_path, script, tool, file_path):
    fake_tool(tmp_path, tool, 0, "all good")
    result = run_hook(script, edit_input(file_path), tmp_path)
    assert result.returncode == 0
    assert result.stdout == ""


@pytest.mark.parametrize("script, tool, file_path", HOOKS)
def test_findings_go_to_claude(tmp_path, script, tool, file_path):
    fake_tool(tmp_path, tool, 1, "line 3: broken")
    result = run_hook(script, edit_input(file_path), tmp_path)
    assert result.returncode == 0
    output = json.loads(result.stdout)["hookSpecificOutput"]
    assert output["hookEventName"] == "PostToolUse"
    assert "line 3: broken" in output["additionalContext"]


def test_failure_without_output_still_reports(tmp_path):
    fake_tool(tmp_path, "shellcheck", 3)
    result = run_hook("check-bash.py", edit_input("a.sh"), tmp_path)
    context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
    assert "exited with code 3" in context


@pytest.mark.parametrize("script, tool, file_path", HOOKS)
def test_malformed_json_input(tmp_path, script, tool, file_path):
    result = run_hook(script, "not json", tmp_path)
    assert result.returncode == 0
    assert "failed to parse stdin" in result.stderr


def test_missing_file_path_is_ignored(tmp_path):
    fake_tool(tmp_path, "ruff", 1, "should not run")
    result = run_hook("format-python.py", json.dumps({"tool_input": {}}), tmp_path)
    assert result.returncode == 0
    assert result.stdout == ""
