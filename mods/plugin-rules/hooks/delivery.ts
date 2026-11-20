/**
 * Delivery of rules to the model: which rules a loop still lacks, attaching them as context beside a prompt or
 * a file tool's result, and forgetting what a loop was sent once its context is gone. Each rule goes to a loop
 * at most once; a rule is marked sent only once its context is certain to reach the model.
 */

import type { Hook, MatchedHook } from "claude-code";
import { toMatchPath } from "./glob";
import { allRules, type Rule } from "./rules";

/** The key of the main conversation's loop; a subagent's loop is keyed by its `agentId`. */
const MAIN_LOOP = "main";
/** The `session.end` reasons after which the conversation goes on without what it was sent. */
const RESETTING_END_REASONS: readonly string[] = ["clear", "resume"];

/** The tools whose `file_path` a rule's `paths:` is matched against. */
export const FILE_TOOLS = { tool: ["Read", "Edit", "Write"] } as const;

/** Loop key → paths of the rules already sent in that loop. */
const sentRules = new Map<string, Set<string>>();

/**
 * The rules not yet in `sent`: every rule without `paths:`, and those with `paths:` whose glob matches
 * `matchPath`. Undefined `matchPath` means no file is in play, so only rules without `paths:` qualify.
 */
function selectPendingRules(rules: readonly Rule[], sent: ReadonlySet<string>, matchPath?: string): Rule[] {
  const pending: Rule[] = [];
  for (const rule of rules) {
    if (sent.has(rule.path)) continue;
    if (appliesTo(rule, matchPath)) pending.push(rule);
  }
  return pending;
}

/** Whether `rule` applies to the file at `matchPath`; a rule without `paths:` applies everywhere. */
function appliesTo(rule: Rule, matchPath: string | undefined): boolean {
  if (rule.pathPatterns.length === 0) return true;
  if (matchPath === undefined) return false;
  return rule.pathPatterns.some((pattern) => pattern.test(matchPath));
}

/** Paths of the rules already sent in `loop`; empty for a loop not seen yet. */
export function sentIn(loop: string): ReadonlySet<string> {
  return sentRules.get(loop) ?? new Set();
}

/** Records `rules` as sent in `loop`, so they are not attached there again. */
function markSent(loop: string, rules: readonly Rule[]): void {
  const sent = sentRules.get(loop) ?? new Set();
  for (const rule of rules) sent.add(rule.path);
  sentRules.set(loop, sent);
}

/** Forgets what `loop` was sent, so its rules are attached again on next use. */
function forgetLoop(loop: string): void {
  sentRules.delete(loop);
}

/** Forgets what every loop was sent. */
export function forgetAll(): void {
  sentRules.clear();
}

/** The rule as the context text the model sees, headed by its path and plugin. */
function formatRule(rule: Rule): string {
  return `Contents of ${rule.path} (rules from the ${rule.plugin} plugin):\n\n${rule.body}`;
}

/** The loop key for a hook event: the subagent's `agentId`, or the main loop when absent. */
function loopKey(agentId: string | undefined): string {
  return agentId ?? MAIN_LOOP;
}

/** A slash command may never reach the model, so its prompt carries no rules. */
export const attachRulesToPrompt: Hook<"prompt.submit"> = async (engine, event, next) => {
  if (event.command !== undefined) return next(event);
  const rules = selectPendingRules(allRules(), sentIn(MAIN_LOOP));
  if (rules.length === 0) return next(event);

  // The engine attaches only context added on the way down, not to the result.
  const context = [...(event.context ?? []), ...rules.map(formatRule)];
  const result = await next({ ...event, context });
  if (result.drop === undefined) markSent(MAIN_LOOP, rules);
  return result;
};

/** Attaches the rules matching the file a Read, Edit or Write touched, unless the call was denied. */
export const attachRulesToToolResult: MatchedHook<"tool.call", typeof FILE_TOOLS> = async (engine, event, next) => {
  const result = await next(event);
  if (result.deny !== undefined) return result;

  const matchPath = toMatchPath(event.file_path, await engine.session.cwd());
  const loop = loopKey(event.agentId);
  const rules = selectPendingRules(allRules(), sentIn(loop), matchPath);
  if (rules.length === 0) return result;

  markSent(loop, rules);
  return { ...result, context: [...(result.context ?? []), ...rules.map(formatRule)] };
};

/** A compaction drops what the loop was sent; a precompute or a skipped one changes nothing yet. */
export const resetAfterCompact: Hook<"session.compact"> = async (engine, event, next) => {
  const result = await next(event);
  if (event.trigger !== "precompute" && result.skip === undefined) forgetLoop(loopKey(event.agentId));
  return result;
};

/** After `/clear` or a resume the conversation lacks what it was sent, so every loop starts over. */
export const resetOnSessionEnd: Hook<"session.end"> = async (engine, event, next) => {
  const result = await next(event);
  if (RESETTING_END_REASONS.includes(event.reason)) forgetAll();
  return result;
};
