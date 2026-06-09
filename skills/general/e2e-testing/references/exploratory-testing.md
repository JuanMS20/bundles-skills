# Exploratory Testing with Real Browser

## Setup

1. **Fresh state**: Clear cookies, localStorage, sessionStorage before each flow
2. **Multiple personas**: Test with different user types (guest, registered, admin)
3. **Multiple viewports**: Desktop (1280x720) + Mobile (375x667) minimum
4. **Network conditions**: Test with throttled network (Fast 3G) at least once

## Session Structure

```
Flow: [name]
Objective: [qué se está validando]
Persona: [guest | user | admin]
Viewport: [desktop | mobile | tablet]
Network: [wifi | throttled | offline]

Steps:
  1. [Action] → [Expected result] → [Actual result] → [Evidence]
  2. ...

Bugs:
  - [Descripción] [Severidad] [Repro steps] [Evidence]

Questions:
  - [¿Algo que no quedó claro? ¿Necesita investigación futura?]
```

## Techniques

### Tours

- **Landmark Tour**: Visitar cada página principal desde la navegación
- **Capability Tour**: Probar cada feature listada en docs/landing
- **Intellectual Tour**: Hacer las preguntas más difíciles que un usuario haría
- **Sleepless Night Tour**: ¿Qué me desvelaría si esto fallara en producción?
- **Obsessive-Compulsive Tour**: Repetir la misma acción 10 veces → ¿cada vez funciona igual?
- **Back Button Tour**: Navegar hacia adelante, luego back → ¿estado consistente?

### Heuristics

- **CRUD**: ¿Se puede Create, Read, Update, Delete cada entidad?
- **0, 1, N**: ¿Qué pasa con 0 items? 1 item? Muchos items?
- **Input**: Vacío, límites, caracteres especiales, XSS attempts
- **Navigation**: Refresh, back, forward, deep link, bookmark
- **Auth**: Sin login, login válido, login inválido, expiración de sesión

### Evidence Collection

| Tipo | Cuándo | Cómo |
|---|---|---|
| Screenshot | Cualquier estado visual relevante | `browser_vision` o manual |
| URL | Navegación o redirección | Copiar de address bar |
| Console errors | Después de cualquier interacción | DevTools → Console |
| Network | Llamadas API fallidas o lentas | DevTools → Network |
| State | localStorage, cookies | DevTools → Application |

## Kimi WebBridge Specific

When using Kimi WebBridge (Edge browser control via localhost:10086):

1. **Navigation**: `browser_navigate(url)` → verify page loads
2. **Interaction**: `browser_click`, `browser_type` → verify state change
3. **Verification**: `browser_vision` → ask specific question about visible state
4. **Evidence**: Screenshot automatically captured by `browser_vision`

**Anti-pattern**: Don't use `browser_vision` for every single step — use it for gates:
- After navigation (verify correct page)
- After form submission (verify success/error state)
- After async operation (verify data loaded)
