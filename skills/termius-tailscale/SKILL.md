---
name: termius-tailscale
description: Use when the user wants to set up SSH access from their iPhone to the Mac running their loopling — so they can restart, debug, or monitor the bot from anywhere, even without a laptop.
---

# Termius + Tailscale — Phone SSH Access

SSH from iPhone → Mac, from anywhere in the world. Useful for looplings: if your bot freezes or needs a restart while you're away from your laptop, you can jump in from Termius on your phone over Tailscale.

This is **fully optional** — run it after your loopling is up and only if you want phone-based terminal access.

---

## What this sets up

- **SSH server on Mac** — enabled via launchd (persists across reboots, on-demand)
- **Tailscale** — private mesh VPN; gives your Mac a stable `100.x.x.x` address reachable from anywhere (no port-forwarding, no dynamic DNS, free for personal use up to 100 devices)
- **Termius on iPhone** — polished SSH client; connect to your Mac with one tap

---

## Prerequisites

- macOS (this skill uses `launchctl` / Homebrew)
- Homebrew installed (`brew`)
- iPhone with Termius installed (free, App Store)
- A Tailscale account (free at tailscale.com — log in with Google/GitHub)

---

## Setup (run in order)

### 1. Enable SSH on Mac

```bash
# Enable the SSH server (launchd loads it on demand — persists after reboots)
sudo launchctl load -w /System/Library/LaunchDaemons/ssh.plist

# Verify it's listening
lsof -i :22
```

> Note: `sudo systemsetup -setremotelogin on` requires Full Disk Access and often fails. Use `launchctl` instead — it works reliably.

### 2. Install Tailscale

```bash
# Download + install via Homebrew cask
brew install --cask tailscale

# If brew cask fails (needs interactive sudo), use the cached pkg instead:
# brew fetch --cask tailscale
# sudo installer -pkg ~/Library/Caches/Homebrew/downloads/*Tailscale*.pkg -target /

# Launch Tailscale
open /Applications/Tailscale.app
```

Then: **click Log In in the Tailscale menu bar icon** and sign in to your Tailscale account. This step requires human interaction (OAuth + macOS VPN extension permission). Can't automate it.

Get your Mac's Tailscale IP:
```bash
tailscale ip -4
# → something like 100.x.x.x — note this, you'll need it in Termius
```

Tailscale auto-starts after login. To verify it's connected:
```bash
tailscale status
```

### 3. Generate an SSH key for Termius

```bash
ssh-keygen -t ed25519 -C "termius-phone" -f ~/.ssh/termius_phone -N ""
cat ~/.ssh/termius_phone.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys && chmod 700 ~/.ssh
```

### 4. Verify SSH works locally

```bash
ssh -i ~/.ssh/termius_phone $(whoami)@$(tailscale ip -4) echo "SSH works"
```

You should see `SSH works` printed back. If you get a connection refused, check that the SSH server is running (`lsof -i :22`).

### 5. Configure Termius on iPhone

You'll need the private key from step 3. Display it:
```bash
cat ~/.ssh/termius_phone
```

In **Termius on iPhone**:
1. **Keychain** tab → **+** → **Paste Key**
   - Label: `termius-phone`
   - Private Key: paste the full contents of `~/.ssh/termius_phone` (from `-----BEGIN` to `-----END`)
   - Leave Public Key, Passphrase, Certificate blank
   - Tap the checkmark (top right)

2. **Hosts** tab → **+** → **New Host**
   - Alias: `My Mac` (or your bot name)
   - Hostname: your Tailscale IP from step 2 (e.g. `100.116.19.90`)
   - Username: your Mac username (`whoami` to confirm)
   - SSH key: `termius-phone`
   - Tap **Save**

3. Tap the host to connect — you should get a terminal on your Mac.

> **Termius tip:** On the Connections screen, swipe left on a host to edit it. Tapping it directly opens the terminal immediately.

### 6. Install Tailscale on iPhone

Install from the App Store (free) and log in with the **same Tailscale account** as your Mac. Once both devices are on the network, the Tailscale IP works from anywhere — home WiFi, cellular, coffee shop, wherever.

---

## Reconnecting after Mac restart

- **SSH server**: stays enabled (launchd loads it on demand at boot)
- **Tailscale**: auto-starts after login (check menu bar — should show your IP)
- **Termius**: just tap your host — no reconfiguration needed

---

## Gotchas

- `sudo systemsetup -setremotelogin on` fails without Full Disk Access — use `launchctl load` instead (works without it)
- `sudo brew install --cask tailscale` fails (brew refuses to run as root) — install as your user, not root
- Tailscale login requires clicking through macOS VPN permission dialog — can't automate this step
- **Mac SSH is key-only by default** — no password auth. Don't try password in Termius; it will fail
- Tailscale must be running on **both** devices for the `100.x.x.x` address to work off home WiFi
- If you need to re-import the key to Termius: `cat ~/.ssh/termius_phone` → paste into Termius Keychain as above
- Local IP (e.g. `192.168.x.x`) only works on home WiFi — always use the Tailscale IP for off-network access

---

## Why Tailscale (not just a local IP)?

Your Mac's local IP (`192.168.x.x`) only works on your home WiFi. Tailscale creates a private mesh VPN — your Mac gets a stable `100.x.x.x` address that's reachable from anywhere, without port-forwarding or dynamic DNS. It's free for personal use (up to 100 devices) and takes about 5 minutes to set up.
