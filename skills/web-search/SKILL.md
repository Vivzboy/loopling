---
name: web-search
description: >
  How the bot searches + scrapes the web for generic research — web search, image search,
  and page scraping. Trigger when the bot needs to find something online, gather facts/links,
  pull images, or read a page that isn't already in its wiki. Use ALONGSIDE last30days
  (multi-source deep research) — this is the quick "search the open web" layer.
---

# web-search — generic web + image search + scraping

The bot's research stack has three layers. **Always search the wiki first** (`brain/wiki_search.py`)
— only hit the web for what you don't already know.

## 1. Built-in (no setup) — `WebSearch` + `WebFetch`
Claude Code's native `WebSearch` (a query → results) and `WebFetch` (a URL → its content)
need nothing. Best first reach for a quick lookup or to read a known page.

## 2. Scrape / search any page — `agent-browser` (bundled skill)
For anything `WebFetch` can't render (SPAs, dynamic content), or to drive a real search-results
page and pull structured results/links/images:
```bash
agent-browser --profile "Default" batch \
  "open https://duckduckgo.com/?q=<query>" \
  "wait --load networkidle" \
  "snapshot -i -c"
agent-browser --profile "Default" get html       # then parse links/images
```
Free, and on a Mac (local) DuckDuckGo/Google/Bing search pages work fine. See `skills/agent-browser/`.

## 3. Web + image search APIs (clean, programmatic, server-safe)
When you want structured JSON results — or **image search** — use a search API. Set the key in
`~/.claude/secrets.local` and call it (curl / the provider SDK). Options:

| Provider | Good for | Notes |
|----------|----------|-------|
| **Serper** (`serper.dev`) | **Google web + Google Images** | Cheapest path to real Google + image results; one key does both. |
| **Tavily** (`tavily.com`) | LLM-tuned web search (clean snippets) | Built for agents; concise results. |
| **Brave Search API** | Independent web index | Privacy-friendly, no Google dependency. |
| **Exa** (`exa.ai`) | Semantic / neural search | "Find pages like this" by meaning. |

Example (Serper — web + images in one provider):
```bash
# Web
curl -s https://google.serper.dev/search -H "X-API-KEY: $SERPER_API_KEY" \
  -H "Content-Type: application/json" -d '{"q":"<query>"}'
# Images
curl -s https://google.serper.dev/images -H "X-API-KEY: $SERPER_API_KEY" \
  -H "Content-Type: application/json" -d '{"q":"<query>"}'
```

## ⚠️ Server vs local gotcha
**Direct DuckDuckGo / Google / Google-Images scraping is bot-blocked from datacenter IPs**
(it works fine from a home/Mac IP). So:
- Running **locally on your Mac** (the normal loopling setup) → agent-browser scraping is fine.
- Running from a **server / cloud** → use a **search API** (Serper/Tavily/Brave/Exa) instead;
  Bing and the APIs work from datacenters, raw Google/DDG scraping does not.

## Always: file what you find
Per the soul's "research → wiki" rule: anything worth keeping goes into `brain/wiki/` so the
bot never re-searches it. Search the wiki before reaching for any of the above.
