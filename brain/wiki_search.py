#!/usr/bin/env python3
"""
loopling — wiki search (keyword FTS + semantic vector).

Usage:
  python3 brain/wiki_search.py "your query"        # both keyword + semantic
  python3 brain/wiki_search.py "your query" --fts    # keyword only (fast)
  python3 brain/wiki_search.py "your query" --vector # semantic only (by meaning)
  python3 brain/wiki_search.py "your query" -n 5     # top 5
"""

import argparse
import sqlite3
from pathlib import Path

HERE       = Path(__file__).parent
FTS_DB     = HERE / "wiki.db"
CHROMA_DIR = HERE / "wiki_chroma"
EMBED_MODEL = "all-MiniLM-L6-v2"

def fts_search(query: str, n: int = 5) -> list:
    if not FTS_DB.exists():
        print("  FTS index not built yet — run: python3 brain/wiki_index.py")
        return []
    conn = sqlite3.connect(FTS_DB)
    try:
        rows = conn.execute("""
            SELECT id, title, category, snippet(wiki, 3, '[', ']', '…', 12), rank
            FROM wiki WHERE wiki MATCH ? ORDER BY rank LIMIT ?
        """, (query, n)).fetchall()
    except sqlite3.OperationalError:
        like = f"%{query}%"
        rows = conn.execute("""
            SELECT id, title, category, substr(body,1,160), 0 FROM wiki
            WHERE title LIKE ? OR body LIKE ? LIMIT ?
        """, (like, like, n)).fetchall()
    conn.close()
    return [{"id": r[0], "title": r[1], "category": r[2], "snippet": r[3]} for r in rows]

def vector_search(query: str, n: int = 5) -> list:
    try:
        import chromadb
        from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
    except ImportError:
        print("  Vector: chromadb not installed")
        return []
    if not CHROMA_DIR.exists():
        print("  Vector index not built yet — run: python3 brain/wiki_index.py")
        return []
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    ef = SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)
    try:
        collection = client.get_collection("wiki", embedding_function=ef)
    except Exception:
        print("  Vector: no wiki collection — run: python3 brain/wiki_index.py")
        return []
    if collection.count() == 0:
        return []
    res = collection.query(query_texts=[query], n_results=min(n, collection.count()))
    out = []
    for i, doc_id in enumerate(res["ids"][0]):
        meta = res["metadatas"][0][i]
        out.append({"id": doc_id, "title": meta["title"], "category": meta["category"],
                    "score": round(1 - res["distances"][0][i], 3)})
    return out

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("--fts", action="store_true", help="Keyword only")
    parser.add_argument("--vector", action="store_true", help="Semantic only")
    parser.add_argument("-n", type=int, default=5)
    args = parser.parse_args()

    do_fts    = args.fts or not args.vector
    do_vector = args.vector or not args.fts

    if do_fts:
        print(f"\n── Keyword results for: '{args.query}' ──")
        rows = fts_search(args.query, args.n)
        for r in rows:
            print(f"  [{r['category']}] {r['title']}")
            print(f"    {r['snippet']}")
            print(f"    → brain/wiki/{r['id']}")
        if not rows:
            print("  No keyword matches.")

    if do_vector:
        print(f"\n── Semantic results for: '{args.query}' ──")
        rows = vector_search(args.query, args.n)
        for r in rows:
            print(f"  [{r['category']}] {r['title']}  (score: {r['score']})")
            print(f"    → brain/wiki/{r['id']}")
        if not rows:
            print("  No semantic matches.")

if __name__ == "__main__":
    main()
