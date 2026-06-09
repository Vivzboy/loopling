---
name: skill-creator
description: >
  How to author a new skill — and WHEN to. Trigger this whenever you're about to do
  something the user will likely need again, or they ask you to "make this a skill /
  automate this / save this workflow". Use it before creating any new skill so the
  result is a good one. Embodies the rule: if you do something manually more than once,
  skillify it.
---

# skill-creator — author skills the right way

## The trigger rule (when to make a skill)

**If you do something manually and it will need to happen again, don't just do it once — turn it into a skill.** The pattern:

1. **Do it manually the first time** on a small sample (3–10 items).
2. **Show the user the output.**
3. **If they approve, codify it immediately** — a skill folder, a script, or a soul section.

> The test: if the user has to ask you for the same thing twice, you failed. The second time should already be automated or documented.

Applies to: research flows, posting/publishing, data pipelines, reporting, deliverables — anything repeatable.

## What a skill is

A **folder** (not just a markdown file) that gives you reusable, non-obvious capability:
a `SKILL.md` + any scripts, assets, reference data, or templates it needs. The filesystem
is progressive disclosure — you load the SKILL.md when relevant, and it points to the rest.

```
skills/<skill-name>/
├── SKILL.md          # frontmatter (name + description) + the how-to
├── <script>.py       # give the model code to run, not just prose to reconstruct
└── reference/…       # specs, examples, data (loaded only when needed)
```

## The 9 principles (from the Anthropic skill-design guidance)

1. **Skills are folders, not just markdown** — include scripts, assets, data, reference code. Use the file system as progressive disclosure.
2. **Pick a clean type** — Library/API reference, Product verification, Data fetching, Business process, Scaffolding, Code quality, CI/CD, Runbook, or Infra ops. Don't straddle types.
3. **Build a Gotchas section** — the highest-signal content. Capture every failure mode as it happens; update the skill after each session when something new is learned.
4. **Don't state the obvious** — the model already knows how to code. Skills should push it *out of its defaults* with non-obvious, project-specific knowledge.
5. **The `description:` is for the model** — it's what's scanned to decide when to trigger the skill. Write it as a **trigger condition**, not a summary.
6. **Give scripts, not just instructions** — code in the skill folder means the model composes rather than reconstructs boilerplate.
7. **Store persistent data in the skill folder** — log files, JSON, SQLite. Skills with memory are more powerful.
8. **Avoid railroading** — give what's needed, then let the model adapt. Don't over-specify every step.
9. **Self-improving** — skills get better over time. Every gotcha hit goes back into the skill.

## Before you build it: boil-the-lake first

Don't hand-roll what already exists. Before writing a skill's scripts, check if a library
or an existing skill/script already does the job (see the `boil-the-lake` skill). A good
skill often just wires together things that already exist.

## Writing the SKILL.md

- **Frontmatter:** `name` + a sharp, trigger-style `description` (when should this fire?).
- **Body:** the non-obvious how — commands, the happy path, decision rules, and a
  **Gotchas** section that you keep growing.
- Keep it tight. If it reads like generic docs the model already knows, cut it.

## After creating

- Place it under `skills/<name>/` (project) or `~/.claude/skills/<name>/` (machine-wide).
- Tell the user it exists + what triggers it.
- Reference it from the soul if it's core to the bot's loop.
