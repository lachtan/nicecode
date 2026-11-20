/**
 * The rules each registered plugin ships in its `rules/` folder: reading them when the plugin registers,
 * parsing a rule file's frontmatter, and the registry the delivery reads.
 */

import type { EngineInterface, Hook } from "claude-code";
import { compileGlob } from "./glob";

export interface Rule {
  plugin: string;
  /** Absolute path of the rule file. */
  path: string;
  /** The compiled globs of its `paths:`; empty for a rule that applies to every file. */
  pathPatterns: readonly RegExp[];
  /** The file's text without its frontmatter. */
  body: string;
}

const FRONTMATTER_FENCE = "---";
const RULES_FOLDER = "rules";
const RULE_EXTENSION = ".md";

/** Plugin name → its rules; a plugin registering again replaces its own. */
const pluginRules = new Map<string, readonly Rule[]>();

export function allRules(): Rule[] {
  const rules: Rule[] = [];
  for (const pluginRuleList of pluginRules.values()) rules.push(...pluginRuleList);
  return rules;
}

/**
 * Reads a rule file's text. A file without `paths:` is a rule for every file. Undefined for a rule whose
 * `paths:` is there but is not a block list of valid globs (an inline list, a string, no item, an unclosed
 * `{`): it is skipped rather than applied to the wrong files.
 */
export function parseRule(plugin: string, path: string, text: string): Rule | undefined {
  const lines = text.replaceAll("\r\n", "\n").split("\n");
  const closingFence = lines[0] === FRONTMATTER_FENCE ? lines.indexOf(FRONTMATTER_FENCE, 1) : -1;
  if (closingFence === -1) return { plugin, path, pathPatterns: [], body: lines.join("\n") };

  const globs = parsePaths(lines.slice(1, closingFence));
  if (globs === undefined) return undefined;
  const pathPatterns = compileGlobs(globs);
  if (pathPatterns === undefined) return undefined;
  const body = lines
    .slice(closingFence + 1)
    .join("\n")
    .replace(/^\n+/, "");
  return { plugin, path, pathPatterns, body };
}

/**
 * The globs listed under `paths:`, none when the key is absent; undefined when no block list follows it
 * (an inline list, a string, nothing).
 */
function parsePaths(frontmatter: readonly string[]): string[] | undefined {
  const keyIndex = frontmatter.findIndex((line) => /^paths:/.test(line));
  if (keyIndex === -1) return [];

  const globs: string[] = [];
  for (const line of frontmatter.slice(keyIndex + 1)) {
    const item = /^\s*-\s+(.*)$/.exec(line);
    if (item === null) break;
    globs.push(unquote((item[1] ?? "").trim()));
  }
  if (globs.length === 0) return undefined;
  return globs;
}

/** Undefined when any of the globs is malformed. */
function compileGlobs(globs: readonly string[]): RegExp[] | undefined {
  const patterns: RegExp[] = [];
  for (const glob of globs) {
    const pattern = compileGlob(glob);
    if (pattern === undefined) return undefined;
    patterns.push(pattern);
  }
  return patterns;
}

function unquote(value: string): string {
  const isQuoted = /^(["']).*\1$/.test(value);
  return isQuoted ? value.slice(1, -1) : value;
}

/**
 * Takes in the rules of every plugin that loads. Reading happens after `next`, so a refused plugin adds
 * none. A rules folder that cannot be read makes the hook throw, and the engine then skips the hook and
 * logs why: the plugin loads without rules and nothing is blocked.
 */
export const registerPluginRules: Hook<"plugin.register"> = async (engine, event, next) => {
  const result = await next(event);
  if (result.refuse !== undefined) return result;
  if (!isAbsolutePath(event.root)) return result;
  pluginRules.set(event.name, await readPluginRules(engine, event.name, event.root));
  return result;
};

async function readPluginRules(engine: EngineInterface, plugin: string, root: string): Promise<Rule[]> {
  const folder = `${root}/${RULES_FOLDER}`;
  if (!(await engine.fs.exists(folder))) return [];

  const fileNames: string[] = [];
  for (const entry of await engine.fs.list(folder)) {
    if (entry.kind === "file" && entry.name.endsWith(RULE_EXTENSION)) fileNames.push(entry.name);
  }
  // The folder is listed in no promised order; sorted, the rules reach the model in the same order every time.
  fileNames.sort();

  const rules: Rule[] = [];
  for (const fileName of fileNames) {
    const path = `${folder}/${fileName}`;
    const rule = parseRule(plugin, path, await engine.fs.read(path));
    if (rule === undefined) {
      engine.ui.log(`skipped rule ${path}: its paths: is not a block list of valid globs`, { to: "debug" });
      continue;
    }
    rules.push(rule);
  }
  return rules;
}

/** A bundled plugin's root is `builtin`, not a folder. */
function isAbsolutePath(path: string): boolean {
  return path.startsWith("/") || /^[A-Za-z]:[\\/]/.test(path) || path.startsWith("\\\\");
}
