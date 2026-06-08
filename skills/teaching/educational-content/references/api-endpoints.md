# API Endpoints — py-chain Simulator

Base URL: `http://localhost:5050`

## Accounts & Balances

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/accounts` | List all accounts with name, balance, nonce |
| GET | `/balance/<address>` | Get single account balance and name |

## Transactions

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/send` | Submit a transaction. Body: `{"from", "to", "amount", "data?"}` |

Response on success:
```json
{
  "success": true,
  "tx": {"from": "...", "to": "...", "amount": N, "timestamp": ..., "tx_hash": "..."},
  "from_balance": N,
  "to_balance": N
}
```

## Mining

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/mine` | Collect pending txs into a new block (PoW simulated, difficulty=2) |

Response on success (note: uses `block_index`, NOT `index`):
```json
{
  "success": true,
  "block_index": 1,
  "hash": "00abcd...",
  "transactions": ["tx1", "tx2"]
}
```

## Chain

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/chain` | Full block list with hashes |
| GET | `/info` | Summary: chain length, pending txs, all accounts, contracts, last block |

`GET /chain` response shape:
```json
{
  "blocks": [{"index": 0, "hash": "...", "transactions": [...], "previous_hash": "...", "nonce": N, "timestamp": ...}],
  "length": 1
}
```

`GET /info` response shape:
```json
{
  "chain_length": 1,
  "pending_tx_count": 0,
  "accounts": {"0xAlice": {"name": "Alice", "balance": 1000.0, "nonce": 0}},
  "contracts": {"addr": {"name": "TaskEscrow", "owner": "0xAlice", "state": {}}},
  "last_block": {"index": 0, "hash": "...", "tx_count": 1}
}
```

## Smart Contracts

| Method | Endpoint | Body | Description |
|--------|----------|------|-------------|
| POST | `/contract/deploy` | `{"name", "source?", "owner"}` | Deploy new contract |
| POST | `/contract/<address>/call` | `{"function", "args":{}, "caller"}` | Call contract function |
| GET | `/contracts` | — | List all deployed contracts |

Available contract functions:
- `store` — args: `{key, value}` — stores key-value pair
- `get` — args: `{key}` — retrieves stored value
- `deposit` — args: `{amount}` — adds tokens to caller's contract balance
- `withdraw` — args: `{amount}` — removes tokens from caller's contract balance
- `transfer_if_condition` — args: `{condition, to, amount}` — releases tokens if condition="true"
- `get_state` — returns full contract state dict

## CORS

All endpoints include CORS headers:
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Headers: Content-Type
Access-Control-Allow-Methods: GET, POST, OPTIONS
```

This enables the dashboard (opened in browser) to fetch from the API without CORS errors.

## Dashboard

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/dashboard` | Serves the HTML dashboard file at `dashboard.html` |

The dashboard is served from Flask (not opened as a local file) to avoid CORS `file://` origin restrictions.

## Admin

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/reset` | Wipes all state, recreates default accounts, starts fresh genesis block |

## Default Accounts

| Address | Name | Initial Balance |
|---------|------|----------------|
| 0xAlice | Alice | 1000.0 |
| 0xBob | Bob | 500.0 |
| 0xCharlie | Charlie | 250.0 |
| 0xDAO | DAO_Treasury | 5000.0 |
| 0xOracle | Oracle_Feed | 100.0 |
| 0xAgent1 | Agent_Alpha | 50.0 |
| 0xAgent2 | Agent_Beta | 30.0 |
