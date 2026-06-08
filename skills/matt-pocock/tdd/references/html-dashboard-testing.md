# HTML Static Dashboard Testing Patterns

For vanilla HTML+CSS+JS dashboards (no frameworks, no bundlers) that use fetch() polling against a local API.

## Why Not a Browser Test Framework?

Educational demos, local-first tools, and single-file dashboards don't justify jsdom/Puppeteer. Static analysis + Node.js verification covers the critical path with zero dependencies.

## 1. File Existence + Basic Structure

```python
def test_archivo_existe():
    assert os.path.isfile(path), f"no existe: {path}"
    print(f"  ✓ existe ({os.path.getsize(path)} bytes)")

def test_html_valido():
    with open(path) as f:
        c = f.read()
    assert "<!DOCTYPE html>" in c or "<!doctype html>" in c
    assert "<html>" in c and "<head>" in c and "<body>" in c and "</html>" in c

def test_css_embebido():
    assert "<style>" in c and "</style>" in c

def test_js_embebido():
    assert "<script>" in c
    # Reject CDN dependencies
    assert "src=" not in c.split("<script")[1].split(">")[0]
```

## 2. API Endpoint Verification

```python
def test_js_endpoints():
    js_blocks = re.findall(r"<script[^>]*>(.*?)</script>", c, re.DOTALL)
    js_all = "\n".join(js_blocks)
    assert "http://localhost:5050" in js_all or '"/info"' in js_all
    assert "/info" in js_all
    assert "/chain" in js_all
```

## 3. Polling Pattern

```python
def test_fetch_y_polling():
    assert "fetch(" in js_all
    assert "setInterval" in js_all or "setTimeout" in js_all
    assert "2000" in js_all or "2 * 1000" in js_all  # 2s refresh
```

## 4. CSS Theme Validation

```python
def test_css_dark_theme():
    css_blocks = re.findall(r"<style>(.*?)</style>", c, re.DOTALL)
    css_all = "\n".join(css_blocks)
    assert any(bg in css_all.lower() for bg in ["#1a", "#111", "#0d", "#1e", "#222"])

def test_css_monospace():
    assert "monospace" in css_all.lower() or "Consolas" in css_all or "Courier" in css_all

def test_no_scroll_horizontal():
    assert "overflow-x" in css_all
    assert "hidden" in css_all
```

## 5. DOM Structure (contenedores)

```python
def test_render_estructura():
    assert any(x in c for x in ["accounts", "cuentas", "wallets"])
    assert any(x in c for x in ["blocks", "chain", "bloques"])
    assert any(x in c for x in ["log", "events", "eventos", "timeline"])
```

## 6. Highlight / Animation

```python
def test_highlight_animation():
    has_animation = "animation" in css_all or "transition" in css_all or "@keyframes" in css_all
    update_highlight = "highlight" in css_all or "flash" in css_all or "update" in css_all
```

## 7. CORS Prevention

When a dashboard is opened via `file://` protocol, browsers block fetch() to localhost. Two fixes:

**Option A — Serve from Flask (preferred):**
```python
@app.after_request
def add_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response

@app.route("/dashboard")
def serve_dashboard():
    path = os.path.join(os.path.dirname(__file__), "..", "dashboard.html")
    if os.path.isfile(path):
        with open(path) as f:
            return f.read(), 200, {"Content-Type": "text/html; charset=utf-8"}
    return "not found", 404
```

**Option B — CORS headers only:** Add the `@app.after_request` block above. Fetch from `file://` still may fail in some browsers; Option A is more reliable.

## 8. Full Integration: Simulate Agent Cycle

For dashboards that display blockchain state, verify the full percept→act→verify cycle:

```python
def test_flujo_completo(info):
    alice0, oracle0 = info["accounts"]["0xAlice"]["balance"], info["accounts"]["0xOracle"]["balance"]
    r = api_post("/send", {"from": "0xAlice", "to": "0xOracle", "amount": 10})
    assert r["success"]
    api_post("/mine")
    info = api_get("/info")
    assert info["accounts"]["0xAlice"]["balance"] == alice0 - 10
    assert info["accounts"]["0xOracle"]["balance"] == oracle0 + 10
```

## Common Pitfalls

1. **file:// CORS**: Chrome blocks fetch from file:// origins. Always serve the dashboard via HTTP.
2. **setInterval context**: The poll function must handle connection errors gracefully without crashing JS.
3. **Highlight timing**: Remove highlight class after animation completes so the same element can re-highlight.
4. **No CDN dependencies**: All CSS/JS must be embedded for offline educational demos.
