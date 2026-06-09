---
name: boil-the-lake
version: 1.0.0
description: |
  Engineering decision-making principles: completeness is cheap with AI, always
  prefer the full implementation over the shortcut. Search before building to
  avoid reinventing one-liners. Distinguish lakes (boilable) from oceans (out of
  scope). Apply to any implementation choice where a shortcut is tempting.
---

# Boil the Lake

Two principles that govern every implementation decision.

---

## 1. Completeness Is Cheap

AI-assisted coding makes the marginal cost of completeness near-zero. When the complete implementation costs minutes more than the shortcut — **do the complete thing. Every time.**

### Lake vs Ocean

| Type | Definition | Do what |
|------|-----------|---------|
| **Lake** | Boilable — 100% test coverage for a module, full feature implementation, all edge cases, complete error paths | Boil it. Completely. |
| **Ocean** | Not boilable — rewriting an entire system from scratch, multi-quarter platform migrations | Flag it as out of scope. Don't start. |

**The test:** Can it be completed in this session? If yes, it's a lake. Boil it.

### How to evaluate approach A vs B

When you see two approaches and approach A is "more complete" at the cost of ~70 more lines:

```
Approach A: full implementation, all edge cases, ~150 LOC
Approach B: covers 90% of cases, ~80 LOC
```

**Always choose A.** The 70-line delta costs seconds with AI coding. "Ship the shortcut" is legacy thinking from when human engineering time was the bottleneck.

### Anti-patterns to refuse

| Pattern | Why it's wrong |
|---------|---------------|
| "Choose B — it covers 90% with less code." | If A is 70 lines more, choose A. |
| "Let's defer tests to a follow-up PR." | Tests are the cheapest lake to boil. Write them now. |
| "This would take 2 weeks." | Reframe: "2 weeks human / ~1 hour AI-assisted." |
| "We can add error handling later." | Error handling is part of the lake. |
| "Skip the edge case for now." | Edge cases are the cheapest line items in a session. |

### What this means in practice

- Write the complete error path, not just the happy path.
- Write the validation at the boundary, not just the core logic.
- Write the full set of API endpoints, not just the first two.
- Write the tests for the module you just wrote, not just the implementation.
- Complete the feature including the loading states and error states in the UI.

---

## 2. Search First, Then Build

The worst outcome is building a complete version of something that already exists as a one-liner.

**Before writing any non-trivial piece of code:**

1. **Check if a library does it.** `httpx`, `boto3`, `sqlalchemy`, `jose`, `passlib` — the ecosystem is vast. A complete auth implementation is 3 imports, not 200 lines.
2. **Check the existing codebase.** The pattern you need may already exist in `services/`, `utils/`, or another module.
3. **Check reference implementations.** Your own existing projects (and well-known open-source ones) have battle-tested patterns for LLM clients, auth, storage, etc. Copy and adapt — don't rebuild.

**Search heuristic:** If a thing sounds like it should have a name, Google it before writing it. "JWT token validation in FastAPI" → `python-jose` + `fastapi.security`. Don't hand-roll a JWT parser.

### What to copy vs build

| Situation | Action |
|-----------|--------|
| LLM client | Reuse an existing client/SDK or copy a battle-tested one from a prior project |
| Agent run loop | Port a proven run-loop from a reference implementation rather than rebuilding |
| Auth (JWT) | Use `python-jose` + `passlib` — standard FastAPI auth pattern |
| Storage abstraction | Build it — it's specific to your project's needs |
| DB migrations | Use Alembic — don't hand-roll |
| File uploads | `aiofiles` + standard patterns |

---

## Gotchas

- **"Complete" doesn't mean "infinite scope".** Boil lakes, flag oceans. The distinction matters — know what's in scope and complete *that* fully.
- **Complete error handling ≠ defensive programming theatre.** Don't validate things that can't fail. Don't catch exceptions you can't handle. Complete = every realistic failure mode is handled.
- **Searching costs seconds; rebuilding costs minutes.** The search always pays off.
