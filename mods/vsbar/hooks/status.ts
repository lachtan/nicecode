/**
 * The line `🖥️ host | 🌿 branch | 💡 model / effort / window | ↓ used % / used tokens | ↑ output tokens`, pinned
 * with `ui.status`. It is shown only in the VS Code extension: a terminal already draws the settings
 * `statusLine`, and `ui.status` takes plain text, so the line has no colors (ANSI codes show up escaped).
 */

import type { EngineInterface, Hook, SessionContextUsage, StreamHook } from "claude-code";

const HOST_ICON = "🖥️";
const BRANCH_ICON = "🌿";
const MODEL_ICON = "💡";
const CONTEXT_ICON = "↓";
const OUTPUT_ICON = "↑";

const OUTPUT_TOKENS = { plugin: "vsbar", key: "outputTokens" } as const;
const EFFORT = { plugin: "vsbar", key: "effort" } as const;

export interface StatusParts {
  host: string;
  /** Empty outside a git repository or on a detached HEAD. */
  branch: string;
  modelId: string;
  effort: string | null;
  context: SessionContextUsage;
  outputTokens: number;
}

/** `1.5M`, `134k` (thousands truncated, not rounded), `950`. */
export function formatTokenCount(value: number): string {
  if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(1).replace(/\.0$/, "")}M`;
  if (value >= 1_000) return `${Math.floor(value / 1_000)}k`;
  return String(value);
}

/** `claude-opus-5-5` → `Opus 5.5`; the session API gives the model id, not its display name. */
export function formatModelName(modelId: string): string {
  const match = /^claude-([a-z]+)-(\d+)-(\d+)/.exec(modelId);
  if (!match) return modelId;
  const [, family = "", major, minor] = match;
  return `${family.charAt(0).toUpperCase()}${family.slice(1)} ${major}.${minor}`;
}

export function formatStatusLine(parts: StatusParts): string {
  const { percent, tokens, window } = parts.context;
  const segments = [`${HOST_ICON} ${parts.host}`];
  if (parts.branch) segments.push(`${BRANCH_ICON} ${parts.branch}`);
  const model = [formatModelName(parts.modelId), parts.effort, formatTokenCount(window)].filter(Boolean);
  segments.push(`${MODEL_ICON} ${model.join(" / ")}`);
  segments.push(`${CONTEXT_ICON} ${percent ?? 0}% / ${formatTokenCount(tokens ?? 0)}`);
  segments.push(`${OUTPUT_ICON} ${formatTokenCount(parts.outputTokens)}`);
  return segments.join(" | ");
}

async function readHostName(engine: EngineInterface): Promise<string> {
  const windowsName = await engine.env.get("COMPUTERNAME");
  if (windowsName) return windowsName.toLowerCase();
  const { exitCode, stdout } = await engine.process.run(["hostname"]);
  return exitCode === 0 ? stdout.trim().toLowerCase() : "?";
}

async function readBranch(engine: EngineInterface): Promise<string> {
  const { exitCode, stdout } = await engine.process.run(["git", "branch", "--show-current"]);
  return exitCode === 0 ? stdout.trim() : "";
}

/** Read once per module load; the host does not change during a session. */
let hostName = "";

async function showStatus(engine: EngineInterface): Promise<void> {
  const surfaces = await engine.session.surfaces();
  if (!surfaces.includes("vscode")) {
    engine.ui.status(undefined);
    return;
  }

  if (hostName === "") hostName = await readHostName(engine);
  const [branch, modelId, usage, outputTokens, effort] = await Promise.all([
    readBranch(engine),
    engine.session.model(),
    engine.session.usage(),
    engine.state.get(OUTPUT_TOKENS),
    engine.state.get(EFFORT),
  ]);

  engine.ui.status(
    formatStatusLine({
      host: hostName,
      branch,
      modelId,
      effort: effort.value ?? null,
      context: usage.context,
      outputTokens: outputTokens.value ?? 0,
    }),
  );
}

export const showOnSessionStart: Hook<"session.start"> = async (engine, event, next) => {
  const result = await next(event);
  await showStatus(engine);
  return result;
};

/** Fires when the context fill, a rate limit or the cost changes, i.e. after each model response. */
export const showOnMeasure: Hook<"session.measure"> = async (engine, event, next) => {
  await showStatus(engine);
  return next(event);
};

/** The session API has no effort getter; each main-loop request states the level it is sent at. */
export const rememberEffort: StreamHook<"turn.step"> = async function* (engine, event, next) {
  if (event.agentId === undefined) {
    // A number is an internal-build budget, not a level worth showing.
    const level = typeof event.effort === "string" ? event.effort : null;
    await engine.state.set(EFFORT, level);
  }
  return yield* next(event);
};

/** Subagents run their own turns; only the main loop's count, as in the terminal statusline. */
export const countTurnOutput: Hook<"turn.complete"> = async (engine, event, next) => {
  const turnOutput = event.usage?.output_tokens ?? 0;
  if (event.agentId === undefined && turnOutput > 0) {
    const { value = 0 } = await engine.state.get(OUTPUT_TOKENS);
    await engine.state.set(OUTPUT_TOKENS, value + turnOutput);
  }
  await showStatus(engine);
  return next(event);
};

export const resetOnClear: Hook<"session.end"> = async (engine, event, next) => {
  if (event.reason === "clear") await engine.state.set(OUTPUT_TOKENS, 0);
  return next(event);
};
