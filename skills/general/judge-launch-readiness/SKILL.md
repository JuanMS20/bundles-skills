---
name: judge-launch-readiness
description: "Checklist 'listo para producción?' — multi-plataforma. Web: deploy config, env, CORS. Móvil: signing, store. Desktop: installer signing. CLI: distribution. Más observabilidad y monitoreo. Use when: antes de deploy, 'está listo?', production readiness, launch check, 'puedo hacer deploy?'."
---

# JUDGE LAUNCH READINESS — Listo para PRODUCCIÓN?

## Principio: Funcionar ≠ Listo para lanzar

La IA genera código que "funciona" en local. Pero producción es otro mundo.
Tu trabajo es encontrar TODO lo que falta para que un usuario real
pueda usar esto sin que explote.

## FASE 0 — Detectar plataforma
- **Web**: app frontend + opcional backend, deployada a hosting
- **Móvil**: APK/IPA, destina a app store o distribución directa
- **Juego**: destina a Steam/store/console/web
- **CLI**: distribuible via npm/brew/cargo/standalone binary
- **Desktop**: installer (exe/dmg/AppImage/deb)
- **Backend/API**: servidor accesible públicamente

## 1. Configuración y Entorno (universal)

- [ ] `.env.example` existe con TODAS las variables necesarias
- [ ] `.env` NO está commiteado (verificar .gitignore)
- [ ] `README.md` tiene instrucciones de instalación claras
- [ ] `README.md` tiene instrucciones de ejecución
- [ ] Versión de runtime está especificada (.nvmrc, requires-python, etc.)
- [ ] `package.json` / `requirements.txt` / `Cargo.toml` completo
- [ ] No hay dependencias sin usar (depcheck, pipdeptree, etc.)

## 2. Seguridad Básica (universal)

- [ ] No hay credenciales hardcodeadas en el código
- [ ] No hay `console.log` / prints con datos sensibles
- [ ] No hay `eval()` con input de usuario
- [ ] No hay SQL injection básico (strings concatenados)
- [ ] Rate limiting en endpoints/funciones públicas
- [ ] CORS configurado correctamente (no `*` en producción) — WEB

## 3. Performance Mínima (universal)

- [ ] Startup time < 2s (verificado con timer real)
- [ ] No hay assets de 10MB+ embebidos
- [ ] No hay memory leaks obvios (crecimiento al navegar/usar)
- [ ] Detalles por plataforma: ver `judge-performance-budget`

## 4. Errores y UX Mínima (universal)

- [ ] Hay manejo de errores de red (offline, timeout)
- [ ] Hay loading states (no elementos que no reaccionan)
- [ ] Hay mensajes de error amigables (no stack traces en producción)
- [ ] Las acciones destructivas piden confirmación
- [ ] Detalles por plataforma: ver `judge-ux-vibe-check`

### Web específico
- [ ] Hay página 404 custom
- [ ] Responsive: funciona en 320px y 1920px

## 5. Datos y Persistencia (universal)

- [ ] Si hay DB: migrations/seeds existen y funcionan
- [ ] Si hay DB: backup strategy documentada
- [ ] Si hay file storage: límites de tamaño configurados
- [ ] Si hay auth: password reset funciona
- [ ] Si hay auth: session expiration configurada

## 6. Observabilidad y Monitoreo (NUEVO)

- [ ] Hay structured logging? (JSON con timestamps, no solo print)
- [ ] Los logs tienen niveles? (DEBUG, INFO, WARN, ERROR)
- [ ] Hay algún sistema de error tracking? (Sentry, Datadog, o equivalente)
- [ ] Hay alertas para errores críticos en producción?
- [ ] Hay métricas básicas? (request count, response time, error rate)
- [ ] Hay un health check endpoint? (GET /health o equivalente)
- [ ] Se puede saber SI la app está caída sin que un usuario lo reporte?

Si NO hay observabilidad:
DECLARAR "Monitoreo: NO CONFIGURADO. No podrás detectar incidentes en producción."

## 7. Distribución por Plataforma

### Web
- [ ] Build de producción funciona sin errores (`npm run build`, etc.)
- [ ] Variables de entorno de producción están configuradas
- [ ] Dominio/URL de producción definido
- [ ] HTTPS/TLS configurado

### Móvil
- [ ] APK/IPA está firmado (debug signing NO es aceptable para producción)
- [ ] App store metadata preparada (screenshots, descripción, privacy policy)
- [ ] Version number incrementado
- [ ] ProGuard/R8 activado (Android)

### Desktop
- [ ] Installer está firmado (code signing)
- [ ] Auto-update mechanism funciona (si aplica)
- [ ] Version number incrementado

### CLI
- [ ] Publicado en repositorio correspondiente? (npm, brew, cargo, AUR)
- [ ] Binarios precompilados para plataformas target (si aplica)
- [ ] Version tag en git

### Juego
- [ ] Build de release funciona (no debug build)
- [ ] Store page preparada (Steam, App Store, Google Play, itch.io)
- [ ] Age rating configurado
- [ ] Crash reporter integrado

## 8. Legal/Compliance Mínimo

- [ ] Si hay formularios: checkbox de términos/privacidad
- [ ] Si hay analytics: GDPR/cookie consent (WEB)
- [ ] Si hay pagos: PCI compliance (no guardar tarjetas en texto plano)
- [ ] Privacy policy accesible pública

## Formato de Veredicto

```
## VEREDICTO JUDGE LAUNCH READINESS

### Plataforma: [Web / Móvil / Juego / CLI / Desktop]

### Estado: [LISTO / NO LISTO / LISTO CON ADVERTENCIAS]

### Checklist: X/Y items completados

### Bloqueantes para Producción:
1. [ ] [descripción] — severidad

### Advertencias:
1. [ ] [descripción]

### Observabilidad:
- Logging: [SÍ/NO] | Error tracking: [SÍ/NO] | Alerting: [SÍ/NO] | Metrics: [SÍ/NO]

### Distribución:
- [Lista de items de distribución por plataforma]

### Recomendaciones de Deploy:
- Plataforma/destino recomendado
- Variables de entorno necesarias
- Pasos de deploy
```

## Preferencia del usuario: "Sin advertencias"

Cuando el usuario dice "debe quedar todo sin advertencias" o "sin warnings":
- **NO** basta con resolver solo los bloqueantes
- **TODAS** las advertencias deben resolverse ANTES de declarar APROBADO
- El flujo es: Judge -> Fix ALL warnings -> Re-judge -> APROBADO

## Reglas de Oro
- **NUNCA** apruebes si hay credenciales hardcodeadas
- **NUNCA** apruebes si no hay manejo de errores básico
- **NUNCA** apruebes si el README no permite a otra persona levantar la app
- **NUNCA** apruebes un móvil/desktop sin code signing
- Si hay >3 bloqueantes -> NO LISTO. Punto.
- Si el usuario pide "sin advertencias" -> TODO debe resolverse, no solo blockers.
