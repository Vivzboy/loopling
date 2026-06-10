# agent-browser

Native Rust browser CLI for AI agents. Use this for **web research, price scraping, and general browsing** — it's ~10x faster than browser-use per command and uses stable accessibility refs instead of DOM indices.

**GitHub:** https://github.com/vercel-labs/agent-browser  
**Installed:** `agent-browser` (global npm)  
**Version:** `agent-browser --version`

---

## When to use agent-browser vs browser-use

| Task | Tool | Why |
|------|------|-----|
| Price research / web scraping | **agent-browser** | 0.2s/cmd, stable refs, batch mode |
| General web browsing / QA | **agent-browser** | Faster, semantic locators |
| Authenticated actions on a logged-in site | **browser-use** | Reads your real Chrome login; React native setter + shadow-DOM upload patterns |

agent-browser is primary for research. browser-use is **required** for any authenticated action — agent-browser can't read your real Chrome login (a permanent constraint, see Gotchas below).

---

## Quick Start

```bash
AB=agent-browser

# Open with Chrome profile (reads real cookies — no login needed)
$AB --profile "Default" open "https://example.com"

# Get accessibility tree with refs (fast, stable)
$AB --profile "Default" snapshot -i -c   # interactive elements only, compact

# Click by ref
$AB --profile "Default" click @e42

# Find by text/role (no ref needed)
$AB --profile "Default" find text "Add to cart" click
$AB --profile "Default" find role button click --name "Search"

# Screenshot
$AB --profile "Default" screenshot /tmp/page.png
$AB --profile "Default" screenshot --annotate /tmp/page_annotated.png  # numbered labels = refs

# Close when done
$AB --profile "Default" close
```

---

## Chrome Profiles

```bash
agent-browser profiles
# Chrome profiles (~/Library/Application Support/Google/Chrome):
#   Default  (Person 1)
#   Profile 2  (Work)
#   Profile 3  (Personal)
```

Use `--profile "<name>"` to select a Chrome profile (run `agent-browser profiles` to list yours). Same as browser-use.

---

## Session Isolation

**⚠️ Critical:** The daemon is global. If you open with `--profile "Default"` and the daemon is already running (from a different profile), `--profile` is silently ignored.

```bash
# Check if running: agent-browser session
# Fix: close first, then reopen with correct profile
agent-browser close
agent-browser --profile "Default" open "https://..."

# Or use named sessions to run multiple profiles simultaneously:
agent-browser --session "work" --profile "Work" open "https://..."
agent-browser --session "personal" --profile "Personal" open "https://..."
```

---

## Snapshot (accessibility tree)

The key advantage over browser-use: stable `@refs` instead of DOM indices that change every session.

```bash
# Full tree
agent-browser snapshot

# Interactive elements only (best for agent use — much shorter output)
agent-browser snapshot -i

# Compact + interactive + limit depth
agent-browser snapshot -i -c -d 5

# Scoped to a CSS selector
agent-browser snapshot -i -s "#product-detail"

# With link URLs included
agent-browser snapshot -i --urls
```

Refs look like `[ref=e42]` in the tree → use as `@e42` in commands. Refs reset on page navigation — always re-snapshot after `open`.

---

## Batch Mode (key efficiency feature)

Multiple commands in a single invocation — eliminates per-command process startup overhead. Use this for multi-step research flows.

```bash
# Argument mode (each quoted string = one command)
agent-browser --profile "Default" batch \
  "open https://example.com/search?q=widgets" \
  "wait --load networkidle" \
  "snapshot -i -c"

# JSON stdin mode
echo '[
  ["open", "https://example.com"],
  ["wait", "--load", "networkidle"],
  ["snapshot", "-i", "-c"],
  ["screenshot", "/tmp/result.png"]
]' | agent-browser --profile "Default" batch --json

# Stop on first error
agent-browser batch --bail "open https://..." "click @e1" "screenshot"
```

---

## Semantic Locators (stable — no ref needed)

```bash
# By ARIA role + accessible name
agent-browser find role button click --name "Add to cart"
agent-browser find role textbox fill --name "Search" "blue widgets"

# By visible text
agent-browser find text "Sign In" click
agent-browser find text "R169.99" text    # Extract the text

# By label, placeholder, alt text
agent-browser find label "Email" fill "test@test.com"
agent-browser find placeholder "Search" fill "widgets"

# By data-testid
agent-browser find testid "price-display" text

# nth match
agent-browser find nth 2 "a[href*='/product/']" click
```

---

## Price Research Pattern

For SA grocery stores — DDG search first, then direct product URL:

