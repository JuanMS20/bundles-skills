# Hermes Agent — Bundles & Skills

Configuración operativa de Hermes Agent: bundles de skills multi-fase, manual de prompts, reglas operativas (AGENTS.md) y leyes de hierro (SOUL.md).

Diseñado para [Hermes Agent](https://hermes-agent.nousresearch.com) por Nous Research.

---

## Estructura

```
.
├── bundles/              # 12 YAMLs — pipelines multi-skill secuenciales
│   ├── el-buhonero.yaml
│   ├── math-engineer.yaml
│   ├── plan-sprint.yaml
│   ├── dev-cycle.yaml
│   ├── qa-bundle.yaml
│   ├── judge.yaml
│   ├── user-chaos.yaml
│   ├── close-out.yaml
│   ├── doc-forge.yaml
│   ├── product-sense.yaml
│   ├── skill-forge.yaml
│   └── video-studio.yaml
├── skills/               # 34 skills — las que usan los bundles + standalone
│   ├── code-review/
│   ├── creative/frontend-design/
│   ├── creative/remotion-video/
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
| **video-studio** | `remotion-video` → `frontend-design` → `grill-with-docs` → `zoom-out` → `qa-testing` | Edición profesional de video: vlogs, tutoriales, TikTok, YouTube, podcasts, entrevistas, motion graphics. Desde concepto hasta render |
| **el-buhonero** | `graphify` → `zoom-out` → `anti-hallucination` | Orientador de flujo: llegas a un repo desconocido, entiende el código y recomienda el pipeline correcto |
|| **math-engineer** | `math-consultant` → `anti-hallucination` → `zoom-out` | Validación matemática: revisa cálculos de física, geometría, probabilidad. Detecta errores y proporciona fórmulas corregidas |
|| **product-sense** | `zoom-out` → `grill-me` → `competitive-intelligence` | Pensamiento crítico de producto: ¿es realmente útil? ¿alguien lo usaría? Auditoría de features, redundancias, valor real |

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
| **Video promocional / contenido** | video-studio | Independiente. Usa grill-with-docs para definir concepto, audiencia, plataforma y estilo antes de editar |
| **No sé qué bundle usar** | el-buhonero | Siempre. Usa grill-me para clarificar, graphify para mapear, y recomienda el flujo correcto |
| **Exploración de codebase desconocida** | el-buhonero | Primero, antes de cualquier bundle. Entiende el proyecto antes de actuar |
| **No sé qué bundle usar (auto-detectado)** | repo-onboarding | Automático. Si el agente detecta repo nuevo sin contexto, carga esta skill primero y recomienda el bundle |
| **Cálculos matemáticos / física de juego** | math-engineer | Cuando la lógica numérica "casi funciona" o necesitas verificar fórmulas antes de implementar |
| **¿Esto es realmente útil?** | product-sense | Cuando el software funciona pero preguntas si alguien lo usaría, si hay features redundantes, o si da valor real |

---

## Skills

Las 34 skills en `skills/` son las únicas referenciadas por los 12 bundles, más skills standalone. Están organizadas por dominio:

### Matt Pocock (flujo de ingeniería)
- `grill-with-docs` — Stress-test de ideas contra documentación
- `grill-me` — Interrogar al usuario hasta que la petición sea clara
- `to-prd` — Convertir contexto en PRD formal
- `to-issues` — Descomponer PRD en issues independientes
- `zoom-out` — Panorama amplio cuando no entiendes el código
- `tdd` — Red-green-refactor, obligatorio para código nuevo
- `diagnose` — Debug disciplinado: repro → hypothesise → instrument → fix
- `improve-codebase-architecture` — Refactorización guiada por deepening
- `handoff` — Compactar sesión para el siguiente agente
- `write-a-skill` — Crear skills con estructura progresiva

### General (calidad, verificación y orientación)
- `anti-hallucination` — Verificación de APIs y datos, evidence-first
- `graphify` — Mapear codebase en knowledge graph con análisis de arquitectura y dependencias
- `math-consultant` — Revisar cálculos matemáticos, detectar errores, proporcionar fórmulas corregidas para física, geometría, y probabilidad
- `repo-onboarding` — Onboarding automático de repos desconocidos: mapear, analizar, recomendar bundle
- `competitive-intelligence` — Investigador topo: teardown sistemático de competidores, features, pricing, estrategias
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
- `remotion-video` — Edición profesional de video con Remotion: formatos por plataforma, transiciones, subtítulos animados, lower thirds, color grading, audio sync

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
