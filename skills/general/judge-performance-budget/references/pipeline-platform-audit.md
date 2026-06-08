# Pipeline Platform Audit — Dev-QA-Judge-Chaos

Análisis de cobertura multi-plataforma del pipeline completo de bundles.
Realizado 2026-06-06.

## Veredicto General

El pipeline produce apps reales y correctas. Para apps web medianas es suficiente.
Para apps multi-plataforma no-web (móvil, juegos, CLI, desktop), JUDGE es el cuello de botella.
Para apps "escalables" enterprise, faltan deploy, load testing y observabilidad.

## Cobertura por Bundle

| Bundle | Multi-plataforma | Issue |
|--------|-----------------|-------|
| dev-cycle | OK | Stack-agnostic, zoom-out + tdd + code-review |
| qa-bundle | OK | Pitfalls para canvas games, RN, single-file |
| judge | PROBLEMA | 3 de 6 skills son web-centric |
| user-chaos | OK | user-chaos-tester y reverse-audit reescritos multi-plataforma |
| close-out | OK | Stack-agnostic |

## Skills con Sesgo Web (dentro de judge)

### judge-performance-budget — 100% WEB
FCP, LCP, TTI, Lighthouse, Chrome DevTools, webpack-bundle-analyzer, WebP/AVIF.
Falta: FPS/frame time (juegos), startup time (CLI), memory/battery (móvil),
IPC latency (desktop), cold start (serverless).

### judge-security-gates — 80% WEB
XSS, CSRF, CSP, innerHTML, X-Frame-Options.
Falta: APK tampering, insecure intents (móvil), save manipulation (juegos),
IPC injection (desktop), supply chain (CLI/serverless).

### judge-ux-vibe-check — 85% WEB
Responsive 320/768/1920, WCAG, focus indicator, navegación teclado.
Falta: UX de CLI (help text, error formatting), UX de juegos (tutorials, HUD clarity, difficulty curve).

### judge-launch-readiness — 40% WEB
CORS, página 404, responsive, GDPR/cookie consent.
Falta: APK signing, app store submission, desktop installer signing,
game console certification.

### judge-functional-test — 30% WEB
Conceptos generales (inventario, edge cases, happy path) pero la sección
"Browser automation" y TODOS los pitfalls son web/Supabase.

### judge-error-handling — 10% WEB
Casi universal. Solo "Error Boundary (React)" es específico. OK.

## Gaps Estructurales del Pipeline

1. **No hay fase de DEPLOY** — judge-launch-readiness pregunta "¿está listo?" pero
   nadie ejecuta el deploy. cloudflare-pages-deploy existe como skill pero no está
   en ninguna bundle del pipeline. La app queda verificada pero no publicada.

2. **No hay LOAD/STRESS TESTING** — judge-performance-budget mide Lighthouse (1 usuario,
   1 navegador). "Escalable" requiere saber qué pasa con 1000 usuarios concurrentes.
   No hay k6, artillery, locust, ni equivalente en el pipeline.

3. **No hay OBSERVABILIDAD post-deploy** — Nada sobre structured logging, métricas
   (Prometheus/Datadog), alerting, dashboards. La app funciona en QA pero nadie
   monitorea qué pasa con usuarios reales en producción.

4. **plan-sprint desconectado** — No hay handoff explícito entre plan-sprint y dev-cycle.
   El usuario lo salta a veces (intencional), pero incluso cuando no, no hay
   encadenamiento formal.

## Skills que se Solapan (nota para consolidación futura)

- **judge-functional-test ↔ qa-testing**: ambos hacen testing sistemático con
  clasificación de bugs. judge-functional-test es "verificación con evidencia",
  qa-testing es "discovery + fix workflow". Complementarios pero redundantes
  en cobertura de edge cases.
- **judge-security-gates ↔ reverse-audit**: ambos hacen security testing.
  judge-security-gates es estático (code patterns), reverse-audit es runtime
  (offensivo). Complementarios.
- **judge-performance-budget ↔ judge-launch-readiness**: ambos chequean bundle size
  y performance mínima. Solapamiento parcial.
