#!/usr/bin/env python3
"""
loopling — voice notes (on-device TTS via Supertonic) → optional Telegram send.

Why Supertonic over macOS `say`: natural cadence, on-device (no API key, no per-char
cost), ~5x realtime, 31 languages. First run downloads ~260MB ONNX models (then cached).

Config via env vars (or edit the defaults below):
    LOOPLING_BOT_TOKEN     Telegram bot token (for --send)
    LOOPLING_OWNER_CHAT_ID Telegram chat id to send to (for --send)
    LOOPLING_TTS_PYTHON    Python with `supertonic` + `soundfile` installed
                           (defaults to this repo's brain/.venv if present, else python3)

Usage:
    python3 voice/tts_say.py "Text to speak"                    # -> /tmp/loopling_vn.ogg
    python3 voice/tts_say.py "Text" --send                      # also send to Telegram
    python3 voice/tts_say.py "Text" --voice F4 --send           # voices M1-M5 / F1-F5
    python3 voice/tts_say.py --file note.txt --send             # read text from a file

Deps:  pip install supertonic soundfile   ;   brew install ffmpeg
"""
import argparse, os, subprocess, sys, tempfile
from pathlib import Path

DEFAULT_VOICE = "M4"
BOT_TOKEN     = os.environ.get("LOOPLING_BOT_TOKEN", "")
OWNER_CHAT_ID = os.environ.get("LOOPLING_OWNER_CHAT_ID", "")

def _python_bin() -> str:
    env = os.environ.get("LOOPLING_TTS_PYTHON")
    if env:
        return env
    venv = Path(__file__).resolve().parent.parent / "brain" / ".venv" / "bin" / "python"
    return str(venv) if venv.exists() else "python3"


def synthesize(text: str, voice: str, out_wav: Path) -> float:
    script = f"""
from supertonic import TTS
tts = TTS(auto_download=True)
style = tts.get_voice_style(voice_name={voice!r})
wav, dur = tts.synthesize({text!r}, voice_style=style)
tts.save_audio(wav, {str(out_wav)!r})
print(float(dur[0]))
"""
    result = subprocess.run([_python_bin(), "-c", script], check=True, capture_output=True, text=True)
    return float(result.stdout.strip().splitlines()[-1])


def wav_to_ogg(in_wav: Path, out_ogg: Path) -> None:
    subprocess.run(["ffmpeg", "-y", "-i", str(in_wav), "-c:a", "libopus", "-b:a", "64k", str(out_ogg)],
                   check=True, capture_output=True)


def send_telegram_voice(ogg_path: Path, caption: str = "") -> None:
    if not BOT_TOKEN or not OWNER_CHAT_ID:
        print("  (skip send: set LOOPLING_BOT_TOKEN + LOOPLING_OWNER_CHAT_ID)", file=sys.stderr)
        return
    cmd = ["curl", "-s", "-X", "POST", f"https://api.telegram.org/bot{BOT_TOKEN}/sendVoice",
           "-F", f"chat_id={OWNER_CHAT_ID}", "-F", f"voice=@{ogg_path}"]
    if caption:
        cmd += ["-F", f"caption={caption}"]
    subprocess.run(cmd, check=True, capture_output=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("text", nargs="?")
    ap.add_argument("--file")
    ap.add_argument("--voice", default=DEFAULT_VOICE)
    ap.add_argument("--out", default="/tmp/loopling_vn.ogg")
    ap.add_argument("--send", action="store_true")
    ap.add_argument("--caption", default="")
    args = ap.parse_args()

    text = Path(args.file).read_text().strip() if args.file else args.text
    if not text:
        ap.error("provide TEXT or --file")

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        wav_path = Path(tmp.name)
    try:
        print(f"Synthesizing ({len(text)} chars, voice {args.voice})...", file=sys.stderr)
        dur = synthesize(text, args.voice, wav_path)
        ogg_path = Path(args.out)
        wav_to_ogg(wav_path, ogg_path)
        print(f"Generated {dur:.2f}s -> {ogg_path}")
        if args.send:
            send_telegram_voice(ogg_path, args.caption)
            print("Sent to Telegram" if BOT_TOKEN and OWNER_CHAT_ID else "Not sent (no creds)")
    finally:
        wav_path.unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
