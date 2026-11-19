---
name: brainstorm
description: >-
  Use when an idea, feature or change needs designing before any code — turns it into an
  agreed design through questions, alternatives and a scoped recommendation. Triggers on
  "brainstorm", "let's design this", "how should we build this". Not for executing an
  approved plan or fixing a bug.
disable-model-invocation: true
user-invocable: true
origin: https://github.com/obra/superpowers/tree/v6.3.0/skills/brainstorming
managed-by: https://github.com/lachtan/nicecode
version: "6.3.0"
last-change: "2026-08-28 09:28:03"
---

# Brainstorm

Turn an idea into a design the user has agreed to. The deliverable is the design, never
code.

## The gate belongs to the harness

If plan mode is active, the plan file and `ExitPlanMode` **are** the approval gate: write
the design there and let the user approve it. Do not build a second gate, a `docs/specs/`
ritual or an approval question of your own. Outside plan mode, present the design in chat
and stop until you hear yes.

## Scale the ceremony, never the agreement

Classify first and say the classification out loud, so the user can override it:

- **Spike** — a feasibility question ("can we…", "is it possible…") whose output is an
  answer, not code you keep. Say what you'll try in two sentences, get a nod, find out as
  cheaply as correctness allows, report a recommendation. Anything you built is labeled
  throwaway.
- **Bounded** — a change to a flow that already exists in this repo and that you can
  read: a flag, an endpoint, a one-file fix. Ask only the questions that change the
  answer, present a short design, stop.
- **Architectural** — a new project or subsystem, or a change to how components fit
  together or to an interface others depend on. Full pass below.

Bounded measures the repo, not your familiarity: knowing this kind of app is not the same
as having the flow in front of you. When two paths are plausible, take the heavier one.
The ratchet is one-way — complexity found mid-task upgrades the path, nothing downgrades
it.

## The pass

1. **Read the current state** — files, docs, recent commits. Before the questions, not
   after.
2. **Check the size first.** If the request holds several independent subsystems ("chat,
   storage, billing and analytics"), say so before refining a single detail. Split it,
   name how the pieces relate and in what order they get built, then design the first
   one. Refining the details of a request that needs decomposing wastes the whole
   conversation.
3. **One question per message.** Multiple choice where the options are real. Purpose,
   constraints, success criteria — not implementation trivia you can decide yourself.
   Stop when the next question wouldn't change the design.
4. **Two or three approaches with trade-offs** (architectural only). Lead with your
   recommendation and why. Cut from every approach every feature nobody asked for.
5. **Present the design.** Sections scaled to their complexity — a few sentences where
   it's obvious. Cover what a reader could get wrong: the boundaries between units, data
   flow, error handling, how it gets tested. Ask after each section whether it holds.
6. **Hand it over.** The agreed design is the deliverable; planning and implementing are
   a separate decision.

In an existing codebase, follow the patterns already there. Where code standing in the
way of this change has a real problem, fold the targeted improvement into the design —
and nothing beyond that.

## Red flags

| Thought | Reality |
|---|---|
| "This is too simple to need a design" | Simple means a two-sentence design, not none. |
| "I'll call it bounded and skip the questions" | Reaching for the lighter label *is* the doubt. Take the heavier path. |
| "I understand this kind of app, so it's bounded" | Bounded measures the repo. A new project has no flow to read — it's architectural. |
| "The design is obvious, I'll start while they read it" | Presenting and starting in one breath skips the agreement. |
| "The spike works, so I'll keep the code" | A spike's output is an answer. Keeping the code is a new request — classify it. |
| "It grew, but I'm nearly done — no need to re-classify" | Say that it grew, then step the path up. |
| "They approved the spike, so the follow-up is approved" | One classification and one agreement per task. |
