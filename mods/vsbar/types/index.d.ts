/** Effort level of the main loop's last request; null before the first one or on a model without effort. */
export type VsbarEffort = string | null;

declare module "claude-code" {
  interface PluginState {
    vsbar: {
      /** Output tokens of the main loop's turns this session, subagents excluded. */
      outputTokens: number;
      effort: VsbarEffort;
    };
  }
}
