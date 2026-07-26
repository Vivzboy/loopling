#!/usr/bin/env python3
"""Reusable Notion upsert client. Copied from the Zuttle outreach sync.

Idempotent: matches on operator name, updates the row if it already exists,
creates it if it does not. Safe to re-run after every scrape.

    export ZUTTLE_NOTION_TOKEN=ntn_...        # or put it in ~/.claude/secrets.local
    python3 bin/notion_push.py --dry-run      # show what would change
    python3 bin/notion_push.py                # push everything
    python3 bin/notion_push.py --stage new    # only untouched leads
    python3 bin/notion_push.py --exclude-skip # leave airports/bus lines out

Notes that cost time to learn:
- The token sees NOTHING until the page is shared with the connection in Notion
  (page menu -> Add connections). Empty results almost always means that, not a bug.
- Select options are exact-match. A casing drift like "Or Tambo" vs "OR Tambo"
  silently creates a second option instead of erroring, hence AREA_FIXES.
- Rate limit is ~3 requests/sec per connection. THROTTLE below keeps us under it;
  429s are retried using the Retry-After header rather than a fixed sleep.
- Updates do NOT touch Stage, Decision Maker, Contact or Notes. Those are the columns
  the team edits in Notion, and the CSV is usually the stale side. Pass
  --overwrite-human when the CSV really is authoritative. New rows get everything.
- Matching is on operator name. Rename in the register, never in Notion, or the next
  push creates a duplicate instead of updating.
"""
import argparse
import csv
import json
import os
import pathlib
import sys
import time
import urllib.error
import urllib.request

API = "https://api.notion.com/v1"
VERSION = "2022-06-28"
# API version 2022-06-28 talks to databases, not the newer "data source" concept.
# Use the DATABASE id here, not the collection:// id the MCP hands back.
DATABASE_ID = os.environ.get("NOTION_DATABASE_ID", "")  # set me
THROTTLE = 0.34  # seconds between requests, ~3/sec

REPO = pathlib.Path(__file__).resolve().parent.parent
REGISTER = REPO / "data/leads/leads_register.csv"
SECRETS = pathlib.Path.home() / ".claude/secrets.local"
TOKEN_KEY = os.environ.get("NOTION_TOKEN_KEY", "NOTION_TOKEN")

AREA_FIXES = {"Or Tambo Airport": "OR Tambo Airport"}
VALID_STAGES = {"new", "qualified", "enriched", "contacted", "replied",
                "replied-warm", "onboarding", "listed", "skip"}


def token() -> str:
    t = os.environ.get(TOKEN_KEY)
    if t:
        return t.strip()
    if SECRETS.exists():
        for line in SECRETS.read_text().splitlines():
            if line.startswith(f"{TOKEN_KEY}="):
                return line.split("=", 1)[1].strip()
    sys.exit(f"No {TOKEN_KEY} in the environment or ~/.claude/secrets.local")


def call(method: str, path: str, body=None, tries: int = 4):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"{API}{path}", data=data, method=method, headers={
        "Authorization": f"Bearer {token()}",
        "Notion-Version": VERSION,
        "Content-Type": "application/json",
    })
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(req) as r:
                time.sleep(THROTTLE)
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < tries - 1:
                time.sleep(float(e.headers.get("Retry-After", 1)) + 0.5)
                continue
            raise SystemExit(f"{method} {path} failed {e.code}: {e.read().decode()[:400]}")
    raise SystemExit(f"{method} {path} gave up after {tries} attempts")


def existing_rows() -> dict:
    """Map lowercased operator name -> page id, for the whole database."""
    out, cursor = {}, None
    while True:
        body = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        res = call("POST", f"/databases/{DATABASE_ID}/query", body)
        for page in res["results"]:
            title = page["properties"].get("Operator", {}).get("title") or []
            if title:
                out[title[0]["plain_text"].strip().lower()] = page["id"]
        if not res.get("has_more"):
            return out
        cursor = res["next_cursor"]


# Columns a human edits in Notion. bin/leads.py already refuses to clobber these on
# a re-scrape; the same rule has to hold in this direction or a push silently undoes
# a co-founder's call notes and stage change.
HUMAN_FIELDS = {"Stage", "Decision Maker", "Contact", "Notes"}


def props_for(row: dict) -> dict:
    def text(v):
        return {"rich_text": [{"text": {"content": v[:2000]}}]}

    stage = row["stage"].strip() or "new"
    if stage not in VALID_STAGES:
        stage = "new"
    area = AREA_FIXES.get(row["area"].strip(), row["area"].strip())

    p = {"Operator": {"title": [{"text": {"content": row["name"][:2000]}}]},
         "Stage": {"select": {"name": stage}}}
    if area:
        p["Area"] = {"select": {"name": area}}
    for col, key in (("category", "Category"), ("decision_maker", "Decision Maker"),
                     ("contact", "Contact"), ("notes", "Notes")):
        if row.get(col, "").strip():
            p[key] = text(row[col].strip())
    for col, key in (("rating", "Rating"), ("review_count", "Reviews")):
        if row.get(col, "").strip():
            try:
                p[key] = {"number": float(row[col])}
            except ValueError:
                pass
    if row.get("phone", "").strip():
        p["Phone"] = {"phone_number": row["phone"].strip()}
    if row.get("website", "").strip():
        p["Website"] = {"url": row["website"].strip()}
    if row.get("updated", "").strip():
        p["Updated"] = {"date": {"start": row["updated"].strip()}}
    return p


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage")
    ap.add_argument("--exclude-skip", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--overwrite-human", action="store_true",
                    help="also push stage/decision_maker/contact/notes over whatever "
                         "is in Notion. Off by default: those are the columns the team "
                         "edits by hand, and the CSV is usually the stale side.")
    args = ap.parse_args()

    rows = list(csv.DictReader(REGISTER.open()))
    if args.stage:
        rows = [r for r in rows if r["stage"] == args.stage]
    if args.exclude_skip:
        rows = [r for r in rows if r["stage"] != "skip"]

    print(f"{len(rows)} rows from the register")
    have = existing_rows()
    print(f"{len(have)} already in Notion")

    created = updated = 0
    for r in rows:
        key = r["name"].strip().lower()
        props = props_for(r)
        if key in have:
            if not args.overwrite_human:
                props = {k: v for k, v in props.items() if k not in HUMAN_FIELDS}
            if not args.dry_run and props:
                call("PATCH", f"/pages/{have[key]}", {"properties": props})
            updated += 1
        else:
            if not args.dry_run:
                call("POST", "/pages", {"parent": {"database_id": DATABASE_ID},
                                        "properties": props})
            created += 1
        if (created + updated) % 25 == 0:
            print(f"  ...{created + updated}/{len(rows)}")

    verb = "would create/update" if args.dry_run else "created/updated"
    print(f"{verb}: {created} new, {updated} existing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
