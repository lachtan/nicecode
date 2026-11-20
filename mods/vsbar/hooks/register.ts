/** Pins a status line under the prompt in the VS Code extension, which draws no settings `statusLine`. */

import type { On } from "claude-code";
import { countTurnOutput, rememberEffort, resetOnClear, showOnMeasure, showOnSessionStart } from "./status";

export function register(on: On): void {
  on("session.start", showOnSessionStart);
  on("session.measure", showOnMeasure);
  on("turn.step", rememberEffort);
  on("turn.complete", countTurnOutput);
  on("session.end", resetOnClear);
}
