# .gitignore — React Native / Expo

Usar como base y ajustar según el proyecto.

```gitignore
# Dependencias
node_modules/

# Expo
.expo/
dist/
web-build/
expo-env.d.ts

# iOS
ios/
*.pbxuser
*.mode1v3
*.mode2v3
*.perspectivev3
*.xcuserstate
*.xcworkspace/xcuserdata
DerivedData/
*.hmap
*.ipa
*.xcuserstate

# Android
android/
*.apk
*.aab
*.jks
*.keystore

# Build
build/
*.tsbuildinfo

# Metro
.metro-health-check*

# Env
.env
.env.local
.env.production

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Debug
npm-debug.*
yarn-debug.*
yarn-error.*

# Testing
coverage/

# ============================================
# DOCUMENTACIÓN (no va a producción)
# ============================================
# Markdown en raíz (excepto README)
*.md
!README.md

# Documentos de oficina
*.docx
*.doc
*.pdf
*.pptx
*.xlsx

# Directorios de documentación
docs/
issues/

# Temporal
*.tmp
*.bak
```

## Notas

- `*.md` + `!README.md` excluye toda la documentación markdown pero mantiene el README del repo
- Ajustar `docs/` y `issues/` según la estructura del proyecto
- Si el proyecto usa Python: agregar `__pycache__/`, `*.pyc`, `.venv/`
- Si usa Docker: agregar `docker-compose.override.yml`
