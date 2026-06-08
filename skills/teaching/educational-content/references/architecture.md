# PyChain Architecture — Internal Design

## Class Hierarchy

```
Py Chain (orchestrator)
├── chain: list[SimpleBlock]     ← blocks in sequence
├── pending_tx: list[dict]       ← unconfirmed transactions
├── accounts: dict[str, Account] ← address → {name, balance, nonce}
└── contracts: dict[str, SimpleContract]  ← address → contract

SimpleBlock
├── index, timestamp, nonce
├── transactions: list[dict]
├── previous_hash: str
└── hash: str  (SHA-256)

SimpleContract
├── name, source, owner, address
└── state: dict  ← key-value store
```

## Block Mining

1. `POST /mine` collects all pending transactions
2. Creates `SimpleBlock(len(chain), pending_tx, chain[-1].hash)`
3. PoW simulation: increment `nonce` until SHA-256 hash starts with `"00"` (difficulty=2)
4. Appends to `chain`, clears `pending_tx`
5. Returns block index + hash

## Transaction Lifecycle

1. `POST /send` deducts from sender balance, credits recipient, appends to `pending_tx`
2. Balances change **immediately** (the tx is visible in the state)
3. `POST /mine` seals the pending tx into a block (the tx becomes immutable)
4. Educational analogy: "pending" = check written, "mined" = check cleared

## Smart Contract Execution

Not an EVM — contracts are Python objects with pre-defined functions:
- `store(key, value)` / `get(key)` — persistent key-value storage
- `deposit(amount)` / `withdraw(amount)` — per-caller balance tracking within the contract
- `transfer_if_condition(condition, to, amount)` — condition-based fund release (escrow pattern)

Each function receives `caller` (the address invoking it) and can read/write `self.state`.

## Security Notes (for teaching context)

- No actual cryptography — hashes are SHA-256 but keys are plain text
- No private key verification — any address can send from any address
- No gas — all operations are free
- No consensus — single node, no network
- This is intentional: students learn the **data model** without the **operational complexity**
