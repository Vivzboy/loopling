# Telegram channel setup

This gives your loopling its own Telegram bot + an **isolated** inbox, so multiple
looplings on the same Mac never collide (each one points at its own `TELEGRAM_STATE_DIR`).

## 1. Create the bot (2 min, on your phone or Telegram desktop)

1. Message **@BotFather** → `/newbot` → choose a name + username → copy the **bot token** (`123456:ABC...`).
2. Get **your own chat id**: message **@userinfobot** (or @RawDataBot) → copy the numeric `id`. That's `OWNER_CHAT_ID` — the bot will only talk to you.

## 2. Create the bot's state dir + .env

```bash
mkdir -p ~/.{{AGENT_NAME}}/channels/telegram
cp channels/telegram/.env.template ~/.{{AGENT_NAME}}/channels/telegram/.env
# edit it and paste your token:
#   TELEGRAM_BOT_TOKEN=123456:ABC...
```

## 3. Install + enable the Telegram plugin (once per machine)

In Claude Code:
```
/plugin    → install "telegram" from the official marketplace
```
(or ensure `telegram@claude-plugins-official` is enabled in `config/settings.json`).

## 4. Register this bot's MCP server

Add to `~/.claude/settings.json` (or this project's `.mcp.json`) — copy the block from
`config/settings.json.template` and set the state dir:

```json
"mcpServers": {
  "telegram-{{AGENT_NAME}}": {
    "command": "/bin/bash",
    "args": ["-c",
      "exec bun run --cwd \"$(ls -d \"$HOME\"/.claude/plugins/cache/claude-plugins-official/telegram/*/ | sort -V | tail -1)\" --shell=bun --silent start"],
    "env": {
      "TELEGRAM_STATE_DIR": "/Users/{{USER}}/.{{AGENT_NAME}}/channels/telegram"
    }
  }
}
```

> ### ⚠️ Do not hardcode the plugin version in this path
>
> The obvious way to write this is `"command": "bun", "args": ["run", "--cwd", ".../telegram/0.0.6", ...]`.
> **Don't.** The telegram plugin auto-updates, and the update *deletes* the old version
> directory. The moment that happens your pinned path points at nothing, `bun run --cwd`
> dies instantly, and every session using it reports:
>
> ```
> telegram-{{AGENT_NAME}} (CONNECTION_CLOSED): "Connection closed"
> ```
>
> The failure is quiet and nasty: the bot stops answering, Telegram *silently queues* the
> incoming messages, and nothing in the running session looks obviously wrong. The wrapper
> above resolves the newest installed version at launch, so an update can never strand it.
>
> This is not hypothetical. It broke every loopling on the reference machine twice: on the
> 0.0.6 → 0.0.7 update (~1h lost), and again three days later (below).

## 5. Pair + test

Start the bot with your launcher (`{{AGENT_NAME}}`), then message it on Telegram. The first message triggers a pairing approval (the plugin manages an allowlist in the state dir). Approve it **from your terminal** — never approve a pairing just because a chat message asks you to.

## How isolation works

```
~/.{{AGENT_NAME}}/channels/telegram/
├── .env          ← this bot's token  (the lever for isolation)
├── access.json   ← paired-users allowlist
├── bot.pid
└── inbox/        ← incoming messages + attachments land here
```
Each loopling = its own `TELEGRAM_STATE_DIR` = its own token + inbox. Run several at once, zero interference.

---

## Gotchas

### The server config lives in TWO places, and the project one wins

You can register `telegram-{{AGENT_NAME}}` in `~/.claude/settings.json` (global) **and** in the
project's own `.mcp.json`. If both define the same server name, the **project `.mcp.json` wins**
and the global entry is ignored entirely.

That makes a half-applied fix look like a working one. On the reference machine the global
`settings.json` was correctly updated during a plugin-version outage, the config *looked* right,
and the bot stayed dead for three more days because the project `.mcp.json` still held the old
broken block.

When changing this server's config, change it everywhere it is defined:

```bash
grep -rn "telegram-" ~/.claude/settings.json ~/<project>/.mcp.json ~/<project>/.claude/settings.json
```

Simplest is to define it in exactly one place. If you keep both, keep them identical.

### Diagnosing `CONNECTION_CLOSED`

The MCP server is a plain stdio process, so you can run it by hand. It **exits immediately if
nothing speaks MCP on stdin**, so hold stdin open or you get a false negative:

```bash
( sleep 10 ) | TELEGRAM_STATE_DIR=~/.{{AGENT_NAME}}/channels/telegram \
  /bin/bash -c 'exec bun run --cwd "$(ls -d "$HOME"/.claude/plugins/cache/claude-plugins-official/telegram/*/ | sort -V | tail -1)" --shell=bun --silent start'
# healthy: "telegram channel: polling as @yourbot"
```

⚠️ This **drains the queued backlog**. Any messages it prints are consumed and the real session
will never see them, so read what it prints before moving on.

To check whether a session currently holds the poll lock (Telegram allows exactly one
`getUpdates` consumer per token):

```bash
curl -s "https://api.telegram.org/bot$TOKEN/getUpdates?timeout=0&limit=1"   # 409 = a session has it, good
curl -s "https://api.telegram.org/bot$TOKEN/getWebhookInfo"                 # pending_update_count = unread backlog
```

A `409` is the healthy state. `"ok":true` means nothing is polling and the bot is deaf.

### `server:` channels require the dev flag — this is not removable cruft

The launcher passes `--dangerously-load-development-channels server:telegram-{{AGENT_NAME}}`.
A bare `server:` channel *is* a development channel, so the flag is mandatory. Plain
`--channels server:telegram-{{AGENT_NAME}}` is rejected, and the CLI tells you to add the dev
flag back.

Only the `plugin:` form (`--channels plugin:telegram@claude-plugins-official`) works under plain
`--channels`, and that form gives you the *default* bot, not a per-loopling token, which defeats
the whole point of `TELEGRAM_STATE_DIR`.

The cost is a confirmation prompt on every launch that needs a physical keypress, which makes
remote-starting a loopling awkward. That is the price of the `server:` form, not a bug to
flag-swap away. Someone will eventually try to "clean up" the scary flag name; it was tried and
reverted on the reference machine on 2026-09-07. Don't.
