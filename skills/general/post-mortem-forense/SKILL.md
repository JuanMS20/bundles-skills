---
name: post-mortem-forense
description: "Análisis forense post-mortem: investiga qué pasó cuando algo falló en producción. Reconstruye la cadena de causalidad, identifica root cause, y genera actionables para prevenir recurrencia. Use when: 'post-mortem', 'qué pasó', 'investigar fallo', 'forense', 'root cause analysis', 'RCA', o después de un incidente en producción."
tags: [forensic, post-mortem, rca, incident-response, debugging]
---

# Post-Mortem Forense

Investigación estructurada de incidentes post-producción. No es debugging (eso es diagnose). Es **reconstruir la secuencia de eventos** para entender qué pasó, por qué, y cómo prevenirlo.

## Cuándo usar

- **Post-incidente:** Algo falló en producción y necesitas entender por qué
- **Post-regresión:** Un feature que funcionaba dejó de funcionar
- **Post-usuario:** Un usuario reportó comportamiento extraño
- **Complemento a diagnose:** Después de arreglar el bug, investigar la causa raíz profunda

## FASE 0 — Contención (antes de investigar)

**PRIORIDAD:** Si el sistema sigue caído o perdiendo datos → ARREGLAR PRIMERO, investigar DESPUÉS.

1. ¿El sistema está funcionando ahora? Si no → estabilizar
2. ¿Se están perdiendo datos activamente? Si sí → mitigar
3. ¿El impacto sigue creciendo? Si sí → contener

Solo cuando esté estable → proceder a investigación.

## FASE 1 — Recolección de Evidencia (15 min)

Recolectar TODO antes de analizar. No saltar a conclusiones.

### 1.1 Logs
- Logs de la aplicación (errors.log, app.log)
- Logs del servidor (nginx, apache, caddy)
- Logs de base de datos (slow query log, error log)
- Logs de infraestructura (docker, systemd, cloudwatch)

### 1.2 Métricas
- CPU/memory/disk usage en momento del fallo
- Request rate y error rate (5xx, 4xx)
- Database connection pool
- Response times (p50, p95, p99)

### 1.3 Estado del sistema
- Último deploy (¿qué cambió?)
- Último cambio de config
- Último cambio de DB schema
- Cambios en dependencias (package-lock, requirements.txt)

### 1.4 Reporte del usuario
- Qué hizo el usuario exactamente
- Qué esperaba que pasara
- Qué pasó en realidad
- Screenshots o recordings si existen

## FASE 2 — Línea de Tiempo (10 min)

Construir una cronología objetiva:

```
HH:MM - Evento (fuente)
14:30 - Deploy v1.2.3 (git log)
14:32 - Primer error 500 en /api/users (nginx log)
14:33 - DB connection pool agotado (app log)
14:35 - Usuario reporta "no puedo login" (ticket)
14:40 - Auto-scaling activado (cloudwatch)
14:42 - Errores cessan (nginx log)
```

**Regla:** Solo hechos con timestamp y fuente. No inferencias todavía.

## FASE 3 — Root Cause Analysis (15 min)

Aplica uno o más métodos:

### 3.1 5 Whys
```
Why 1: ¿Por qué falló? → Error 500 en /api/users
Why 2: ¿Por qué hubo error 500? → DB connection timeout
Why 3: ¿Por qué timeout? → Pool agotado
Why 4: ¿Por qué agotado? → Query lenta bloqueaba conexiones
Why 5: ¿Por qué query lenta? → Missing index en tabla users
ROOT CAUSE: Falta índice en users.email
```

### 3.2 Fishbone (Ishikawa)
Categorías:
- **Person:** ¿Error humano? ¿Falta de conocimiento?
- **Process:** ¿Falta de procedure? ¿Procedure incorrecta?
- **Technology:** ¿Bug? ¿Config incorrecta? ¿Dependency issue?
- **Environment:** ¿Infra? ¿Network? ¿Load?

### 3.3 Causal Chain
```
Trigger → Contributing Factor 1 → Contributing Factor 2 → Failure
```

## FASE 4 — Verificación de Root Cause

**CRITICAL:** No aceptes la root cause sin verificar:

1. ¿Puedes **reproducir** el problema en staging/dev con la misma condición?
2. ¿El fix propuesto **resuelve** el problema (no solo el síntoma)?
3. ¿Hay **evidencia directa** (logs, métricas) que soporte la root cause?
4. ¿Podría haber **otra causa** que explique los mismos síntomas?

Si no puedes verificar → marcar como "root cause probable, no confirmada".

## FASE 5 — Actionables

Generar items concretos, no recomendaciones vagas:

| # | Acción | Tipo | Prioridad | Owner |
|---|--------|------|-----------|-------|
| 1 | Agregar índice en users.email | Fix | P0 | Dev |
| 2 | Agregar query timeout de 30s | Hardening | P1 | Dev |
| 3 | Alerta cuando pool > 80% | Monitoring | P1 | Ops |
| 4 | Review de queries lentas mensual | Process | P2 | Tech Lead |

**Tipos:**
- **Fix:** Cambio de código/config que resuelve el problema
- **Hardening:** Prevención para que no vuelva a pasar
- **Detection:** Monitoreo para detectar antes la próxima vez
- **Process:** Cambio de workflow o procedure

## FASE 6 — Reporte Post-Mortem

Formato estándar:

```markdown
# Post-Mortem: [Título del Incidente]

## Resumen
- **Cuándo:** [fecha, hora, duración]
- **Impacto:** [qué se afectó, cuántos usuarios, datos perdidos]
- **Root cause:** [una oración]
- **Fix:** [qué se hizo]

## Línea de Tiempo
[tabla cronológica]

## Root Cause Analysis
[5 Whys o Fishbone]

## Actionables
[tabla con acciones]

## Lecciones Aprendidas
[qué salió bien, qué mejorar]
```

## Anti-patterns

- **No confundir con debugging:** Diagnose (matt-pocock) es para encontrar y arreglar el bug. Este skill es para **entender por qué pasó** y prevenir recurrencia.
- **No saltar a conclusiones:** Recolecta evidencia ANTES de hypothesize.
- **No blamear:** El post-mortem es blameless. Focus en process y technology, no en personas.
- **No action items vagos:** "Mejorar el monitoreo" no es un actionable. "Agregar alerta de CPU > 90% en docker" sí lo es.

## Relación con otros skills

- **diagnose (matt-pocock):** Predecesor. Diagnose encuentra y arregla; forense investiga la causa raíz profunda.
- **judge-error-handling:** Si el error no se manejó bien, forense expone por qué.
- **user-chaos-tester:** Si un usuario torpe encontró el bug, forense investiga la causa.
- **reverse-audit:** Si la vulnerabilidad fue explotada, forense investiga el impacto.
