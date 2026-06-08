# Pitfalls — Sprint Planning

## 1. Branch Ownership (CRÍTICO)

**Problema:** Crear `integration` desde `main` sin preguntar si el usuario puede tocar `main`.

**Solución:** SIEMPRE preguntar antes de crear branches:
- ¿Qué branches puedo tocar?
- ¿Cuáles son intocables?
- ¿Necesito que alguien haga push por mí?

**Patrón correcto:**
```
main (protegido, nadie push directo)
├── camara (Juan Esteban trabaja aquí)
├── home_screen (Zaira trabaja aquí)
├── mapa (Villalobos trabaja aquí)
└── integration (rama separada, recibe PRs de todas)
```

**Error común:** asumir que el usuario tiene permisos de push a `main` o a ramas ajenas.

## 2. .gitignore — Preguntar qué excluir

**Problema:** Asumir qué archivos no van a producción.

**Solución:** Preguntar al usuario:
- ¿Archivos markdown van al repo?
- ¿Documentos de Word/PDF van?
- ¿Hay carpetas de docs que excluir?

No todos los proyectos excluyen lo mismo. Un README.md siempre debe incluirse.

## 3. PRD desde documentación existente

**Problema:** Entrevistar al usuario cuando ya hay docs (TAREAS_PENDIENTES, RESUMEN_EJECUTIVO, etc.).

**Solución:** Sintetizar desde lo que existe. El PRD se construye desde hechos, no desde preguntas. Solo preguntar si hay gaps críticos.

## 4. Regla de Diseño

**Problema:** Features nuevas que no encajan visualmente con el resto de la app.

**Solución:** Si el usuario menciona "respetar el diseño existente", documentar en:
- CONTEXT.md → sección "Regla de Diseño"
- PRD.md → Further Notes

Cualquier issue nueva debe referenciar esta regla en sus acceptance criteria.
