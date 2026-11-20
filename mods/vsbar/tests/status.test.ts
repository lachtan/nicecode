/** The vsbar line: its format, the output tokens it counts, and where it is shown. */

import type { EngineInterface, RenderSurface } from "claude-code";
import { expect, test } from "claude-code/testing";
import { countTurnOutput, formatModelName, formatStatusLine, formatTokenCount, showOnMeasure } from "../hooks/status";

type TurnEvent = Parameters<typeof countTurnOutput>[1];
type TurnNext = Parameters<typeof countTurnOutput>[2];
type MeasureEvent = Parameters<typeof showOnMeasure>[1];
type MeasureNext = Parameters<typeof showOnMeasure>[2];

const CONTEXT = { percent: 13, tokens: 134_200, window: 1_000_000 };

interface FakeEngine {
  engine: EngineInterface;
  state: Map<string, unknown>;
  /** Every `ui.status` call's text, `undefined` for a clear. */
  statusTexts: (string | undefined)[];
  /** Every `process.run` argv. */
  commands: string[][];
}

/** An engine drawing on `surfaces`, in a repository on `master`, on host `devbox`. */
function fakeEngine(surfaces: RenderSurface[]): FakeEngine {
  const state = new Map<string, unknown>();
  const statusTexts: (string | undefined)[] = [];
  const commands: string[][] = [];
  const engine = {
    env: { get: async () => undefined },
    process: {
      run: async (argv: string[]) => {
        commands.push(argv);
        const stdout = argv[0] === "hostname" ? "DEVBOX\n" : "master\n";
        return { exitCode: 0, stdout, stderr: "" };
      },
    },
    session: {
      surfaces: async () => surfaces,
      model: async () => "claude-opus-5-5",
      usage: async () => ({ context: CONTEXT }),
    },
    state: {
      get: async (ref: { key: string }) => ({ value: state.get(ref.key), version: 0 }),
      set: async (ref: { key: string }, value: unknown) => {
        state.set(ref.key, value);
        return { isSet: true, version: 0 };
      },
    },
    ui: { status: (text: string | undefined) => void statusTexts.push(text) },
  } as unknown as EngineInterface;
  return { engine, state, statusTexts, commands };
}

const TURN_NEXT = (async () => ({ text: "" })) as unknown as TurnNext;
const MEASURE_NEXT = (async () => ({ changed: ["context"] })) as unknown as MeasureNext;

function finishedTurn(outputTokens: number, agentId?: string): TurnEvent {
  return { usage: { output_tokens: outputTokens }, agentId } as unknown as TurnEvent;
}

test("the line has every part", () => {
  const line = formatStatusLine({
    host: "debian-dev",
    branch: "master",
    modelId: "claude-opus-5-5",
    effort: "high",
    context: CONTEXT,
    outputTokens: 11_600,
  });

  expect(line).toBe("🖥️ debian-dev | 🌿 master | 💡 Opus 5.5 / high / 1M | ↓ 13% / 134k | ↑ 11k");
});

test("a line outside git, without effort and before the first response leaves those parts out", () => {
  const line = formatStatusLine({
    host: "devbox",
    branch: "",
    modelId: "claude-haiku-5-5",
    effort: null,
    context: { window: 200_000 },
    outputTokens: 0,
  });

  expect(line).toBe("🖥️ devbox | 💡 Haiku 5.5 / 200k | ↓ 0% / 0 | ↑ 0");
});

test("token counts truncate thousands and keep one decimal of millions", () => {
  expect(formatTokenCount(950)).toBe("950");
  expect(formatTokenCount(11_999)).toBe("11k");
  expect(formatTokenCount(1_000_000)).toBe("1M");
  expect(formatTokenCount(1_500_000)).toBe("1.5M");
});

test("a model id that is not claude-<family>-<major>-<minor> is shown as it is", () => {
  expect(formatModelName("claude-sonnet-5-5")).toBe("Sonnet 5.5");
  expect(formatModelName("my-gateway-model")).toBe("my-gateway-model");
});

test("only the main loop's output tokens count", async () => {
  const { engine, state } = fakeEngine(["vscode"]);

  await countTurnOutput(engine, finishedTurn(1_000), TURN_NEXT);
  await countTurnOutput(engine, finishedTurn(5_000, "agent-1"), TURN_NEXT);
  await countTurnOutput(engine, finishedTurn(500), TURN_NEXT);

  expect(state.get("outputTokens")).toBe(1_500);
});

test("in VS Code the line is shown", async () => {
  const { engine, statusTexts } = fakeEngine(["vscode"]);

  await showOnMeasure(engine, {} as MeasureEvent, MEASURE_NEXT);

  expect(statusTexts).toEqual(["🖥️ devbox | 🌿 master | 💡 Opus 5.5 / 1M | ↓ 13% / 134k | ↑ 0"]);
});

test("in a terminal the line is cleared and no command runs", async () => {
  const { engine, statusTexts, commands } = fakeEngine(["terminal"]);

  await showOnMeasure(engine, {} as MeasureEvent, MEASURE_NEXT);

  expect(statusTexts).toEqual([undefined]);
  expect(commands).toEqual([]);
});
