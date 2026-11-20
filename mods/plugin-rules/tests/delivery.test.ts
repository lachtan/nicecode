/**
 * Delivery: each rule reaches a loop once, beside a prompt or a file tool's result or in the prompt a subagent
 * starts with, only when its context is certain to reach the model; a compaction or a /clear makes a loop take
 * its rules again.
 */

import type { EngineInterface, PluginRegisterInput, PromptSubmitInput, PromptSubmitResult } from "claude-code";
import { expect, test } from "claude-code/testing";
import {
  attachRulesToPrompt,
  attachRulesToSubagentPrompt,
  attachRulesToToolResult,
  forgetAll,
  resetAfterCompact,
  resetOnSessionEnd,
  sentIn,
} from "../hooks/delivery";
import { registerPluginRules } from "../hooks/rules";

type PromptNext = Parameters<typeof attachRulesToPrompt>[2];
type ToolNext = Parameters<typeof attachRulesToToolResult>[2];
type ToolEvent = Parameters<typeof attachRulesToToolResult>[1];
type SpawnNext = Parameters<typeof attachRulesToSubagentPrompt>[2];
type SpawnEvent = Parameters<typeof attachRulesToSubagentPrompt>[1];
type CompactNext = Parameters<typeof resetAfterCompact>[2];
type CompactEvent = Parameters<typeof resetAfterCompact>[1];
type EndNext = Parameters<typeof resetOnSessionEnd>[2];
type EndEvent = Parameters<typeof resetOnSessionEnd>[1];

const CWD = "/proj";
const RULES_ROOT = "/plugins/core/rules";
const CLEAN_CODE = `${RULES_ROOT}/clean-code.md`;
const BASH = `${RULES_ROOT}/bash.md`;
const SCRIPTS = `${RULES_ROOT}/scripts.md`;
const SUBAGENT = "agent-1";

const RULE_FILES: Record<string, string> = {
  "clean-code.md": "---\n---\n# Clean Code\n",
  "bash.md": '---\npaths:\n  - "**/*.sh"\n---\n# Bash\n',
  "scripts.md": '---\npaths:\n  - "scripts/*.sh"\n---\n# Scripts\n',
};

/** Engine with the core plugin's rules on disk and the session's working directory. */
const ENGINE = {
  fs: {
    exists: async () => true,
    list: async () => Object.keys(RULE_FILES).map((name) => ({ name, kind: "file" })),
    read: async (path: string) => RULE_FILES[path.slice(path.lastIndexOf("/") + 1)] ?? "",
  },
  session: { cwd: async () => CWD },
} as unknown as EngineInterface;

/** Registers the core plugin once per test, so the registry holds exactly its three rules. */
async function startWithCoreRules(): Promise<void> {
  const core = { name: "core", root: "/plugins/core" } as unknown as PluginRegisterInput;
  const allow = (async () => ({ allow: true })) as unknown as Parameters<typeof registerPluginRules>[2];
  await registerPluginRules(ENGINE, core, allow);
  forgetAll();
}

/** The paths named in the `Contents of <path> (...)` line of each context entry. */
function contextPaths(context: readonly string[] | undefined): string[] {
  const paths: string[] = [];
  for (const entry of context ?? []) {
    const match = /^Contents of (\S+) \(rules from the core plugin\):/.exec(entry);
    if (match?.[1] !== undefined) paths.push(match[1]);
  }
  return paths;
}

const PROMPT = { text: "hi", wait: false, origin: { kind: "user" } } as unknown as PromptSubmitInput;

/** Stands for the chain beneath: records the context it was handed and answers `result`, or enters it. */
function promptNext(handed: (readonly string[] | undefined)[], result?: PromptSubmitResult): PromptNext {
  const next = async (input: PromptSubmitInput) => {
    handed.push(input.context);
    return result ?? { text: input.text, context: input.context };
  };
  return next as unknown as PromptNext;
}

function readOf(filePath: string, agentId?: string): ToolEvent {
  return { tool: "Read", tool_use_id: "t1", file_path: filePath, agentId } as unknown as ToolEvent;
}

const READ_RESULT = { result: "file text", text: "file text" };

function toolNext(result: object = READ_RESULT): ToolNext {
  return (async () => result) as unknown as ToolNext;
}

