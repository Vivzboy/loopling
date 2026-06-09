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
- `--session "<name>"` isolates concurrent runs — give each task/bot its own session so
  two jobs sharing a profile don't trample each other's browser state.

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
- **React controlled inputs** (e.g. TikTok/Instagram search) ignore plain `fill`/`type` —
  set the value via the React native setter + dispatch an `input` event (see agent-browser
  skill for the exact eval snippet). Same applies here.
- **Portrait video posts** are often blocked headless — may need a manual/visible step.
- Profile is read from disk at open time; close + reopen to pick up a fresh login.
