---
name: ci-cd-setup
description: "Genera y configura pipelines CI/CD con GitHub Actions. Detecta stack, crea workflows de lint+type check+tests+build, configura branch protection y secrets. Use when: 'configurar CI', 'GitHub Actions', 'automatizar tests', 'pipeline', 'no se rompe al mergear', primer setup de proyecto, o cuando el proyecto no tiene CI."
---

# CI-CD SETUP — El pipeline corre solo, no cuando te acuerdes

## Principio: Sin CI/CD, cada deploy es apuesta a ciegas.

Si los tests corren solo cuando vos te acordas, no existen.
CI/CD automatiza: cada push, cada PR -> lint, tests, build.
Si algo falla, el PR no se mergea. Punto.

## FASE 0 — Detectar stack

Revisar archivos raíz del proyecto:

| Archivo | Stack | CI steps |
|---------|-------|----------|
| package.json (react/vite/next) | Web JS | install, lint, typecheck, test, build |
| package.json (express/fastify) | Backend JS | install, lint, test, build |
| requirements.txt / pyproject.toml | Python | install, ruff/mypy, pytest |
| Cargo.toml | Rust | fmt, clippy, test, build |
| go.mod | Go | vet, test, build |
| pubspec.yaml | Flutter | analyze, test, build |
| Gemfile | Ruby | rubocop, rspec |
| pom.xml / build.gradle | Java | compile, test, package |

Si hay DB (Supabase, Prisma, etc.): añadir step de migration check.

## FASE 1 — Generar workflow

Crear `.github/workflows/ci.yml`:

### Web (React/Vite/Next/Node)

```yaml
name: CI
on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]

jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version-file: '.nvmrc'
          cache: 'npm'
      - run: npm ci
      - run: npm run lint
      - run: npx tsc --noEmit
      - run: npm test
      - run: npm run build
```

### Python

```yaml
name: CI
on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]

jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pip install ruff mypy pytest
      - run: ruff check .
      - run: mypy . --ignore-missing-imports
      - run: pytest
```

### Con Supabase (añadir step antes del deploy)

```yaml
      - name: Supabase migration check
        run: |
          npx supabase link --project-ref ${{ secrets.SUPABASE_PROJECT_REF }}
          npx supabase db push --dry-run
        env:
          SUPABASE_ACCESS_TOKEN: ${{ secrets.SUPABASE_ACCESS_TOKEN }}
```

### Flutter/Móvil

```yaml
      - uses: subosito/flutter-action@v2
        with:
          channel: stable
      - run: flutter pub get
      - run: flutter analyze
      - run: flutter test
```

## FASE 2 — Branch protection

Configurar via GitHub CLI (recomendado) o instrucciones para UI:

```bash
# Requerir checks de CI antes de merge
gh api repos/{owner}/{repo}/branches/main/protection \
  -X PUT \
  -f required_status_checks[strict]=true \
  -f required_status_checks[contexts][]="CI / ci" \
  -f enforce_admins=true \
  -f required_pull_request_reviews[required_approving_review_count]=1
```

Reglas:
- main/master: PR required, CI debe pasar, no push directo
- Develop (si existe): CI debe pasar, PR recomendado

## FASE 3 — Secrets

Identificar qué secrets necesita el CI:

| Secreto | Dónde | Cómo |
|---------|-------|------|
| Tokens de deploy | GitHub repo secrets | `gh secret set NOMBRE` |
| Supabase keys | GitHub repo secrets | `gh secret set SUPABASE_ACCESS_TOKEN` |
| Cloudflare tokens | GitHub repo secrets | `gh secret set CLOUDFLARE_API_TOKEN` |
| npm tokens | GitHub repo secrets | `gh secret set NODE_AUTH_TOKEN` |

NUNCA commitear secrets en el YAML. Siempre via `${{ secrets.NOMBRE }}`.

```bash
# Verificar que NO hay secrets hardcodeados en el workflow
grep -r "sk-\|key_\|token_" .github/workflows/
# Output debe ser ${{ secrets.* }} únicamente
```

## FASE 4 — Deploy automático (opcional pero recomendado)

Si el proyecto usa hosting con integración nativa (Vercel, Cloudflare Pages, Netlify, Railway), el deploy puede ser automático:

### Cloudflare Pages
- Deploy automático al merge a main via Cloudflare Git integration (no necesita workflow YAML)
- Ver: skill `cloudflare-pages-deploy`

### Vercel
- Importar repo en vercel.com, auto-deploy en push

### Genérico (workflow de deploy)
```yaml
  deploy:
    needs: ci
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      # ... build steps ...
      - name: Deploy
        run: [comando de deploy]
```

## FASE 5 — Verificación

- [ ] `.github/workflows/ci.yml` existe y tiene sintaxis YAML válida
- [ ] CI corre en al menos un PR (verificar en GitHub Actions tab)
- [ ] CI pasa en verde
- [ ] Branch protection activado (no se puede pushear directo a main)
- [ ] Secrets configurados (no hardcodeados en YAML)
- [ ] Si hay deploy automático: verificar que el deploy ocurre tras merge a main

**Sin estas verificaciones, el CI/CD no existe.** Un YAML sin correr = decoracion.

## Pitfalls

### npm ci falla con version mismatch
Si no hay `.nvmrc` o `engines` en package.json, la version de Node del runner puede no matchear.
Fix: crear `.nvmrc` con la version exacta (ej: `20`).

### Supabase db push --dry-run falla sin link
El step necesita `supabase link` primero con `SUPABASE_PROJECT_REF` y `SUPABASE_ACCESS_TOKEN`.
Si faltan, el step falla pero el CI sigue (lo que es incorrecto). Asegurar que el step sea required.

### Cache de npm/actions rompe builds
Si `cache: 'npm'` no encuentra lockfile, falla. Verificar que `package-lock.json` existe y está commiteado.

### Branch protection bloquea primer push
Si activas branch protection antes del primer PR, no puedes pushear nada. Setup branch protection DESPUES del primer PR mergeado.
