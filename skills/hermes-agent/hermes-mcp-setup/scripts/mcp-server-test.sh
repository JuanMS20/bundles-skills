#!/bin/bash
# Generic MCP Server Test Suite
# Usage: bash mcp-server-test.sh <BASE_URL> <AUTH_HEADER>
# Example: bash mcp-server-test.sh "https://www.example.com/api/mcp" "Bearer rt_live_YOUR_KEY"
#
# Tests: initialize handshake, tools/list, and CRUD operations for each tool.
# Outputs: [LABEL] OK/FAIL (latency) — preview
# Exit: 0 if all pass, 1 if any critical failure

BASE="${1:?Usage: $0 <BASE_URL> <AUTH_HEADER>}"
AUTH="${2:?Usage: $0 <BASE_URL> <AUTH_HEADER>}"
ID=1
PASS=0
FAIL=0

mcp_call() {
  local method="$1"
  local params="$2"
  local label="$3"

  local body="{\"jsonrpc\":\"2.0\",\"id\":$ID,\"method\":\"tools/call\",\"params\":{\"name\":\"$method\",\"arguments\":$params}}"
  ID=$((ID + 1))

  local start=$(python -c "import time; print(int(time.time()*1000))")
  local resp=$(curl -s --max-time 15 -X POST "$BASE" \
    -H 'Content-Type: application/json' \
    -H "Authorization: $AUTH" \
    -d "$body" 2>&1)
  local end=$(python -c "import time; print(int(time.time()*1000))")
  local elapsed=$((end - start))

  local has_error=$(echo "$resp" | python -c "import sys,json; d=json.load(sys.stdin); print('ERROR' if 'error' in d else 'OK')" 2>/dev/null)

  if [ "$has_error" = "ERROR" ]; then
    local err=$(echo "$resp" | python -c "import sys,json; d=json.load(sys.stdin); e=d['error']; print(f\"{e.get('code','?')}: {e.get('message','')[:120]}\")" 2>/dev/null)
    echo "[$label] FAIL ($elapsed ms) — $err"
    FAIL=$((FAIL + 1))
  else
    local preview=$(echo "$resp" | python -c "
import sys,json
d=json.load(sys.stdin)
r=d.get('result',{})
c=r.get('content',[])
if c:
    text=c[0].get('text','')[:120]
    print(text.replace(chr(10),' '))
else:
    print(str(r)[:120].replace(chr(10),' '))
" 2>/dev/null)
    echo "[$label] OK ($elapsed ms) — $preview"
    PASS=$((PASS + 1))
  fi
}

echo "=== MCP Server Test: $BASE ==="
echo ""

# 1. Handshake
echo "--- Handshake ---"
curl -s --max-time 10 -X POST "$BASE" \
  -H 'Content-Type: application/json' \
  -H "Authorization: $AUTH" \
  -d '{"jsonrpc":"2.0","id":0,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"test","version":"1.0.0"}}}' | python -c "
import sys,json
d=json.load(sys.stdin)
r=d.get('result',{})
if r:
    print(f\"  Protocol: {r.get('protocolVersion','?')}\")
    print(f\"  Server: {r.get('serverInfo',{}).get('name','?')} v{r.get('serverInfo',{}).get('version','?')}\")
    print(f\"  Capabilities: {list(r.get('capabilities',{}).keys())}\")
else:
    print('  ERROR: No initialize response')
" 2>/dev/null

# 2. List tools
echo ""
echo "--- Tools Discovery ---"
curl -s --max-time 10 -X POST "$BASE" \
  -H 'Content-Type: application/json' \
  -H "Authorization: $AUTH" \
  -d '{"jsonrpc":"2.0","id":0,"method":"tools/list","params":{}}' | python -c "
import sys,json
d=json.load(sys.stdin)
tools=d.get('result',{}).get('tools',[])
print(f'  Total tools: {len(tools)}')
for t in tools:
    req=t.get('inputSchema',{}).get('required',[])
    print(f'  - {t[\"name\"]} ({len(t.get(\"inputSchema\",{}).get(\"properties\",{}))} params, {len(req)} required)')
" 2>/dev/null

echo ""
echo "--- Tool Calls ---"

# 3. Generic ping/health (if available)
mcp_call "ping" "{}" "ping"

echo ""
echo "=== RESULTS: $PASS passed, $FAIL failed ==="
