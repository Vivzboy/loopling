#!/usr/bin/env python3
"""Fetch a URL past Cloudflare Turnstile with Scrapling, print clean content.

Run with the scrapling venv:
  ~/claude-apps/bizzy/data/experiments/scrapling-trial/.venv/bin/python scrape.py <url> [options]

Options:
  --plain             fast HTTP fetch, no browser (for unguarded sites)
  --html              print raw HTML instead of clean text
  --selector CSS      print the text of elements matching a CSS selector
  --no-solve          stealth fetch WITHOUT actively solving Cloudflare (rarely wanted)

Default = StealthyFetcher with solve_cloudflare=True (the mode that beats Turnstile).
"""
import argparse
import sys


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("url")
    ap.add_argument("--plain", action="store_true", help="fast HTTP fetch, no browser")
    ap.add_argument("--html", action="store_true", help="print raw HTML")
    ap.add_argument("--selector", help="CSS selector; print matching elements' text")
    ap.add_argument("--no-solve", action="store_true", help="stealth fetch without solving Cloudflare")
    args = ap.parse_args()

    from scrapling.fetchers import Fetcher, StealthyFetcher

    if args.plain:
        page = Fetcher.get(args.url, timeout=30)
    else:
        page = StealthyFetcher.fetch(
            args.url,
            headless=True,
            solve_cloudflare=not args.no_solve,
            network_idle=True,
            timeout=90000,
        )

    status = getattr(page, "status", "?")
    print(f"[status {status}]", file=sys.stderr)

    if args.selector:
        for el in page.css(args.selector):
            print(el.get_all_text(strip=True))
    elif args.html:
        print(getattr(page, "html_content", "") or "")
    else:
        print(page.get_all_text(strip=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
