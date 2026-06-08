# Network & DNS Workarounds (Windows)

When browser tools, web_search, or web_extract fail with DNS/connection errors on Windows, these patterns bypass the issue.

## DNS Resolution Failure

**Symptom:** `net::ERR_NAME_NOT_RESOLVED`, `getaddrinfo failed`, `DNS request timed out`

**Root cause:** Windows DNS client service or configured DNS server is unresponsive. The host's default DNS (often router-level) may be down.

**Fix chain:**
```bash
# 1. Verify DNS is the problem (try Google DNS directly)
nslookup example.com 8.8.8.8

# 2. If that works, bypass DNS with curl --resolve
curl -sL -m 15 --resolve example.com:443:IP_ADDRESS "https://example.com/path"

# 3. Get the IP from step 1, use it in step 2
```

**Why not just fix DNS?** Temporary network state — not worth modifying system DNS for a session-level issue. The `--resolve` flag is zero-persistence.

## SPA Route Discovery

When exploring an unfamiliar web app (especially Next.js/React SPAs), static routes may not exist in HTML. Probe with batch curl:

```bash
for path in /login /register /dashboard /settings /admin /api /docs; do
  status=$(curl -sL -o /dev/null -w "%{http_code}" -m 5 "https://example.com$path")
  echo "$path → $status"
done
```

- 200 = route exists (may still be client-rendered)
- 404 = route doesn't exist
- 301/302 = redirect (follow with `-L`)

## Extracting Content from SSR Pages

Next.js SSR pages return full HTML on first load. Extract structured data without a browser:

```bash
# Get raw HTML
curl -sL -m 15 "https://example.com/page" > page.html

# Extract specific patterns (meta tags, links, text)
grep -oP '(?:content|href|src|placeholder)="[^"]*"' page.html

# Extract text content between tags
sed 's/>/>\n/g' page.html | grep -i "keyword"
```

**Limitation:** Client-side rendered content (React hydration, dynamic imports) won't appear in curl output. For that, browser tools or Playwright are required.

## MCP Server HTTP Connection Test

Before configuring an MCP server in Hermes, verify the endpoint is reachable:

```bash
# Test MCP endpoint directly
curl -sL -m 10 -H "Authorization: Bearer TOKEN" \
  "https://example.com/api/mcp" -X POST \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'
```

If this returns a valid JSON response with tools, the MCP config will work. If it returns HTML or an error, debug the endpoint before adding to config.yaml.
