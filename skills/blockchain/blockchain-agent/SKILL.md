---
name: blockchain-agent
description: Interactúa con py-chain, una blockchain educativa simulada. Consulta balances, envía tokens, mina bloques, despliega contratos y llama funciones. Usa curl para comunicarse con la API REST en localhost:5050. Use when the user mentions py-chain, blockchain simulada, check/send/mine/deploy/contract, or asks about agentes en blockchain.
---

# py-chain Blockchain Agent

## 📡 API Base

```
http://localhost:5050
```

La blockchain simulada corre en localhost. Si no está corriendo, pedí al usuario que ejecute `python py-chain.py` en el directorio del proyecto.

## 🔧 Comandos disponibles

Usa `curl` para todas las llamadas. No uses `requests` ni otras librerías.

### Consultar balance

```bash
curl -s http://localhost:5050/balance/0xAlice
# → {"address":"0xAlice","name":"Alice","balance":1000.0}
```

El usuario puede referirse a las cuentas por su nombre o dirección:
- `0xAlice` / "Alice" → consulta balance de Alice
- `0xBob` / "Bob" → consulta balance de Bob
- `0xAgent1` / "Agent_Alpha" → consulta balance de Agent_Alpha
- etc. (cualquier dirección en el formato 0x...)

Si la cuenta no existe, devuelve `balance: 0.0` y `name: "Unknown"`.

### Cuentas disponibles

```
0xAlice   → Alice          (1000.0 tokens)
0xBob     → Bob            (500.0 tokens)
0xCharlie → Charlie        (250.0 tokens)
0xDAO     → DAO_Treasury   (5000.0 tokens)
0xOracle  → Oracle_Feed    (100.0 tokens)
0xAgent1  → Agent_Alpha    (50.0 tokens)
0xAgent2  → Agent_Beta     (30.0 tokens)
```

### Enviar tokens

```bash
curl -s -X POST http://localhost:5050/send \
  -H "Content-Type: application/json" \
  -d '{"from":"0xAlice","to":"0xBob","amount":50}'
```

La respuesta incluye el tx_hash anidado en `tx.tx_hash`.

### Minar bloque

```bash
curl -s -X POST http://localhost:5050/mine
```

Responde con `block_index`, `hash`, `transactions[]`.

### Ver estado completo

```bash
curl -s http://localhost:5050/info
```

Devuelve cuentas con balances, pending_tx_count, chain_length, last_block.

### Ver la cadena

```bash
curl -s http://localhost:5050/chain
```

Devuelve `{"blocks": [...], "length": N}`.

### Desplegar contrato

```bash
curl -s -X POST http://localhost:5050/contract/deploy \
  -H "Content-Type: application/json" \
  -d '{"name":"MiContrato","source":"","owner":"0xAlice"}'
```

### Llamar función de contrato

```bash
curl -s -X POST http://localhost:5050/contract/{address}/call \
  -H "Content-Type: application/json" \
  -d '{"function":"store","args":{"key":"msg","value":"hello"},"caller":"0xAlice"}'
```

### Funciones del contrato disponibles

Todo contrato desplegado expone estas funciones (definidas en `contract.execute()` en models.py):

| Función | Args | Descripción |
|---------|------|-------------|
| `store` | `key`, `value` | Almacena un valor en el estado interno del contrato |
| `get` | `key` | Recupera un valor del estado interno |
| `deposit` | `amount` | Registra depósito del `caller` en `balance_{caller}` (estado interno, no blockchain) |
| `withdraw` | `amount` | Retira del balance interno del `caller` |
| `transfer_if_condition` | `condition`, `to`, `amount` | Transfiere si `condition == "true"`. Usa `balance_{owner}`, no `balance_{caller}` |
| `get_state` | — | Devuelve todo el estado interno del contrato |

**⚠️ Dato clave**: `transfer_if_condition` solo acepta `condition: "true"` como string literal. NO evalúa expresiones arbitrarias. Además, opera sobre la clave interna `balance_{owner}`, no sobre el balance real de la blockchain ni de `balance_{caller}`.

### Resetear blockchain

```bash
curl -s -X POST http://localhost:5050/reset
```

## 🧠 Comportamiento como agente

Cuando el usuario te pida analizar la blockchain y tomar decisiones:

1. **Percibir**: consultá `/info` para ver el estado completo (balances, bloques, transacciones pendientes)
2. **Razonar**: analizá los datos con tu LLM. Considerá:
   - ¿Qué cuentas tienen saldo bajo/alto?
   - ¿Hay transacciones pendientes?
   - ¿Hay contratos desplegados?
   - ¿Qué acción tendría sentido? (comprar datos del Oracle, invertir en DAO, pedir fondos, minar, etc.)
3. **Actuar**: ejecutá la acción vía curl (send, mine, deploy, etc.)
4. **Explicar**: contale al usuario qué viste, qué decidiste y qué pasó

### Orquestación multi-agente

Cuando el usuario quiera coordinar múltiples agentes (Agent_Alpha, Agent_Beta):

1. **Deploy**: creá un contrato TaskEscrow como intermediario
2. **Fund (blockchain)**: usá `/send` para transferir tokens reales desde una cuenta principal (ej: Alice) a la dirección del contrato — esto son tokens reales en la blockchain
3. **Deposit (contrato)**: llamá `deposit` en el contrato para registrar el depósito en su estado interno (`balance_{caller}`). Ambos sistemas (blockchain y contrato) son independientes — cada uno necesita su propio depósito
4. **Register**: cada agente se registra enviando 1 token real al contrato vía `/send`
5. **Evaluate**: compará los balances de los agentes con `/info` y elegí al mejor candidato
6. **Pay**: llamá `transfer_if_condition` en el contrato con `condition: "true"` — esto descuenta de `balance_{owner}` (el dueño debe haber hecho `deposit` primero), no del saldo blockchain
7. **Mine**: miná el bloque para sellar todas las transacciones
8. **Explain**: contá toda la historia — qué contratos se usaron, quién ganó y por qué

⚠️ **Pitfall común**: `transfer_if_condition` falla con `"Condition '' not met"` si no pasás `condition: "true"` exactamente como string. También necesita que el owner tenga saldo en el estado interno del contrato vía la función `deposit`, no solo en la blockchain.

NO uses reglas fijas. Usá tu criterio como LLM para decidir.

> 📎 Ver `references/multi-agent-orchestration.md` para un recipe completo con comandos curl exactos y errores conocidos.

## ⚠️ Notas

- Si `curl` falla con "Connection refused", la blockchain no está corriendo. Pedí al usuario que la inicie.
- Todas las respuestas de la API son JSON.
- Los errores de la API vienen con código HTTP 400 y un objeto `{"error": "mensaje"}`.
- `/send` devuelve `tx.tx_hash` (anidado), no top-level.
- `/mine` devuelve `block_index` (no `index`) y `transactions` (array).
- Hay un dashboard HTML en `dashboard.html` que muestra el estado visual de la blockchain. Si el usuario quiere ver los cambios en tiempo real, indicale que abra ese archivo en el navegador mientras interactuás con la blockchain.
