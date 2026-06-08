---
name: project-mapper
description: "Map any codebase/project into a structured blueprint (YAML). Analyzes architecture, components, features, data models, config, and user flows. Use when creating a manual, documentation, onboarding guide, or need to understand a project holistically. Integrates zoom-out techniques for multi-layer analysis."
---

# Project Mapper

Analyzes a project and produces a structured blueprint YAML that serves as input for `manual-writer` or any documentation task.

## When to Use

- Before writing any manual or user guide
- When onboarding to an unfamiliar codebase
- When the user says "mapear", "analizar proyecto", "entender el sistema", "¿qué hace este proyecto?"
- As first step of the doc-forge pipeline

## Process

### FASE 1 — Discovery (Zoom-Out)

Execute in order. Each step fills a section of the blueprint.

**Step 1: Top-level scan**
```
- search_files(target='files', pattern='*') in project root
- Identify config files: package.json, pyproject.toml, Cargo.toml, etc.
- Read the top-level config to determine tech stack
- Read README.md if exists
```

**Step 2: Architecture layers**
```
For each layer detected:
  - Frontend: src/, app/, pages/, components/
  - Backend: api/, server/, routes/, controllers/
  - Database: schema/, migrations/, models/, prisma/
  - Config: .env.example, config/, settings/
  - Infra: docker*, terraform/, k8s/, deploy/
  
  For each layer:
    - List key files (search_files with file_glob)
    - Read entry points (index.*, main.*, app.*)
    - Identify patterns (MVC, component-based, service layer)
```

**Step 3: Feature mapping**
```
- Search for route definitions (routes, pages, endpoints)
- Search for UI components (screens, pages, views)
- For each feature: name, description, entry point file
```

**Step 4: Data model**
```
- Find schema files (*.sql, schema.prisma, models/*.py)
- List entities/tables with key fields
- Identify relationships (foreign keys, references)
```

**Step 5: User flows**
```
- Identify auth flows (login, register, logout)
- Identify main CRUD operations
- Identify role-based access if applicable
```

### FASE 2 — Synthesize Blueprint

Write the blueprint to `<project_root>/docs/blueprint.yaml`:

```yaml
# Blueprint generado por project-mapper
# Fecha: YYYY-MM-DD
# Proyecto: [nombre]

meta:
  name: ""
  description: ""
  version: ""
  generated: "YYYY-MM-DD"

stack:
  language: ""
  framework: ""
  runtime: ""
  package_manager: ""
  database: ""
  deployment: ""

architecture:
  pattern: ""  # MVC, component-based, layered, etc.
  layers:
    - name: ""
      path: ""
      responsibility: ""
      key_files: []

features:
  - name: ""
    description: ""
    entry_point: ""
    type: ""  # page, endpoint, service, background-job
    user_roles: []  # who can access

data_models:
  - name: ""
    table: ""
    fields:
      - name: ""
        type: ""
        description: ""
    relationships:
      - type: ""  # has_many, belongs_to, many_to_many
        target: ""

config:
  env_vars:
    - name: ""
      required: true/false
      description: ""
  config_files: []

user_flows:
  - name: ""
    steps: []
    roles: []

dependencies:
  key_packages:
    - name: ""
      version: ""
      purpose: ""
```

### FASE 3 — Validate

- [ ] Every feature has an entry_point that exists on disk
- [ ] Every data_model references a real table/schema
- [ ] stack section matches actual config files
- [ ] No invented components — only things found in code
- [ ] Blueprint is valid YAML (python3 -c "import yaml; yaml.safe_load(open('...'))")

## Pitfalls

- **Inventing architecture**: Only describe patterns you found evidence for in code. "Looks like MVC" needs 3+ indicators (routes/, models/, views/ or equivalent).
- **Missing implicit features**: Auth, error handling, logging, health checks are features too. Don't skip them.
- **Shallow scan**: Reading only top-level files misses the real architecture. Always go 2-3 levels deep.
- **Stale assumptions**: If the project has both old and new patterns (e.g., class components AND hooks), document BOTH with a note on which is current.

## Output

The blueprint YAML is the artifact. Inform the user:
1. Where it was saved
2. Summary: N features, N data models, N layers
3. Next step: feed to `manual-writer`
