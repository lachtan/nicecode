# lab

Experimental work-in-progress skills and components. Things land here until
they prove out — then they move to `core` (or stay parked here indefinitely
if they don't).

## Skills

- `brainstorm` — turns an idea into an agreed design through questions before any code:
  classifies the request as spike / bounded / architectural so the ceremony scales, and
  leaves the approval gate to plan mode instead of rebuilding one.
- `craft-code` — one prompt for the whole coding task: a ladder that stops at the simplest
  rung that holds, interface and error rules while you write, and a red-flag pass before you
  call it done. Merges what `coding-discipline`, `strategic-design` and the ponytail ladder
  each said separately.
- `debug` — blocks any fix until the cause is named, and stops after three failed
  fixes to question the premise instead of trying a fourth.
- `final-review` — reviews a finished implementation against the plan it followed: writes a
  brief of the goal, the closed decisions and the behavior that had to stay frozen, then hands
  it with the diff to a subagent that sees nothing else. Counterpart to `plan-review`.
- `handoff` — renders the session's context as a copy-pasteable brief for a fresh session:
  only what the repo does not show (decisions, what was ruled out, constraints, what is left),
  no chronology and no code.
- `ops-review` — reviews an infrastructure change (Ansible, Terraform, container and
  deployment manifests, CI config, deploy scripts) against its own stated goal, with
  idempotency and cross-file reference integrity as the main axes.
- `plan-review` — judges whether an implementation plan can be executed without guessing:
  verifies the file paths and symbols it claims exist, and flags decisions deferred to
  implementation time. Completeness only, not design critique.
- `preview-simplify` — proposes concrete simplifications for recently changed code, without
  editing it. Overlaps the bundled `/simplify`, which applies the fixes instead.
- `quick-review` — single-pass read-only review of changed code against clean-code rules,
  security and correctness. Overlaps the bundled `/code-review`.
- `skillify` — capture the current session's repeatable process into a reusable skill.

`brainstorm` and `debug` are rewritten derivatives of
[obra/superpowers](https://github.com/obra/superpowers) v6.3.0 (MIT, Jesse Vincent);
each `SKILL.md` names its upstream directory in `origin`.

`craft-code` takes its ladder from [ponytail](https://github.com/DietrichGebert/ponytail)
(MIT, Dietrich Gebert) and its think-before-coding gate from
[andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills); both are
listed in its `origin`. Its design material is distilled from Ousterhout,
*A Philosophy of Software Design*, and Kanat-Alexander, *Code Simplicity*.
