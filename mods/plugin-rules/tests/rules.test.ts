/**
 * A rule file's frontmatter, and the plugin.register hook: the rules of a plugin that loads are read from
 * its `rules/` folder, a refused or bundled plugin adds none, and registering again replaces them.
 */

import type { EngineInterface, PluginRegisterInput, PluginRegisterResult } from "claude-code";
import { expect, test } from "claude-code/testing";
import { compileGlob } from "../hooks/glob";
import { allRules, parseRule, registerPluginRules } from "../hooks/rules";

type RegisterNext = Parameters<typeof registerPluginRules>[2];

const PATH = "/plugins/core/rules/bash.md";

function patternsOf(globs: readonly string[]): (RegExp | undefined)[] {
  return globs.map(compileGlob);
}

test("a file without frontmatter is a rule for every file, its text whole", () => {
  const rule = parseRule("core", PATH, "# Bash\n\nUse set -euo pipefail.\n");
  expect(rule).toEqual({ plugin: "core", path: PATH, pathPatterns: [], body: "# Bash\n\nUse set -euo pipefail.\n" });
});

test("an empty frontmatter is dropped from the body", () => {
  const rule = parseRule("core", PATH, "---\n---\n\n# Clean Code\n");
  expect(rule?.pathPatterns).toEqual([]);
  expect(rule?.body).toBe("# Clean Code\n");
});

test("a block list under paths: gives the globs, quoted or not, beside other keys", () => {
  const text = '---\ndescription: "Python"\npaths:\n  - "**/*.py"\n  - **/*.pyi\n  - \'**/*.pyw\'\n---\n# Python\n';
  const rule = parseRule("core", PATH, text);
  expect(rule?.pathPatterns).toEqual(patternsOf(["**/*.py", "**/*.pyi", "**/*.pyw"]));
  expect(rule?.body).toBe("# Python\n");
});

test("the generated keys go with the frontmatter, and Windows line ends are read", () => {
  const text =
    '---\r\npaths:\r\n  - "**/*.sh"\r\nmanaged-by: https://github.com/lachtan/nicecode\r\n' +
    'version: "1.1.2"\r\nlast-change: "2026-09-25 14:46:28"\r\n---\r\n\r\n# Bash\r\n';
  const rule = parseRule("core", PATH, text);
  expect(rule?.pathPatterns).toEqual(patternsOf(["**/*.sh"]));
  expect(rule?.body).toBe("# Bash\n");
});

test("a block list without indent gives the same globs", () => {
  const rule = parseRule("core", PATH, '---\npaths:\n- "**/*.sh"\n- "**/*.bash"\n---\n# Bash\n');
  expect(rule?.pathPatterns).toEqual(patternsOf(["**/*.sh", "**/*.bash"]));
});

test("paths: that is not a block list of valid globs skips the rule", () => {
  const unreadableFrontmatters = [
    'paths: ["**/*.sh"]',
    'paths: "**/*.sh"',
    "paths:",
    "paths:\ndescription: Bash",
    'paths:\n  - "**/*.sh"\n  - "**/*.{ps1"',
  ];
  for (const frontmatter of unreadableFrontmatters) {
    expect(parseRule("core", PATH, `---\n${frontmatter}\n---\n# Bash\n`)).toBeUndefined();
  }
});

/** A `rules/` folder in memory: file name → text. `debugLog` takes the lines the hook logs. */
function engineWithRules(files: Record<string, string>, debugLog: string[] = []): EngineInterface {
  const fs = {
    exists: async (path: string) => path.endsWith("/rules") && Object.keys(files).length > 0,
    list: async () => {
      const entries = Object.keys(files).map((name) => ({
        name,
        kind: "file",
        size: 0,
        mtimeMs: 0,
        isLink: false,
      }));
      return [...entries, { name: "drafts.md", kind: "dir", size: 0, mtimeMs: 0, isLink: false }];
    },
    read: async (path: string) => files[path.slice(path.lastIndexOf("/") + 1)] ?? "",
  };
  const ui = { log: (text: string) => debugLog.push(text) };
  return { fs, ui } as unknown as EngineInterface;
}

function plugin(name: string, root: string): PluginRegisterInput {
  return { name, root } as unknown as PluginRegisterInput;
}

function nextAnswering(result: PluginRegisterResult): RegisterNext {
  return (async () => result) as unknown as RegisterNext;
}

const ALLOW: PluginRegisterResult = { allow: true };

test("a plugin that loads adds the .md files of its rules folder", async () => {
  const engine = engineWithRules({ "bash.md": "# Bash\n", "notes.txt": "not a rule" });

  const result = await registerPluginRules(engine, plugin("reg-a", "/plugins/a"), nextAnswering(ALLOW));

  expect(result).toEqual(ALLOW);
  const paths = allRules()
    .filter((rule) => rule.plugin === "reg-a")
    .map((rule) => rule.path);
  expect(paths).toEqual(["/plugins/a/rules/bash.md"]);
});

test("the rules of a plugin are kept sorted by file name", async () => {
  const engine = engineWithRules({ "python.md": "# Python\n", "bash.md": "# Bash\n", "csharp.md": "# C#\n" });

  await registerPluginRules(engine, plugin("reg-e", "/plugins/e"), nextAnswering(ALLOW));

  const paths = allRules()
    .filter((rule) => rule.plugin === "reg-e")
    .map((rule) => rule.path);
  expect(paths).toEqual(["/plugins/e/rules/bash.md", "/plugins/e/rules/csharp.md", "/plugins/e/rules/python.md"]);
});

test("a skipped rule is named in the debug log and the plugin's other rules load", async () => {
  const debugLog: string[] = [];
  const engine = engineWithRules({ "bad.md": '---\npaths: "**/*.sh"\n---\n# Bad\n', "good.md": "# Good\n" }, debugLog);

  await registerPluginRules(engine, plugin("reg-f", "/plugins/f"), nextAnswering(ALLOW));

  const paths = allRules()
    .filter((rule) => rule.plugin === "reg-f")
    .map((rule) => rule.path);
  expect(paths).toEqual(["/plugins/f/rules/good.md"]);
  expect(debugLog.length).toBe(1);
  expect(debugLog[0]).toContain("/plugins/f/rules/bad.md");
});

test("a refused plugin and a bundled one add no rules", async () => {
  const engine = engineWithRules({ "bash.md": "# Bash\n" });

  const refused = await registerPluginRules(engine, plugin("reg-b", "/plugins/b"), nextAnswering({ refuse: "no" }));
  await registerPluginRules(engine, plugin("reg-c", "builtin"), nextAnswering(ALLOW));

  expect(refused).toEqual({ refuse: "no" });
  expect(allRules().filter((rule) => rule.plugin === "reg-b" || rule.plugin === "reg-c")).toEqual([]);
});

test("registering a plugin again replaces its rules", async () => {
  await registerPluginRules(engineWithRules({ "old.md": "old" }), plugin("reg-d", "/plugins/d"), nextAnswering(ALLOW));
  await registerPluginRules(engineWithRules({ "new.md": "new" }), plugin("reg-d", "/plugins/d"), nextAnswering(ALLOW));

  const bodies = allRules()
    .filter((rule) => rule.plugin === "reg-d")
    .map((rule) => rule.body);
  expect(bodies).toEqual(["new"]);
});
