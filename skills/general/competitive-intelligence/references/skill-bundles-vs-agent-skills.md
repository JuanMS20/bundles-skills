# Skill Bundles vs Agent Skills — Diferencias Clave (2026)

## Agent Skills (estandar abierto)
- Anunciado por Anthropic, 18 dic 2025
- agentskills.io — estandar portatil
- Estructura: carpeta + SKILL.md
- Soportado por: Claude Code, Cursor, VS Code/Copilot, Codex CLI, Gemini CLI, Hermes
- Cada skill = individuo, no agrupado

## Skill Bundles (EXCLUSIVO de Hermes)
- YAML que agrupa MULTIPLES skills bajo un slash command
- Puede incluir: skills + memory + cron jobs + subagents
- No tiene equivalente directo en otras herramientas
- Otros tools tienen equivalentes parciales:
  - GitHub Copilot: Custom Agents (perfiles, no bundles)
  - VS Code: Agent Skills (individuales)
  - Cursor: Custom rules (solo instrucciones)
  - Claude Code: Skills (individuales)

## Opinion de usuarios
- Critica comun: "demasiadas skills bundled" (Theo: 100+ skills irrelevantes)
- Defensa: "son utiles para power users que configuran profiles" (Teknium)
- Patron: power users limpian skills innecesarias, usuarios promedio se confunden
- Menos es mas: 30 skills puede ser desastre para debug
- Profiles separados > un solo profile universal

## Fuentes
- Reddit r/hermesagent
- Twitter/X (@theo, @boxmining, @akshay_pachaar)
- hermes-agent.nousresearch.com/docs
- GitHub NousResearch/hermes-agent issues