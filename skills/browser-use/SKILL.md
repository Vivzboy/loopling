---
name: browser-use
description: >
  Drive a REAL Chrome profile from disk for AUTHENTICATED browser actions — logging
  into and acting on sites where you're already signed in (social posting, dashboards,
  portals). Use this (not agent-browser) whenever the task needs to be logged in as the
  user. Triggers: "post to X/TikTok/Instagram", "log in and do X", "click through my
  authenticated dashboard".
---

# browser-use — authenticated, real-Chrome browser automation

**What it is:** a Python CLI that drives your **real, on-disk Chrome profile** — so it
inherits your existing logged-in sessions (no cookie export, no expiry). This is the
companion to `agent-browser`:

| Task | Tool |
|------|------|
| Web research, reading pages, scraping (logged-out) | **agent-browser** (fast headless) |
| Anything that must be **logged in** (post, act on a dashboard) | **browser-use** (this) |

`agent-browser` runs its own "Chrome for Testing" binary and **cannot** read real Chrome's
authenticated cookies — so for any signed-in action, use browser-use.

## Install (once)

```bash
python3 -m venv ~/.browser-use-env && ~/.browser-use-env/bin/pip install browser-use
BU=~/.browser-use-env/bin/browser-use   # handy alias
```

## Core usage

```bash
BU=~/.browser-use-env/bin/browser-use
$BU --session mybot --profile "Default" open "https://example.com/home"
$BU --session mybot --profile "Default" get title         # read state
$BU --session mybot --profile "Default" screenshot /tmp/x.png
$BU --session mybot --profile "Default" close             # ALWAYS close when done
```

- `--profile "<name>"` picks which Chrome profile to use (its logged-in sessions). Run
  Chrome → `chrome://version` (Profile Path) to find profile names; "Default" = Person 1.
- `--session "<name>"` isolates concurrent runs (see next section — this is the big one).

## Session isolation — run many without colliding (hard rule)

**Every command should pass a `--session <name>`.** Without it, it uses the `default`
session, which collides with *any* other browser-use user (another bot, your own browsing,
a scheduled job). A named session gets its **own daemon process, its own Unix socket
(`~/.browser-use/<name>.sock`), its own Chrome temp-profile copy, and its own CDP port** —
so two named sessions run in complete parallel with zero interference.

Naming convention that keeps an always-on bot + its scheduled jobs from trampling each other:
- **Live/interactive** runs → the bot's base name, e.g. `--session mybot`.
- **Each scheduled job gets its OWN suffixed name**, never the base name:
  - morning job → `--session mybot-am`
  - evening job → `--session mybot-pm`

  Two scheduled jobs sharing one session name would share the same daemon/socket/Chrome
  temp profile and corrupt each other's state mid-run. One session name = one concurrent
  user. (Enforce this from the launchd prompt; don't override it inside the job.)

## Detecting a logged-out / expired session

After `open`, check the title:
```bash
$BU --session mybot --profile "Default" get title
# title contains "Log in" / "Sign in"  → the session expired
```
If logged out, use `$BU handoff` to let the user log in manually in visible Chrome, then
close and retry. Never try to brute-force credentials.

## ⚠️ Bot-detection hygiene (hard rule for social / detection-sensitive sites)

Many platforms fingerprint automation. When acting on them:
- **Type, don't paste.** Use real keystroke typing with a small delay (`type`, `delay 10–20ms`); never paste via clipboard or `execCommand('insertText')` into user-facing fields.
- **Real clicks.** Prefer real pixel-coordinate mouse clicks over programmatic `.click()` where possible; use JS `dispatchEvent` only when an overlay blocks native clicks.
- **Human pacing.** 2–5s pauses between major steps (upload → caption → submit). Robotic speed = detection. Vary the durations slightly — don't hardcode `sleep(3)` everywhere.
- **Fresh session per action.** Don't reuse one browser session across many posts in a tight loop — looks robotic.
- **Don't flood.** Cap actions per platform per day; leave real gaps between them.

(These are the same rules that kept our content bots from getting shadow-banned.)

## Gotchas
- **Always `close`** when done — a left-open daemon blocks the next run / wrong profile.
  `$BU sessions` lists active ones; `$BU --session <name> close` (or `close --all`) cleans up.
- **Click by index, not `eval`.** React ignores synthetic JS click events — get the element
  index from `$BU --session <s> state` and `click <index>` (or click pixel `x y`).
- **React controlled inputs** (e.g. search fields) ignore plain `fill`/`type` — set the
  value via the React native setter + dispatch an `input` event (see the agent-browser skill
  for the exact eval snippet).
- **Verify which account is loaded before any destructive/posting action.** If multiple
  profiles exist, confirm the logged-in identity first (check the page) — wrong-profile
  posting is a real incident class.
- **Keep Chrome alive across the wrapper.** If a long action outlives the launching process,
  kill only the browser-use wrapper PID, not Chrome — Chrome is held open via CDP and dies
  if you kill it directly.
- **Set a sane viewport** on open if buttons hide (`--window-size=1440,900`); some profiles
  start very narrow and hide controls below ~1000px.
- **Portrait video posts** are often blocked headless — may need a manual/visible step.
- Profile is read from disk at open time; close + reopen to pick up a fresh login.
