import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

_mod_path = Path(__file__).resolve().parent.parent / "build.py"
_spec = importlib.util.spec_from_file_location("build", _mod_path)
build = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(build)


def plugin_entry(name: str, version: object = "1.0.0") -> dict:
    return {"name": name, "description": f"{name} plugin", "version": version, "author": {"name": "tester"}}


def make_repo(root: Path, plugins: list[dict], files: dict[str, str]) -> Path:
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    catalog = {"name": "test", "owner": {"name": "Test"}, "description": "Test marketplace", "plugins": plugins}
    files = {"src/marketplace.json": json.dumps(catalog), **files}
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return root


def demo_repo(root: Path) -> Path:
    return make_repo(root, [plugin_entry("demo")], {"src/demo/skills/one/SKILL.md": "# One\n"})


def hook(event: str, tools: list[str] | None = None, command: str = "run") -> dict:
    return {"event": event, "command": command, **({"tools": tools} if tools is not None else {})}


# -- hook translation --------------------------------------------------------


class TestTranslateHooks:
    @pytest.mark.parametrize(
        "event, expected",
        [("before-tool", "PreToolUse"), ("after-tool", "PostToolUse")],
    )
    def test_translates_a_tool_event(self, event, expected):
        result = build.translate_hooks({"hooks": [hook(event, ["shell"])]})

        assert result == {"hooks": {expected: [{"matcher": "Bash", "hooks": [{"type": "command", "command": "run"}]}]}}

    @pytest.mark.parametrize(
        "event, expected",
        [("session-start", "SessionStart"), ("prompt-submit", "UserPromptSubmit")],
    )
    def test_translates_an_event_without_tools_into_a_group_without_matcher(self, event, expected):
        result = build.translate_hooks({"hooks": [hook(event)]})

        assert result == {"hooks": {expected: [{"hooks": [{"type": "command", "command": "run"}]}]}}

    @pytest.mark.parametrize(
        "tools, matcher", [(["shell"], "Bash"), (["edit"], "Edit|Write"), (["shell", "edit"], "Bash|Edit|Write")]
    )
    def test_translates_the_tools_into_a_matcher(self, tools, matcher):
        result = build.translate_hooks({"hooks": [hook("before-tool", tools)]})

        assert result["hooks"]["PreToolUse"][0]["matcher"] == matcher

    def test_replaces_the_plugin_root_placeholder(self):
        result = build.translate_hooks({"hooks": [hook("session-start", command="python3 {plugin_root}/a.py")]})

        assert result["hooks"]["SessionStart"][0]["hooks"][0]["command"] == "python3 ${CLAUDE_PLUGIN_ROOT}/a.py"

    def test_merges_the_same_event_and_matcher_into_one_group(self):
        hooks = [
            hook("after-tool", ["edit"], "one"),
            hook("after-tool", ["shell"], "two"),
            hook("after-tool", ["edit"], "three"),
        ]

        groups = build.translate_hooks({"hooks": hooks})["hooks"]["PostToolUse"]

        assert [(group["matcher"], [h["command"] for h in group["hooks"]]) for group in groups] == [
            ("Edit|Write", ["one", "three"]),
            ("Bash", ["two"]),
        ]

    @pytest.mark.parametrize(
        "entry, message",
        [
            (hook("on-exit"), "unknown event"),
            (hook("before-tool", ["browser"]), "unknown tools"),
            (hook("before-tool"), "needs tools"),
            (hook("before-tool", []), "needs tools"),
            (hook("session-start", ["shell"]), "takes no tools"),
        ],
    )
    def test_rejects_an_invalid_entry(self, entry, message):
        with pytest.raises(build.BuildError, match=message):
            build.translate_hooks({"hooks": [entry]})


# -- rendering ---------------------------------------------------------------


