#!/usr/bin/env python3
"""
loopling — Todo Manager (SQLite-backed task list).

Usage:
    python3 todos/todos.py add "Title" [--project P] [--priority 1-3] [--due YYYY-MM-DD] [--notes "..."]
    python3 todos/todos.py list [--project P] [--all]
    python3 todos/todos.py done <id>
    python3 todos/todos.py cancel <id>
    python3 todos/todos.py edit <id> [--title T] [--project P] [--priority N] [--due D] [--notes N]
    python3 todos/todos.py summary          # short, Telegram-ready summary of open items
    python3 todos/todos.py projects         # list all projects

Priority: 1=high, 2=medium, 3=low (default 2). DB lives next to this file (todos.db).
"""
import sqlite3, argparse, sys, os
from datetime import date

DB = os.path.join(os.path.dirname(__file__), "todos.db")


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS todos (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT NOT NULL,
                project     TEXT DEFAULT 'general',
                status      TEXT DEFAULT 'open',   -- open | done | cancelled
                priority    INTEGER DEFAULT 2,      -- 1=high 2=medium 3=low
                due_date    TEXT,
                notes       TEXT,
                created_at  TEXT DEFAULT (datetime('now','localtime')),
                completed_at TEXT
            )
        """)


def cmd_add(args):
    init_db()
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO todos (title, project, priority, due_date, notes) VALUES (?,?,?,?,?)",
            (args.title, args.project or "general", args.priority or 2, args.due, args.notes))
        todo_id = cur.lastrowid
    print(f"✅ Added #{todo_id}: {args.title} [{args.project or 'general'}]")


def cmd_list(args):
    init_db()
    with get_db() as conn:
        q = "SELECT * FROM todos WHERE 1=1"; params = []
        if not args.all: q += " AND status='open'"
        if args.project: q += " AND project=?"; params.append(args.project)
        q += " ORDER BY priority ASC, due_date ASC NULLS LAST, id ASC"
        rows = conn.execute(q, params).fetchall()
    if not rows:
        print("No todos found."); return
    pl = {1: "🔴", 2: "🟡", 3: "🟢"}; sl = {"open": "[ ]", "done": "[x]", "cancelled": "[-]"}
    cur_proj = None
    for r in rows:
        if r["project"] != cur_proj:
            cur_proj = r["project"]; print(f"\n── {cur_proj.upper()} ──")
        due = f" (due {r['due_date']})" if r["due_date"] else ""
        notes = f"\n     {r['notes']}" if r["notes"] and args.all else ""
        print(f"  {sl.get(r['status'],'   ')} #{r['id']} {pl.get(r['priority'],'  ')} {r['title']}{due}{notes}")
    print()


def cmd_done(args):
    init_db()
    with get_db() as conn:
        row = conn.execute("SELECT * FROM todos WHERE id=?", (args.id,)).fetchone()
        if not row: print(f"No todo #{args.id}"); sys.exit(1)
        conn.execute("UPDATE todos SET status='done', completed_at=datetime('now','localtime') WHERE id=?", (args.id,))
    print(f"✅ Done: #{args.id} {row['title']}")


def cmd_cancel(args):
    init_db()
    with get_db() as conn:
        row = conn.execute("SELECT * FROM todos WHERE id=?", (args.id,)).fetchone()
        if not row: print(f"No todo #{args.id}"); sys.exit(1)
        conn.execute("UPDATE todos SET status='cancelled' WHERE id=?", (args.id,))
    print(f"➖ Cancelled: #{args.id} {row['title']}")


def cmd_edit(args):
    init_db()
    updates, params = [], []
    for field, val in [("title", args.title), ("project", args.project), ("priority", args.priority),
                       ("due_date", args.due), ("notes", args.notes)]:
        if val is not None: updates.append(f"{field}=?"); params.append(val)
    if not updates: print("Nothing to update."); return
    params.append(args.id)
    with get_db() as conn:
        conn.execute(f"UPDATE todos SET {', '.join(updates)} WHERE id=?", params)
    print(f"✏️  Updated #{args.id}")


def cmd_summary(args):
    init_db()
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM todos WHERE status='open' ORDER BY priority ASC, due_date ASC NULLS LAST, id ASC").fetchall()
    if not rows: print("No open todos."); return
    today = date.today().isoformat()
    overdue = [r for r in rows if r["due_date"] and r["due_date"] < today]
    rest = [r for r in rows if not (r["due_date"] and r["due_date"] < today)]
    lines = [f"📋 Open todos ({len(rows)} total)"]
    if overdue:
        lines.append(f"\n🚨 Overdue ({len(overdue)}):")
        for r in overdue: lines.append(f"  #{r['id']} {r['title']} [{r['project']}] — due {r['due_date']}")
    by_project = {}
    for r in rest: by_project.setdefault(r["project"], []).append(r)
    for proj, items in sorted(by_project.items()):
        preview = ", ".join(f"#{r['id']} {r['title']}" for r in items[:3])
        suffix = f" +{len(items)-3} more" if len(items) > 3 else ""
        lines.append(f"\n{proj}: {preview}{suffix}")
    print("\n".join(lines))


def cmd_projects(args):
    init_db()
    with get_db() as conn:
        rows = conn.execute("SELECT project, COUNT(*) n FROM todos WHERE status='open' GROUP BY project ORDER BY n DESC").fetchall()
    if not rows: print("No open todos."); return
    for r in rows: print(f"  {r['project']}: {r['n']} open")


def main():
    parser = argparse.ArgumentParser(description="loopling Todo Manager")
    sub = parser.add_subparsers(dest="cmd")
    p = sub.add_parser("add"); p.add_argument("title"); p.add_argument("--project","-p"); p.add_argument("--priority","-P",type=int,choices=[1,2,3]); p.add_argument("--due","-d"); p.add_argument("--notes","-n")
    p = sub.add_parser("list"); p.add_argument("--project","-p"); p.add_argument("--all","-a",action="store_true")
    p = sub.add_parser("done"); p.add_argument("id",type=int)
    p = sub.add_parser("cancel"); p.add_argument("id",type=int)
    p = sub.add_parser("edit"); p.add_argument("id",type=int); p.add_argument("--title"); p.add_argument("--project","-p"); p.add_argument("--priority","-P",type=int,choices=[1,2,3]); p.add_argument("--due","-d"); p.add_argument("--notes","-n")
    sub.add_parser("summary"); sub.add_parser("projects")
    args = parser.parse_args()
    if not args.cmd: parser.print_help(); sys.exit(0)
    {"add":cmd_add,"list":cmd_list,"done":cmd_done,"cancel":cmd_cancel,"edit":cmd_edit,"summary":cmd_summary,"projects":cmd_projects}[args.cmd](args)


if __name__ == "__main__":
    main()
