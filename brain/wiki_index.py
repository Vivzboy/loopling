#!/usr/bin/env python3
"""
loopling — wiki indexer.
Indexes all wiki markdown files into:
  1. SQLite FTS5 — keyword search
  2. ChromaDB    — vector/semantic search (local, no API key)

Usage:
  python3 brain/wiki_index.py            # index all wiki files
  python3 brain/wiki_index.py --rebuild  # wipe and reindex from scratch
"""

import argparse
import re
import sqlite3
from pathlib import Path

HERE       = Path(__file__).parent
WIKI_DIR   = HERE / "wiki"
FTS_DB     = HERE / "wiki.db"
CHROMA_DIR = HERE / "wiki_chroma"
EMBED_MODEL = "all-MiniLM-L6-v2"

# ── helpers ──────────────────────────────────────────────────────────────────

def parse_md(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    body = re.sub(r"^---.*?---\s*", "", text, flags=re.DOTALL)  # strip YAML frontmatter
    m = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
    title = m.group(1).strip() if m else path.stem.replace("-", " ").title()
    return {
        "id": str(path.relative_to(WIKI_DIR)),
        "title": title,
        "category": path.parent.name,
        "body": body.strip(),
        "path": str(path),
    }

def all_wiki_files():
    return [p for p in WIKI_DIR.rglob("*.md") if p.name != "_index.md"]

# ── SQLite FTS ────────────────────────────────────────────────────────────────

def build_fts(entries: list, rebuild: bool = False):
    conn = sqlite3.connect(FTS_DB)
    cur = conn.cursor()
    if rebuild:
        cur.execute("DROP TABLE IF EXISTS wiki")
        cur.execute("DROP TABLE IF EXISTS wiki_meta")
    cur.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS wiki USING fts5(
            id UNINDEXED, title, category UNINDEXED, body,
            tokenize = 'porter unicode61'
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS wiki_meta (
            id TEXT PRIMARY KEY, path TEXT, category TEXT, title TEXT
        )
    """)
    for e in entries:
        cur.execute("DELETE FROM wiki WHERE id = ?", (e["id"],))
        cur.execute("INSERT INTO wiki(id, title, category, body) VALUES (?,?,?,?)",
                    (e["id"], e["title"], e["category"], e["body"]))
        cur.execute("INSERT OR REPLACE INTO wiki_meta(id, path, category, title) VALUES (?,?,?,?)",
                    (e["id"], e["path"], e["category"], e["title"]))
    conn.commit()
    conn.close()
    print(f"  FTS: indexed {len(entries)} entries -> {FTS_DB.name}")

# ── ChromaDB vector search ────────────────────────────────────────────────────

def build_chroma(entries: list, rebuild: bool = False):
    try:
        import chromadb
        from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
    except ImportError:
        print("  Vector: chromadb not installed — skipping (keyword search still works)")
        return

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    ef = SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)
    if rebuild:
        try:
            client.delete_collection("wiki")
        except Exception:
            pass
    collection = client.get_or_create_collection("wiki", embedding_function=ef)

    if rebuild:
        ids_to_add = [e["id"] for e in entries]
    else:
        existing = set(collection.get()["ids"])
        ids_to_add = [e["id"] for e in entries if e["id"] not in existing]

    to_add = [e for e in entries if e["id"] in ids_to_add]
    if not to_add:
        print(f"  Vector: all {len(entries)} entries already indexed")
        return
    collection.add(
        ids=[e["id"] for e in to_add],
        documents=[f"{e['title']}\n\n{e['body']}" for e in to_add],
        metadatas=[{"category": e["category"], "title": e["title"], "path": e["path"]} for e in to_add],
    )
    print(f"  Vector: added {len(to_add)} entries -> {CHROMA_DIR.name}/")

# ── main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rebuild", action="store_true", help="Wipe and reindex everything")
    args = parser.parse_args()

    WIKI_DIR.mkdir(parents=True, exist_ok=True)
    entries = [parse_md(f) for f in all_wiki_files()]
    print(f"Indexing {len(entries)} wiki entries (rebuild={args.rebuild})...")
    build_fts(entries, rebuild=args.rebuild)
    build_chroma(entries, rebuild=args.rebuild)
    print("Done.")

if __name__ == "__main__":
    main()