class TestRender:
    def test_writes_the_claude_manifests(self, tmp_path):
        rendered = build.render(demo_repo(tmp_path))

        manifest = json.loads(rendered["plugins/demo/.claude-plugin/plugin.json"].content)
        marketplace = json.loads(rendered[".claude-plugin/marketplace.json"].content)
        assert manifest == {"name": "demo", "description": "demo plugin", "author": {"name": "tester"}}
        assert marketplace["metadata"] == {"description": "Test marketplace"}
        assert marketplace["plugins"][0]["source"] == "./plugins/demo"

    def test_ships_neither_tests_nor_the_neutral_hooks(self, tmp_path):
        files = {
            "src/demo/skills/one/SKILL.md": "# One\n",
            "src/demo/skills/one/test_one.py": "",
            "src/demo/hooks/tests/test_hook.py": "",
            "src/demo/hooks.json": json.dumps({"hooks": [hook("session-start")]}),
        }

        rendered = build.render(make_repo(tmp_path, [plugin_entry("demo")], files))

        assert sorted(path for path in rendered if path.startswith("plugins/")) == [
            "plugins/demo/.claude-plugin/plugin.json",
            "plugins/demo/hooks/hooks.json",
            "plugins/demo/skills/one/SKILL.md",
        ]

    def test_leaves_out_ignored_files(self, tmp_path):
        files = {
            "src/demo/skills/one/SKILL.md": "# One\n",
            ".gitignore": "__pycache__/\n",
            "src/demo/__pycache__/a.pyc": "",
        }

        rendered = build.render(make_repo(tmp_path, [plugin_entry("demo")], files))

        assert not any("__pycache__" in path for path in rendered)

    def test_keeps_the_executable_bit(self, tmp_path):
        repo = make_repo(tmp_path, [plugin_entry("demo")], {"src/demo/scripts/run.sh": "#!/bin/sh\n"})
        (repo / "src/demo/scripts/run.sh").chmod(0o755)

        assert build.render(repo)["plugins/demo/scripts/run.sh"].is_executable

    def test_rejects_a_plugin_missing_from_the_catalog(self, tmp_path):
        repo = make_repo(tmp_path, [], {"src/orphan/README.md": "# Orphan\n"})

        with pytest.raises(build.BuildError, match="not listed in src/marketplace.json: orphan"):
            build.render(repo)

    def test_rejects_a_catalog_entry_without_a_plugin(self, tmp_path):
        repo = make_repo(tmp_path, [plugin_entry("ghost")], {})

        with pytest.raises(build.BuildError, match="missing from src/: ghost"):
            build.render(repo)

    @pytest.mark.parametrize("version", ["1.0", "v1.0.0", 1, None])
    def test_rejects_an_invalid_version(self, tmp_path, version):
        repo = make_repo(tmp_path, [plugin_entry("demo", version)], {"src/demo/README.md": "# Demo\n"})

        with pytest.raises(build.BuildError, match="is not a MAJOR.MINOR.PATCH string"):
            build.render(repo)

    def test_names_the_hook_file_of_an_invalid_hook(self, tmp_path):
        files = {"src/demo/hooks.json": json.dumps({"hooks": [hook("on-exit")]})}
        repo = make_repo(tmp_path, [plugin_entry("demo")], files)

        with pytest.raises(build.BuildError, match="src/demo/hooks.json: unknown event"):
            build.render(repo)


# -- writing and checking ----------------------------------------------------


class TestMain:
    def test_check_passes_right_after_a_build(self, tmp_path):
        repo = demo_repo(tmp_path)

        assert build.main([], repo) == 0
        assert build.main(["--check"], repo) == 0

    def test_check_reports_a_changed_source(self, tmp_path, capsys):
        repo = demo_repo(tmp_path)
        build.main([], repo)
        (repo / "src/demo/skills/one/SKILL.md").write_text("# Changed\n")

        assert build.main(["--check"], repo) == 1
        assert "plugins/demo/skills/one/SKILL.md" in capsys.readouterr().out

    def test_check_reports_a_hand_edited_output_file(self, tmp_path, capsys):
        repo = demo_repo(tmp_path)
        build.main([], repo)
        (repo / "plugins/demo/skills/one/SKILL.md").write_text("# Edited by hand\n")

        assert build.main(["--check"], repo) == 1
        assert "plugins/demo/skills/one/SKILL.md" in capsys.readouterr().out

    def test_check_reports_an_extra_output_file(self, tmp_path, capsys):
        repo = demo_repo(tmp_path)
        build.main([], repo)
        (repo / "plugins/demo/extra.md").write_text("# Extra\n")

        assert build.main(["--check"], repo) == 1
        assert "plugins/demo/extra.md" in capsys.readouterr().out

    def test_check_writes_nothing(self, tmp_path):
        repo = demo_repo(tmp_path)

        assert build.main(["--check"], repo) == 1
        assert not (repo / "plugins").exists()

    def test_build_removes_an_output_file_whose_source_is_gone(self, tmp_path):
        repo = make_repo(tmp_path, [plugin_entry("demo")], {"src/demo/a/one.md": "", "src/demo/b/two.md": ""})
        build.main([], repo)
        (repo / "src/demo/b/two.md").unlink()

        build.main([], repo)

        assert not (repo / "plugins/demo/b").exists()
        assert build.main(["--check"], repo) == 0

    def test_build_error_exits_1(self, tmp_path, capsys):
        repo = make_repo(tmp_path, [plugin_entry("ghost")], {})

        assert build.main([], repo) == 1
        assert "ghost" in capsys.readouterr().err
