# Hermes Agent Integration — py-chain

Pattern for using Hermes (LLM-powered agent) to interact with a simulated blockchain
via skills and curl commands. Designed for educational demos where students see a real
AI agent perceiving blockchain state and making decisions.

## The skill pattern

A Hermes skill for blockchain interaction has:

1. **Purpose declaration** — frontmatter with name, description, and triggers
2. **API base** — URL of the running simulation
3. **Commands** — curl commands for every endpoint, with real examples
4. **Agent behaviour** — instructions for the LLM to perceive→reason→act autonomously
5. **Error handling** — what to do when the server is down or returns errors

## Minimal skill frontmatter

```yaml
---
name: blockchain-agent
description: Interactúa con py-chain, una blockchain educativa simulada.
Use when the user mentions py-chain, blockchain simulada, check/send/mine/deploy/contract.
---
```

## Curl commands documented in skill

Each endpoint gets a curl example with the real addresses from the simulation:

### Check balance
```bash
curl -s http://localhost:5050/balance/0xAlice
# → {"address":"0xAlice","name":"Alice","balance":1000.0}
```

### Send tokens
```bash
curl -s -X POST http://localhost:5050/send \
  -H "Content-Type: application/json" \
  -d '{"from":"0xAlice","to":"0xBob","amount":50}'
```

### Mine block
```bash
curl -s -X POST http://localhost:5050/mine
```

### Full state
```bash
curl -s http://localhost:5050/info
```

## Agent behaviour instructions

The skill should instruct Hermes to act as an autonomous blockchain agent:

1. **Percibir**: consult `/info` for full state (balances, blocks, pending txs, contracts)
2. **Razonar**: analyze with LLM — which accounts are low/high? Are there pending txs? What action makes sense?
3. **Actuar**: execute via curl (send, mine, deploy, call)
4. **Explicar**: tell the user what was observed, decided, and what happened

> NO use reglas fijas. Use el criterio del LLM para decidir.

## Multi-agent orchestration flow

When demonstrating coordination between multiple agents (e.g. Agent_Alpha, Agent_Beta):

1. **Deploy escrow** — create a contract as intermediary (`POST /contract/deploy`)
2. **Fund** — deposit tokens from a main account into the contract (call `deposit`)
3. **Register** — each agent sends 1 token to the contract as a registration signal
4. **Evaluate** — compare agent balances via `/info`, choose the best candidate
5. **Pay** — call `transfer_if_condition` with `condition="true"` to release funds
6. **Mine** — mine the block to seal all transactions
7. **Explain** — narrate: what contracts were used, who won and why

This flow demonstrates: trustless escrow, on-chain competition, autonomous payment, and LLM-based evaluation.

## API response shape gotchas

Verified from real integration tests:

- **`POST /send`** — returns `tx.tx_hash` nested inside `tx` object, NOT at top level
- **`POST /mine`** — returns `block_index` (not `index`), `transactions` array (not `tx_count`)
- **`GET /chain`** — returns `{"blocks": [...], "length": N}`, NOT a flat array
- **`POST /contract/deploy`** — returns `{"success": true, "address": "0x...", "name": "..."}`

Test these shapes by writing a tracer bullet test before documenting them in the skill.

## Accepting natural language

The skill should let users refer to accounts by name or address:
- "check balance of 0xAlice" or "revisa el balance de Alice" → `/balance/0xAlice`
- "send 50 from Alice to Bob" or "envía 50 de Alice a Bob" → POST /send

Map common names to 0x-prefixed addresses automatically.

## Loading the skill

```
hermes skills list              # verify it's listed
hermes <query>                  # Hermes auto-loads matching skills
```

Or invoke the skill by mentioning a trigger phrase like "py-chain" or "blockchain".

## Error handling

- `Connection refused` → blockchain not running. Ask user to start it.
- HTTP 400 → `{"error": "message"}` — parse and report the specific error.
- Account doesn't exist → balance returns `0.0`, name returns `"Unknown"`.
- Insufficient funds → API returns HTTP 400 with `{"error": "Saldo insuficiente"}`.

## Video production tip

For the demo video, show a split-screen layout:
- **Left**: terminal with Hermes session (user asking in natural language, Hermes reasoning + curl calls)
- **Right**: dashboard web page showing blockchain state updating in real time

This makes it clear that Hermes is the agent, py-chain is the blockchain, and the user just talks to Hermes.
