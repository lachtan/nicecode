/** The pane: pressing a skill unchecks it as disabled, pressing it again checks it back. */

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
