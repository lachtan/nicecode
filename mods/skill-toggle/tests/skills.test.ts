/** The plugin.register hook: a plugin loads without its disabled skills, and all its skills are remembered. */

import type { EngineInterface, PluginRegisterInput, PluginRegisterResult } from "claude-code";
import { expect, test } from "claude-code/testing";
import { disableSkills } from "../hooks/skills";

type RegisterNext = Parameters<typeof disableSkills>[2];

const ALL_SKILLS = ["core:commit", "core:plan-loop"];

/** Only `name` and `provides.skills` matter to the hook. */
const CORE_PLUGIN = { name: "core", provides: { skills: ALL_SKILLS } } as unknown as PluginRegisterInput;

/**
 * The kit raises no `plugin.register` and its `$` is the test's, not a plugin's, so the hook is called
 * directly with an engine that has only the store it uses.
 */
function engineWithStore(entries: Map<string, unknown>): EngineInterface {
  const store = {
    get: async (key: string) => entries.get(key),
    set: async (key: string, value: unknown) => void entries.set(key, value),
    keys: async () => [...entries.keys()],
  };
  return { store } as unknown as EngineInterface;
}

/** Stands for the chain beneath the hook: records which skills it was handed and allows the plugin. */
function recordingNext(passedSkills: string[][]): RegisterNext {
  const next = async (input: PluginRegisterInput): Promise<PluginRegisterResult> => {
    passedSkills.push([...input.provides.skills]);
    return { allow: true };
  };
  return next as unknown as RegisterNext;
}

test("a disabled skill is kept out, the plugin's skills are remembered", async () => {
  const entries = new Map<string, unknown>([["disabled", ["core:commit"]]]);
  const passedSkills: string[][] = [];

  await disableSkills(engineWithStore(entries), CORE_PLUGIN, recordingNext(passedSkills));

  expect(passedSkills).toEqual([["core:plan-loop"]]);
  expect(entries.get("skills:core")).toEqual(ALL_SKILLS);
});

test("a hand-edited disabled value that is not a list disables nothing", async () => {
  const entries = new Map<string, unknown>([["disabled", "core:commit"]]);
  const passedSkills: string[][] = [];

  await disableSkills(engineWithStore(entries), CORE_PLUGIN, recordingNext(passedSkills));

  expect(passedSkills).toEqual([ALL_SKILLS]);
});
