---
name: windows-software-removal
description: >-
  Uninstall Windows software from CLI when the official uninstaller fails or
  you have no GUI access. Covers process termination, running native uninstallers
  from git-bash, and manual fallback (files + registry).
category: devops
triggers:
  - user asks to uninstall/remove/delete a Windows application
  - user wants to 'completely remove X'
  - uninstaller fails from CLI environment
  - manual software removal needed
---

# Windows Software Removal (CLI)

## Strategy (try in order)

1. **Kill running processes** — prevents locked files
2. **Try the official uninstaller** — some work from CLI
3. **Manual fallback** — files + registry when uninstaller fails

---

## Step 1: Locate the installation

```bash
# Find the executable
where <name>

# Find the install dir
ls "/c/Users/<user>/AppData/Local/Programs/<name>/"

# Check for uninstaller
ls "/c/Users/<user>/AppData/Local/Programs/<name>/unins*.exe"
```

**Also check package managers** — the same app may be installed via multiple managers:

```bash
# npm global
npm list -g <name>

# bun global
bun pm ls -g | grep -i <name>
```

Common install paths:
- `C:\Users\<user>\AppData\Local\Programs\<name>\`
- `C:\Program Files\<name>\`
- `C:\Program Files (x86)\<name>\`

## Step 2: Kill processes

```bash
taskkill /F /IM <name>.exe
taskkill /F /IM "<name> app.exe"   # if there's a launcher variant
```

Check with `tasklist | grep -i <name>`.

## Step 3: Try the official uninstaller

**Inno Setup uninstallers** (`unins000.exe`) often work silently:

```bash
# From git-bash — use cmd.exe /c wrapper
cmd.exe /c "C:\path\to\unins000.exe" /VERYSILENT /SUPPRESSMSGBOXES
```

**Why `/VERYSILENT` instead of `/SILENT`:** Inno Setup's `/SILENT` shows a progress bar. `/VERYSILENT` skips everything. `/SUPPRESSMSGBOXES` suppresses confirmation dialogs.

**Other uninstallers** (MSI, NSIS, custom):
```bash
# MSI
cmd.exe /c "msiexec /x {product-code}" /quiet /norestart

# NSIS (often has _uninstall.exe or uninst.exe)
cmd.exe /c "C:\path\to\uninst.exe" /S
```

**Common failure modes from git-bash:**
- Uninstaller returns exit code 1 silently — likely needs a desktop session
- Uninstaller hangs — run with a short timeout
- Uninstaller spawns a GUI dialog — not visible in CLI, must fall back to manual

## Step 4: Manual fallback (when uninstaller fails)

```bash
# 4a — delete program directory
rm -rf "/c/Users/<user>/AppData/Local/Programs/<name>/"

# 4b — delete user data / config / models
rm -rf "/c/Users/<user>/.<name>/"
# or wherever the app stores its user data (check docs)

# 4c — clean startup entry
cmd.exe /c "reg delete HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v <name> /f"

# 4d — clean environment variables if the app set them
cmd.exe /c "reg delete HKCU\Environment /v <NAME>_HOST /f"
cmd.exe /c "reg delete HKCU\Environment /v <NAME>_MODELS /f"
# repeat for each env var the app creates

# 4e — check for Windows service
sc query <name>
sc delete <name>
```

## Step 5: Verify

```bash
# Program directory gone
ls "/c/Users/<user>/AppData/Local/Programs/<name>/" 2>/dev/null || echo "GONE"

# Startup entry gone
reg.exe query "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v <name> 2>/dev/null || echo "GONE"
```

## Pitfalls

- **Orphaned binaries after `bun remove -g`:** Bun's global uninstall can leave the `.exe` in `~/.bun/bin/` even after `bun remove -g` succeeds. Always verify with `where <name>` after uninstall and manually `rm -f` any leftovers.
- **Multiple package managers for one app:** An app can be installed via npm AND bun simultaneously. Check both with `npm list -g` and `bun pm ls -g`. Remove from all, then verify `where <name>` returns nothing.
- **Uninstaller from git-bash:** Inno Setup uninstallers often fail from git-bash because they need the Windows subsystem to display a GUI or interact with the shell process tree. Always wrap in `cmd.exe /c "..."` and use `/VERYSILENT /SUPPRESSMSGBOXES`.
- **User data can be huge** (model files, caches, databases). The `.ollama/models` dir for Ollama can be 10+ GB. Always check `du -sh ~/.name/` before deleting, and ask the user before nuking large data dirs.
- **Some apps register both HKCU and HKLM startup entries** — check both. Also check `shell:startup` folder: `C:\Users\<user>\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\`.
- **PATH entries:** Some apps add themselves to the system PATH. Clean with `reg delete HKCU\Environment /v PATH /f` only if you know what you're removing — better to edit the PATH value instead of deleting the whole key.

## Real-world examples

See `references/ollama-uninstall-recipe.md` for a complete recipe removing Ollama from Windows via CLI.
