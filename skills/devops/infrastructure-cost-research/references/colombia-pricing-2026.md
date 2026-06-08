# Colombia Infrastructure Pricing — May 2026

**TRM at time of research:** $3,759 COP/USD (May 12, 2026)
**Source:** dolar-colombia.com

## Hosting (Static Frontend)

| Provider | Free Tier | Paid Tier | Bandwidth (Free) | Key Advantage |
|----------|-----------|-----------|------------------|---------------|
| Cloudflare Pages | $0 | $0 (Workers paid separately) | Unlimited | CDN 300+ cities, DDoS protection, no bandwidth cap |
| Netlify | $0 | $20/mo (~75K COP) | 100 GB/mo | Credit-based system since Sep 2025, 300 credits/mo free |
| Vercel Hobby | $0 | $20/user/mo (~75K COP) | 100 GB/mo | Best for Next.js, overkill for static HTML |
| GitHub Pages | $0 | N/A | 100 GB soft limit | Simple, no custom domain SSL on free |
| Firebase Hosting | $0 (Spark) | Pay-as-you-go (Blaze) | 360 MB/day (~10.8 GB/mo) | Natural fit if already using Google ecosystem |

**Winner:** Cloudflare Pages — unlimited bandwidth, free DDoS, global CDN, $0.

## Database

| Provider | Free Tier | Pro/Scale Tier | DB Type | Auth Included |
|----------|-----------|----------------|---------|---------------|
| Supabase | 500 MB DB, 50K MAUs, 1 GB storage, unlimited API | $25/mo (~94K COP): 8 GB DB, 100K MAUs, 100 GB storage | PostgreSQL | Yes (50K MAUs free) |
| Firebase Firestore | 1 GiB storage, 10 GiB egress, 50K reads/day | Blaze pay-as-you-go | NoSQL (document) | Yes (50K MAUs free) |
| Firebase Realtime DB | 1 GB storage, 10 GB download/mo, 100 concurrent | Blaze: $5/GB stored, $1/GB downloaded | NoSQL (JSON tree) | Yes |
| Neon | 0.5 GB storage, 100 CU-hours/mo | $5/mo min (~19K COP), $0.106/CU-hour | PostgreSQL | No |
| PlanetScale | 5 GB storage, 1B rows reads/mo | $29/mo (~109K COP) | MySQL | No |

**Supabase free tier limits (important):**
- Projects pause after 1 week of inactivity
- Max 2 active projects
- No daily backups (Pro has 7-day retention)
- Shared CPU, 500 MB RAM

**Supabase Pro includes $10/mo compute credits** (covers one Micro instance: 2-core ARM, 1 GB RAM).

**Winner for NOVVA VALLE:** Supabase — PostgreSQL real, auth + storage + edge functions bundled, RLS for access control.

## Domains (.co / .com)

| Registrar | .co USD | .co COP | .com USD | .com COP | Notes |
|-----------|---------|---------|----------|----------|-------|
| Cloudflare Registrar | ~$10-12 | ~$38K-45K | ~$10-11 | ~$38K-41K | **At cost, no markup.** Same price for renewal. |
| Namecheap | ~$8-10 | ~$30K-38K | ~$10-12 | ~$38K-45K | First year often discounted |
| Registro Colombia | N/A | $30,000 | N/A | N/A | Official .co operator, restricted TLDs only (.org.co, .edu.co, .gov.co) |
| ClickPanda | N/A | $44,990 | N/A | $54,990 | Local Colombian registrar |
| Hostinger | ~$10-12 | ~$38K-45K | ~$10-15 | ~$38K-56K | Often bundled with hosting |

**Winner:** Cloudflare Registrar — price of cost, automatic renewal at same price, free DNS, DNSSEC included.

## SSL / Security

| Feature | Cost | Provider |
|---------|------|----------|
| SSL certificate | $0 | Let's Encrypt (auto via Cloudflare/Netlify/Vercel) |
| Universal SSL | $0 | Cloudflare (included with DNS) |
| DDoS protection | $0 | Cloudflare Free |
| WAF (basic) | $0 | Cloudflare Free |
| Rate limiting | $0 | Cloudflare Workers (100K req/day free) |
| Dedicated SSL/wildcard | $50-200/year | Only if specifically needed |

**Rule:** If a provider charges for SSL, it's a red flag. Move on.

## Google Apps Script (Current Backend)

| Aspect | Free Tier Limit |
|--------|----------------|
| Execution time | 6 min per script run |
| Total daily execution | 90 min |
| URL Fetch calls | 20,000/day |
| Email recipients | 100/day |
| Cost | $0 |
| SLA | None |
| Uptime guarantee | None |

**GAS is not a production backend.** Fine for prototyping, but no SLA, hard limits, and no guaranteed uptime.

## Architecture Options Summary

| Option | Components | Annual Cost (COP) | Annual Cost (USD) | Scalability |
|--------|-----------|-------------------|-------------------|-------------|
| Minimal | GitHub Pages + GAS + Sheets | $0 | $0 | Very low |
| Budget | Cloudflare Pages + GAS + Sheets + .co domain | ~$38,000 | ~$10 | Low |
| Recommended | Cloudflare Pages + Supabase Free + .co domain | ~$38,000 | ~$10 | Medium-High |
| Production | Cloudflare Pages + Supabase Pro + .co domain | ~$132,000 | ~$35 | High |
| Full Google | Firebase Hosting + Firestore + Auth + .co domain | ~$38,000-85,000 | ~$10-23 | Medium-High |

## Source URLs (retrieved May 2026)
- Supabase: https://supabase.com/pricing
- Firebase: https://firebase.google.com/pricing
- Netlify: https://www.netlify.com/pricing/pro-vs-free/
- Cloudflare Pages: https://developers.cloudflare.com/pages/functions/pricing/
- Vercel: https://vercel.com/docs/plans
- Neon: https://neon.com/ (pricing page)
- Colombia domains: https://blog.clickpanda.com/dominios/cuanto-cuesta-dominio-pagina-web-colombia/
- Cloudflare Registrar: https://domains.cloudflare.com/
- TRM: https://www.dolar-colombia.com/
