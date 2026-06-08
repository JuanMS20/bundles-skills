---
name: infrastructure-cost-research
description: "Research and compare real cloud infrastructure costs (hosting, databases, domains, SSL) for a project. Produces a technical guide with local pricing, comparison tables, architecture options, and scalability analysis."
triggers:
  - pricing research for hosting databases domains
  - cuanto cuesta how much for infrastructure
  - deployment cost comparison
  - infrastructure budget document
  - scalability cost analysis
  - guia tecnica with pricing
---

# Infrastructure Cost Research

## When to use
- User asks about real-world costs for deploying an application
- User needs a document/presentation comparing cloud providers
- User mentions "precios", "costos", "cuánto cuesta", "budget", "escalabilidad"
- Planning phase before choosing a stack or provider

## Methodology

### Step 1: Understand current stack
Before searching, confirm what the project currently uses:
- Frontend (static HTML, React, etc.)
- Backend (serverless, containers, traditional server)
- Database (sheets, SQL, NoSQL)
- Current hosting (GitHub Pages, Vercel, etc.)
- Target geography (affects pricing, latency, compliance)

### Step 2: Parallel research (use web_search, NOT browser)
Run 3-5 searches in parallel covering:
- **Hosting providers**: search "[provider] pricing [year] free pro monthly"
- **Database services**: search "[service] pricing [year] free tier monthly"
- **Domain registrars**: search "dominio [ext] precio [country] [year]" OR "domain [ext] pricing [year]"
- **Local pricing**: include the target country name to find local registrars/providers

Key providers to always check:
| Category | Always check | Also consider |
|----------|-------------|---------------|
| Static hosting | Cloudflare Pages, Netlify, Vercel | GitHub Pages, Firebase Hosting |
| Database (SQL) | Supabase, Neon | PlanetScale, Firebase |
| Database (NoSQL) | Firebase Firestore | Supabase (has both) |
| Domains | Cloudflare Registrar, Namecheap | Local registrars |
| Auth | Supabase Auth, Firebase Auth | Clerk, Auth0 |
| Edge/serverless | Cloudflare Workers, Supabase Edge Functions | Netlify Functions, Vercel Functions |

### Step 3: Extract detailed pricing
After initial searches, use web_extract on the official pricing pages (max 5 URLs per call). Get:
- Free tier limits (storage, bandwidth, requests, MAUs)
- Paid tier monthly cost
- Overage rates
- Compute add-on pricing
- Any hidden costs (egress, custom domains, backups)

### Step 4: Currency conversion
- Find current exchange rate (search "[currency] to USD today" or "TRM dolar [country]")
- Convert all prices to local currency AND USD
- Use the rate from the search, not a hardcoded one — rates change

### Step 5: Write the document
Structure as a technical guide (markdown), not a chat response. Use this template:

```markdown
# Guía Técnica: Despliegue y Escalabilidad - [PROJECT]
## Infraestructura, Costos y Seguridad

**Fecha:** [Month Year]
**TRM/tipo de cambio:** [rate]
**Proyecto:** [description]
**Stack actual:** [current tech]

---

## 1. Estado Actual
Table: current components, tech, cost

## 2. Opciones de Hosting
For each provider: table with pricing, limits, features
Mark recommended option with a star

## 3. Opciones de Base de Datos
Same format. Include scalability tiers (0-100 users, 100-1K, 1K-10K, 10K+)

## 4. Dominios
Local pricing table by extension (.co, .com, etc.)
Registrar comparison

## 5. SSL y Seguridad
What's free (almost everything modern), what costs money
Threat model specific to the project

## 6. Arquitecturas Recomendadas
ASCII diagrams of 2-3 options (minimal, recommended, full)
Cost table per option

## 7. Comparativa de Costos Anuales
Summary table in local currency

## 8. Plan de Migración
Phased plan (weeks) if migrating from current stack

## 9. Recomendación Final
Pick one. Justify with 3-5 bullet points.

## 10. Glosario Técnico
For non-technical stakeholders
```

### Step 6: Save reference data
Save the raw pricing data as a reference file under this skill for future updates:
- File: `references/<country>-pricing-<year>.md`
- Include: provider names, free tier limits, paid tier costs, source URLs
- This lets you quickly update prices without re-researching everything

## Pitfalls
- **Don't use browser for pricing pages** — web_search + web_extract is faster and cheaper. Browser only for dynamic pricing calculators.
- **Don't hardcode exchange rates** — always search for current rate at time of research.
- **Don't forget overage costs** — the base price is not the whole story. Egress, backups, custom domains, compute add-ons add up.
- **Don't recommend AWS/GCP raw** — managed services (Supabase, Neon, Firebase) are simpler and often cheaper for small-to-medium projects.
- **Don't present one option** — give 2-3 architecture options with different cost/complexity tradeoffs.
- **SSL is always free** — any modern hosting includes SSL. If a provider charges for SSL, flag it as a red flag.
- **Google Sheets is not a database** — if the current stack uses Sheets, explicitly call out the scalability ceiling.

## Colombia-specific knowledge
- TRM (exchange rate): search "TRM dolar colombia hoy" — typically 3,500-4,200 COP/USD
- Domain .co: approximately 30,000-45,000 COP/year from local registrars, approximately 10-12 USD from Cloudflare
- Cloudflare Registrar sells at cost (no markup) — always recommend for domains
- Google Apps Script is free but has hard limits (6 min execution, 90 min/day total)
- For detailed Colombia pricing data: load `references/colombia-pricing-2026.md`

## References
- `references/colombia-pricing-2026.md` — Detailed pricing data for Colombia (hosting, DB, domains, security) as of May 2026
