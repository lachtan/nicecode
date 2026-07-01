import pytest

import ponytail


@pytest.fixture(autouse=True)
def _config_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(tmp_path))


def _prompt(text, sid="s1"):
    return {"hook_event_name": "UserPromptSubmit", "session_id": sid, "prompt": text}


def _marker(sid="s1"):
    return ponytail.marker_path({"session_id": sid})


@pytest.mark.parametrize("text", ["/ponytail on", "/ponytail anchor"])
def test_activate_writes_marker_and_emits_anchor(text):
    out = ponytail.handle_prompt(_prompt(text))
    assert _marker().exists()
    assert "YAGNI" in out


def test_plain_prompt_emits_anchor_while_active():
    ponytail.handle_prompt(_prompt("/ponytail on"))
    assert "YAGNI" in ponytail.handle_prompt(_prompt("just do the thing"))


def test_plain_prompt_silent_when_inactive():
    assert ponytail.handle_prompt(_prompt("just do the thing")) == ""


def test_deactivate_removes_marker():
    ponytail.handle_prompt(_prompt("/ponytail on"))
    for text in ("stop ponytail", "/ponytail off"):
        ponytail.handle_prompt(_prompt("/ponytail on"))
        assert ponytail.handle_prompt(_prompt(text)) == ""
        assert not _marker().exists()


@pytest.mark.parametrize("text", ["/ponytail", "/ponytail-audit"])
def test_bare_and_audit_never_activate(text):
    assert ponytail.handle_prompt(_prompt(text)) == ""
    assert not _marker().exists()


def test_session_start_reloads_body_only_while_active():
    start = {"hook_event_name": "SessionStart", "session_id": "s1"}
    assert ponytail.handle_session_start(start) == ""
    ponytail.handle_prompt(_prompt("/ponytail on"))
    assert "The shortest path to done" in ponytail.handle_session_start(start)


def test_unsafe_session_id_is_ignored():
    assert ponytail.marker_path({"session_id": "../evil"}) is None
    assert ponytail.handle_prompt(_prompt("/ponytail on", sid="../evil")) == ""
