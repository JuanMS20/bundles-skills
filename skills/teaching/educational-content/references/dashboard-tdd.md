# Dashboard TDD — Testing static HTML dashboards first

Use TDD vertical (red-green-refactor) for static HTML/CSS/JS dashboards that poll a REST API for state visualization.

## Why test a static HTML file?

Without tests, you don't know if:
- The file can be parsed by a browser (DOCTYPE, valid tags)
- JS references the correct API endpoints
- CSS has the required visual constraints (dark theme, monospace, no scroll)
- UI containers exist for all required data types
- Polling mechanism is configured correctly
- Highlight animation exists for change detection

## Test categories (12 tests for a dashboard)

| # | Category | What it tests |
|---|----------|---------------|
| 1-4 | Structure | File exists, DOCTYPE + html + head + body, CSS and JS are embedded (no external deps) |
| 5 | Endpoints | JS references the correct API base URL and endpoint paths |
| 6 | Polling | Uses `fetch()` + `setInterval` at the correct interval (2000ms) |
| 7-9 | CSS | Dark background detected, monospace font family, `overflow-x: hidden` |
| 10-11 | Rendering | HTML has containers for accounts, blocks, and event log; JS has DOM manipulation functions |
| 12 | Animation | CSS has `animation`, `transition`, or `@keyframes` for change highlight |

## Implementation pattern

### Test structure

```python
import os, re

DASHBOARD = "path/to/dashboard.html"

def test_archivo_existe():
    assert os.path.isfile(DASHBOARD)

def test_html_valido():
    with open(DASHBOARD) as f:
        content = f.read()
    assert "<!DOCTYPE html>" in content.lower()
    assert "<html" in content and "<head>" in content and "<body>" in content
    assert "<style>" in content       # CSS embedded
    assert "<script" in content      # JS embedded (no external src)

def test_js_endpoints():
    js_blocks = re.findall(r"<script[^>]*>(.*?)</script>", content, re.DOTALL)
    js_all = "\n".join(js_blocks)
    assert "/info" in js_all

def test_fetch_y_polling():
    assert "fetch(" in js_all
    assert "setInterval" in js_all or "setTimeout" in js_all
    assert "2000" in js_all or "2 * 1000" in js_all

def test_css_dark_theme():
    css_blocks = re.findall(r"<style>(.*?)</style>", content, re.DOTALL)
    css_all = "\n".join(css_blocks)
    assert "background" in css_all
    has_dark = any(bg in css_all.lower() for bg in
                   ["#1a", "#1e", "#0d", "#111", "#222", "#1b", "#2d"])

def test_css_monospace():
    assert "monospace" in css_all.lower() or "Consolas" in css_all or "Courier" in css_all

def test_no_scroll_horizontal():
    assert "overflow-x" in css_all and "hidden" in css_all

def test_render_estructura():
    has_accounts = any(x in content for x in ["accounts", "cuentas", "wallets"])
    has_blocks = any(x in content for x in ["blocks", "chain", "bloques"])
    has_log = any(x in content for x in ["log", "events", "eventos", "timeline"])

def test_js_funciones_render():
    assert "function " in js_all or "=>" in js_all
    assert "innerHTML" in js_all or "textContent" in js_all

def test_highlight_animation():
    has_animation = "animation" in css_all or "transition" in css_all or "@keyframes" in css_all
```

### Dashboard HTML that passes these tests

The minimal dashboard structure:

- Dark background (`#111` or similar) on `body`
- `font-family: 'Consolas', 'Courier New', monospace`
- `overflow-x: hidden` on `body`
- Three panel containers with class/id referencing accounts, blocks, and log
- JS with `fetch()` + `setInterval(..., 2000)` polling
- CSS transition or animation class (e.g. `.highlight`) that changes background with fade

### Running the tests

```bash
python issues/tests/test_04_dashboard.py
```

Expected: 12/12 tests pass if the dashboard is correct.

## TDD vertical for dashboards

1. **Write all tests first** — all fail RED (file doesn't exist)
2. **Build minimal HTML** — make structure tests pass first
3. **Iterate** — add JS, CSS, rendering until all 12 pass GREEN
4. **Refactor** — check for duplicate CSS, inline scripts, valid HTML5

## Pitfalls

- **Don't use external CSS/JS CDNs.** Tests check for embedded `<style>` and `<script>`. External deps break the "works offline" requirement.
- **Don't skip `overflow-x: hidden`.** For video recording at 1920x1080, horizontal scroll ruins the visual.
- **Don't forget the highlight animation.** Without it, users can't tell what changed between polls.
- **Don't use Gradio, React, or any framework.** Plain HTML+CSS+JS ensures zero dependencies, works offline, and is debuggable in any browser.
- **Don't name variables generically.** `info` gets reassigned across poll cycles leading to stale prints. Use distinct names per snapshot: `info_before`, `info_after_send`, `info_after_mine`.
- **Animation timing matters.** CSS transition 0.6s + JS class removal at 2s gives visible but not distracting feedback.
- **Opening `dashboard.html` as local file (`file://`) fails with CORS.** The browser blocks `fetch()` from `file://` to `http://localhost`. Fix: add CORS headers to the Flask API and serve the dashboard from a Flask route (`/dashboard`).
- **CORS setup in Flask:**
  ```python
  @app.after_request
  def add_cors(response):
      response.headers["Access-Control-Allow-Origin"] = "*"
      response.headers["Access-Control-Allow-Headers"] = "Content-Type"
      response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
      return response
  ```

## See also

- [agent-skill-tdd.md](agent-skill-tdd.md) — TDD for Hermes skills (backend-side)
- [hermes-agent-integration.md](hermes-agent-integration.md) — Split-screen: Hermes terminal + dashboard for video
