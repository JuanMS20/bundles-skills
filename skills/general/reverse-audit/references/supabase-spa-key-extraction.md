# Supabase Anon Key Extraction from Running SPA

When auditing a Supabase-backed SPA in production, the anon key is needed to test API endpoints directly via curl. This documents what works and what doesn't.

## The Problem

The anon key is required as `apikey` header for all Supabase REST API calls. Without it, every request returns `"No API key found in request"`. The key is embedded in the JS bundle at build time by Vite (`import.meta.env.VITE_SUPABASE_ANON_KEY`).

## What Doesn't Work

1. **Global scope search:** `createClient(url, key)` runs in ES module scope. The key is NOT on `window`, `globalThis`, or any accessible object. Traversing all window properties won't find it.

2. **Monkey-patching fetch/XHR AFTER page load:** The Supabase client captures a reference to `fetch` at instantiation time. Patching `window.fetch` after the app loads doesn't intercept calls made by the already-instantiated client.

3. **Bundle text search:** Vite minifies long strings. The anon key appears as `eyJhbG...X78` with literal `...` in the middle of the bundle JS. Regex for `eyJ[a-zA-Z0-9_-]{100,}` only captures the visible portion (~127 chars), not the full key (~200+ chars).

4. **`.env.local` in local repo:** May also be truncated with `...` if someone partially redacted it. Don't assume the local file matches production.

5. **`performance.getEntriesByType('resource')`:** Shows API call URLs but NOT request headers. Can confirm the Supabase project URL and endpoints used, but not the key.

## What Works

1. **Cloudflare Pages env vars:** If the app deploys via Cloudflare Pages, the real key is in `Settings → Environment variables`. Requires dashboard access.

2. **Network tab intercept:** Open browser DevTools BEFORE page load → Network tab → filter for `supabase.co` → inspect request headers → copy `apikey` value. This is the most reliable method.

3. **Kimi WebBridge `network` tool:** `network` cmd=`start` before navigation, then `list` to capture requests with headers. The `apikey` header appears in the request details.

4. **Local repo with unredacted `.env.local`:** If the developer has the full key locally (not truncated).

5. **Build artifacts:** If you can trigger a new build with `console.log(supabaseAnonKey)` added to `supabase.ts`, the key appears in the build output. Destructive — requires code change.

## Quick Verification Pattern

Once you have the anon key, verify it works:

```bash
curl -s "https://<project>.supabase.co/rest/v1/profiles?select=*&limit=1" \
  -H "apikey: <anon_key>" \
  -H "Authorization: Bearer <anon_key>"
```

- 200 with data: key works, RLS may be permissive
- 200 with empty array: key works, RLS blocks unauthenticated reads
- 401/403: key is invalid or expired
