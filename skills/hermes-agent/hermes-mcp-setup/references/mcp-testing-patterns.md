# MCP Server Testing Patterns

Systematic approach for testing MCP servers beyond `hermes mcp test`.
Covers false-negatives, CRUD lifecycle, edge cases, and security probes.

## Why Manual Testing?

`hermes mcp test` does a GET probe. Many MCP servers return `text/plain` on GET
but respond correctly to POST + JSON-RPC. When `hermes mcp test` fails with
"Content-Type 'text/plain', not an MCP response", the server may still work —
test manually with curl before concluding it's broken.

## Test Levels

### Level 1: Handshake (2 calls)
```bash
# Initialize
curl -s -X POST "$URL" -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"test","version":"1.0.0"}}}'

# List tools
curl -s -X POST "$URL" -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}'
```

### Level 2: CRUD Lifecycle (per entity)
For each entity (products, categories, orders, etc.):
1. **List empty** — should return `[]` (not `null`)
2. **Create** with all fields — verify response has `id`
3. **Create** with only required fields — should succeed
4. **Get** by ID — verify fields match
5. **Update** — change 1-2 fields, verify
6. **List** — should include created item
7. **Delete** — verify returns success
8. **Get deleted** — should return `null` or error

### Level 3: Validation & Edge Cases
- Missing required fields → should return structured error, not DB constraint
- Invalid UUID format → should validate before DB query
- Invalid enum values → should reject unknown statuses
- Empty string for required field → should validate
- Negative numbers for quantities/prices → should reject
- SQL injection in string fields → should be sanitized (parameterized queries)
- XSS payloads in URL/string fields (`javascript:`, `<script>`) → should reject

### Level 4: Business Logic
- Cancel completed order → should block
- Delete category with products → should block
- Status machine enforcement (can't skip states?)
- Duplicate creates (same name) → what happens?

### Level 5: Compatibility
- GET request to MCP endpoint → Content-Type must be `application/json` or `text/event-stream`
- POST without Content-Type header → should still work per JSON-RPC spec
- Large payloads (100+ items) → timeout behavior
- Concurrent requests → race conditions?

## Common Bug Patterns Found in Practice

| Pattern | Symptom | Root Cause |
|---------|---------|------------|
| Schema lies about required fields | `null value in column "X" violates not-null constraint` | inputSchema says field is optional but DB has NOT NULL |
| Raw Postgres errors exposed | `invalid input syntax for type uuid` | No input validation before query |
| No state machine | Can cancel completed orders | Missing business rule check |
| GET probe fails | Clients can't auto-discover | Server returns text/plain on GET |
| `null` vs `[]` inconsistency | Filtered list returns `null` | Missing coercion for empty results |
| XSS in URL fields | `javascript:` URLs accepted | No URL scheme validation |
| Create response incomplete | No nested items in order creation | Missing join/eager load in response |

## Script

See `scripts/mcp-server-test.sh` — generic test runner for Level 1 + basic tool calls.
For deep CRUD testing, write a tailored script per server using the patterns above.
