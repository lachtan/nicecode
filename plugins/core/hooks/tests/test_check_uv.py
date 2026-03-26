#!/usr/bin/env python3

import json
import subprocess
import sys
from pathlib import Path

HOOK = Path(__file__).parent.parent / "check-uv.py"


def run_hook(command: str) -> subprocess.CompletedProcess:
    data = json.dumps({"tool_input": {"command": command}})
    return subprocess.run(
        [sys.executable, str(HOOK)],
        input=data,
        capture_output=True,
        text=True,
    )


# --- Povolené příkazy (exit 0) ---


def test_uv_pip_install_allowed():
    assert run_hook("uv pip install requests").returncode == 0


def test_uv_add_allowed():
    assert run_hook("uv add numpy").returncode == 0


def test_uv_venv_allowed():
    assert run_hook("uv venv .venv").returncode == 0


def test_unrelated_command_allowed():
    assert run_hook("ls -la").returncode == 0


def test_empty_command_allowed():
    assert run_hook("").returncode == 0


def test_missing_command_key_allowed():
    data = json.dumps({"tool_input": {}})
    result = subprocess.run(
        [sys.executable, str(HOOK)],
        input=data,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0


# --- Zakázané příkazy (exit 2) ---


def test_pip_blocked():
    assert run_hook("pip install requests").returncode == 2


def test_pip3_blocked():
    assert run_hook("pip3 install flask").returncode == 2


def test_pipx_blocked():
    assert run_hook("pipx install black").returncode == 2


def test_python_m_pip_blocked():
    assert run_hook("python -m pip install numpy").returncode == 2


def test_python3_m_pip_blocked():
    assert run_hook("python3 -m pip install numpy").returncode == 2


def test_python_m_venv_blocked():
    assert run_hook("python -m venv .venv").returncode == 2


def test_python3_m_venv_blocked():
    assert run_hook("python3 -m venv .venv").returncode == 2


def test_python_m_ensurepip_blocked():
    assert run_hook("python -m ensurepip").returncode == 2


def test_python3_m_ensurepip_blocked():
    assert run_hook("python3 -m ensurepip").returncode == 2


def test_easy_install_blocked():
    assert run_hook("easy_install requests").returncode == 2


# --- Edge cases ---


def test_pip_in_longer_command_blocked():
    assert run_hook("sudo pip install something").returncode == 2


def test_extra_whitespace_normalized_blocked():
    assert run_hook("python  -m  pip  install  x").returncode == 2


def test_stderr_message_on_block():
    result = run_hook("pip install requests")
    assert "Forbidden" in result.stderr or "uv" in result.stderr.lower()


# --- False positives: substring nesmí matchovat ---


def test_catpipe_in_path_allowed():
    assert (
        run_hook(
            "git restore --staged trading-servers/ansible/playbooks/config_catpipe_servers.yaml"
        ).returncode
        == 0
    )


def test_pipeline_allowed():
    assert run_hook("cat pipeline.yaml").returncode == 0


def test_pipenv_allowed():
    assert run_hook("pipenv install requests").returncode == 0


def test_pip_as_part_of_filename_allowed():
    assert run_hook("cat /tmp/pip_backup.txt").returncode == 0


# --- Bypass přes compound commands ---


def test_uv_then_pip_via_and_blocked():
    assert run_hook("uv sync && pip install requests").returncode == 2


def test_uv_then_pip_via_or_blocked():
    assert run_hook("uv sync || pip install requests").returncode == 2


def test_uv_then_pip_via_semicolon_blocked():
    assert run_hook("uv sync; pip install requests").returncode == 2


def test_uv_then_pip_via_pipe_blocked():
    assert run_hook("uv sync | pip install requests").returncode == 2


def test_malformed_json_input():
    result = subprocess.run(
        [sys.executable, str(HOOK)],
        input="not json",
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "failed to parse stdin" in result.stderr
