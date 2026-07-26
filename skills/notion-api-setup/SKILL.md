---
name: notion-api-setup
description: Wire a repo or agent to a Notion workspace via the REST API. Use when asked to "connect X to Notion", "sync this into Notion", "put our leads/CRM/tasks in Notion", "get a Notion token", "share this with the team in Notion", or when a script needs to read/write Notion pages or databases headlessly (cron, agent runs, CI) where interactive OAuth will not work. Also covers creating the integration in the browser, sharing pages with it, and the failure modes that look like bugs but are not.
---

# Notion API setup

Connect code to a Notion workspace. The API is stable and well documented; almost all
the pain is in three things nobody tells you, all in Gotchas below.

## Pick the auth type first

| Type | What it is | Use when |
|---|---|---|
| **Internal integration** | One static token, workspace-scoped, shared by everyone | A team repo where a shared bot identity is fine. Simplest. |
| **Personal Access Token** | Static token scoped to one user | Same simplicity, but per person: attributable and individually revocable. |
| **OAuth (public)** | Browser authorization per user | Distributing to workspaces you do not control. |
| **Notion MCP** | OAuth under the hood, no token in a file | Interactive Claude Code work. Useless in cron or CI. |

Recommend **PAT per person** for a team repo and **MCP** for interactive work. A single
shared internal token is the least effort and the most rotation pain: one leak means
everyone re-pastes, and nothing is attributable to a person. Say that once, then build
what the user asked for.

**MCP and API are not interchangeable.** The MCP is interactive-only, so anything
scheduled needs a token regardless.

## Creating an internal integration (browser)

No API for this, so it is a browser job. Do it yourself rather than handing it back.

```bash
BU=~/.browser-use-env/bin/browser-use
$BU --session notionsetup --profile "Default" open "https://www.notion.so/profile/integrations"
$BU --session notionsetup --profile "Default" get title       # confirm the right account
$BU --session notionsetup --profile "Default" screenshot /tmp/n.png
```

Flow: **New connection** → name it → **Access token** (not OAuth) → pick the workspace →
**Create connection**. Read/Update/Insert content are on by default.

Then **Content access → Add** and pick pages. Children inherit, so adding the top-level
sections covers a whole workspace. Teamspaces do not appear in that picker, only pages,
so add the top-level pages instead of searching for the teamspace name.

### Getting the token out

It is not in an `<input>`, so reading `.value` returns nothing. Click the eye icon, then
walk text nodes (including shadow roots) for a string starting `ntn_`:

```bash
$BU --session notionsetup --profile "Default" click <eye-index>
$BU --session notionsetup --profile "Default" eval "(() => { const out=[]; const walk=(root)=>{ const tw=document.createTreeWalker(root, NodeFilter.SHOW_TEXT); let n; while(n=tw.nextNode()){ const t=n.textContent.trim(); if(/^ntn_/.test(t)) out.push(t); } for(const el of root.querySelectorAll('*')){ if(el.shadowRoot) walk(el.shadowRoot);} }; walk(document); return out[0]; })()"
```

Store it in `~/.claude/secrets.local` as `<PROJECT>_NOTION_TOKEN=ntn_...`, never in the repo.

## Calling the API

Stdlib only, no SDK needed. `scripts/notion_client.py` in this skill folder is a working
client with throttling, 429 retry and upsert. Copy it and change the database id.

```bash
curl -s -X POST https://api.notion.com/v1/search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" -d '{"query":"","page_size":5}'
```

Creating databases and pages is easier through the **Notion MCP** (SQL-ish DDL, no JSON
property gymnastics). Use MCP to build the schema, the API to sync data into it.

## Gotchas

1. **The token sees nothing until a page is shared with it.** A brand new integration
   returns empty results for everything. This looks exactly like a broken token or a
   wrong id, and it is neither. Share the page (page menu → **Add connections**), or add
   it under Content access on the integration. **Check this first, always.**

2. **Version `2022-06-28` has databases, not data sources.** The MCP hands back
   `collection://<uuid>` data source ids. Those 400 with `invalid_request_url` against
   `/data_sources/{id}/query` on this version. Use the **database id** from the database
   URL instead. Newer versions add data sources; do not mix the two.

3. **Upserts key on something. Whatever you pick, never edit it in Notion.** Matching on
   title means one rename in the UI creates a duplicate on the next push rather than
   updating. Either rename in the source of truth only, or store the returned
   `notion_page_id` back in your CSV/DB and match on that.

4. **Do not push over columns humans edit.** A sync that PATCHes every field silently
   undoes someone's call notes and stage change. Split fields into machine-owned
   (scraped) and human-owned (notes, stage, owner), and only ever write the machine ones
   on update. New rows get everything.

5. **Select options are exact-match and fail silently.** `"Or Tambo"` vs `"OR Tambo"`
   quietly creates a second option instead of erroring. Normalise before pushing.

6. **Rate limits:** ~3 requests/sec per connection, plus a per-workspace cap that scales
   with plan. 429 comes back with `Retry-After`; honour it rather than sleeping a fixed
   amount. Max 1000 blocks and 500KB per request, 2000 chars per rich text field.

7. **Deleting is archiving.** `PATCH /pages/{id}` with `{"archived": true}`. There is no
   hard delete via the API.

8. **Bulk loading through the MCP burns context.** Hundreds of rows means hundreds of
   objects in the tool call. Write a script and use the token, or fall back to Notion's
   own CSV import (database → `...` → **Merge with CSV**, and it must be *Merge*, not
   Import, or you get a second database).

## Handing a shared token to a team

If the user insists on one shared token (they often will), reduce the blast radius:

- Share only the pages the integration needs, not the whole workspace.
- Send it with `--solo` on the mailer so it does not auto-BCC personal accounts.
- Tell them plainly what it can reach, and where to rotate it: the integration page,
  **Refresh access token**. Everyone re-pastes after a rotation.
- Note that nothing written with it is attributed to a person, so an **Owner** person
  property on the database matters more than usual.
