#!/usr/bin/env python3
"""
wiki_utils.py — programmatic API for the loopling brain.

The CLI (`wiki_index.py` / `wiki_search.py`) is for keyword + semantic search. This module
is the programmatic layer a session script imports to read/write notes and track coverage —
so the bot can file knowledge and remember what it has already done, in code.

    import sys; sys.path.insert(0, "brain")
    from wiki_utils import get_index, search_wiki, write_entry, update_entry, coverage_check, add_coverage

After writing notes, rebuild the search index:  python3 brain/wiki_index.py
"""
from __future__ import annotations

import re
import subprocess
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).parent
WIKI_DIR = HERE / "wiki"
INDEX_FILE = WIKI_DIR / "_index.md"
COVERAGE_FILE = WIKI_DIR / "_coverage.md"


def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9_]", "_", name.lower().strip()).strip("_")


def _today() -> str:
    # NOTE: callers can pass an explicit date; this is a best-effort fallback.
    return datetime.now().strftime("%Y-%m-%d")


# ── read ──────────────────────────────────────────────────────────────────────

def get_index() -> str:
    """The _index.md catalog — read at session start for the lay of the land."""
    return INDEX_FILE.read_text() if INDEX_FILE.exists() else "(wiki index empty)"


def entry_path(category: str, name: str) -> Path:
    return WIKI_DIR / category / f"{_slug(name)}.md"


def read_entry(category: str, name: str) -> str | None:
    p = entry_path(category, name)
    return p.read_text() if p.exists() else None


def list_entries(category: str | None = None) -> list[Path]:
    if category:
        return sorted((WIKI_DIR / category).glob("*.md"))
    return sorted(f for f in WIKI_DIR.rglob("*.md") if not f.name.startswith("_"))


def search_wiki(query: str, top_n: int = 5) -> list[dict]:
    """Lightweight keyword search over note files (programmatic). For richer
    keyword+semantic search, shell out to wiki_search.py instead."""
    terms = query.lower().split()
    results = []
    for md in WIKI_DIR.rglob("*.md"):
        if md.name.startswith("_"):
            continue
        text = md.read_text()
        low = text.lower()
        score = sum(low.count(t) for t in terms)
        if score:
            idx = next((low.find(t) for t in terms if low.find(t) >= 0), 0)
            results.append({
                "category": md.relative_to(WIKI_DIR).parts[0] if len(md.relative_to(WIKI_DIR).parts) > 1 else "",
                "name": md.stem.replace("_", " ").title(),
                "path": str(md),
                "score": score,
                "snippet": text[max(0, idx - 50):idx + 150].strip(),
            })
    results.sort(key=lambda r: r["score"], reverse=True)
    return results[:top_n]


# ── write ─────────────────────────────────────────────────────────────────────

def write_entry(category: str, name: str, content: str, reindex: bool = False) -> Path:
    """Write/overwrite a note + add it to _index.md. Set reindex=True to rebuild the
    search index now (or run `python3 brain/wiki_index.py` later)."""
    p = entry_path(category, name)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    _update_index(category, name, p)
    if reindex:
        reindex_now()
    return p


def update_entry(category: str, name: str, facts: list[str] | None = None,
                 sources: list[str] | None = None, notes: str = "", date: str = "") -> Path:
    """Merge new facts/sources/notes into a note (create if missing) — appends to
    ## Facts / ## Sources / ## Notes without clobbering existing content."""
    day = date or _today()
    content = read_entry(category, name) or f"# {name}\n"
    for header, items in (("## Facts", facts), ("## Sources", sources)):
        if items:
            block = "\n".join(f"- {x} *(added {day})*" for x in items)
            content = (content.replace(f"{header}\n", f"{header}\n{block}\n")
                       if header in content else content + f"\n{header}\n{block}\n")
    if notes:
        content = (content.replace("## Notes\n", f"## Notes\n- {notes} *(added {day})*\n")
                   if "## Notes" in content else content + f"\n## Notes\n- {notes} *(added {day})*\n")
    return write_entry(category, name, content)


def reindex_now():
    subprocess.run(["python3", str(HERE / "wiki_index.py")], check=False)


# ── coverage (anti-repetition: "have I already done this?") ───────────────────

def coverage_check(topic: str) -> list[str]:
    """Has this topic/task been covered before? Returns matching coverage lines."""
    if not COVERAGE_FILE.exists():
        return []
    t = topic.lower()
    return [ln.strip() for ln in COVERAGE_FILE.read_text().splitlines()
            if t in ln.lower() and ln.strip().startswith("|")]


def add_coverage(topic: str, note: str = "", date: str = "", category: str = ""):
    """Log that the bot did/covered something, so future sessions don't repeat it."""
    day = date or _today()
    if COVERAGE_FILE.exists():
        content = COVERAGE_FILE.read_text()
    else:
        content = ("# Coverage log\n\nWhat the bot has already done/covered — checked to avoid "
                   "repeating work. One row per item.\n\n| Date | Topic | Category | Note |\n"
                   "|------|-------|----------|------|\n")
    content += f"| {day} | {topic} | {category} | {note} |\n"
    COVERAGE_FILE.write_text(content)


# ── index maintenance ─────────────────────────────────────────────────────────

def _update_index(category: str, name: str, path: Path):
    day = _today()
    rel = path.relative_to(WIKI_DIR)
    if INDEX_FILE.exists():
        content = INDEX_FILE.read_text()
    else:
        content = ("# Wiki Index\n\nLLM-maintained knowledge base. Read at session start.\n\n"
                   "| Title | Category | Path | Date |\n|-------|----------|------|------|\n")
    row = f"| {name} | {category} | {rel} | {day} |"
    if re.search(rf"\|[^\n]*{re.escape(str(rel))}[^\n]*\|", content):
        content = re.sub(rf"\|[^\n]*{re.escape(str(rel))}[^\n]*\|[^\n]*\n", row + "\n", content)
    else:
        content += row + "\n"
    INDEX_FILE.write_text(content)


if __name__ == "__main__":
    print("Wiki dir:", WIKI_DIR)
    print("Entries:", len(list_entries()))
    print(get_index()[:200])
