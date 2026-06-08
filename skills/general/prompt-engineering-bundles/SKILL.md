---
name: prompt-engineering-bundles
description: |
  Prompts reutilizables para los 8 bundles de desarrollo del repo bundles-skills.
  Pipeline: plan-sprint → dev-cycle → qa-bundle → judge → user-chaos → close-out
  + doc-forge (opcional) + skill-forge (opcional).
  Use when running any development bundle or when user asks about prompts.
---

# Prompt Engineering para Bundles de Desarrollo

## Referencias

- `references/skill-quality-research-2026-06.md` — Research de calidad de skills (agentskills.io, SkillsBench)
- `references/judge-qa-role-separation.md` — **Separación de roles entre qa-bundle/judge/user-chaos. ÚSALO cuando trabajes con estos bundles.**
- `templates/bundle-yaml-template.yaml` — Template para crear/actualizar bundles YAML
- **Bundles YAML**: `C:\Users\ASUS\AppData\Local\hermes\skill-bundles\*.yaml` (8 bundles)
- **Repo original**: `github.com/JuanMS20/bundles-skills` (rama `master/bundles/`)
- Los 8 YAMLs locales son idénticos al repo (verificado Junio 2026)

## CRITICAL: No Crear Bundles Nuevos

**El usuario tiene su propio repo con 8 bundles definidos.** NUNCA crear bundles nuevos sin que lo pida explícitamente. Si dice "mejorar bundles" = mejorar los YAML existentes, NO crear nuevos ni actualizar el PDF.

## Estructura de cada bundle YAML
```yaml
name: nombre-del-bundle
description: Qué hace el bundle
skills:
  - skill-1
  - skill-2
instruction: |
  Prompt que se ejecuta cuando se activa el bundle.
  Referencia las skills por nombre para indicar
  en qué fase se usa cada una.
```

**Pitfall: `hermes config set` con listas**
`hermes config set` serializa listas como strings, no como arrays YAML.
Fix: editar el YAML directamente después, o usar `sed` para convertir:
```bash
# Esto crea un string, no una lista:
hermes config set agent.disabled_toolsets '["vision"]'
# Fix: editar YAML para que sea:
# disabled_toolsets:
# - vision
```

