# Scheduling — autonomous runs via launchd

For recurring autonomous sessions (a morning briefing, a research pass, an evening
review…) that fire even when you're not at the keyboard. macOS uses **launchd** for this.

> Interactive use (you chatting to it live) doesn't need any of this — just run the
> launcher and leave it open. Scheduling is only for *unattended* recurring runs.

## 1. Install the wrapper

```bash
cp scheduling/cron-wrapper.sh.template cron-wrapper.sh
# edit cron-wrapper.sh: substitute {{AGENT_NAME}}, {{BOT_TOKEN}}, {{OWNER_CHAT_ID}}, {{USER}}
chmod +x cron-wrapper.sh
```
The wrapper runs one headless `claude -p "<prompt>"` session and **force-kills it after 40 min** (watchdog) so a hung run never blocks future jobs. It pings you on Telegram if that happens.

## 2. Create a job

```bash
cp scheduling/launchd/com.USER.AGENT.session.plist.template \
   ~/Library/LaunchAgents/com.<USER>.<AGENT_NAME>.sessiona.plist
# edit it: substitute placeholders, set the Hour/Minute, and write the session PROMPT
launchctl load ~/Library/LaunchAgents/com.<USER>.<AGENT_NAME>.sessiona.plist
```
Each job = one `.plist`. Want a morning research pass + an evening review? Two plists, two times. The **prompt** in `ProgramArguments` tells the bot what to do that session — keep it short and point it at the soul.

`StartCalendarInterval` schedule keys:
- `Hour` + `Minute` → daily at HH:MM
- add `Weekday` (0=Sun) → specific day(s)
- add `Month` + `Day` → specific dates

## 3. Manage jobs

```bash
launchctl list | grep <AGENT_NAME>                  # is it loaded?
launchctl start com.<USER>.<AGENT_NAME>.sessiona     # run it now (test)
tail -f data/launchd.log                             # watch output
```

### Permanently disable a job (survives reboot)
macOS reloads `~/Library/LaunchAgents/` on every login, so `launchctl unload` alone does **not** stick. To kill a job for good:
```bash
launchctl disable "gui/$(id -u)/com.<USER>.<AGENT_NAME>.sessiona"
launchctl unload  ~/Library/LaunchAgents/com.<USER>.<AGENT_NAME>.sessiona.plist
```
Re-enable:
```bash
launchctl enable "gui/$(id -u)/com.<USER>.<AGENT_NAME>.sessiona"
launchctl load   ~/Library/LaunchAgents/com.<USER>.<AGENT_NAME>.sessiona.plist
```

## Gotchas
- **PATH matters.** launchd runs with a minimal env — the plist sets `PATH` so `claude`, `python3`, `ffmpeg`, `browser-use` resolve. Adjust to your install paths.
- **Browser sessions:** if scheduled runs use `browser-use`, give each job its own `--session <name>` so concurrent jobs don't trample shared Chrome state.
- **The Mac must be awake.** Scheduled jobs only fire when the machine is on (and not asleep). For 24/7, keep it plugged in with sleep disabled, or run on an always-on Mac.
