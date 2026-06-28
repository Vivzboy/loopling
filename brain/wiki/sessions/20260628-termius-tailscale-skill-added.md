# Session — 2026-06-28: Termius + Tailscale optional skill added

**Date:** 2026-06-28
**Topics:** Optional infrastructure skill, phone SSH access, session logging

---

## What happened

### Termius + Tailscale skill added to loopling

Jacques identified that looplings run always-on in a terminal, and if the bot freezes while you're away from your laptop, you need a way to reach it. Termius (iOS SSH client) + Tailscale (private mesh VPN) solves this cleanly.

**What was added:**
- `skills/termius-tailscale/SKILL.md` — step-by-step guide: SSH server, Tailscale install + login, keygen, Termius iPhone config, gotchas from real production experience
- `skills/README.md` — new "Optional infrastructure" section
- `SETUP.md` Step 8 — optional nudge at handoff

**Key design decision:** NOT auto-installed during bootstrap. Tailscale requires interactive login (macOS VPN permission dialog). The skill sits in the arsenal; the user runs it manually when ready.

### Session logging pattern established

Both bizzy and loopling wikis now have a `sessions/` category for logging what was discussed, built, and decided in notable sessions — so future context is never lost.

---

## Commits

- `86aabdd` — "Add optional Termius + Tailscale skill for phone SSH access"
