# Skills

Two kinds live here: **bundled** skill files (shipped in this folder — your bot has them
day one) and **install-once** tools (CLIs/plugins the bot uses, installed per machine).
The soul tells the bot how + when to use each.

## ✅ Bundled (already in this repo — ready to use)

| Skill | What it gives the bot |
|-------|-----------------------|
| `agent-browser/` | Fast headless web (~0.2s/cmd) for research / reading / scraping (logged-out). |
| `browser-use/` | Drives your **real Chrome profile** for **authenticated** actions (post, act on dashboards) + bot-detection hygiene rules. |
| `boil-the-lake/` | Engineering decision principle (Garry Tan): completeness is cheap, **search before building**, don't hand-roll what a library does. |
| `coding-standards/` | Code organisation rules (file-size limits, structure-by-domain, naming). |
| `skill-creator/` | **How + when to author new skills** — the "skillify anything you do manually more than once" rule + the Anthropic skill-design principles. |

Rule of thumb the soul encodes: **agent-browser for reading, browser-use for authenticated doing.**

## 🔧 Install-once (per machine — not bundled)

- **`last30days`** — multi-source research (Reddit, YouTube + transcripts, HN, GitHub, Polymarket). The go-to for "what's happening with X lately."
  `/plugin → install "last30days"` (marketplace `mvanhorn/last30days-skill`), then enable in `config/settings.json`.
- **`agent-browser` CLI** — the bundled skill documents it; install the binary so `agent-browser` is on PATH.
- **`browser-use` CLI** — `pip install browser-use` into a dedicated venv (e.g. `~/.browser-use-env`).
- **Voice** — TTS: `pip install supertonic soundfile` + `brew install ffmpeg` (→ `voice/tts_say.py`). STT: `brew install openai-whisper` (→ `voice/STT.md`).
- **`gstack`** (optional) — if your bot writes/ships code, adds a virtual eng team (plan/review/qa/ship). Install into `~/.claude/skills/gstack/`.

## 🧩 Specialised extension: content / posting bots

If your loopling's purpose is **content publishing** (like the bots loopling was distilled
from), there's a richer skill set for that lineage — TikTok/Instagram/YouTube/X posting,
video rendering, karaoke captions, voiceover, analytics. It's **not bundled** here (it's
heavy + assumes a content purpose), but the patterns exist if you go that direction — ask
your agent to build the posting skills it needs (using `skill-creator`), reusing `browser-use`
for the authenticated posting + its bot-detection rules.

## Adding your own

Per the soul's "no one-off work" rule + the `skill-creator` skill: when the bot does
something repeatable, codify it as a skill — a folder here (or in `~/.claude/skills/`) with
a `SKILL.md` (sharp `description:` trigger) + any scripts, and a **Gotchas** section that
grows every time a failure mode is hit.
