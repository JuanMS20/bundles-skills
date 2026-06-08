# Hermes Agent — Bundles & Skills

Configuración operativa de Hermes Agent: bundles de skills multi-fase, reglas operativas (AGENTS.md) y leyes de hierro (SOUL.md).

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
├── AGENTS.md             # Reglas operativas — jerarquía, proceso, anti-patrones
└── SOUL.md               # Leyes de hierro — Layer 1, inquebrantables
```

---

## Bundles — Pipelines Secuenciales

Cada bundle carga múltiples skills en orden y orquesta fases secuenciales con gates de aprobación.

| Bundle | Skills | Propósito |
|--------|--------|-----------|
| **plan-sprint** | `grill-with-docs` → `to-prd` → `to-issues` | Planeación: stress-test de ideas → PRD → issues en vertical slices |
| **dev-cycle** | `zoom-out` → `tdd` → `code-review` | Desarrollo: contexto → implementar con TDD → revisión estática |
| **qa-bundle** | `qa-testing` → `anti-hallucination` → `zoom-out` → `tdd` → `diagnose` | QA: testing sistemático → fix incremental → verificación runtime |
| **judge** | `judge-functional-test` → `judge-error-handling` → `judge-security-gates` → `judge-performance-budget` → `judge-ux-vibe-check` → `judge-launch-readiness` | Verificación 6-fases: funcional → errores → seguridad → performance → UX → launch readiness |
| **user-chaos** | `user-chaos-tester` → `judge-ux-vibe-check` → `reverse-audit` → `anti-hallucination` → `zoom-out` | Testing post-judge: usuario torpe + UX check + auditoría ofensiva |
| **close-out** | `improve-codebase-architecture` → `ci-cd-setup` → `migration-safety` → `diagnose` → `handoff` | Cierre de feature: arquitectura → CI/CD → migraciones → bugs → handoff |
| **doc-forge** | `project-mapper` → `manual-writer` → `pdf-export` → `zoom-out` | Documentación: mapear → escribir manual → exportar PDF |
| **skill-forge** | `write-a-skill` → `write-stack-skill` | Creación y auditoría de skills |

### Flujo de desarrollo completo

```
plan-sprint → dev-cycle → qa-bundle → judge → user-chaos → close-out
```

No todos los proyectos necesitan todos los bundles. Las fases se adaptan al tipo de proyecto.

---

## AGENTS.md — Reglas Operativas

Define el comportamiento del agente:

- **Jerarquía de reglas** con desempate (Seguridad > Honestidad > TDD > Cambios quirúrgicos > Modo trivial)
- **Verificación unificada** — skill → doc oficial → declarar confianza
- **Flujo de ingeniería** mapeado a skills de Matt Pocock (grill-me, tdd, diagnose, etc.)
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
