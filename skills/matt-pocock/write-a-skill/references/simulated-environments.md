# Simulated Environments for Educational Demos

Patrón reusable para construir entornos simulados donde agentes de IA (LLMs reales) puedan operar como lo harían en producción.

## El Patrón (3 capas)

```
┌──────────────────────┐
│   Agent Interaction   │  ← Hermes / LLM habla con la API
│   (API REST real)     │     Igual que en producción
├──────────────────────┤
│   Simulation Layer    │  ← Lógica del entorno simulado
│   (pure models)       │     Sin side effects, testeable
├──────────────────────┤
│   Presenter (opcional)│  ← Output visual para demos
│   (ANSI / JSON)       │     Separado del modelo
└──────────────────────┘
```

## Por qué funciona

- **API real** → el agente interactúa igual que con el sistema real. No hay diferencia entre el demo y producción desde la perspectiva del agente.
- **Modelos puros** → la lógica de negocio se puede testear sin infraestructura (sin servidor, sin red, sin dependencias externas).
- **Presenter separado** → puedes tener output bonito para el video y tests silenciosos para desarrollo.

## Ejemplo: py-chain (blockchain simulada)

```
chain/
├── models.py     ← Lógica pura: PyChain, SimpleBlock, SimpleContract
│                   Sin prints, sin Flask, sin dependencias externas.
│                   Testeable en < 2s: 24 tests unitarios.
├── api.py        ← Flask REST API (endpoints reales: /send, /mine, /balance)
│                   El agente habla con esto via HTTP.
├── presenter.py  ← ANSI output para la terminal (bonito pero opcional)
└── cli.py        ← Bootstrap: banner + app.run()
```

El agente (Hermes) llama a `POST /send`, `POST /mine`, `GET /balance/0xAlice` exactamente como llamaría a Ethereum JSON-RPC o Solana RPC en producción.

## Cuándo usar este patrón

- Demos educativos donde el estudiante debe ver el concepto sin la complejidad operativa
- Workshops donde el setup debe ser `pip install flask && python demo.py`
- Prototipos rápidos donde la infraestructura real sería demasiado lenta o cara
- Pruebas de concepto de "agente autónomo en sistema X"

## Contraste: el antipatrón

En vez de construir un simulador con API y dejar que el LLM decida, es tentador escribir scripts con `if/else` y llamarlos "agentes". Esto:
- No demuestra el concepto real (razonamiento LLM)
- No es extensible a sistemas reales
- El usuario lo notará ("¿y la parte agéntica?")
