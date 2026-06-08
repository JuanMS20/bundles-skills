# Kilo Code — Real-World Optimization Findings

Sesion de optimizacion: 2026-05-28. Configuracion: 64 skills, 26 agents, 15 rules.

## Resultados

```
                    ANTES       DESPUES     AHORRO
Rules globales:     8           5           -38%
Rules total:        15          9           -40%
Skills activas:     64          33          -48%
Agents activos:     26          16          -38%
Tokens/request:     ~5,500      ~2,133      -61%
```

## Patrones de redundancia encontrados

### 1. Rules que duplican skills
3 rules con applyTo: ** replicaban contenido de skills:
- typescript-patterns.md duplicaba typescript-patterns/ skill
- python-patterns.md duplicaba python-patterns/ skill
- golang-patterns.md duplicaba golang-patterns/ skill

### 2. Rules que se solapan entre si
- security.instructions.md (14 lineas) solapaba con engineering-rules
- coding-style.instructions.md (14 lineas) solapaba con engineering-rules
- elite-engineering.instructions.md (81 lineas) solapaba con engineering-rules

### 3. Skills que se solapan entre si
5 pares: tdd+tdd-workflow, write-a-skill+skill-creator, frontend-design+frontend-patterns, senior-architect+senior-fullstack, grill-me+grill-with-docs

### 4. Agents con referencias a skills archivadas
8 agents referenciaban skills que ya no existian post-archiving.
Siempre escanear agents con: re.findall(r'`([^`]+)`', content)

## Fórmula de estimacion rapida

```
tokens_per_request ~=
  (global_rules_bytes / 3) +
  (skill_count * 100) +
  (agent_count * 200) +
  5000  # system prompt + tools
```

## Archivos archivados (recuperables)

Skills: 30 skills archivadas en _archive/
Agents: 10 agents archivados en _archive/
Rules: 7 rules eliminadas