**Bundles actuales (8 archivos en `C:\Users\ASUS\AppData\Local\hermes\skill-bundles\`):**
| Bundle | Skills | Propósito |
|--------|--------|-----------|
| plan-sprint | grill-with-docs, to-prd, to-issues | Requirements → PRD → Issues |
| dev-cycle | zoom-out, tdd, code-review, **feature-dev**, **frontend-design** | TDD + code review + feature workflow + UI design |
| qa-bundle | qa-testing, anti-hallucination, zoom-out, tdd, diagnose | QA + fixes + verificación runtime |
| judge | judge-functional-test, judge-error-handling, judge-security-gates, judge-performance-budget, judge-ux-vibe-check, judge-launch-readiness | Pipeline 6 fases post-QA |
| user-chaos | user-chaos-tester | Testing desde fuera (caos puro) |
| close-out | improve-codebase-architecture, diagnose, handoff | Cierre + handoff |
| doc-forge | project-mapper, manual-writer, pdf-export, zoom-out | Manual + PDF |
| skill-forge | write-a-skill, anti-hallucination | Creación de skills |

### Estado actual (Junio 2026) — v4 corregido

**PDF v4 generado:** `C:\Users\ASUS\Downloads\manual-prompts-bundles-v4.pdf` (38 páginas, 50 KB)

El bundle `judge` es monolítico con 6 fases secuenciales (Levantamiento → Funcional → Errores → Seguridad → Performance → UX → Launch + Veredicto). El `qa-bundle` hace testing + fixes con TDD antes de judge. `user-chaos` complementa con testing desde fuera.

**Corrección v4 vs v3:**
- `user-chaos` YA NO duplica `judge-ux-vibe-check` — FASE 2 ahora es "Navegación Confusa" (hallazgos de flujo, no scoring)
- `user-chaos` YA NO duplica seguridad de judge — FASE 3 ahora es "Validación Cruzada" (verificar post-caos)
- `qa-bundle` ahora existe como bundle 3 explícito con testing + fixes TDD + verificación runtime

**Separación de roles (CRITICAL):**

| Bundle | Rol | Hace | NO hace |
|--------|-----|------|---------|
| **qa-bundle** | QA Engineer | Ejecuta tests, encuentra bugs, fixea con TDD | No emite veredicto formal |
| **judge** | Technical Auditor | Evalúa evidencia ajena, emite veredicto APROBADO/RECHAZADO | No ejecuta tests ni hace fixes |
| **user-chaos** | Tester de Caos | Rompe la app como usuario torpe/impaciente/creativo | No duplica UX scoring ni seguridad formal |

**Por qué importa:** Si judge dice "Eres un QA Engineer" y qa-bundle también dice "Eres un QA Engineer", ambos bundles tienen el mismo rol → el agente ejecuta tests en lugar de evaluar evidencia. El rol define el *modo de operación*, no solo el dominio.

**Pitfall — Comparar YAMLs local vs remoto:** `web_extract` trunca YAMLs grandes. Usar `curl -sL <raw_url>` + `cat <local_path>` para comparación byte a byte confiable.

## Reglas de Ejecución

### Research Obligatorio (mínimo 50 búsquedas)

Cuando el usuario pide research para prompts o documentación:
- **Mínimo 50 búsquedas** antes de escribir contenido
- Categorizar: papers académicos, docs oficiales, best practices, herramientas, anti-patterns
- Citar fuentes en el output (URLs, autores, fechas)
- "5 búsquedas no es research" — el usuario lo rechazará
- Usar delegate_task con toolsets=["web"] para paralelizar búsquedas

### Entrega en PDF (no Markdown)

Cuando el usuario pide un manual/documento:
- **Entregar PDF**, no Markdown
- Guardar en `C:\Users\ASUS\Downloads\` o `C:\Users\ASUS\Documents\`
- Usar reportlab para generar PDF (WeasyPrint falla en Windows sin GTK)
- **Code blocks/prompts: fontSize >= 14** (16 preferido). NUNCA < 12.
- Si el PDF tiene código pequeño, el usuario lo rechazará inmediatamente

### Estructura del Manual por Bundles

Cada bundle tiene:
1. Propósito (1 oración)
2. Prompt Base (XML tags estructurados)
3. Técnicas Aplicadas (con fuentes)
4. Verification checklist
5. Ejemplos few-shot

## Resumen Rápido por Bundle (v3)

| Bundle | Propósito | Regla Clave |
|--------|-----------|-------------|
| plan-sprint | Alinear requirements | 3 preguntas máximo por ronda |
| dev-cycle | Implementar con TDD | 1 issue = 1 PR, tests antes de código |
| qa-bundle | QA + fixes + runtime check | Bugs por severidad, TDD para fixes |
| judge | Verificación 6 fases post-QA | Secuencial, cada fase debe pasar |
| user-chaos | Testing desde fuera | Mínimo 5 vectores de caos |
| close-out | Cierre completo | CI/CD obligatorio antes de cerrar |
| doc-forge | Documentación | Muestra ANTES de escribir todo |
| skill-forge | Creación de skills | anti-hallucination obligatorio |

## Anti-Hallucination Universal

1. Nunca declarar "completado" sin evidencia
2. No confiar en claims de la IA — ejecutar siempre
3. Triple verificación post-deploy
4. Declarar limitaciones explícitamente
5. Evidencia > Claims (curl output, test output, screenshots)

## XML Tags Universales

```xml
<role>Rol específico</role>
<context>Datos relevantes</context>
<instructions>Paso a paso</instructions>
<constraints>Qué NO hacer</constraints>
<examples>Few-shot (2-3)</examples>
<output_format>Schema explícito</output_format>
<verification>Cómo verificar</verification>
```

## Reglas de Posición

- Instrucciones clave: AL PRINCIPIO o FINAL
- Preguntas: AL FINAL después del contexto
- Restricciones: Después de instrucciones
- Ejemplos: Después de constraints

## Calidad de Bundle YAMLs (Research Skills 2026-06-08)

Aplicar estos criterios cuando se crea o mejora un bundle YAML:

### Criterios de Calidad (Tax Test)
Aplicar a cada oración del `instruction`: **"¿El agente haría esto mal sin esta instrucción?"**
Si NO → eliminar. Cada línea es un impuesto sobre el contexto.

### Estructura Requerida por Bundle
Cada bundle YAML debe tener:
1. **description** = routing trigger (no documentación). Incluir trigger phrases reales del usuario.
2. **instruction** con secciones:
   - Fases/proceso paso a paso
   - Output template exacto (cómo se ve el resultado)
   - Gotchas (hechos reales del entorno, no genéricos)
   - Verificación (checklist de calidad)
   - Si falla (qué hacer cuando algo falla)
3. **Negative examples**: "NO confíes en claims", "NO fabriques números"

### Anti-Hallucination en Bundles
- Gotchas > "lo obvio" (el modelo ya sabe lo obvio)
- Ejemplos negativos previenen alucinaciones comunes
- Output templates = contrato de formato consistente
- Scripts deterministas para parsing/formatting

### Pitfall: Confundir "mejorar bundles" con "actualizar PDF"
**SEÑAL DE ALERTA:** Si el usuario dice "mejorar calidad de bundles", se refiere a los ARCHIVOS YAML en `~/.hermes/skill-bundles/`, NO al PDF manual ni a las skills subyacentes que ya existen.

## Anti-Patterns

| Anti-Patrón | Solución |
|-------------|----------|
| Few-Shot Pollution | Verificar cada ejemplo contra requirements |
| Instruction Stacking | Máximo 8-10 reglas por prompt |
| Format Via Example | Schema explícito SIEMPRE |
| Persona Stuffing | Rol específico, no "experto mundial" |
| Negation Overload | Framing positivo ("usa X" > "no uses Y") |
| **Rol Duplicado entre Bundles** | Si dos bundles comparten el mismo `<role>`, uno de ellos está mal definido. judge=Auditor, qa=Engineer, chaos=Tester |
| Confundir targets | "Mejorar bundles" = YAML files, NO el PDF manual |

## Generación de PDF (v3)

Cuando el usuario pide entregar el manual como PDF:
1. WeasyPrint falla en Windows sin GTK → usar reportlab directamente
2. Script comprobado: escribir script Python que use `reportlab.lib` con `SimpleDocTemplate`
3. **fontSize >= 14** para código/prompts (16 preferido)
4. `Preformatted` para bloques de código, `Paragraph` para texto normal
5. Parsear markdown manualmente (headings, bullets, code blocks, tables)
6. Output a `C:\Users\ASUS\Downloads\`
7. Verificar tamaño > 0 después de generar