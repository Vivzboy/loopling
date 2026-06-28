# Skills

Two kinds live here: **bundled** skill files (shipped in this folder — your bot has them
day one) and **install-once** tools (CLIs/plugins the bot uses, installed per machine).
The soul tells the bot how + when to use each.

## ✅ Bundled (already in this repo — ready to use)

| Skill | What it gives the bot |
|-------|-----------------------|
| `agent-browser/` | Fast headless web (~0.2s/cmd) for research / reading / scraping (logged-out). |
| `browser-use/` | Drives your **real Chrome profile** for **authenticated** actions (act on dashboards / portals / web apps you're signed into) + bot-detection hygiene rules. |
| `web-search/` | The generic research/search layer — web + **image search**: WebSearch/WebFetch, httpx→DuckDuckGo (free, local), agent-browser scraping, and the search APIs (Serper/Tavily/Brave/Exa) for clean/programmatic/server use. |
| `boil-the-lake/` | Engineering decision principle (Garry Tan): completeness is cheap, **search before building**, don't hand-roll what a library does. |
| `coding-standards/` | Code organisation rules (file-size limits, structure-by-domain, naming). |
| `skill-creator/` | **How + when to author new skills** — the "skillify anything you do manually more than once" rule + the Anthropic skill-design principles. |

Rule of thumb the soul encodes: **agent-browser for reading, browser-use for authenticated doing.**

## 🔧 Install-once (per machine — not bundled)

- **`last30days`** — multi-source research (Reddit, YouTube + transcripts, HN, GitHub, Polymarket). The go-to for "what's happening with X lately."
  Repo: <https://github.com/mvanhorn/last30days-skill> · `/plugin → install "last30days"` (marketplace `mvanhorn/last30days-skill`), then enable in `config/settings.json`.
- **`agent-browser` CLI** — the bundled skill documents it. Repo: <https://github.com/vercel-labs/agent-browser>. Install with `brew install agent-browser` (or `npm install -g agent-browser`), so `agent-browser` is on PATH.
- **`browser-use` CLI** — `pip install browser-use` into a dedicated venv (e.g. `~/.browser-use-env`). Docs: <https://docs.browser-use.com/open-source/browser-use-cli> · Repo: <https://github.com/browser-use/browser-use>.
- **Voice** — TTS: `pip install supertonic soundfile` + `brew install ffmpeg` (→ `voice/tts_say.py`). STT: `brew install openai-whisper` (→ `voice/STT.md`).
- **compound-engineering** (`ce-*` skills) — plan / review / qa / ship dev workflows. Marketplace `EveryInc/compound-engineering-plugin` → `/plugin install compound-engineering@compound-engineering-plugin`. (Enabled by `config/settings.json`.)
- **Search API keys** (optional, for the `web-search` skill) — e.g. `SERPER_API_KEY` (Google web + images), or Tavily/Brave/Exa. Put them in `~/.claude/secrets.local`.
- **`gstack`** (optional) — if your bot writes/ships code, adds a virtual eng team (plan/review/qa/ship). Install into `~/.claude/skills/gstack/`.

## 🎨 Optional media tools (bundled skill, needs an API key)

For bots whose purpose involves media. Each documents its API; the **key pattern** is: on setup
the agent asks the user for the key and stores it in `~/.claude/secrets.local` — never hardcoded,
read at runtime. (Same pattern for every API-key tool here, incl. the search APIs above.)

| Skill | Gives the bot | Key |
|-------|---------------|-----|
| `stock-images/` | Free stock photos + videos (Pexels). | `PEXELS_API_KEY` (free) |
| `ai-media/` | AI **image** + **video** generation via PiAPI (GPT-image / Flux / Seedance). **Paid** — has a cost-control hard rule. | `PIAPI_KEY` (paid) |

## 🔌 Optional infrastructure

For keeping your loopling reachable and recoverable — not required for the bot to work, but nice to have if you want to manage it from your phone.

| Skill | What it gives you |
|-------|-------------------|
| `termius-tailscale/` | SSH from your iPhone to the Mac running your bot, from anywhere — so you can restart, debug, or monitor it without a laptop. Uses Tailscale (free VPN) + Termius (iOS SSH client). |

These don't get auto-wired during setup. Run the relevant skill manually after your loopling is live, if you want it.

## 🧩 Building skills for your bot's purpose

loopling ships the *generic* spine — browse, research, voice, and the engineering rules.
Whatever your bot's purpose needs beyond that (a domain API, a specific workflow, a data
integration, a publishing pipeline, …) have your agent **build those skills itself** using
`skill-creator`, reusing `browser-use` for anything authenticated. The kit deliberately
stays lean and purpose-agnostic — your bot grows exactly the skills its job demands, no more.

## Adding your own

Per the soul's "no one-off work" rule + the `skill-creator` skill: when the bot does
something repeatable, codify it as a skill — a folder here (or in `~/.claude/skills/`) with
a `SKILL.md` (sharp `description:` trigger) + any scripts, and a **Gotchas** section that
grows every time a failure mode is hit.
