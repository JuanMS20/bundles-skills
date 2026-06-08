# py-chain Pattern: Simulated Blockchain Backend

Template for building a simulated blockchain for educational demos.
Used in the "Agentes de IA en Blockchain" university class.

## Architecture (chain/ package)

```
chain/
├── __init__.py       ← exports: PyChain, SimpleBlock, SimpleContract
├── models.py         ← pure domain logic (no prints, no Flask)
├── presenter.py      ← ANSI output formatting (decoupled from logic)
├── api.py            ← Flask routes (thin, calls models + presenter)
└── cli.py            ← entrypoint (banner + app.run())
```

## Key design decisions

### 1. Models are pure

`models.py` has zero side effects. Methods return dicts, never print.
This makes the entire blockchain logic testable without a server:

```python
# models.py — pure
def send_transaction(self, from_addr, to_addr, amount, data=None):
    # ... validate, update balances ...
    return {"success": True, "tx": tx, "from_balance": ..., "to_balance": ...}

def mine_block(self):
    block = SimpleBlock(...)
    block.mine_block(difficulty=2)
    self.chain.append(block)
    return block
```

### 2. Presenter is all output

`presenter.py` has only print functions. Import where console output is needed:

```python
# presenter.py
def block_mined(block): ...
def transaction_sent(from_name, to_name, amount): ...
def contract_deployed(name, address): ...
```

Called by the API layer after state changes, never by models.

### 3. Global state is isolated

The single `PyChain()` instance lives in `api.py` as `_chain_state`.
The `/reset` endpoint replaces it with a fresh instance.
No module-level state in `models.py`.

### 4. Default accounts

Pre-loaded on startup — students see a running system immediately:

| Address | Name | Balance |
|---|---|---|
| 0xAlice | Alice | 1000 |
| 0xBob | Bob | 500 |
| 0xCharlie | Charlie | 250 |
| 0xDAO | DAO_Treasury | 5000 |
| 0xOracle | Oracle_Feed | 100 |
| 0xAgent1 | Agent_Alpha | 50 |
| 0xAgent2 | Agent_Beta | 30 |

### 5. API endpoints

`GET  /info` — full state dump
`GET  /accounts` — all accounts
`GET  /balance/<addr>` — single account
`POST /send` — `{"from", "to", "amount", "data?"}`
`POST /mine` — mine pending txs into a block
`GET  /chain` — full chain with blocks
`POST /contract/deploy` — `{"name", "source?", "owner"}`
`POST /contract/<addr>/call` — `{"function", "args", "caller"}`
`POST /reset` — wipe everything

## Agent base class pattern

```python
class BlockchainAgent:
    def __init__(self, address, name):
        self.address = address
        self.name = name
        self.balance = 0

    def update_balance(self):
        data = api_get(f"/balance/{self.address}")
        if data:
            self.balance = data["balance"]

    def __str__(self):
        return f"{self.name} ({self.address})"


class AutonomousAgent(BlockchainAgent):
    """Adds perceive() → decide() → act() loop."""
    ...
```

## Demo pattern

Each demo:
1. Imports from `agent_base` (shared colors, step/pause, agent class)
2. Connects to localhost:5050 via HTTP
3. Runs steps with `time.sleep()` between them
4. Ends with a summary of concepts demonstrated