```bash
AB="agent-browser --profile Default"

# 1. Navigate directly to product URL (from DDG search)
$AB open "https://example.com/category?q=widgets"

# 2. Wait for page and snapshot scoped to product section
$AB wait --load networkidle
$AB snapshot -i -c -s ".product-grid, .search-results, main"

# 3. Extract price from specific product
$AB find text "Blue Widget" text
# or
$AB eval "Array.from(document.querySelectorAll('[class*=\"price\"]')).map(e=>e.innerText).filter(t=>t.match(/R\d/))"

# 4. Screenshot for verification
$AB screenshot /tmp/ww_product.png
```

**Batch version (fast):**
```bash
agent-browser --profile "Default" batch \
  "open https://example.com/category?q=widgets" \
  "wait --load networkidle" \
  "eval Array.from(document.querySelectorAll('[class*=\"price\"]')).map(e=>e.innerText).filter(t=>t.match(/R\\d/))" \
  "screenshot /tmp/results.png"
```

---

## Annotated Screenshots

The `--annotate` flag overlays numbered labels on interactive elements. Each label `[N]` = ref `@eN`. Best for debugging what's on screen:

```bash
agent-browser screenshot --annotate /tmp/page.png
# Output also lists: [1] @e1 button "Submit", [2] @e2 link "Home", etc.

# Then interact by ref:
agent-browser click @e2
```

---

## Useful Commands Reference

```bash
# Navigation
agent-browser open <url>
agent-browser back / forward / reload

# Content
agent-browser get title
agent-browser get url
agent-browser get text <sel>
agent-browser eval "<js>"

# Interaction
agent-browser click <sel|@ref>
agent-browser fill <sel|@ref> "text"     # clear + fill
agent-browser type <sel|@ref> "text"     # type into element
agent-browser keyboard type "text"       # type at current focus
agent-browser keyboard inserttext "text" # insert without key events
agent-browser press "Enter"
agent-browser upload <sel|@ref> "/path/to/file.mp4"
agent-browser scroll down 500

# State
agent-browser wait <sel>                 # wait for element
agent-browser wait --text "Welcome"      # wait for text
agent-browser wait --load networkidle
agent-browser is visible <sel>

# Tabs
agent-browser tab new [url]
agent-browser tab <n>

# Cookies / Storage
agent-browser cookies
agent-browser storage local

# Auth state (save/restore login)
agent-browser state save ./my-auth.json
agent-browser state load ./my-auth.json

# Sessions
agent-browser session list
agent-browser close
agent-browser close --all
```

---

## Config File

Set persistent defaults at `~/.agent-browser/config.json`:

```json
{
  "headed": false,
  "maxOutput": 50000
}
```

Project-level overrides: `./agent-browser.json` in the working directory.

---

## Gotchas

- **`--profile` silently ignored if daemon running** — run `agent-browser close` first, or use `--session <name>` for isolation. "Daemon already running" warning = profile flag was ignored.
- **Refs reset on navigation** — `@e42` from a snapshot is only valid until you `open` a new URL. Always re-snapshot after navigation.
- **snapshot -i is the right default** — full snapshot is very verbose. Always pass `-i` for interactive elements only. Add `-c` for compact.
- **batch mode for research** — don't call agent-browser one command at a time. Group the whole research flow into a single `batch` call.
- **React controlled inputs need eval** — some sites' search/input fields are React-controlled. `fill` and `type` don't trigger React's onChange. Use `eval` with React native setter: `Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(input, val)` + `dispatchEvent(new Event('input', {bubbles:true}))`.
- **`--profile` copies profile to temp dir (read-only snapshot)** — changes aren't written back to Chrome. Cookies loaded from disk at open time. Same limitation as browser-use.
- **Two profiles simultaneously** — use distinct `--session "<a>"` / `--session "<b>"` names with their respective `--profile` flags to run both without conflict.
- **⛔ Cannot access authenticated sessions from real Google Chrome (PERMANENT)** — agent-browser runs "Chrome for Testing" (its own downloaded binary at `~/.agent-browser/browsers/chrome-*/`), NOT the real Google Chrome. Cookies for sites you're logged into are stored on disk by real Chrome, encrypted via macOS Keychain using real Chrome's app-specific key. Chrome for Testing has a different app key and cannot decrypt them. The cookies exist on disk but are unreadable. Result: agent-browser always sees a logged-out state for any site you're signed into, regardless of `--profile` flag. This is a design constraint — NOT fixable by configuration. Always use browser-use for authenticated actions. (Confirmed 2026-04-08)
- **Shadow DOM / file upload** — `upload` command works on visible `<input type=file>` elements. Shadow DOM inputs may need `eval` to trigger the file chooser.
- **Annotated screenshot breaks on non-Chrome engines** — `--annotate` only works with Chrome/Lightpanda backends. Safari/WebDriver doesn't support it.
- **`wait --load networkidle` before snapshot** — always wait for the page to settle before snapshotting. Especially on SPAs that load content after initial render.
