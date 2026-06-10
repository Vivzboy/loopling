# 🔁 loopling

**An agent-loop starter kit. Point your Claude Code (or Codex) agent at this repo, tell it *"become bot X"*, and it self-assembles into an always-on, Telegram-driven autonomous agent — with a brain, a memory, voice, research + browser skills, and a schedule.**

Not a framework you have to learn. A repo your agent *reads* and *transforms itself into*.

> "Just point your agent at this and say *transform it into a [purpose] bot* — and it goes."

loopling is distilled from a family of real, in-production agents (a business brain, a content bot, a video-clipping bot) — their shared, battle-tested architecture, stripped of anyone's specific identity so you can grow your own.

---

## What you get

A bot that:
- **Lives in your terminal** — you start it with one command (e.g. `myagent`) and leave it running, always on.
- **Talks to you on Telegram** — text + voice notes in, text + voice notes + screenshots out.
- **Has a brain** — a local, compounding knowledge wiki (keyword + semantic search, no API keys) so it never re-learns the same thing twice.
- **Has a memory** — durable facts about you and your goals that survive across sessions.
- **Researches + searches** — multi-source deep research (`last30days`), plus web + **image** search (DuckDuckGo free/local; Serper/Tavily/Brave/Exa APIs) and page scraping.
- **Browses** — fast headless web (`agent-browser`) + authenticated real-Chrome sessions (`browser-use`).
- **Makes media** *(optional, key-gated)* — stock photos/videos (Pexels) + AI image/video generation (PiAPI), if your purpose needs it.
- **Speaks + listens** — on-device TTS (Supertonic) for voice replies, Whisper for transcribing your voice notes.
- **Runs on a schedule** — launchd jobs fire it at set times (morning briefing, research passes, etc.) even when you're not there.
- **Keeps a to-do list, and improves itself** — codifies repeated work into skills, files every learning into the wiki.

You supply: **the purpose.** loopling supplies: **everything else.**

> The battle-tested behaviours — the "hard rules" (research→wiki, explain-the-tech,
> no-one-off-work, listen/note/learn) and Karpathy's 4 — come **pre-baked into the soul
> template verbatim**. The bootstrapping agent only fills in your bot's identity, purpose,
> and personality; it doesn't have to (and shouldn't) re-derive the rules.

---

## Requirements (read this first)

loopling is currently **Claude Code + macOS specific.** It assumes:
- **macOS** (uses `launchd` for scheduling, `caffeinate` to stay awake, Homebrew paths).
- **[Claude Code](https://claude.com/claude-code)** installed (`claude` on your PATH). *(Codex works for the build step too, but the launcher + channels assume Claude Code.)*
- **Homebrew**, **Python 3.10+**, **Node/bun** (for the Telegram plugin), **ffmpeg**.
- A **Telegram account** (you'll make a bot with @BotFather — takes 2 minutes).

Cross-platform support (Linux/systemd, etc.) is a future direction. Today: Mac.

---

## 🚀 Quickstart — the magic part

1. **Clone it** into your agent-apps folder and rename it to your bot:
   ```bash
   git clone <this-repo> ~/claude-apps/myagent && cd ~/claude-apps/myagent
   ```

2. **Open Claude Code in it and say one thing:**
   ```
   Read SETUP.md and turn this into a <purpose> bot called <name>.
   ```
   For example:
   > *"Read SETUP.md and turn this into a personal fitness-coaching bot called Coach."*

3. **The agent does the rest** — it interviews you briefly (purpose, name, your context, schedule), then fills in the soul, wires the brain, sets up your Telegram bot, writes your launcher + schedule, and tells you the one command to start it.

4. **Activate it and leave it on:**
   ```bash
   myagent          # starts your always-on agent in the terminal
   ```
   Message it on Telegram. It's alive.

That's it. No framework, no config language — your agent reads the kit and becomes the bot.

---

## What's inside

```
loopling/
├── README.md              ← you are here
├── SETUP.md               ← the agent-executable bootstrap (the heart of the kit)
├── soul/
│   └── CLAUDE.md.template  ← identity placeholders + the hard rules (pre-baked, verbatim)
├── brain/                  ← the compounding knowledge wiki
│   ├── wiki_index.py        ← FTS5 (keyword) + ChromaDB (semantic) indexer
│   ├── wiki_search.py       ← search it
│   ├── requirements.txt
│   └── wiki/_index.md       ← the catalog (+ category folders)
├── memory/
│   └── MEMORY.md.template   ← durable cross-session facts pattern
├── todos/
│   └── todos.py             ← a SQLite to-do CLI
├── voice/
│   ├── tts_say.py           ← on-device TTS → Telegram voice notes (Supertonic)
│   └── STT.md               ← transcribe inbound voice notes (Whisper)
├── channels/telegram/
│   ├── SETUP.md             ← BotFather → .env → MCP server wiring
│   └── .env.template
├── launcher/
│   └── launcher.sh.template ← the `myagent` shell function for ~/.zshrc
├── scheduling/
│   ├── launchd/com.USER.AGENT.session.plist.template
│   ├── cron-wrapper.sh.template  ← watchdog'd scheduled-run wrapper
│   └── SETUP.md             ← scheduling + enable/disable jobs
├── config/
│   ├── settings.json.template       ← MCP servers + plugins + permissions
│   ├── settings.local.json.template
│   └── secrets.local.template
└── skills/                 ← bundled skills (+ install notes for the rest):
    ├── README.md             agent-browser · browser-use · web-search · boil-the-lake
    ├── agent-browser/        coding-standards · skill-creator
    ├── browser-use/
    ├── web-search/
    ├── boil-the-lake/
    ├── coding-standards/
    └── skill-creator/
```

---

## The architecture (how a loopling thinks)

```
        ┌─────────────── Telegram (you) ───────────────┐
        │  text / voice in        text / voice / 📸 out  │
        └───────────────▲───────────────────┬───────────┘
                        │                   │
                 (Whisper STT)        (Supertonic TTS)
                        │                   │
   ┌────────────────────┴───────────────────▼────────────────────┐
   │                     THE LOOPLING (Claude Code)               │
   │   soul/CLAUDE.md  →  who it is + its hard rules              │
   │   brain/wiki      →  what it knows (search before learning)  │
   │   memory/         →  durable facts about you                 │
   │   todos/          →  what's outstanding                      │
   │   skills          →  research (last30days), browse (agent-   │
   │                      browser / browser-use), + your own      │
   └──────────────────────────────────────────────────────────────┘
                        ▲                   ▲
                 (you, live in        (launchd, on a
                  terminal: `myagent`)  schedule: cron-wrapper.sh)
```

**The loop:** at session start it reads its soul + wiki index + memory; it works; it files every learning back into the wiki and notes durable facts to memory; it codifies anything repeatable into a skill. Each run leaves it smarter than the last.

---

## Philosophy

- **Agent-native, not framework-native.** The setup instructions are written for an LLM to execute, not a human to wire by hand.
- **Compounding, not stateless.** A loopling that researches something files it. It never pays to learn the same fact twice.
- **Yours, not ours.** Everything specific to its creators has been stripped to placeholders. The patterns are the product.

Built with ❤️ by the team behind a small flock of these bots. Spawn your own.
