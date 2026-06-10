---
name: stock-images
description: >
  Fetch real stock photos + videos for the bot's output (covers, illustrations, b-roll).
  OPTIONAL — needs a free Pexels API key. Trigger when the bot needs a real photo/video of a
  generic subject. For real photos of a SPECIFIC person/place/event, prefer DuckDuckGo Images
  (see the web-search skill).
---

# stock-images — Pexels (free stock photos + videos)

**Optional + key-gated.** Pexels gives free, high-quality stock photos and videos. Good for
generic subjects (a desk, a city, "happy team"). For a *specific* real person/place/event,
DuckDuckGo Images (the `web-search` skill) returns more authentic results.

## Setup (the key pattern)
On setup, **ask the user for their Pexels API key** (free at <https://www.pexels.com/api/>) and
store it in `~/.claude/secrets.local` as `PEXELS_API_KEY`. The bot reads it from there — never
hardcode it. (This same pattern applies to every API-key tool: ask once on setup → store in
secrets → read at runtime.)

## Usage
```bash
# Photos
curl -s "https://api.pexels.com/v1/search?query=<query>&per_page=10" \
  -H "Authorization: $PEXELS_API_KEY"        # → photos[].src.original
# Videos
curl -s "https://api.pexels.com/videos/search?query=<query>&per_page=10" \
  -H "Authorization: $PEXELS_API_KEY"        # → videos[].video_files[].link
```
Pick a result, download the file, use it. Free tier is generous (rate-limited, not paid).

## Notes
- Pexels CDN URLs are broadly reachable (including from servers) — handy when other image hosts
  are blocked.
- Attribution isn't required but is appreciated.
