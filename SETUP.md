# SETUP.md — Agent bootstrap procedure

> **You are Claude Code, reading this inside a freshly-cloned `loopling` repo. Your job: transform this kit into the user's bot.** Follow these steps in order. Do the work — don't just explain it. Ask the user the questions in Step 1, then execute Steps 2–8, confirming each. Keep the user in the loop with short progress notes.

If the user said something like *"turn this into a `<purpose>` bot called `<name>`"*, you already have the two most important inputs. Use them and only ask for what's missing.

---

## Step 0 — Preflight

Confirm the environment (loopling is macOS + Claude Code specific):
```bash
uname -a                                   # expect Darwin (macOS)
command -v claude && claude --version       # Claude Code present (note the binary path)
for c in brew python3 pip3 ffmpeg bun; do command -v "$c" >/dev/null || echo "missing: $c"; done
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

Install the brain deps into your **system** python so the bot can run `python3 brain/wiki_index.py`
from anywhere (don't bury them in a venv the soul won't activate):
```bash
pip3 install --break-system-packages -r brain/requirements.txt    # chromadb + sentence-transformers
python3 brain/wiki_index.py               # builds the (empty) index
```
> **Note:** `--break-system-packages` is needed on macOS with Homebrew Python 3.12+ (which blocks system-level installs by default). It's safe here — you're only adding research/embedding libs, not touching system tools.
- The brain is `brain/wiki/` (markdown notes) + `brain/wiki.db` (FTS5 keyword) + `brain/wiki_chroma/`
  (semantic). First index downloads the embedding model (~90MB, cached).
- Category folders already exist (`notes/`, `people/`, `concepts/`, `projects/`, `sessions/`) — add more freely. The `sessions/` folder is the bot's diary — after any notable session it writes an entry there (what was discussed/built/decided, and why). This is what gives the bot real long-term memory.
- Seed it: write 1–3 starter notes under `brain/wiki/<category>/` capturing `OWNER_CONTEXT`, then
  re-run `python3 brain/wiki_index.py`.
- `brain/wiki_utils.py` is the programmatic API (`get_index`, `search_wiki`, `write_entry`,
  `update_entry`, `coverage_check`, `add_coverage`) — the bot uses it to file knowledge and track
  what it's already done, so it never repeats work. The soul already says **search before
  researching, file every learning**.

---

## Step 4 — Set up Telegram (the channel)

Follow **`channels/telegram/SETUP.md`** exactly. Summary:
1. Create a bot via @BotFather → get the token + your own chat_id.
2. `mkdir -p ~/.<AGENT_NAME>/channels/telegram && cp channels/telegram/.env.template ~/.<AGENT_NAME>/channels/telegram/.env` and fill the token.
3. **Register the MCP server in `~/.claude/settings.json`** (the global config — the canonical place; the launcher loads the server from here). Copy the `mcpServers` block from `config/settings.json.template`, substitute `{{USER}}`/`{{AGENT_NAME}}`, set `TELEGRAM_STATE_DIR` to `~/.<AGENT_NAME>/channels/telegram`. Two gotchas:
   - **Verify the plugin version in the path** first: `ls ~/.claude/plugins/cache/claude-plugins-official/telegram/` — use whatever version folder is actually there (the template shows `0.0.6`; yours may differ).
   - **Strip the `"// …"` comment keys** when merging — JSON has no comments; they're just docs.
4. Also merge `enabledPlugins` + `extraKnownMarketplaces` from the template (see Step 4b) and install the plugins.

This gives the bot its own isolated inbox + identity (multiple looplings never collide — each has its own `TELEGRAM_STATE_DIR`).

---

## Step 4b — Install the plugins

loopling uses a few Claude Code plugins. Install them once per machine; `config/settings.json`
then enables them (copy its `enabledPlugins` + `extraKnownMarketplaces` into `~/.claude/settings.json`):
```
# In Claude Code:
/plugin marketplace add mvanhorn/last30days-skill
/plugin marketplace add EveryInc/compound-engineering-plugin
/plugin install telegram@claude-plugins-official
/plugin install last30days@last30days-skill
/plugin install compound-engineering@compound-engineering-plugin
```
- **telegram** — the channel (Step 4). **last30days** — multi-source research.
- **compound-engineering** — the `ce-*` plan/review/qa/ship dev skills (great if the bot writes
  code; skip if not).

Skip any plugin the bot won't use.

## Step 5 — Voice (optional but lovely)

- **TTS (bot speaks):** `pip3 install --break-system-packages supertonic soundfile` (system python) + `brew install ffmpeg`. Then `voice/tts_say.py` sends voice notes to Telegram — set `LOOPLING_BOT_TOKEN` + `LOOPLING_OWNER_CHAT_ID` via env (or `~/.claude/secrets.local`). First run downloads ~260MB of ONNX models. (`voice/tg_send.py` sends long text, auto-splitting over Telegram's 4096-char limit.)
- **STT (bot listens):** `voice/STT.md` documents transcribing inbound Telegram voice notes with Whisper (`brew install openai-whisper`). The soul references this flow.

Tell the bot (in its soul) when to use voice — e.g. "reply by voice when the user is likely away from their laptop."

---

## Step 5b — Make the bundled skills discoverable

The kit ships skill files in `skills/`: the spine (`agent-browser`, `browser-use`,
`web-search`, `boil-the-lake`, `coding-standards`, `skill-creator`) plus optional key-gated
ones (`stock-images`, `ai-media`). Symlink every skill folder into the project's
`.claude/skills/` so Claude Code auto-loads them (the loop handles all of them):
```bash
mkdir -p .claude/skills
for s in skills/*/; do ln -sfn "$PWD/$s" ".claude/skills/$(basename "$s")"; done
```
Then install the **install-once** tools the bot's purpose needs (see `skills/README.md`):
`last30days` (research), the `agent-browser` + `browser-use` CLIs, voice deps, and any API
keys (`SERPER_API_KEY`, `PEXELS_API_KEY`, `PIAPI_KEY`…) the optional skills need — stored in
`~/.claude/secrets.local`. Skip what this bot won't use.

## Step 6 — Install the launcher (start it from your terminal)

1. Open `launcher/launcher.sh.template`, substitute `{{AGENT_NAME}}`, and confirm the Claude Code path — `command -v claude`; if it isn't `$HOME/.local/bin/claude`, update the path in the function. Append the function to `~/.zshrc`.
2. `source ~/.zshrc`.
3. Now `<AGENT_NAME>` is a command that `cd`s into the project, keeps the Mac awake (`caffeinate`), and launches Claude Code attached to the bot's Telegram channel. Calling it immediately wires the **live two-way** Telegram connection (the bot's single polling connection).

To run it always-on: start it in a terminal (or a `tmux`/`screen` session) and leave it. It responds to Telegram in real time.

> **Live vs scheduled:** the launcher holds the bot's one live polling connection. Scheduled launchd jobs (Step 7) deliberately do **not** open a polling connection (`--strict-mcp-config`) and report via a one-way push instead — so a scheduled run can never steal your live connection, and the two coexist. See `scheduling/SETUP.md`.

---

## Step 7 — Scheduling (optional, for autonomous runs)

If the user wants recurring autonomous sessions (Step 1 `SCHEDULE`), follow **`scheduling/SETUP.md`**:
1. Fill `scheduling/cron-wrapper.sh.template` (substitute `{{AGENT_NAME}}`, `{{BOT_TOKEN}}`, `{{OWNER_CHAT_ID}}`, `{{USER}}`), `chmod +x`, and **place it at the repo root as `cron-wrapper.sh`** — the plist references `~/claude-apps/<AGENT_NAME>/cron-wrapper.sh`.
2. Fill `scheduling/launchd/com.USER.AGENT.session.plist.template` — substitute the label, schedule time, and the session prompt (including `{{AGENT_DISPLAY}}`). Name one plist per job (e.g. `com.<user>.<agent>.morning.plist`). Install to `~/Library/LaunchAgents/` and `launchctl load` it.
3. The wrapper has a watchdog (force-kills hung runs) — keep it. Give each scheduled run its own browser-use `--session` name (see the browser-use skill) so concurrent jobs never collide.
4. Optional: also schedule `scheduling/browser-use-cleanup.sh` (every ~2h) to sweep leaked browser temp dirs if the bot uses browser-use heavily.

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

> **Optional — phone SSH access:** If the user wants to manage their loopling from their iPhone (restart it, check logs, open a terminal while away from their laptop), point them at `skills/termius-tailscale/SKILL.md`. It sets up Tailscale + Termius in ~10 minutes. Not auto-installed — requires interactive Tailscale login.

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
