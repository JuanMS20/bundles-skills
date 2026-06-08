# OpenCode — Complete Uninstall on Windows

> Verified: 2026-05-28 on Windows 11 + Bun 1.3.7

## Installation Modes Found

OpenCode was installed simultaneously via:
1. **Bun global package** (`opencode-ai@1.15.11`) — CLI at `~/.bun/bin/opencode`
2. **Desktop app** (NSIS installer) — binaries at `~/AppData/Local/opencode/`

Both coexist and must be removed separately.

## File Locations (6 directories + 1 binary)

### 1. Desktop App Binaries
```
~/AppData/Local/opencode/
├── OpenCode.exe        (31MB — desktop app)
├── opencode-cli.exe    (183MB — CLI bundled with desktop)
└── uninstall.exe       (144KB — NSIS uninstaller)
```
**Remove:** `cd ~/AppData/Local/opencode && ./uninstall.exe /S`

### 2. Bun Global Binary (LEFT BEHIND by `bun remove -g`)
```
~/.bun/bin/opencode     (15KB — binary shim)
```
**Remove:** `rm -f ~/.bun/bin/opencode`
**Pitfall:** `bun remove -g opencode-ai` removes the package metadata but the binary persists in `~/.bun/bin/`. Known Bun behavior — cleans package store but not bin directory shims.

### 3. User Config
```
~/.config/opencode/
├── opencode.json       (main config)
├── AGENTS.md           (Matt Pocock skills setup)
├── agents/             (agent definitions)
├── commands/           (custom commands)
├── instructions/       (custom instructions)
├── skills/             (skill definitions)
├── node_modules/       (dependencies)
├── bun.lock
└── package.json
```
**Remove:** `rm -rf ~/.config/opencode/`

### 4. AppData Roaming
```
~/AppData/Roaming/opencode/
├── EBWebView/          (Chromium webview cache)
└── opencode.json       (secondary config)
```
**Remove:** `rm -rf ~/AppData/Roaming/opencode/`

### 5. Cache
```
~/.cache/opencode/
├── bin/
├── models.json
├── node_modules/
├── package.json
├── packages/
├── bun.lock
└── version
```
**Remove:** `rm -rf ~/.cache/opencode/`

### 6. Local Share (persistent data)
```
~/.local/share/opencode/
├── opencode.db         (SQLite — session history)
├── opencode.db-shm
├── opencode.db-wal
├── auth.json           (authentication tokens)
├── bin/
├── log/
├── repos/
├── snapshot/
├── storage/
└── tool-output/
```
**Remove:** `rm -rf ~/.local/share/opencode/`

## Registry Check

```bash
reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall" /s /f "opencode"
reg query "HKLM\Software\Microsoft\Windows\CurrentVersion\Uninstall" /s /f "opencode"
```

The NSIS uninstaller typically cleans its own registry entry when run with `/S`.

## Complete Removal Script

```bash
#!/bin/bash
# OpenCode complete removal — Windows (Git Bash / MSYS)
set -e

echo "=== OpenCode Complete Uninstall ==="

# 1. Desktop app
if [ -d ~/AppData/Local/opencode ]; then
    echo "Removing desktop app..."
    cd ~/AppData/Local/opencode && ./uninstall.exe /S
    sleep 2
fi

# 2. Bun global package
if bun pm ls -g 2>/dev/null | grep -q opencode; then
    echo "Removing Bun package..."
    bun remove -g opencode-ai
fi

# 3. Binary shim (bun remove leaves this)
rm -f ~/.bun/bin/opencode

# 4. All data directories
rm -rf ~/.config/opencode/
rm -rf ~/AppData/Roaming/opencode/
rm -rf ~/.cache/opencode/
rm -rf ~/.local/share/opencode/

# 5. Verify
echo ""
echo "=== Verification ==="
which opencode 2>/dev/null && echo "Still in PATH!" || echo "Not in PATH"
[ -d ~/.config/opencode ] && echo "Config dir exists!" || echo "Config clean"
[ -d ~/.local/share/opencode ] && echo "Data dir exists!" || echo "Data clean"
[ -f ~/.bun/bin/opencode ] && echo "Binary still exists!" || echo "Binary clean"

echo ""
echo "OpenCode fully removed."
```
