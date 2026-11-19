/**
 * Disables chosen skills of installed plugins: `/skill-toggle` opens a pane of checkboxes, and every
 * plugin then loads without the skills checked there.
 */

import type { On } from "claude-code";
import { COMMAND, openPane, PANE, registerCommand, renderPane } from "./pane";
import { disableSkills } from "./skills";

export function register(on: On): void {
  on("plugin.register", disableSkills);
  on("session.start", registerCommand);
  on("command.run", { command: COMMAND }, openPane);
  on("ui.render", { component: "Pane", requestId: PANE }, renderPane);
}
