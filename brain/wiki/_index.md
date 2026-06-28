# Wiki Index

The bot's compounding knowledge base. **Read this at session start.** **Search before researching:**

```bash
python3 brain/wiki_search.py "your query"          # keyword + semantic
python3 brain/wiki_search.py "your query" --fts     # keyword only
python3 brain/wiki_search.py "your query" --vector  # semantic only
```

Entries: 1

| Title | Category | Path | Date |
|-------|----------|------|------|
| Session — Termius/Tailscale optional skill added | sessions | sessions/20260628-termius-tailscale-skill-added.md | 2026-06-28 |

---

## How the bot uses the wiki

1. **Before researching anything**, search here first — never re-learn a known fact or contradict a verified one.
2. **After learning anything**, write a note to `brain/wiki/<category>/<slug>.md`, add a row above, and re-index:
   ```bash
   python3 brain/wiki_index.py
   ```
3. Categories are just folders under `brain/wiki/` (starter set: `notes/`, `people/`, `concepts/`, `projects/`, `sessions/`). Add new ones freely.
   - **`sessions/`** is special — it's the bot's own diary. After any notable session (something built, decided, or investigated in depth), write an entry here: what was discussed, what was built, decisions + why, open threads. This is what gives the bot real long-term memory across sessions.

A note is one markdown file: a `# Title` heading, then the content. That's it.
