#!/usr/bin/env python3

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

HOOK = Path(__file__).parent.parent / "scripts" / "check-edited-file.py"

# Fake tools are shell scripts, which Windows cannot run from PATH.
pytestmark = pytest.mark.skipif(sys.platform == "win32", reason="fake tools are shell scripts")

# (tool a check runs, a file it handles)
TOOLS = [
    ("ruff", "a.py"),
    ("shellcheck", "a.sh"),
    ("markdownlint-cli2", "a.md"),
    ("md-mermaid-lint", "a.md"),
    ("pwsh", "a.PS1"),
]


def run_hook(stdin: str, path_dir: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(HOOK)],
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


def context_of(result: subprocess.CompletedProcess) -> str:
    output = json.loads(result.stdout)["hookSpecificOutput"]
    assert output["hookEventName"] == "PostToolUse"
    return output["additionalContext"]


@pytest.mark.parametrize("tool, file_path", TOOLS)
def test_other_extension_is_ignored(tmp_path, tool, file_path):
    fake_tool(tmp_path, tool, 1, "should not run")
    result = run_hook(edit_input("a.txt"), tmp_path)
    assert result.returncode == 0
    assert result.stdout == ""


@pytest.mark.parametrize("tool, file_path", TOOLS)
def test_missing_tool_is_skipped_silently(tmp_path, tool, file_path):
    result = run_hook(edit_input(file_path), tmp_path)
    assert result.returncode == 0
    assert result.stdout == ""
    assert result.stderr == ""


@pytest.mark.parametrize("tool, file_path", TOOLS)
def test_clean_file_reports_nothing(tmp_path, tool, file_path):
    fake_tool(tmp_path, tool, 0, "all good")
    result = run_hook(edit_input(file_path), tmp_path)
    assert result.returncode == 0
    assert result.stdout == ""


@pytest.mark.parametrize("tool, file_path", TOOLS)
def test_findings_go_to_claude(tmp_path, tool, file_path):
    fake_tool(tmp_path, tool, 1, "line 3: broken")
    result = run_hook(edit_input(file_path), tmp_path)
    assert result.returncode == 0
    context = context_of(result)
    assert "line 3: broken" in context
    assert "exited with code 1" in context


def test_failure_without_output_still_reports(tmp_path):
    fake_tool(tmp_path, "shellcheck", 3)
    context = context_of(run_hook(edit_input("a.sh"), tmp_path))
    assert "exited with code 3" in context
    assert "(no output)" in context


def test_unrunnable_tool_goes_to_claude(tmp_path):
    tool = tmp_path / "shellcheck"
    tool.write_bytes(b"\x00\x01")
    tool.chmod(0o755)
    result = run_hook(edit_input("a.sh"), tmp_path)
    assert result.returncode == 0
    assert "could not be started" in context_of(result)


def test_all_markdown_findings_go_in_one_message(tmp_path):
    fake_tool(tmp_path, "markdownlint-cli2", 1, "MD032 blanks")
    fake_tool(tmp_path, "md-mermaid-lint", 1, "mermaid parse error")
    context = context_of(run_hook(edit_input("a.md"), tmp_path))
    assert "[markdownlint]" in context
    assert "MD032 blanks" in context
    assert "[mermaid]" in context
    assert "mermaid parse error" in context


def test_only_failing_check_is_reported(tmp_path):
    fake_tool(tmp_path, "md-mermaid-lint", 1, "mermaid parse error")
    context = context_of(run_hook(edit_input("a.md"), tmp_path))
    assert "[mermaid]" in context
    assert "[markdownlint]" not in context


def test_malformed_json_input(tmp_path):
    result = run_hook("not json", tmp_path)
    assert result.returncode == 0
    assert "failed to parse stdin" in result.stderr


def test_missing_file_path_is_ignored(tmp_path):
    fake_tool(tmp_path, "ruff", 1, "should not run")
    result = run_hook(json.dumps({"tool_input": {}}), tmp_path)
    assert result.returncode == 0
    assert result.stdout == ""
