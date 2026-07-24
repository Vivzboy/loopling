# Scrapling Skill

**What:** A Python scraper that gets past **Cloudflare Turnstile / "Just a moment…" managed challenges** that block Firecrawl and browser-use. Also has self-healing selectors (they auto-relocate when a site changes its HTML, so scrapers survive redesigns), automatic proxy rotation, and it ships a CLI + an MCP server.

**When to reach for it (the trigger):** a page is behind a Cloudflare Turnstile / managed challenge and Firecrawl / agent-browser / browser-use come back empty, 403, or a "Just a moment…" page. This is the fallback when the fast tools get walled.

**When NOT to:** it does **not** beat enterprise-grade bot management (G2 / Crunchbase level: DataDome, PerimeterX, CF Enterprise). Those return a hard 403 that is not a solvable challenge, and nothing off-the-shelf reliably beats them. Also don't use it as the default, it launches a stealth browser and waits to solve, so it's slower than Firecrawl. Fast tools first, Scrapling when they fail.

## Install

Install into a venv (Scrapling 0.4.11+ needs Python 3.10+):
```bash
pip install "scrapling[fetchers]"   # the [fetchers] extra is REQUIRED (base install has no browser fetchers)
scrapling install                    # downloads camoufox / playwright browsers (~100MB+, one-time)
```

## Helper script (fastest path)

```bash
VENV=<your-venv>/bin/python
# stealth + solve Cloudflare (default) -> clean text
$VENV skills/scrapling/scrape.py "https://guarded-site.co.za"
$VENV .../scrape.py "https://site" --html                 # raw HTML instead of text
$VENV .../scrape.py "https://site" --selector "h2.title"  # just the elements matching a CSS selector
$VENV .../scrape.py "https://unguarded-site" --plain       # fast HTTP fetch, no browser
```

## Python API (the key bit)

```python
from scrapling.fetchers import Fetcher, StealthyFetcher

# THE one that beats Turnstile. solve_cloudflare=True is OFF by default — you MUST pass it.
page = StealthyFetcher.fetch(url, headless=True, solve_cloudflare=True, network_idle=True, timeout=90000)

# fast plain HTTP (no browser) for unguarded pages
page = Fetcher.get(url, timeout=30)

page.status                      # HTTP status
page.html_content                # raw HTML
page.get_all_text(strip=True)    # clean text
page.css("h2.title")             # CSS select -> elements (.get_all_text(), .attrib['href'])
page.css_first("a")              # first match
```

## Gotchas (from the 2026-07-24 trial — read this)

- **`solve_cloudflare=True` is OFF by default.** Without it, `StealthyFetcher` still gets 403'd by Cloudflare. This is the #1 mistake (I made it on the first trial run). Always pass it for guarded sites.
- **Base `pip install scrapling` has no fetchers.** You need `scrapling[fetchers]` + `scrapling install` for the browsers, else you get "install with extras" ModuleNotFoundError.
- **Proven:** it detected + solved a live Cloudflare Turnstile ("turnstile version discovered: embedded → Cloudflare captcha is solved"). That's the exact wall we hit with browser-use.
- **Does NOT beat** hard enterprise anti-bot (G2, Crunchbase both hard-403'd it — those aren't solvable Turnstile challenges).
- First stealth run is slow (browser launch + challenge solve). Budget 30–90s per guarded page.
- Update this skill's gotchas whenever a new SA site works or fails, so we learn what it can/can't crack.

## MCP

Scrapling ships an MCP server (`scrapling mcp`). Wire into `.mcp.json` for tool-level access from a session (no scripts) when you want it always-on.

## Where it sits in the research stack

Firecrawl (fast, clean markdown/JSON) → **if blocked by Turnstile/managed challenge → Scrapling** → still 403 (enterprise) → hard target, needs residential proxies or a different approach. agent-browser/browser-use for screenshots + authenticated sessions.
