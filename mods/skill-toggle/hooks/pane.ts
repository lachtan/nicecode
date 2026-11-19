/** The `/skill-toggle` command and its pane: a checkbox for each plugin skill, checked = enabled. */

import type { EngineInterface, Hook, RenderElement, RenderInput } from "claude-code";
import { loadDisabled, loadSkills, toggleDisabled } from "./skills";

export const COMMAND = "skill-toggle";
export const PANE = "skill-toggle";

export const registerCommand: Hook<"session.start"> = async (engine, event, next) => {
  await engine.command.register({ name: COMMAND, description: "Choose plugin skills to disable" });
  return next(event);
};

export const openPane: Hook<"command.run"> = async (engine) => {
  await engine.ui.open({ id: PANE, title: "Plugin skills", focus: true });
  return { text: "Plugin skills pane opened." };
};

export async function renderPane(engine: EngineInterface, event: RenderInput<"Pane">) {
  const { Box, Text, Button } = engine.ui.resolve(event);
  const pluginSkills = await loadSkills(engine);
  const disabled = await loadDisabled(engine);

  const rows: RenderElement[] = [];
  for (const [plugin, skills] of Object.entries(pluginSkills)) {
    if (skills.length === 0) continue;
    rows.push(Text({ bold: true, children: plugin }));
    for (const skill of skills) {
      const isDisabled = disabled.includes(skill);
      const mark = isDisabled ? "[ ]" : "[x]";
      const name = skill.replace(`${plugin}:`, "");
      rows.push(Button({ key: skill, plain: true, label: `${mark} ${name}`, onPress: () => toggleSkill(engine, skill) }));
    }
  }
  rows.push(Button({ label: "Apply (reload plugins)", onPress: () => reloadPlugins(engine) }));

  return Box({ flexDirection: "column", children: rows });
}

/** Checks or unchecks the skill and redraws the pane. */
async function toggleSkill(engine: EngineInterface, skill: string): Promise<void> {
  await toggleDisabled(engine, skill);
  engine.ui.invalidate("ui.render");
}

/**
 * Skills are read when plugins load, so a change takes effect only after a reload. Not awaited: the reload
 * reloads this mod too, while this handler still runs.
 */
function reloadPlugins(engine: EngineInterface): void {
  void engine.command.run({ command: "reload-plugins" }).catch((error) => showReloadError(engine, error));
}

function showReloadError(engine: EngineInterface, error: unknown): void {
  engine.ui.toast(`Reloading plugins failed: ${String(error)}`);
}
