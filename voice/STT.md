# STT — transcribing inbound Telegram voice notes (Whisper)

Your loopling can *listen*: when the owner sends a Telegram voice note, transcribe it with [Whisper](https://github.com/openai/whisper) (on-device, free) and respond to the text normally.

## Install

```bash
brew install openai-whisper        # or: pip install -U openai-whisper  (needs ffmpeg)
command -v whisper                 # confirm (often /opt/homebrew/bin/whisper)
```

## The flow (the bot does this when a voice note arrives)

A Telegram voice note arrives as a `<channel ... attachment_file_id="...">` message (or a file in the channel `inbox/`).

1. **Fetch the audio** — use the Telegram MCP `download_attachment` tool with the `attachment_file_id` → returns a local `.ogg`/`.oga`/`.m4a` path.
2. **Transcribe:**
   ```bash
   whisper /tmp/voice.ogg --model base --language en --output_format txt --output_dir /tmp/
   cat /tmp/voice.txt
   ```
3. **Respond** to the transcribed text like any other message.

## Notes

- **Models:** `base` (~5s, fine for most), `small` (more accurate), `large` (best). Start with `base`.
- **Language:** omit `--language` to auto-detect (good for mixed / non-English speech).
- **Word timestamps** (if you ever need them, e.g. captions): add `--word_timestamps True --output_format json`.

Reference this file from the soul so the bot knows to transcribe voice notes automatically.
