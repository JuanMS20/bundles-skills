# Hermes Agent — Bundles & Skills

Configuración operativa de Hermes Agent: bundles de skills multi-fase, manual de prompts, reglas operativas (AGENTS.md) y leyes de hierro (SOUL.md).

Diseñado para [Hermes Agent](https://hermes-agent.nousresearch.com) por Nous Research.

---

## Estructura

```
.
├── bundles/              # 8 YAMLs — pipelines multi-skill secuenciales
│   ├── plan-sprint.yaml
│   ├── dev-cycle.yaml
│   ├── qa-bundle.yaml
│   ├── judge.yaml
│   ├── user-chaos.yaml
│   ├── close-out.yaml
│   ├── doc-forge.yaml
│   └── skill-forge.yaml
├── skills/               # 28 skills — las que usan los bundles
│   ├── code-review/
│   ├── creative/frontend-design/
│   ├── devops/ci-cd-setup/
│   ├── devops/migration-safety/
│   ├── doc-forge/
│   ├── general/           # judge-*, qa-testing, user-chaos-tester, etc.
│   ├── matt-pocock/      # tdd, diagnose, zoom-out, grill-with-docs, etc.
│   └── software-development/feature-dev/
├── manual/               # Manual de prompts para bundles
│   └── manual-prompts-bundles-v5.pdf
├── AGENTS.md             # Reglas operativas — jerarquía, proceso, anti-patrones
└── SOUL.md               # Leyes de hierro — Layer 1, inquebrantables
```

---

## Bundles — Pipelines Secuenciales

Cada bundle carga múltiples skills en orden y orquesta fases secuenciales con gates de aprobación explícita entre fases.

| Bundle | Skills | Propósito |
|--------|--------|-----------|
| **plan-sprint** | `grill-with-docs` → `to-prd` → `to-issues` | Planeación: stress-test de ideas → PRD → issues en vertical slices |
| **dev-cycle** | `zoom-out` → `tdd` → `code-review` → `feature-dev` → `frontend-design` | Desarrollo: contexto → TDD → revisión → feature discovery → diseño UI |
| **qa-bundle** | `qa-testing` → `diagnose` → `anti-hallucination` | QA: testing sistemático → fix incremental → verificación runtime |
| **judge** | `judge-functional-test` → `judge-error-handling` → `judge-security-gates` → `judge-performance-budget` → `judge-ux-vibe-check` → `judge-launch-readiness` | Verificación 6-fases: funcional → errores → seguridad → performance → UX → launch readiness |
| **user-chaos** | `user-chaos-tester` → `reverse-audit` → `anti-hallucination` → `zoom-out` | Testing post-judge: usuario torpe + auditoría ofensiva + verificación |
| **close-out** | `improve-codebase-architecture` → `ci-cd-setup` → `migration-safety` → `handoff` | Cierre de feature: arquitectura → CI/CD → migraciones → handoff |
| **doc-forge** | `project-mapper` → `manual-writer` → `pdf-export` | Documentación: mapear → escribir manual → exportar PDF |
| **skill-forge** | `write-a-skill` → `write-stack-skill` | Creación y auditoría de skills |

### Flujo de desarrollo completo

```
plan-sprint → dev-cycle → qa-bundle → judge → user-chaos → close-out → doc-forge
```

### Uso por situación

No todos los proyectos necesitan todos los bundles. Las fases se adaptan al tipo de proyecto:

| Situación | Bundles a usar | Orden |
|---|---|---|
| **Proyecto nuevo** | plan-sprint → dev-cycle → qa-bundle → judge → user-chaos → close-out | Secuencial completo |
| **Feature simple en proyecto existente** | dev-cycle → qa-bundle → judge | Skip plan-sprint si PRD ya existe |
| **Feature con UI** | frontend-design → dev-cycle → qa-bundle → judge | Diseño antes de código |
| **Bug fix en producción** | diagnose → dev-cycle → qa-bundle | Skip judge si no cambia comportamiento externo |
| **Hotfix crítico** | diagnose → dev-cycle (fix mínimo) → qa-bundle (smoke) | Rápido, skip plan/judge/chaos |
| **Refactor interno** | zoom-out → dev-cycle → qa-bundle → close-out | Skip judge si no cambia API externa |
| **Security audit puntual** | judge (solo FASE 3) | Independiente |
| **Documentación sola** | doc-forge | Independiente |

---

## Skills

Las 28 skills en `skills/` son las únicas referenciadas por los 8 bundles. Están organizadas por dominio:

### Matt Pocock (flujo de ingeniería)
- `grill-with-docs` — Stress-test de ideas contra documentación
- `to-prd` — Convertir contexto en PRD formal
- `to-issues` — Descomponer PRD en issues independientes
- `zoom-out` — Panorama amplio cuando no entiendes el código
- `tdd` — Red-green-refactor, obligatorio para código nuevo
- `diagnose` — Debug disciplinado: repro → hypothesise → instrument → fix
- `improve-codebase-architecture` — Refactorización guiada por deepening
- `handoff` — Compactar sesión para el siguiente agente
- `write-a-skill` — Crear skills con estructura progresiva

### General (calidad y verificación)
- `anti-hallucination` — Verificación de APIs y datos, evidence-first
- `qa-testing` — Testing sistemático con TODOs estructurados
- `user-chaos-tester` — Testing como usuario torpe, busca anomalías de flujo
- `reverse-audit` — Auditoría ofensiva desde fuera del sistema
- `judge-functional-test` — Veredicto sobre funcionalidad
- `judge-error-handling` — Veredicto sobre resiliencia
- `judge-security-gates` — Veredicto sobre seguridad
- `judge-performance-budget` — Veredicto sobre performance
- `judge-ux-vibe-check` — Veredicto sobre UX
- `judge-launch-readiness` — Veredicto final de lanzamiento
- `write-stack-skill` — Crear skills específicas de stack

### Desarrollo
- `code-review` — Revisión estática antes de merge
- `feature-dev` — Workflow de 7 fases con 3 agentes especializados

### Diseño
- `frontend-design` — Workflow anti-AI-slop de 8 fases para UI estética

### DevOps
- `ci-cd-setup` — Pipelines de CI/CD con GitHub Actions
- `migration-safety` — Migraciones DB que no rompen producción

### Documentación
- `project-mapper` — Mapear codebase en blueprint YAML
- `manual-writer` — Generar manuales de usuario/desarrollador
- `pdf-export` — Exportar Markdown a PDF profesional

---

## Manual de Prompts

`manual/manual-prompts-bundles-v5.pdf` contiene:
- Prompts detallados para cada bundle
- Estructura XML (`<context>`, `<instructions>`, `<examples>`, `<constraints>`, `<output_format>`, `<verification>`)
- Separación de roles: `qa-bundle` = QA Engineer (ejecuta), `judge` = Technical Auditor (evalúa sin ejecutar), `user-chaos` = Tester de Caos
- Mapa de uso por etapa del proyecto
- Fuentes ≥ 14px

---

## AGENTS.md — Reglas Operativas

Define el comportamiento del agente:

- **Jerarquía de reglas** con desempate (Seguridad > Honestidad > TDD > Cambios quirúrgicos > Modo trivial)
- **Verificación unificada** — skill → doc oficial → declarar confianza
- **Flujo de ingeniería** mapeado a skills de Matt Pocock
- **Anti-patrones** con consecuencias y alternativas
- **Context engineering** — just-in-time, progressive disclosure, compresión activa
- **Seguridad** — sanitización, confirmación de destructivos, subagentes
- **Auto-mejora** — captura reactiva de errores, patrones repetidos → skills

## SOUL.md — Leyes de Hierro

Layer 1. Se cargan ANTES que todo, cada turno. Inquebrantables:

1. **Verificación antes de claims** — evidencia fresca, no "debería funcionar"
2. **Carga skills antes de actuar** — las skills contienen conocimiento verificado
3. **Verifica que las herramientas funcionan** — un claim en memoria no es evidencia
4. **Cambios quirúrgicos** — toca solo lo necesario, no "mejores" código adyacente

---

## Instalación

### Bundles

Copia los YAMLs a tu directorio de bundles de Hermes:

```bash
# Linux/macOS
cp bundles/*.yaml ~/.hermes/skill-bundles/

# Windows (MSYS/git-bash)
cp bundles/*.yaml /c/Users/<tu-usuario>/AppData/Local/hermes/skill-bundles/
```

### Skills

Las skills se copian al directorio de skills de Hermes:

```bash
# Linux/macOS
cp -r skills/* ~/.hermes/skills/

# Windows (MSYS/git-bash)
cp -r skills/* /c/Users/<tu-usuario>/AppData/Local/hermes/skills/
```

### AGENTS.md y SOUL.md

Coloca estos archivos en la raíz de tu proyecto o en tu home directory:

```bash
cp AGENTS.md SOUL.md /tu/proyecto/
```

Hermes detecta automáticamente `AGENTS.md` en el directorio de trabajo.

---

## Requisitos

- [Hermes Agent](https://hermes-agent.nousresearch.com) instalado
- Skills referenciadas por los bundles deben estar instaladas (verificables con `hermes skills list`)

---

## Licencia

Uso personal. Compartido como referencia de configuración para la comunidad de Hermes Agent.
