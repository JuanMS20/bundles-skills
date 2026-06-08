---
name: invisible-browser
description: Anti-detection browsing with InvisiblePlaywright on Windows. Patched Firefox (C++ level fingerprint spoofing) via Playwright-compatible API. For tasks where anti-bot detection blocks normal browser tools.
---

# InvisiblePlaywright — Anti-Detection Browser

## 📌 Descubrimiento automático por Hermes (MCP)

Registrado como MCP server en config.yaml → el agente HERMES **descubre automáticamente** estas tools en cada sesión:

| Tool MCP | Descripción |
|----------|-------------|
| `stealth_navigate(url)` | Navegar + info básica (URL, título) |
| `stealth_extract(url)` | Extraer texto visible |
| `stealth_screenshot(url)` | Screenshot PNG (base64) |
| `stealth_click(url, selector)` | Click en elemento CSS |
| `stealth_fill(url, selector, text)` | Llenar campo de formulario |
| `stealth_meta(url)` | Meta tags (OG, description) |
| `stealth_links(url)` | Todos los enlaces |
| `stealth_evaluate(url, js)` | JavaScript arbitrario |
| `stealth_reset()` | Reinicia el navegador (limpia cookies/estado) |

⚠️ `stealth_meta`, `stealth_links`, `stealth_evaluate` usan `page.evaluate()` → fallan en sites con CSP restrictivo. Usar `stealth_extract` o `stealth_navigate` para esos casos.

## Instalación

Paquete y binario ya instalados en el venv de Hermes. Binario: `C:\Users\ASUS\AppData\Local\invisible-playwright\Cache\firefox-7\firefox.exe`

## Uso desde execute_code() (alternativa al MCP)

```python
from hermes_tools import terminal
result = terminal('python "C:/Users/ASUS/AppData/Local/hermes/scripts/invisible-browser/stealth_browser.py" extract --url https://ejemplo.com --headless')
```

## Uso directo (import)

```python
from invisible_playwright import InvisiblePlaywright
with InvisiblePlaywright(headless=True) as browser:
    page = browser.new_page()
    page.goto("https://ejemplo.com")
    text = page.text_content("body")
```

## MCP Server

Script: `C:\Users\ASUS\AppData\Local\hermes\scripts\invisible-browser\stealth_browser_mcp.py`
Registrado en config.yaml con `command: python`, args como YAML list.

Arquitectura: stdio JSON-RPC. Hermes lanza el proceso al inicio, se comunica vía stdin/stdout. El browser se reusa entre llamadas. Llamar `stealth_reset()` entre sesiones no relacionadas.

## StealthBrowser (wrapper Python)

```python
import sys
sys.path.insert(0, r"C:\Users\ASUS\AppData\Local\hermes\scripts\invisible-browser")
from stealth_browser import StealthBrowser

with StealthBrowser(headless=True, seed=42) as sb:
    sb.navigate("https://ejemplo.com")
    sb.click("#boton")
    sb.fill("#campo", "texto")
    sb.extract_text()
    sb.extract_links()
    sb.screenshot("captura.png")
    sb.get_seed()
    sb.save_state("state.json")
    sb.load_state("state.json")
```

## Detección verificada

- `navigator.webdriver` = False | Sin Chrome properties | 5 plugins reales
- User-Agent Firefox 150 realista | reCAPTCHA v3: 0.90/1.0 | CreepJS: 0 lies | FP Pro: No detectado

## Archivos

- `scripts\invisible-browser\stealth_browser.py` — CLI + StealthBrowser class
- `scripts\invisible-browser\stealth_browser_mcp.py` — MCP server
- Config: `config.yaml` → `mcp_servers.invisible-browser`
