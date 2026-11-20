/**
 * Delivers the `rules/*.md` of installed plugins to the model, which Claude Code does not load from plugins
 * itself: each rule goes along once per loop, as a reminder beside a prompt or a file tool's result, or at the
 * end of the prompt a subagent starts with.
 */

import type { On } from "claude-code";
import {
  attachRulesToPrompt,
  attachRulesToSubagentPrompt,
  attachRulesToToolResult,
  FILE_TOOLS,
  resetAfterCompact,
  resetOnSessionEnd,
} from "./delivery";
import { registerPluginRules } from "./rules";

export function register(on: On): void {
  on("plugin.register", registerPluginRules);
  on("prompt.submit", attachRulesToPrompt);
  on("agent.spawn", attachRulesToSubagentPrompt);
  on("tool.call", FILE_TOOLS, attachRulesToToolResult);
  on("session.compact", resetAfterCompact);
  on("session.end", resetOnSessionEnd);
}
