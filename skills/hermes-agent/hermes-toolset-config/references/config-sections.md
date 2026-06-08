# Hermes Config — Toolset Sections Reference

Extracted from config.yaml real (host Windows, profile default).

## agent.disabled_toolsets

```yaml
agent:
  disabled_toolsets: []   # default: nothing disabled
  # Nombres válidos: vision, browser, tts, image_gen, web, terminal, file,
  # session_search, skills, memory, code_execution, delegation, messaging,
  # clarify, todo, cronjob, kanban, computer_use, mcp-<server_name>
```

## platform_toolsets (CLI default)

```yaml
platform_toolsets:
  cli:
    - browser
    - clarify
    - code_execution
    - computer_use
    - cronjob
    - delegation
    - file
    - image_gen
    - mcp-Roblox_Studio
    - memory
    - messaging
    - session_search
    - skills
    - terminal
    - todo
    - tts
    - vision
    - web
```

## auxiliaries (no se desactivan con disabled_toolsets)

Estos son sub-sistemas internos, no toolsets expuestos como tools:

```yaml
auxiliary:
  vision:        # modelo auxiliar para vision_analyze (non-vision models)
  web_extract:   # modelo para extracción web
  compression:   # compresión de contexto
  skills_hub:    # búsqueda en Skills Hub
  approval:      # aprobación de comandos
  mcp:           # procesamiento MCP
  title_generation:
  triage_specifier:
  kanban_decomposer:
  profile_describer:
  curator:
  session_search:
```

`disabled_toolsets` solo afecta toolsets expuestos como tools en el system prompt.
No desactiva auxiliaries (esos se configuran en `auxiliary.*`).
