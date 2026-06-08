---
name: technical-docs
description: "Framework para redactar documentación técnica de software: README, API reference, ADRs, guías, changelogs, arquitectura. Use when user pide 'documentar', 'README', 'API docs', 'changelog', 'ADR', 'guía de uso', 'arquitectura', o necesita producir docs para un desarrollo de software."
---

# Technical Docs

Framework para producir documentación técnica de calidad profesional. Basado en Diátaxis framework, GitBook/Slite best practices (2026).

## Tipos de Documento

| Tipo | Audiencia | Propósito |
|------|-----------|-----------|
| README | Developers (nuevos) | Qué es, cómo empiezo, qué hace |
| API Reference | Developers (integradores) | Endpoints, params, responses, ejemplos |
| ADR | Equipo de desarrollo | Decisión arquitectónica + contexto + consecuencias |
| Tutorial | Usuarios nuevos | Aprendizaje guiado paso a paso |
| How-to Guide | Usuarios con contexto | Resolver objetivo específico |
| Changelog | Todos | Qué cambió, cuándo, impacto |
| Architecture Doc | Equipo técnico | Componentes, relaciones, "por qué" estratégico |

## Workflow

1. **Identificar tipo** de documento necesario
2. **Identificar audiencia** primaria (¿developer? ¿usuario final? ¿PM?)
3. **Aplicar template** correspondiente (ver abajo)
4. **Escribir** siguiendo principios
5. **Checklist** de calidad

## Principios

- **Task-first**: el lector viene a hacer algo. Que lo encuentre rápido.
- **Ejemplos ejecutables**: cada snippet debe funcionar copy-paste. Cero pseudocódigo en docs de API.
- **Una idea por sección**: si un H2 tiene 5 temas, son 5 H2s.
- **Máximo 2 niveles de subpáginas**: más profundo = confusión.
- **Cross-reference > duplicación**: linkear antes que copiar.
- **Heading descriptivos**: "Instalar dependencias" > "Setup".
- **Consistencia terminológica**: mismo término siempre, sinónimos generan confusión.

## Templates

### README

```
# [Nombre del Proyecto]
> Una línea que diga qué hace y para quién.

## Requisitos
- [lista con versiones mínimas]

## Instalación
[pasos exactos, comandos ejecutables]

## Uso rápido
[ejemplo mínimo funcional]

## Estructura del proyecto
[árbol de directorios con descripción de cada uno]

## Configuración
[variables de entorno, opciones, defaults]

## Contribuir
[link a CONTRIBUTING.md o instrucciones mínimas]

## Licencia
[tipo + link]
```

### API Reference

Por endpoint:
```
## [MÉTODO] [ruta]

**Descripción**: [qué hace en una línea]

### Parámetros

| Nombre | Tipo | Requerido | Descripción |
|--------|------|-----------|-------------|
| ...    | ...  | ...       | ...         |

### Request de ejemplo
[bloque de código con curl o fetch real]

### Response (200)
[bloque JSON con estructura real]

### Errores
| Código | Causa |
|--------|-------|
| 400    | ...   |
| 401    | ...   |
```

### ADR (Architecture Decision Record)

Basado en MADR template:
```
# ADR-[NÚMERO]: [Título de la decisión]

## Estado
[Propuesto | Aceptado | Deprecado | Reemplazado por ADR-XXX]

## Contexto
[Qué situación motivó esta decisión. Qué problema resuelve.]

## Decisión
[Qué se decidió. Ser específico.]

## Alternativas consideradas
1. [Alternativa A] — [por qué se descartó]
2. [Alternativa B] — [por qué se descartó]

## Consecuencias
- [Qué cambia, qué facilita, qué dificulta]
```

### Changelog

Seguir [Keep a Changelog](https://keepachangelog.com):
```
## [Versión] - YYYY-MM-DD

### Added
- [nuevas features]

### Changed
- [cambios en funcionalidad existente]

### Deprecated
- [lo que se va a eliminar pronto]

### Fixed
- [bugs corregidos]
```

### Architecture Doc

```
# Arquitectura: [Nombre del Sistema]

## Visión general
[diagrama o descripción de alto nivel del sistema]

## Componentes
| Componente | Responsabilidad | Tecnología |
|------------|----------------|------------|
| ...        | ...            | ...        |

## Flujo de datos
[cómo se comunican los componentes]

## Decisiones clave
[links a ADRs relevantes]

## Constraints y límites
[no funcionales conocidos: escalabilidad, disponibilidad, etc.]
```

## Checklist de Calidad

- [ ] Audiencia identificada y el lenguaje es apropiado
- [ ] Todo ejemplo es ejecutable (no pseudocódigo)
- [ ] Terminología consistente en todo el documento
- [ ] Secciones < 300 palabras c/u (si es más, dividir)
- [ ] Cross-references donde había tentación de duplicar
- [ ] Sin información que será stale en <30 días (versiones exactas de deps solo en requirements)
- [ ] Heading describe el contenido (no genérico)
- [ ] Si es API: tiene request ejemplo, response ejemplo, errores

## Pitfalls

- **Documentar lo obvio y omitir lo implícito**: "Click en OK" no necesita docs. "El sistema asume UTF-8" sí necesita.
- **Docs huérfanos**: sin owner, sin review, sin update. Si nadie lo mantiene, va a estar stale.
- **Sobre-estructurar**: no todo proyecto necesita 7 tipos de doc. Empezar con README + lo que falta.
- **Asumir contexto**: el lector no sabe lo que tú sabes. Explicitar suposiciones.
- **Capturas como única fuente**: texto es versionable, buscable, accesible. Screenshots son complemento.