async function readFile(filePath: string, agentId?: string): Promise<string[]> {
  const result = await attachRulesToToolResult(ENGINE, readOf(filePath, agentId), toolNext());
  return contextPaths(result.context);
}

test("the first prompt carries the rules without paths:, the next one none", async () => {
  await startWithCoreRules();
  const handed: (readonly string[] | undefined)[] = [];

  await attachRulesToPrompt(ENGINE, { ...PROMPT, context: ["mine"] }, promptNext(handed));
  await attachRulesToPrompt(ENGINE, PROMPT, promptNext(handed));

  expect(handed[0]?.[0]).toBe("mine");
  expect(contextPaths(handed[0])).toEqual([CLEAN_CODE]);
  expect(handed[1]).toBeUndefined();
});

test("a slash command carries no rules and marks none", async () => {
  await startWithCoreRules();
  const handed: (readonly string[] | undefined)[] = [];
  const command = { ...PROMPT, command: { name: "compact", args: "" } };

  await attachRulesToPrompt(ENGINE, command, promptNext(handed));

  expect(handed[0]).toBeUndefined();
  expect(sentIn("main").size).toBe(0);
});

test("a dropped prompt marks nothing", async () => {
  await startWithCoreRules();

  await attachRulesToPrompt(ENGINE, PROMPT, promptNext([], { drop: "blocked" }));

  expect(sentIn("main").size).toBe(0);
});

test("reading a matching file attaches its rule once, beside the rules not yet sent", async () => {
  await startWithCoreRules();

  expect(await readFile(`${CWD}/build.sh`)).toEqual([BASH, CLEAN_CODE]);
  expect(await readFile(`${CWD}/test.sh`)).toEqual([]);
});

test("reading a file no glob matches attaches only the rules without paths:", async () => {
  await startWithCoreRules();

  expect(await readFile(`${CWD}/main.py`)).toEqual([CLEAN_CODE]);
  expect(await readFile(`${CWD}/run.sh`)).toEqual([BASH]);
});

test("a denied call attaches and marks nothing", async () => {
  await startWithCoreRules();

  const result = await attachRulesToToolResult(ENGINE, readOf(`${CWD}/a.sh`), toolNext({ deny: "no" }));

  expect(result).toEqual({ deny: "no" });
  expect(sentIn("main").size).toBe(0);
});

test("each loop takes the rules on its own", async () => {
  await startWithCoreRules();
  await attachRulesToPrompt(ENGINE, PROMPT, promptNext([]));

  expect(await readFile(`${CWD}/a.sh`, SUBAGENT)).toEqual([BASH, CLEAN_CODE]);
  expect(await readFile(`${CWD}/a.sh`)).toEqual([BASH]);
});

test("a file tool's result keeps the context it already had", async () => {
  await startWithCoreRules();
  const answered = toolNext({ ...READ_RESULT, context: ["mine"] });

  const result = await attachRulesToToolResult(ENGINE, readOf(`${CWD}/main.py`), answered);

  expect(result.context?.[0]).toBe("mine");
  expect(contextPaths(result.context)).toEqual([CLEAN_CODE]);
});

test("a glob is matched on the path relative to the working directory", async () => {
  await startWithCoreRules();

  expect(await readFile("/elsewhere/scripts/build.sh")).toEqual([BASH, CLEAN_CODE]);
  expect(await readFile(`${CWD}/scripts/build.sh`)).toEqual([SCRIPTS]);
});

const TASK = "Count the tests.";
const SPAWN = { prompt: TASK, fork: false, subagentType: "general-purpose" } as unknown as SpawnEvent;
const STARTED = { model: "haiku", agentId: SUBAGENT };

/** Stands for the chain beneath: records the prompt the subagent would start with and answers `result`. */
function spawnNext(handedPrompts: string[], result: object = STARTED): SpawnNext {
  const next = async (input: SpawnEvent) => {
    handedPrompts.push(input.prompt);
    return result;
  };
  return next as unknown as SpawnNext;
}

