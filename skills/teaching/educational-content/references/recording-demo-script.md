# Recording Demo Script Template

Structured split-screen recording script for educational demos.
Use this when you need a shot-by-shot guide that maps **what the teacher does** → **what students see** → **what it teaches**.

## Screen Layout

```
┌──────────────────────────┬──────────────────────────┐
│  Terminal (left half)    │  Dashboard / Browser     │
│  Hermes / CLI / backend  │  (right half)            │
├──────────────────────────┼──────────────────────────┤
│  Teacher voiceover       │                          │
│  (narration throughout)  │                          │
└──────────────────────────┴──────────────────────────┘
```

Tips:
- Terminal: 20+ px font, dark background, light text
- Dashboard: full-screen browser (no address bar, no tabs)
- No mouse cursor idle movements — move deliberately

## Per-Demo Script Structure

Each demo gets its own table. Each row is ~30-60 seconds of footage.

| Paso | En pantalla | Qué hace/profesor | Qué ven estudiantes | Enseña |
|------|-------------|-------------------|---------------------|--------|
| N | Terminal or Dashboard | Exact action + what teacher says | Observable result on screen | One-line concept |
| ... | ... | ... | ... | ... |

### Column Rules

- **Paso**: simple number. One logical step per row.
- **En pantalla**: which screen element to focus (Terminal 1, Terminal 2, Dashboard, Slide)
- **Qué hace**: imperative action ("Ejecutá", "Señalá", "Decí") + exact teacher line in *italics*
- **Qué ven**: concrete visual change — numbers changing, highlights appearing, blocks appearing. Be specific with values so the editor can verify.
- **Enseña**: single concept, framed as a takeaway the teacher can say: "El agente percibe la blockchain", "Los contratos retienen fondos como escrow"

## Example (from py-chain blockchain + Hermes demo)

| Paso | En pantalla | Qué hace | Qué ven | Enseña |
|------|-------------|----------|---------|--------|
| 2.1 | Terminal 2 (Hermes) | Decí: *"Hermes, cargá el skill blockchain-agent y mostrame el estado de la blockchain"* | Hermes consulta `/info` vía curl, muestra cuentas, saldos, bloques | El agente percibe la blockchain como cualquier nodo |
| 2.2 | Terminal 2 (Hermes) | Decí: *"Analizá el estado y decidí qué acción tomar. Explicá tu razonamiento."* | Hermes razona en voz alta con el LLM: *"Oracle tiene 100 tokens, voy a comprar datos del Oracle porque..."* | El agente razona con IA real — no if/else |
| 2.2 | Dashboard | Señalá | Los números cambian, highlight verde en cuentas afectadas, nuevo evento en el log | Las decisiones del agente modifican el estado on-chain |
| 2.3 | Terminal 2 (Hermes) | Decí: *"Miná un bloque para confirmar todo"* | Hermes mina, muestra hash, bloque nuevo | Las acciones del agente quedan registradas para siempre |
| 2.3 | Dashboard | Mostrá | Nuevo bloque aparece en la cadena visual | Inmutabilidad: cualquiera puede auditarlo |

## Full Demo Outline (for the editor)

After the per-demo scripts, add a summary timing table:

| Bloque | Duración | Qué mostrás | Enseñanza principal |
|--------|----------|-------------|---------------------|
| Intro | 5 min | Slides + contexto | Why this matters |
| Demo 1 | 3 min | Terminal + dashboard | Fundamental concepts |
| Demo 2 | 5 min | Hermes autonomous agent | Perceive→reason→act loop with real LLM |
| Demo 3 | 5 min | Hermes orchestrates agents | Smart contracts as trustless coordination |
| Cierre | 3 min | Conclusions | Takeaways + real-world cases |

## Recording Tips

- If something goes wrong mid-demo, only re-record that clip — not the whole class
- Demos are interactive: narrate while the agent processes (don't record silent)
- Reset simulated state between demos (POST /reset or restart the backend)
- Highlight changes on dashboard by pointing or circling with cursor
- For split-screen with a terminal + dashboard: position terminal on LEFT, dashboard on RIGHT (standard video convention for Western reading direction)
