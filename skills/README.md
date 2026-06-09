# Skills — the must-haves + how to install them

loopling leans on a few high-leverage skills/tools. These are **installed once per
machine** (they're not bundled here — they live in `~/.claude/` or as CLIs), and the
soul tells the bot how to use them. Install the ones your bot's purpose needs.

## Research — `last30days`
Multi-source research (Reddit, YouTube + transcripts, Hacker News, GitHub, Polymarket).
The bot's go-to for "what's happening with X lately."
```
# In Claude Code: /plugin → install "last30days" (marketplace: mvanhorn/last30days-skill)
# Then enable it in ~/.claude/settings.json (see config/settings.json.template).
```

## Browse — `agent-browser` (fast headless) + `browser-use` (real Chrome)
- **agent-browser** — native Rust CLI (~0.2s/cmd), stable accessibility refs, batch mode. Use for **research / reading pages / scraping**. Install globally (see https://github.com/ — the agent-browser project) so `agent-browser` is on PATH.
- **browser-use** — drives your **real Chrome profile** from disk (no cookie export), so it can act on **authenticated** sites. Use for logged-in actions (posting, etc.).
  ```bash
  pip install browser-use      # into a dedicated venv, e.g. ~/.browser-use-env
  ```
Rule of thumb the soul should encode: **agent-browser for reading, browser-use for authenticated doing.**

## Voice — Supertonic (TTS) + Whisper (STT)
- TTS: `pip install supertonic soundfile` + `brew install ffmpeg` → use `voice/tts_say.py`.
- STT: `brew install openai-whisper` → see `voice/STT.md`.

## Optional — connectors via MCP
Gmail, Google Calendar, etc. are added as MCP servers (or via Claude's connectors) when
the bot's purpose needs them. Document each in the soul's "Tools available" section so the
bot knows it has them.

## Optional — `gstack` (engineering workflows)
If your bot writes/ships code, [gstack](https://github.com/) adds a virtual eng team
(plan / review / qa / ship). Install into `~/.claude/skills/gstack/` and reference from the soul.

---

### Adding your own skills
Per the soul's "no one-off work" rule: when the bot does something repeatable, codify it
as a skill — a folder under here (or `~/.claude/skills/`) with a `SKILL.md` + any scripts.
Good skills are folders (scripts + assets), have a sharp `description:` trigger, and a
**Gotchas** section that grows every time a failure mode is hit.
