---
name: coding-standards
version: 1.0.0
description: |
  Code quality and structure rules for all projects. Apply these whenever writing
  or refactoring code: file size limits (300 lines max), folder structure, module
  splits, naming conventions. Triggered by any new file creation, refactoring task,
  or when a file is getting large. Also applies to "set up project structure" tasks.
---

# Coding Standards

These are non-negotiable rules for code quality and structure. Apply them in every session.

---

## File Size: 300-Line Hard Limit

**No file should exceed 300 lines.** When a file approaches this limit, split it.

### How to split

| Situation | Split strategy |
|-----------|---------------|
| Multiple route handlers in one file | One file per route group (`auth_routes.py`, `project_routes.py`, `run_routes.py`) |
| Service file doing multiple things | Extract each responsibility to its own module (`storage.py`, `llm_client.py`, `email_service.py`) |
| Large React component | Extract sub-components to their own files in the same folder |
| Multiple Pydantic models in one file | Split by domain (`user_schemas.py`, `run_schemas.py`, `project_schemas.py`) |
| Utility functions accumulating | Group by domain (`string_utils.py`, `date_utils.py`, `auth_utils.py`) |

**Rule:** If you can name what the split piece does in 3 words, it deserves its own file.

---

## Folder Structure: Organise by Domain, Not by Type

### Good (by domain/feature)
```
app/
├── api/routes/
│   ├── auth_routes.py       # auth endpoints only
│   ├── project_routes.py    # project CRUD
│   └── run_routes.py        # run management + SSE
├── services/
│   ├── agent/
│   │   ├── run_loop.py
│   │   ├── tools/
│   │   │   ├── file_tools.py
│   │   │   ├── web_tools.py
│   │   │   └── task_tools.py
│   │   └── context_compactor.py
│   ├── storage.py
│   └── llm_client.py
└── models/
    ├── database.py
    └── schemas.py
```

### Bad (everything at one level)
```
app/
├── routes.py          # all routes in one file
├── services.py        # all services in one file
└── models.py          # all models in one file
```

---

## Naming Conventions

| Thing | Convention | Example |
|-------|-----------|---------|
| Python files | `snake_case.py` | `run_loop.py`, `llm_client.py` |
| Python classes | `PascalCase` | `StorageClient`, `RunConfig` |
| Python functions | `snake_case` | `get_project`, `start_run` |
| React components | `PascalCase.tsx` | `BotCard.tsx`, `RunProgress.tsx` |
| React hooks | `use` prefix | `useRun`, `useProject` |
| Next.js pages | `kebab-case/page.tsx` | `bot-workspace/page.tsx` |
| API endpoints | `kebab-case` | `/api/projects`, `/api/runs/{id}/start` |
| Env vars | `SCREAMING_SNAKE_CASE` | `DATABASE_URL`, `LLM_PROVIDER` |

---

## Module Rules

1. **One responsibility per file.** A file that does two things should be two files.
2. **No circular imports.** Services import from models, routes import from services. Never the reverse.
3. **Config at the top, logic at the bottom.** Constants and config before functions/classes.
4. **No magic strings.** Use constants or enums for status values, tier names, event types.
5. **`__init__.py` as thin re-exports only** — never put logic in `__init__.py`.

---

## Gotchas

- **`utils.py` is a code smell.** If you're writing a `utils.py`, ask what domain it belongs to and name it that instead.
- **`main.py` in FastAPI should only wire things together** — no business logic, no DB queries. Route handlers live in `api/routes/`.
- **React component files that contain a page AND its sub-components** will exceed 300 lines fast. Extract sub-components immediately.
- **SQLAlchemy models and Pydantic schemas are different things** — keep them in separate files. Models describe DB tables. Schemas describe API I/O.
