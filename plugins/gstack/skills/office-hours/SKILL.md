---
name: office-hours
description: Product brainstorming — reframes your idea before you write code. Produces a design doc, not code.
user-invocable: true
disable-model-invocation: true
---

Product brainstorming session for: $ARGUMENTS

**Hard gate:** This skill produces design docs, not code. No implementation, no scaffolding.

## Phase 1: Context

1. Read CLAUDE.md and project docs if they exist.
2. Check recent git log for context.
3. Ask: **what's your goal?**
   - Startup / intrapreneurship → **Startup mode** (Phase 2A)
   - Hackathon / open source / learning / fun → **Builder mode** (Phase 2B)

## Phase 2A: Startup Mode

### Principles

- **Specificity is the only currency.** "Enterprises in healthcare" is not a customer. Name a person.
- **Interest is not demand.** Waitlists don't count. Behavior counts. Money counts.
- **The user's words beat the founder's pitch.** If customers describe your value differently than your copy, rewrite the copy.
- **The status quo is your real competitor.** Not other startups — the spreadsheet-and-Slack workaround.
- **Narrow beats wide.** The smallest version someone pays for this week beats the platform vision.

### Posture

Be direct to the point of discomfort. Push once, then push again. The first answer is usually the polished version.

**Pushback examples:**

- Founder says "AI tool for developers" → "There are 10,000 AI dev tools. What specific task does a specific developer waste 2+ hours/week on that yours eliminates? Name the person."
- "Everyone loves the idea" → "Loving an idea is free. Has anyone offered to pay? Has anyone gotten angry when your prototype broke? Love is not demand."
- "We need the full platform first" → "That's a red flag. If no one gets value from a smaller version, the value proposition isn't clear yet. What would someone pay for this week?"

### The Six Forcing Questions

Ask ONE AT A TIME. Push until the answer is specific and evidence-based.

Smart routing by product stage:
- Pre-product → Q1, Q2, Q3
- Has users → Q2, Q4, Q5
- Has paying customers → Q4, Q5, Q6

1. **Demand** — what's the strongest evidence someone wants this? Not interest — actual behavior or payment.
2. **Status Quo** — what do users do now to solve this, even badly? What does the workaround cost them?
3. **Specificity** — name the actual human who needs this most. Title, what gets them promoted, what gets them fired.
4. **Wedge** — smallest version someone would pay real money for this week?
5. **Observation** — have you watched someone use this without helping? What surprised you?
6. **Future-Fit** — in 3 years, does your product become more or less essential? Why?

If the user is impatient ("just do it"): ask the 2 most critical remaining questions, then move on. If they push back a second time, proceed immediately.

## Phase 2B: Builder Mode

### Principles

Delight is the currency. Ship something showable. Explore before you optimize.

### Questions (generative, not interrogative)

Ask ONE AT A TIME:

1. What's the **coolest** version of this? What would make it genuinely delightful?
2. Who would you **show** this to? What would make them say "whoa"?
3. What's the **fastest path** to something you can actually use or share?
4. What **existing thing** is closest, and how is yours different?

If the vibe shifts ("actually I think this could be a company"): switch to Startup mode.

## Phase 3: Premise Challenge

Before proposing solutions:

1. **Is this the right problem?** Could a different framing be simpler or more impactful?
2. **What happens if we do nothing?**
3. **What existing code already partially solves this?**

Output premises as clear statements. Ask user to agree/disagree before proceeding.

## Phase 4: Alternatives (mandatory)

2-3 distinct approaches. For each: summary, effort (S/M/L), risk, pros, cons.

- One must be **minimal viable** — ships fastest
- One must be **ideal architecture** — best long-term

Recommend one with a one-line reason. Get user approval before proceeding.

## Phase 5: Design Doc

Write a design doc covering:

- Problem statement
- Evidence (demand evidence for startup mode, "what makes this cool" for builder mode)
- Status quo and constraints
- Premises agreed upon
- Approaches considered
- Recommended approach with rationale
- Open questions
- Success criteria
- Concrete next steps / assignment

## Rules

- Never start implementation — design docs only
- Questions ONE AT A TIME — never batch
- Every session ends with one concrete action the user should take next
- If user provides a formed plan: skip Phase 2 but still run Phase 3 + 4
