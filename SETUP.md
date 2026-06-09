# SETUP.md — Agent bootstrap procedure

> **You are an AI coding agent (Claude Code / Codex) reading this inside a freshly-cloned `loopling` repo. Your job: transform this kit into the user's bot.** Follow these steps in order. Do the work — don't just explain it. Ask the user the questions in Step 1, then execute Steps 2–8, confirming each. Keep the user in the loop with short progress notes.

If the user said something like *"turn this into a `<purpose>` bot called `<name>`"*, you already have the two most important inputs. Use them and only ask for what's missing.

---

## Step 0 — Preflight

Confirm the environment (loopling is macOS + Claude Code specific):
```bash
uname -a                                  # expect Darwin (macOS)
command -v claude && claude --version      # Claude Code present
command -v brew python3 ffmpeg bun || true # core deps
```
If anything's missing, tell the user what to install (`brew install ffmpeg`, install Claude Code, etc.) before continuing. Don't proceed past a missing `claude` or `python3`.

---

## Step 1 — Interview the user (briefly)

Gather these. Infer what you can from their one-liner; ask only for the gaps. Keep it to a couple of friendly questions, not a form.

| Variable | Meaning | Example |
|----------|---------|---------|
| `AGENT_NAME` | The bot's name (lowercase slug for paths) | `coach` |
| `AGENT_DISPLAY` | How it refers to itself | `Coach` |
| `PURPOSE` | One or two sentences: what is this bot *for*? | "A personal fitness-coaching bot that plans workouts and keeps me accountable." |
| `OWNER_NAME` | The human it works for | `Sam` |
| `OWNER_CONTEXT` | A few durable facts about the owner + goals (informs personality + memory seed) | "Trains 4x/week, training for a 10k, hates fluff." |
| `PERSONALITY` | Tone (direct/warm/funny/formal…) | "Encouraging but blunt, no corporate fluff." |
| `TELEGRAM` | Will they use Telegram? (recommended) | yes |
| `SCHEDULE` | Any recurring autonomous runs? | "Daily 6am: plan today's workout." |

Record the answers — you'll substitute them into the templates below. Use the slug `AGENT_NAME` consistently for the project dir, the Telegram server key (`telegram-<AGENT_NAME>`), and the launcher function.

---

## Step 2 — Write the soul

1. Copy `soul/CLAUDE.md.template` → `.claude/CLAUDE.md` (create `.claude/` at the repo root).
2. Replace every `{{PLACEHOLDER}}` with the Step-1 values. Write the **Identity**, **Personality**, and **Purpose / Mission** sections in full from the interview — these are the parts that make this bot *this* bot.
3. **Keep all the "Hard Rules" and "Karpathy's 4 Rules" sections verbatim** — they're the battle-tested behaviours (research→wiki, explain-the-tech, no-one-off-work, listen/note/learn). Only adapt the examples to the bot's domain.
4. Delete the template's placeholder commentary once filled.

The soul is the single most important file. Spend the most care here.

---

## Step 3 — Wire the brain (knowledge wiki)

```bash
cd brain
python3 -m venv .venv && source .venv/bin/activate   # or use the system python
pip install -r requirements.txt                       # chromadb + sentence-transformers
python3 wiki_index.py                                  # builds the (empty) index
```
- The brain is `brain/wiki/` (markdown notes) + `wiki.db` (FTS5 keyword) + `wiki_chroma/` (semantic). First index downloads the embedding model (~90MB, cached).
- Seed it: write 1–3 starter notes under `brain/wiki/<category>/` capturing the `OWNER_CONTEXT`, then re-run `wiki_index.py`.
- The soul already instructs the bot to **search the wiki before researching** and **file every learning** — that's the compounding loop.

---

## Step 4 — Set up Telegram (the channel)

Follow **`channels/telegram/SETUP.md`** exactly. Summary:
1. Create a bot via @BotFather → get the token + your own chat_id.
2. `cp channels/telegram/.env.template ~/.<AGENT_NAME>/channels/telegram/.env` and fill the token.
3. Register the `telegram-<AGENT_NAME>` MCP server in `config/settings.json` (copy the template block, set `TELEGRAM_STATE_DIR` to `~/.<AGENT_NAME>/channels/telegram`).
4. Make sure the official telegram plugin is installed/enabled (see `config/settings.json.template`).

This is what gives the bot its own isolated inbox + identity (multiple looplings never collide — each has its own `TELEGRAM_STATE_DIR`).

---

## Step 5 — Voice (optional but lovely)

- **TTS (bot speaks):** `voice/tts_say.py` sends Supertonic voice notes to Telegram. Set `OWNER_CHAT_ID` + `BOT_TOKEN` via env (see the file header). First run downloads ~260MB of ONNX models.
- **STT (bot listens):** `voice/STT.md` documents transcribing inbound Telegram voice notes with Whisper (`brew install openai-whisper` or the binary). The soul references this flow.

Tell the bot (in its soul) when to use voice — e.g. "reply by voice when the user is likely away from their laptop."

---

## Step 6 — Install the launcher (start it from your terminal)

1. Open `launcher/launcher.sh.template`, substitute `AGENT_NAME`, append the resulting function to `~/.zshrc`.
2. `source ~/.zshrc`.
3. Now `<AGENT_NAME>` is a command that `cd`s into the project, keeps the Mac awake (`caffeinate`), and launches Claude Code attached to the bot's Telegram channel.

To run it always-on: start it in a terminal (or a `tmux`/`screen` session) and leave it. It will respond to Telegram in real time.

---

## Step 7 — Scheduling (optional, for autonomous runs)

If the user wants recurring autonomous sessions (Step 1 `SCHEDULE`), follow **`scheduling/SETUP.md`**:
1. Fill `scheduling/cron-wrapper.sh.template` (bot token, chat_id, paths) → place in the project root.
2. Fill `scheduling/launchd/com.USER.AGENT.session.plist.template` (label, schedule time, the session prompt) → install to `~/Library/LaunchAgents/` and `launchctl load` it.
3. The wrapper has a watchdog (force-kills hung runs) — keep it.

---

## Step 8 — Hand off

Tell the user, concisely:
- ✅ what got created (soul, brain, telegram, launcher, schedule).
- ▶️ the one command to start it: **`<AGENT_NAME>`**.
- 💬 to message the bot on Telegram to confirm it's alive.
- 🔧 anything still needing their action (e.g. paste the BotFather token, grant macOS permissions).

Then commit:
```bash
git add -A && git commit -m "Bootstrap <AGENT_NAME> from loopling"
```

---

## Substitution cheat-sheet

| Placeholder | Used in |
|-------------|---------|
| `{{AGENT_NAME}}` | dir, launcher fn, `telegram-<name>` server, `~/.<name>/` state dir |
| `{{AGENT_DISPLAY}}` | soul identity, voice captions |
| `{{PURPOSE}}` | soul mission |
| `{{OWNER_NAME}}` | soul, memory seed |
| `{{OWNER_CONTEXT}}` | soul personality + first wiki/memory notes |
| `{{PERSONALITY}}` | soul personality |
| `{{OWNER_CHAT_ID}}` | telegram .env, voice, cron-wrapper |
| `{{BOT_TOKEN}}` | telegram .env, voice, cron-wrapper |
| `{{USER}}` | launchd plist label, paths |

Work through the steps, keep the user posted, and leave them with a living bot. Go.
