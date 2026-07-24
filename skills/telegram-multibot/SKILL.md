# Spinning up a sibling loopling's Telegram session

**What:** How one agent (or you, scripting it) spins up *another* loopling's interactive
Telegram-bot session on the same Mac — e.g. bizzy starting a slimjan session — without
killing whatever's currently running, and without losing mobile Remote Control.

Each loopling's launcher (see `launcher/launcher.sh.template`) runs an interactive
`claude` process attached to its own `--dangerously-load-development-channels
server:telegram-{{AGENT_NAME}}`. Several of these run at once, each isolated by its own
`TELEGRAM_STATE_DIR` (see `channels/telegram/SETUP.md`).

## The rule: spin it up exactly like a human would

If an agent needs to start a sibling loopling's session programmatically, do it by opening
a real, visible, foreground Terminal.app window and running the actual launcher function —
**never** invoke `claude` directly through a headless/backgrounded shell call.

```bash
osascript -e 'tell application "Terminal" to do script "{{AGENT_NAME}}"'
```

This opens a fresh login shell (sources `~/.zshrc`, so the launcher function is available)
in a real foreground window — identical to a person typing it themselves. Two reasons this
matters:

1. **Remote Control parity.** Claude Code's mobile Remote Control registers a genuinely
   interactive foreground session the same way it would for a human-launched one. A
   headless/backgrounded `claude` call has no controlling terminal and its lifecycle is
   tied to the calling tool call instead of a persistent window — don't rely on it behaving
   the same.
2. **No silent process collisions.** Every loopling's telegram bun server
   (`bun run --cwd .../telegram/<version> --shell=bun --silent start`) has an **identical**
   `ps` cmdline — `TELEGRAM_STATE_DIR` is an env var, invisible to `ps aux`. There is no way
   to tell one loopling's bot process apart from another's by cmdline alone.

## Gotcha: never blanket-`pkill` by cmdline pattern

Because every loopling's telegram bun server looks identical in `ps`, a launcher that does
something like `pkill -f "bun.*telegram"` at startup (to clean up its own stale process from
a crashed prior run) will kill **every other loopling's live session** too — including one
mid-conversation. This bit a real deployment (bizzy's `claudet` launcher, 2026-07-24): the
pkill was meant to clear claudet's own zombie process, but it nuked bizzy's active telegram
server the moment claudet started elsewhere.

If a launcher needs stale-process cleanup, scope it by **parent process**, not cmdline:

```bash
for _pid in $(pgrep -f "bun.*telegram" 2>/dev/null); do
    _ppid=$(ps -o ppid= -p "$_pid" 2>/dev/null | tr -d ' ')
    _pcmd=$(ps -o command= -p "$_ppid" 2>/dev/null)
    # only kill if orphaned (parent already dead) or parent matches THIS launcher's own signature
    if [ -z "$_pcmd" ] || echo "$_pcmd" | grep -q "server:telegram-{{AGENT_NAME}}"; then
        kill "$_pid" 2>/dev/null
    fi
done
```

The default `launcher.sh.template` doesn't include any pkill (it's not needed for normal use)
— don't add one without this scoping.
