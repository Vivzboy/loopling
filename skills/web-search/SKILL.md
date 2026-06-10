---
name: web-search
description: >
  How the bot searches the open web for generic research — web search + image search + page
  scraping. Trigger when it needs to find something online, gather facts/links, or pull
  images that aren't already in its wiki. Pairs with last30days (multi-source deep research);
  this is the quick, free "search the web" layer.
---

# web-search — web + image search + scraping

**Always search the wiki first** (`python3 brain/wiki_search.py "…"`). Only hit the web for
what you don't already know. Two tiny, free tools cover most of it; one API replaces them when
you're on a server.

## 1. Web search — `httpx` → DuckDuckGo HTML (the default)
A plain HTTP request, no browser overhead — fast. Returns clean HTML you can parse:
```python
import httpx
from bs4 import BeautifulSoup
q = "your query"
r = httpx.get(f"https://duckduckgo.com/html/?q={q.replace(' ', '+')}",
              headers={"User-Agent": "Mozilla/5.0"}, timeout=15, follow_redirects=True)
soup = BeautifulSoup(r.text, "html.parser")
results = [(a.get_text(strip=True), a["href"]) for a in soup.select("a.result__a")]
```
This is the default research tool — `httpx` + `BeautifulSoup` handles most news/info sites.

## 2. Image search — DuckDuckGo Images
Real photos (people, places, events) — far better than AI/stock for authentic imagery:
```python
import httpx, re
def ddg_image_urls(query, n=10):
    h = {"User-Agent": "Mozilla/5.0"}
    # DDG requires a one-shot token (vqd) before the image endpoint
    tok = re.search(r"vqd=([\d-]+)&",
        httpx.get(f"https://duckduckgo.com/?q={query.replace(' ','+')}", headers=h).text)
    vqd = tok.group(1) if tok else None
    j = httpx.get("https://duckduckgo.com/i.js",
        params={"l":"us-en","o":"json","q":query,"vqd":vqd,"f":"","p":"1"}, headers=h).json()
    return [r["image"] for r in j.get("results", [])[:n]]
```

## 3. Escalate to `agent-browser` for JS-heavy pages
When `httpx` returns empty/broken content (dynamic SPAs), or you need to click/scroll a real
search-results page, use the bundled `agent-browser` skill (`open` → `wait --load networkidle`
→ `snapshot -i -c` / `get html`).

## 4. Zero-setup quick lookup — `WebSearch` / `WebFetch`
Claude Code's built-in `WebSearch` (query → results) and `WebFetch` (URL → content) need no
deps. Fine as a first reach for a one-off lookup.

## 5. Search APIs — clean JSON results, image search, and the server fix
For structured results, reliable **image search**, or when running on a **server**, use a
search API (set the key in `~/.claude/secrets.local`):

| Provider | Good for | Notes |
|----------|----------|-------|
| **Serper** (`serper.dev`) | **Google web + Google Images** | Cheapest path to real Google + image results; one key does both. |
| **Tavily** (`tavily.com`) | LLM-tuned web search (clean snippets) | Built for agents; concise results. |
| **Brave Search API** | Independent web index | Privacy-friendly, no Google dependency. |
| **Exa** (`exa.ai`) | Semantic / neural search | "Find pages like this" by meaning. |

Example (Serper — web + images in one provider):
```bash
curl -s https://google.serper.dev/search  -H "X-API-KEY: $SERPER_API_KEY" \
  -H "Content-Type: application/json" -d '{"q":"<query>"}'   # web
curl -s https://google.serper.dev/images  -H "X-API-KEY: $SERPER_API_KEY" \
  -H "Content-Type: application/json" -d '{"q":"<query>"}'   # images
```

### ⚠️ Why a server needs one
**Raw DuckDuckGo / Google scraping (#1 + #2) is bot-blocked from datacenter IPs** — fine
locally on your Mac (the normal loopling setup), blocked from a cloud server. So: local →
the free DDG tools are great; on a **server** → use a search API (Serper/Tavily/Brave/Exa).

## Always: file what you find
Per the soul's "research → wiki" rule, anything worth keeping goes into `brain/wiki/` so the
bot never re-searches it.
