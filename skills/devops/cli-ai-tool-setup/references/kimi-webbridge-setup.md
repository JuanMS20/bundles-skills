# Kimi WebBridge — Setup on Windows via WSL

## What It Is
Browser extension by Moonshot AI that lets AI agents control Chrome/Edge via Chrome DevTools Protocol (CDP). Officially supports Hermes, Claude Code, Cursor, Codex.

## When To Use vs Hermes Built-in Browser Tools
Hermes already has `browser_*` tools (Playwright/CDP) that avoid screenshot costs. WebBridge adds value ONLY when you need:
- Use YOUR existing browser sessions (cookies, logins preserved)
- Automate sites requiring prior authentication without re-login
- Direct CDP bridge to your real Chrome/Edge

## Windows Installation (via WSL)

The official `install.sh` does NOT support Windows (MINGW64). Run through WSL instead:

```bash
# Install daemon via WSL
wsl curl -fsSL https://cdn.kimi.com/webbridge/install.sh | wsl bash

# Verify daemon status
wsl bash -c "~/.kimi-webbridge/bin/kimi-webbridge status"
```

Expected output when daemon is running but extension not connected:
```json
{"extension_connected":false,"port":10086,"running":true,"version":"v1.9.17"}
```

## Chrome Extension
After daemon is running, install the Chrome extension:
- Chrome Web Store: https://chromewebstore.google.com/detail/kimi-webbridge/fldmhceldgbpfpkbgopacenieobmligc
- Edge Add-ons: also available

Once installed, `extension_connected` should flip to `true`.

## Cost Savings Context
The Reddit claim ($50→$0.50) is about avoiding `computer_use` (screenshot-heavy, macOS-only). Hermes `browser_*` tools already achieve similar savings without WebBridge. WebBridge is an alternative, not a requirement.

## Pitfalls
1. Install script fails on native Windows — must use WSL
2. Daemon runs in WSL, extension in Windows Chrome — they communicate via localhost:10086
3. If extension shows "Disconnected", restart Chrome after daemon is running
