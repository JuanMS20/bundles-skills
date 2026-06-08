# Ollama — Full Uninstall Recipe (from CLI)

## Context
Ollama installs to `C:\Users\<user>\AppData\Local\Programs\Ollama\` and stores models in `C:\Users\<user>\.ollama\models\`. It registers a startup entry in `HKCU\...\Run` and may set env vars like `OLLAMA_HOST`, `OLLAMA_MODELS`, `OLLAMA_DEBUG`.

## Steps (applied 2026-05-21)

```bash
# 1. Kill processes
taskkill /F /IM ollama.exe
taskkill /F /IM "ollama app.exe"

# 2. Try native uninstaller (from git-bash, needs cmd.exe wrapper)
cmd.exe /c "C:\Users\ASUS\AppData\Local\Programs\Ollama\unins000.exe" /VERYSILENT /SUPPRESSMSGBOXES
# → failed silently, exit code 1

# 3. Manual fallback
rm -rf "/c/Users/ASUS/AppData/Local/Programs/Ollama/"
rm -rf "/c/Users/ASUS/.ollama/"

# 4. Clean registry
cmd.exe /c "reg delete HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v Ollama /f"
cmd.exe /c "reg delete HKCU\Environment /v OLLAMA_HOST /f"
cmd.exe /c "reg delete HKCU\Environment /v OLLAMA_MODELS /f"
cmd.exe /c "reg delete HKCU\Environment /v OLLAMA_DEBUG /f"

# 5. Verify
ls "/c/Users/ASUS/AppData/Local/Programs/Ollama/" 2>/dev/null || echo "GONE"
reg.exe query "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v Ollama 2>/dev/null || echo "GONE"
```

## Notes
- Models dir was empty (10K) this time — no models had been downloaded
- No Windows service was registered (`sc query Ollama` returned SERVICE_NOT_FOUND)
- The Inno Setup uninstaller (`unins000.exe`) fails from git-bash even with `/VERYSILENT /SUPPRESSMSGBOXES` and `cmd.exe /c` wrapper
