/**
 * The pane: pressing a skill unchecks it as disabled and pressing it again checks it back, without touching
 * the other skills; Apply reloads the plugins and shows a toast when that fails.
 */

import { expect, mock, test } from "claude-code/testing";

const PANE = {
  plugin: "skill-toggle",
  component: "Pane",
  requestId: "skill-toggle",
  props: {
    title: "Plugin skills",
    isFocused: true,
    bodyColumns: 40,
    placement: "dock",
    scroll: { offset: 0, bodyRows: 20 },
    view: {},
  },
} as const;

const APPLY_KEY = "apply";
const RELOAD_COMMAND = "reload-plugins";

test("pressing a skill unchecks it as disabled, pressing it again checks it", async (engine, on) => {
  mock.store(on, { "skills:core": ["core:commit"] });

  for (const surface of ["terminal", "desktop"] as const) {
    const ui = await engine.ui.mount({ ...PANE, surface });
    expect((await ui.find({ key: "core:commit" }))?.text).toBe("[x] commit");
    await ui.press({ key: "core:commit" });
    expect((await ui.find({ key: "core:commit" }))?.text).toBe("[ ] commit");
    await ui.press({ key: "core:commit" });
    expect((await ui.find({ key: "core:commit" }))?.text).toBe("[x] commit");
    await ui.unmount();
  }
});

test("pressing a skill leaves the other plugins' disabled skills disabled", async (engine, on) => {
  mock.store(on, {
    "skills:core": ["core:commit", "core:plan-loop"],
    "skills:lab": ["lab:debug"],
    disabled: ["lab:debug"],
  });

  const ui = await engine.ui.mount({ ...PANE, surface: "desktop" });
  await ui.press({ key: "core:commit" });

  expect((await ui.find({ key: "core:commit" }))?.text).toBe("[ ] commit");
  expect((await ui.find({ key: "lab:debug" }))?.text).toBe("[ ] debug");
  await ui.unmount();
});

test("pressing Apply reloads the plugins", async (engine, on) => {
  mock.store(on, { "skills:core": ["core:commit"] });
  const clock = mock.clock(on);
  const commandsRun: string[] = [];
  on("command.run", { command: RELOAD_COMMAND }, (_hookEngine, event) => {
    commandsRun.push(event.command);
    return { text: "" };
  });

  const ui = await engine.ui.mount({ ...PANE, surface: "desktop" });
  await ui.press({ key: APPLY_KEY });
  await clock.settle();

  expect(commandsRun).toEqual([RELOAD_COMMAND]);
  await ui.unmount();
});

test("a failed reload shows a toast", async (engine, on) => {
  mock.store(on, { "skills:core": ["core:commit"] });
  const clock = mock.clock(on);
  const toasts: string[] = [];
  on("command.run", { command: RELOAD_COMMAND }, () => {
    throw new Error("reload broke");
  });
  on("ui.toast", (_hookEngine, event) => {
    toasts.push(event.text);
    return { value: undefined };
  });

  const ui = await engine.ui.mount({ ...PANE, surface: "desktop" });
  await ui.press({ key: APPLY_KEY });
  await clock.settle();

  expect(toasts).toEqual([expect.stringContaining("Reloading plugins failed:")]);
  await ui.unmount();
});
