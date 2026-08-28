# lab

Experimental work-in-progress skills and components. Things land here until
they prove out — then they move to `core` (or stay parked here indefinitely
if they don't).

## Skills

- `brainstorm` — turns an idea into an agreed design through questions before any code:
  classifies the request as spike / bounded / architectural so the ceremony scales, and
  leaves the approval gate to plan mode instead of rebuilding one.
- `debug` — blocks any fix until the cause is named, and stops after three failed
  fixes to question the premise instead of trying a fourth.
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
- `strategic-design` — design rules for keeping code cheap to change: interface depth,
  complexity as an accumulating cost, when to design twice.

`brainstorm` and `debug` are rewritten derivatives of
[obra/superpowers](https://github.com/obra/superpowers) v6.3.0 (MIT, Jesse Vincent);
each `SKILL.md` names its upstream directory in `origin`.
