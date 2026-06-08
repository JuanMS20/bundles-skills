# Multi-Agent Orchestration — Working Recipe

Flujo completo probado para coordinar Agent_Alpha y Agent_Beta usando un contrato TaskEscrow.

## 0. Estado inicial

```json
// GET /info
{
  "0xAlice":   { "balance": 1000 },
  "0xDAO":     { "balance": 5000 },
  "0xOracle":  { "balance": 100 },
  "0xAgent1":  { "balance": 50  },   // Agent_Alpha
  "0xAgent2":  { "balance": 30  },   // Agent_Beta
}
```

## 1. Deploy TaskEscrow (Alice como owner)

```bash
curl -s -X POST http://localhost:5050/contract/deploy \
  -H "Content-Type: application/json" \
  -d '{"name":"TaskEscrow","source":"","owner":"0xAlice"}'
# → {"address":"cd6f7cfbe99a680e","success":true}
```

## 2. Fund — tokens reales a la dirección del contrato

```bash
curl -s -X POST http://localhost:5050/send \
  -H "Content-Type: application/json" \
  -d '{"from":"0xAlice","to":"0x<CONTRACT_ADDRESS>","amount":200}'
# Aca se transfieren tokens reales (blockchain-level)
```

## 3. Deposit — registrar en estado interno del contrato

```bash
curl -s -X POST http://localhost:5050/contract/<CONTRACT_ADDRESS>/call \
  -H "Content-Type: application/json" \
  -d '{"function":"deposit","args":{"amount":200},"caller":"0xAlice"}'
# → {"result":"Deposited 200, new balance: 200","success":true}
# Sin este paso, transfer_if_condition falla (balance_owner = 0)
```

## 4. Register — agentes pagan fianza de 1 token real

```bash
curl -s -X POST http://localhost:5050/send \
  -H "Content-Type: application/json" \
  -d '{"from":"0xAgent1","to":"0x<CONTRACT_ADDRESS>","amount":1}'

curl -s -X POST http://localhost:5050/send \
  -H "Content-Type: application/json" \
  -d '{"from":"0xAgent2","to":"0x<CONTRACT_ADDRESS>","amount":1}'
```

## 5. Evaluate — usar /info para comparar

```bash
curl -s http://localhost:5050/info
# Elegir agente con mejor capitalización / historial
```

## 6. Pay — transfer_if_condition

⚠️ El param `condition` debe ser literalmente `"true"`. No acepta expresiones.

```bash
curl -s -X POST http://localhost:5050/contract/<CONTRACT_ADDRESS>/call \
  -H "Content-Type: application/json" \
  -d '{"function":"transfer_if_condition","args":{"condition":"true","to":"0xAgent1","amount":50},"caller":"0xAlice"}'
# → {"result":"Condition met! Transferred 50 to 0xAgent1","success":true}
```

## 7. Mine

```bash
curl -s -X POST http://localhost:5050/mine
```

## 8. Verify

```bash
curl -s http://localhost:5050/info
# Ver cambios en balances y estado del contrato
```

## Errores conocidos

| Error | Causa | Solución |
|-------|-------|----------|
| `"Condition '' not met"` | Faltó `condition:"true"` en args | Agregar el parámetro exacto |
| `"Insufficient funds in contract"` | No se llamó `deposit` antes | Llamar `deposit` con caller=owner |
| `"Contrato no encontrado"` | Contract address incorrecta | Verificar con GET /contracts |
