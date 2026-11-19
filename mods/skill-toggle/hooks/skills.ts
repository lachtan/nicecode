/**
 * Disabling of plugin skills, and what the mod keeps for it in its store across sessions: the skills
 * checked as disabled, and every skill each plugin ships, which the pane lists because a disabled
 * skill no longer loads. Each plugin's skills sit under a key of their own, so plugins registering
 * at the same time never overwrite each other.
 */

import type { EngineInterface, Hook } from "claude-code";

/** Store key prefix of one plugin's skills: `skills:<plugin>`. */
const SKILLS_KEY_PREFIX = "skills:";
/** Store key of the disabled skills, each as `<plugin>:<skill>`. */
const DISABLED_KEY = "disabled";

/** Plugin name → every skill it ships, as `<plugin>:<skill>`. */
export type PluginSkills = Record<string, readonly string[]>;

/** The store can be edited by hand, so anything that is not a list of strings reads as an empty list. */
function asStringList(value: unknown): string[] {
  if (!Array.isArray(value)) return [];
  return value.filter((item): item is string => typeof item === "string");
}

export async function loadSkills(engine: EngineInterface): Promise<PluginSkills> {
  const pluginSkills: PluginSkills = {};
  for (const key of await engine.store.keys()) {
    if (!key.startsWith(SKILLS_KEY_PREFIX)) continue;
    const plugin = key.slice(SKILLS_KEY_PREFIX.length);
    pluginSkills[plugin] = asStringList(await engine.store.get(key));
  }
  return pluginSkills;
}

async function rememberSkills(engine: EngineInterface, plugin: string, skills: readonly string[]): Promise<void> {
  await engine.store.set(SKILLS_KEY_PREFIX + plugin, skills);
}

export async function loadDisabled(engine: EngineInterface): Promise<string[]> {
  return asStringList(await engine.store.get(DISABLED_KEY));
}

export async function toggleDisabled(engine: EngineInterface, skill: string): Promise<void> {
  const disabled = await loadDisabled(engine);
  const toggled = disabled.includes(skill) ? disabled.filter((name) => name !== skill) : [...disabled, skill];
  await engine.store.set(DISABLED_KEY, toggled);
}

/** Lets each plugin load without its disabled skills, and remembers all its skills for the pane. */
export const disableSkills: Hook<"plugin.register"> = async (engine, event, next) => {
  await rememberSkills(engine, event.name, event.provides.skills);
  const disabled = await loadDisabled(engine);
  const skills = event.provides.skills.filter((skill) => !disabled.includes(skill));
  return next({ ...event, provides: { ...event.provides, skills } });
};