test("a new subagent starts with the rules without paths: after its task, and is not sent them again", async () => {
  await startWithCoreRules();
  const handedPrompts: string[] = [];

  await attachRulesToSubagentPrompt(ENGINE, SPAWN, spawnNext(handedPrompts));

  const prompt = handedPrompts[0] ?? "";
  expect(prompt.startsWith(`${TASK}\n\nContents of ${CLEAN_CODE} (rules from the core plugin):`)).toBe(true);
  expect(prompt.includes(BASH)).toBe(false);
  expect(prompt.includes(SCRIPTS)).toBe(false);
  expect(await readFile(`${CWD}/a.sh`, SUBAGENT)).toEqual([BASH]);
});

test("a fork, a resumed run and a workflow agent keep their prompt and mark nothing", async () => {
  await startWithCoreRules();
  const leftAlone = [
    { ...SPAWN, fork: true },
    { ...SPAWN, resume: { agentId: SUBAGENT } },
    { ...SPAWN, workflow: { runId: "wf_1", agentIndex: 1 } },
  ];

  for (const spawn of leftAlone) {
    const handedPrompts: string[] = [];
    await attachRulesToSubagentPrompt(ENGINE, spawn as unknown as SpawnEvent, spawnNext(handedPrompts));

    expect(handedPrompts).toEqual([TASK]);
    expect(sentIn(SUBAGENT).size).toBe(0);
  }
});

test("a spawn that answers no agentId marks nothing", async () => {
  await startWithCoreRules();

  for (const answer of [{ deny: "no" }, { model: "haiku" }]) {
    const result = await attachRulesToSubagentPrompt(ENGINE, SPAWN, spawnNext([], answer));

    expect(result).toEqual(answer);
    expect(sentIn(SUBAGENT).size).toBe(0);
  }
});

function compactNext(result: object): CompactNext {
  return (async () => result) as unknown as CompactNext;
}

function compactionBy(trigger: string, agentId?: string): CompactEvent {
  return { trigger, agentId, messages: [] } as unknown as CompactEvent;
}

const COMPACTED = compactNext({ messages: [] });
const ALL_RULES_OF_A_SCRIPT = [BASH, CLEAN_CODE];
const SCRIPT = `${CWD}/a.sh`;

test("a compaction makes the main loop take the rules again, a precompute or a skipped one does not", async () => {
  await startWithCoreRules();
  await readFile(SCRIPT);
  await readFile(SCRIPT, SUBAGENT);

  await resetAfterCompact(ENGINE, compactionBy("precompute"), COMPACTED);
  await resetAfterCompact(ENGINE, compactionBy("auto"), compactNext({ skip: "x" }));
  expect(await readFile(SCRIPT)).toEqual([]);

  await resetAfterCompact(ENGINE, compactionBy("manual"), COMPACTED);
  expect(await readFile(SCRIPT, SUBAGENT)).toEqual([]);
  expect(await readFile(SCRIPT)).toEqual(ALL_RULES_OF_A_SCRIPT);
});

test("a subagent's compaction makes only that subagent take the rules again", async () => {
  await startWithCoreRules();
  await readFile(SCRIPT);
  await readFile(SCRIPT, SUBAGENT);

  await resetAfterCompact(ENGINE, compactionBy("auto", SUBAGENT), COMPACTED);

  expect(await readFile(SCRIPT)).toEqual([]);
  expect(await readFile(SCRIPT, SUBAGENT)).toEqual(ALL_RULES_OF_A_SCRIPT);
});

function endOf(reason: string): EndEvent {
  return { reason, sessionId: "s1" } as unknown as EndEvent;
}

const END_NEXT = (async () => ({ sessionId: "s1" })) as unknown as EndNext;

test("a /clear or a resume makes every loop take the rules again, an exit does not", async () => {
  await startWithCoreRules();
  await readFile(SCRIPT);
  await readFile(SCRIPT, SUBAGENT);

  await resetOnSessionEnd(ENGINE, endOf("prompt_input_exit"), END_NEXT);
  expect(await readFile(SCRIPT)).toEqual([]);
  expect(await readFile(SCRIPT, SUBAGENT)).toEqual([]);

  for (const reason of ["clear", "resume"]) {
    await resetOnSessionEnd(ENGINE, endOf(reason), END_NEXT);
    expect(await readFile(SCRIPT)).toEqual(ALL_RULES_OF_A_SCRIPT);
    expect(await readFile(SCRIPT, SUBAGENT)).toEqual(ALL_RULES_OF_A_SCRIPT);
  }
});
