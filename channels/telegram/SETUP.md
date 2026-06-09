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
    "command": "bun",
    "args": ["run", "--cwd",
      "/Users/{{USER}}/.claude/plugins/cache/claude-plugins-official/telegram/0.0.6",
      "--shell=bun", "--silent", "start"],
    "env": {
      "TELEGRAM_STATE_DIR": "/Users/{{USER}}/.{{AGENT_NAME}}/channels/telegram"
    }
  }
}
```
> The plugin version folder (`0.0.6`) may differ — check `~/.claude/plugins/cache/claude-plugins-official/telegram/`.

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
