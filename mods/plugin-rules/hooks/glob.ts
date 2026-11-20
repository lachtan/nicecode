/**
 * Matching of a file path against the globs in a rule's `paths:`. The plugin API has no glob matcher, so this
 * covers the syntax rules use: `**` + `/`, `**`, `*`, `?` and `{a,b}`. Every other character is literal.
 */

/**
 * The pattern a path with `/` as its separator (toMatchPath) is tested against; undefined for a glob whose
 * `{` is never closed.
 */
export function compileGlob(glob: string): RegExp | undefined {
  let pattern = "";
  let openBraces = 0;
  let index = 0;
  while (index < glob.length) {
    if (glob.startsWith("**/", index)) {
      pattern += "(?:.*/)?";
      index += 3;
      continue;
    }

    if (glob.startsWith("**", index)) {
      pattern += ".*";
      index += 2;
      continue;
    }

    const char = glob.charAt(index);
    if (char === "*") {
      pattern += "[^/]*";
    } else if (char === "?") {
      pattern += "[^/]";
    } else if (char === "{") {
      pattern += "(?:";
      openBraces++;
    } else if (char === "}" && openBraces > 0) {
      pattern += ")";
      openBraces--;
    } else if (char === "," && openBraces > 0) {
      pattern += "|";
    } else {
      pattern += escapeRegExp(char);
    }
    index++;
  }
  if (openBraces > 0) return undefined;
  return new RegExp(`^${pattern}$`);
}

/**
 * The path a rule's globs are matched against: relative to `cwd` when the file is under it, else as given,
 * with `/` as the separator either way so that Windows paths match too.
 */
export function toMatchPath(filePath: string, cwd: string): string {
  const path = toForwardSlashes(filePath);
  const rootPrefix = `${toForwardSlashes(cwd).replace(/\/+$/, "")}/`;
  if (!path.startsWith(rootPrefix)) return path;
  return path.slice(rootPrefix.length);
}

function toForwardSlashes(path: string): string {
  return path.replaceAll("\\", "/");
}

function escapeRegExp(char: string): string {
  return char.replace(/[.*+?^${}()|[\]\\/]/g, "\\$&");
}
