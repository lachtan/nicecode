# CLAUDE.md template

## Behavior

- Conduct all communication and all planning with the user in Czech.
- When given a direct, unambiguous task (e.g., "save this plan"), execute it immediately without exploring the codebase first.

## Engineering Principles

1. **Don't assume. Don't hide confusion. Surface tradeoffs.**
   - If an instruction is ambiguous, stop and ask for clarification before acting.
   - Do not make assumptions about user intent, data formats, or scope.
   - Explicitly surface tradeoffs when multiple implementation paths exist.

2. **Minimum code that solves the problem. Nothing speculative.**
   - Implement only the logic requested. Avoid premature abstraction, design patterns (like Strategy or Factory), or future-proofing that is not explicitly required.
   - If a simple solution exists, prefer it over complex, generalized ones.

3. **Touch only what you must. Clean up only your own mess.**
   - Changes must be surgical. Do not reformat files, update type hints, or rewrite existing code unless it is strictly required to fulfill the specific task.
   - If your changes introduce orphans (e.g., unused imports, dead variables), clean them up. Otherwise, leave existing code untouched.

4. **Define success criteria. Loop until verified.**
   - Before coding, define clear success criteria or a verification plan.
   - Iterate and self-correct until the verification tests pass. Ensure each step of the implementation is verified against the goal.

## Claude Code

- When editing Claude Code prompt files (skills, rules, commands, subagents, hooks), follow the format from the
  [official docs](https://code.claude.com/docs), not neighboring files — they may be wrong.
- A skill's `description` is what triggers the skill — state concisely *when* to invoke it (the situations and keywords),
  key use case first, not prose about what it contains.
- Keep these files concise and actionable, and write them in English unless the user says otherwise.

## Git

- Do not include "Co-Authored-By: ..." in commit messages unless explicitly asked.
