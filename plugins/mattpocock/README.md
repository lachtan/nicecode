# mattpocock

A hand-picked subset of [mattpocock/skills](https://github.com/mattpocock/skills), copied into
this repo instead of pulled from GitHub, so an upstream update cannot bring in behaviour or hooks
nobody reviewed. The copy is pinned to upstream commit
[`4ae2317`](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d)
(release 1.3.2); each skill's `origin` points at the file it came from. MIT, see [LICENSE](LICENSE).

## Skills

- `grill-me` — relentless interview that sharpens a plan or design; runs only when you type
  `/grill-me`. Upstream `grill-me` just calls the `grilling` skill, so this copy carries the
  `grilling` text directly.
- `research` — background agent that researches a question against primary sources and saves
  the findings as a Markdown file in the repo.

To take over another skill, copy its `SKILL.md` body from the same commit unchanged, add this
repo's frontmatter (see `CLAUDE.md`) and list it here.
