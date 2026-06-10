#!/usr/bin/env python3
"""
tg_send.py — send a long Telegram text message, splitting into ≤4096-char chunks at
line boundaries (Telegram rejects messages over 4096 chars). Every agent that reports
back to Telegram eventually hits this.

Config via env (same as voice/tts_say.py):
    LOOPLING_BOT_TOKEN, LOOPLING_OWNER_CHAT_ID

Usage:
    python3 voice/tg_send.py "a very long\\nmultiline message"
    some_command | python3 voice/tg_send.py            # reads from stdin
"""
import os, sys, time, urllib.request, urllib.parse

BOT_TOKEN = os.environ.get("LOOPLING_BOT_TOKEN", "")
CHAT_ID   = os.environ.get("LOOPLING_OWNER_CHAT_ID", "")
MAX_CHARS = 4000  # margin below Telegram's 4096


def send_chunk(text: str):
    if not BOT_TOKEN or not CHAT_ID:
        print("(skip: set LOOPLING_BOT_TOKEN + LOOPLING_OWNER_CHAT_ID)", file=sys.stderr)
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": CHAT_ID, "text": text}).encode()
    urllib.request.urlopen(url, data=data, timeout=10)


def send(message: str):
    if len(message) <= MAX_CHARS:
        send_chunk(message)
        return
    chunk = ""
    for line in message.split("\n"):
        candidate = f"{chunk}\n{line}" if chunk else line
        if len(candidate) > MAX_CHARS:
            if chunk:
                send_chunk(chunk)
                time.sleep(0.5)
            chunk = line
        else:
            chunk = candidate
    if chunk:
        send_chunk(chunk)


if __name__ == "__main__":
    send(sys.argv[1] if len(sys.argv) > 1 else sys.stdin.read())
