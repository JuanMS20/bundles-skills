# Referencia: Blockchain Simulada (py-chain)

Caso de estudio completo de un simulador educativo construido con el patrón
`educational-content`. Usado en un curso universitario sobre agentes de IA en blockchain.

## Estructura final

```
blockchain-ai-class/
├── py-chain.py              ← Entrypoint (10 líneas, importa chain.cli)
├── chain/
│   ├── __init__.py           ← Exports: PyChain, SimpleBlock, SimpleContract
│   ├── models.py             ← Lógica pura (sin prints, sin Flask, 100% testeable)
│   ├── api.py                ← Flask routes, llama a presenter para output
│   ├── presenter.py          ← Funciones ANSI para cada evento
│   └── cli.py                ← Banner + app.run()
├── demos/
│   ├── agent_base.py         ← BlockchainAgent base + step/pause + ANSI constants
│   ├── api_helper.py         ← api_get/api_post con urllib (stdlib)
│   ├── demo-1-basics.py      ← Cuentas, transacciones, minería
│   ├── demo-2-agent.py       ← Loop perceive→decide→act
│   └── demo-3-swarm.py       ← Multi-agente + contrato escrow
├── tests/
│   ├── test_models.py        ← 24 tests unitarios sobre models.py
│   └── test_integration.py   ← Tests de API (usa curl para HTTP 4xx)
├── slides.md                 ← 13 slides para presentación
├── storyboard.md             ← Timeline minuto a minuto del video
└── README.md
```

## Lecciones específicas

### 1. Separación models/presenter

**Antes:** `mine_block()` imprimía ANSI colors. `send_transaction()` imprimía flechitas.
No se podía testear la lógica sin capturar stdout.

**Después:** `chain/models.py` es puro — métodos devuelven dicts con resultados.
`chain/presenter.py` tiene funciones como `block_mined(block)`, `transaction_sent(from, to, amount)`.
La API llama al presenter DESPUÉS de modificar el estado, no durante.

### 2. La instancia global de PyChain

**Error típico:** Poner `chain = PyChain()` en `models.py` como variable de módulo.
**Solución:** Crearla en `api.py` (`_chain_state = PyChain()`) y exponer getter/setter
para que el CLI y el reset endpoint puedan manipularla sin acoplamiento circular.

### 3. Tests de errores HTTP 4xx con urllib

`urllib.request.urlopen()` lanza `HTTPError` para 4xx. La respuesta se lee con
`e.read()`. Sin embargo, en algunos entornos esta lectura puede colgar.
**Workaround:** Usar `curl` vía `subprocess.check_output` para tests de integración
que verifican rutas de error.

### 4. Duplicación de clases agente

Los demos 2 y 3 tenían clases de agente similares pero separadas. La solución:
extraer `BlockchainAgent` base a `demos/agent_base.py` con `address`, `name`,
`balance`, `update_balance()`, y `__str__()`. Demo-2 extiende con
`perceive→decide→act`. Demo-3 usa la clase base directamente.

### 5. Materiales de video

`slides.md` + `storyboard.md` son entregables de primera clase, no un afterthought.
Para un video de 1 hora, el storyboard incluye:
- Bloque de intro (5 min)
- Fundamentos (10 min + demo 3 min)
- Concepto central (12 min + demo 5 min)
- Coordinación (12 min + demo 6 min)
- Casos reales + cierre (10 min)
- Preguntas (5 min)
