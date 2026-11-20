/** Glob matching, one test per piece of syntax the matcher knows, and the path the globs are matched on. */

import { expect, test } from "claude-code/testing";
import { compileGlob, toMatchPath } from "../hooks/glob";

function matches(path: string, glob: string): boolean {
  const pattern = compileGlob(glob);
  if (pattern === undefined) throw new Error(`malformed glob: ${glob}`);
  return pattern.test(path);
}

test("**/ matches any number of folders, none included", () => {
  expect(matches("test.sh", "**/*.sh")).toBe(true);
  expect(matches("scripts/ci/test.sh", "**/*.sh")).toBe(true);
  expect(matches("/etc/profile.d/test.sh", "**/*.sh")).toBe(true);
  expect(matches("src/test/a.ts", "src/**/a.ts")).toBe(true);
  expect(matches("src/a.ts", "src/**/a.ts")).toBe(true);
  expect(matches("srcx/a.ts", "src/**/a.ts")).toBe(false);
});

test("** without a slash matches the rest of the path", () => {
  expect(matches("src/a.ts", "src/**")).toBe(true);
  expect(matches("src/deep/er/a.ts", "src/**")).toBe(true);
  expect(matches("lib/a.ts", "src/**")).toBe(false);
});

test("* and ? stay within one path segment", () => {
  expect(matches("README.md", "*.md")).toBe(true);
  expect(matches("docs/README.md", "*.md")).toBe(false);
  expect(matches("file1.txt", "file?.txt")).toBe(true);
  expect(matches("file10.txt", "file?.txt")).toBe(false);
  expect(matches("a/b", "a?b")).toBe(false);
  // Unlike in some glob libraries, a leading dot is no exception.
  expect(matches(".env", "*")).toBe(true);
});

test("a glob matches the whole path, not a part of it", () => {
  expect(matches("src/a.ts", "src/*.ts")).toBe(true);
  expect(matches("lib/src/a.ts", "src/*.ts")).toBe(false);
  expect(matches("src/a.tsx", "src/*.ts")).toBe(false);
});

test("braces match any one of their alternatives, nested ones too", () => {
  expect(matches("a/b.ps1", "**/*.{ps1,psm1}")).toBe(true);
  expect(matches("b.psm1", "**/*.{ps1,psm1}")).toBe(true);
  expect(matches("b.psd1", "**/*.{ps1,psm1}")).toBe(false);
  expect(matches("a.ts", "*.{ts,js{,x}}")).toBe(true);
  expect(matches("a.jsx", "*.{ts,js{,x}}")).toBe(true);
  expect(matches("a.tsx", "*.{ts,js{,x}}")).toBe(false);
});

test("a comma or a closing brace outside braces is an ordinary character", () => {
  expect(matches("a,b.txt", "a,b.txt")).toBe(true);
  expect(matches("a.txt", "a,b.txt")).toBe(false);
  expect(matches("a}.txt", "a}.txt")).toBe(true);
});

test("every other character is literal, the ones a regular expression reads specially too", () => {
  expect(matches("scripts/test_sh", "**/*.sh")).toBe(false);
  expect(matches("c++/main.cpp", "c++/*.cpp")).toBe(true);
  expect(matches("cc/main.cpp", "c++/*.cpp")).toBe(false);
  expect(matches("routes/[id].ts", "routes/[id].ts")).toBe(true);
  expect(matches("routes/i.ts", "routes/[id].ts")).toBe(false);
  expect(matches("notes/a(b).md", "notes/a(b).md")).toBe(true);
  expect(matches("a^b$c|d", "a^b$c|d")).toBe(true);
});

test("a glob with an unclosed brace is malformed", () => {
  expect(compileGlob("**/*.{ps1,psm1")).toBeUndefined();
  expect(compileGlob("{a,{b,c}")).toBeUndefined();
});

test("a file under the working directory is matched relative to it", () => {
  expect(toMatchPath("/home/me/proj/src/a.sh", "/home/me/proj")).toBe("src/a.sh");
  expect(toMatchPath("/home/me/proj/src/a.sh", "/home/me/proj/")).toBe("src/a.sh");
});

test("a file outside the working directory keeps its absolute path", () => {
  expect(toMatchPath("/etc/a.sh", "/home/me/proj")).toBe("/etc/a.sh");
  expect(toMatchPath("/home/me/project2/a.sh", "/home/me/proj")).toBe("/home/me/project2/a.sh");
});

test("a Windows path is matched with forward slashes", () => {
  const matchPath = toMatchPath("C:\\proj\\src\\a.ps1", "C:\\proj");
  expect(matchPath).toBe("src/a.ps1");
  expect(matches(matchPath, "**/*.{ps1,psm1}")).toBe(true);
  expect(toMatchPath("D:\\other\\a.ps1", "C:\\proj")).toBe("D:/other/a.ps1");
});
