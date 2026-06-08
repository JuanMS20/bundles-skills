# Hermes Memory Providers — Research Summary (May 2026)

## Comparison Table

| Provider | Cost | Dependencies | API Key | Storage | Key Features |
|----------|------|-------------|---------|---------|--------------|
| **Holographic** | Free | None (pure Python) | No | Local SQLite | FTS5, trust scoring, HRR algebra, 9 actions |
| **Hindsight** | Free (local) | `hindsight-client` pip | Yes (LLM) | Local files | Auto-synthesis, timeline, fact extraction via LLM |
| **Honcho** | Paid (cloud) | API key | Yes | Cloud | Most community-recommended, best UX |
| **Mem0** | Paid (cloud) | API key | Yes | Cloud | Open-source option available with self-host |
| **SuperMemory** | Paid | API key | Yes | Cloud | High-capacity, API-first |
| **OpenViking** | Free | Running server | No | Local | Requires persistent server process |

## Recommendation: Holographic for Free Tier

### Why Holographic won
- **Zero barriers**: No API keys, no running servers, no external deps beyond Python stdlib + sqlite3
- **Rich tool surface**: 9 actions including `reason` (deductive inference), `contradict` (detect contradictions), `probe` (exploratory search)
- **Trust scoring**: Facts get a trust score (0-1) that adjusts based on `fact_feedback` ratings over time
- **HRR algebra**: Holographic Reduced Representation enables compositional/associative retrieval — can find related facts even without keyword overlap
- **Auto-extract**: Set `auto_extract: true` to extract facts from session conversations automatically

### Why others were rejected
- **Hindsight**: "Local" mode still requires an LLM API key for extraction/synthesis — not truly free without an existing key
- **Honcho**: Best overall per community consensus, but paid cloud service
- **Mem0**: Paid cloud; self-hosted option exists but heavier setup
- **SuperMemory**: Paid, API-only
- **OpenViking**: Requires running a persistent server process — operational overhead

## Holographic Actions

| Action | Purpose |
|--------|---------|
| `add` | Store a new fact |
| `search` | FTS5 keyword search |
| `probe` | Exploratory search (fuzzy/conceptual) |
| `related` | Find facts related to a given fact |
| `reason` | Deductive inference over stored facts |
| `contradict` | Detect contradictions between facts |
| `update` | Modify an existing fact |
| `remove` | Delete a fact |
| `list` | List all facts (paginated) |

Plus `fact_feedback` for trust calibration.

## Community Sources

- Reddit r/hermesagent: Honcho most recommended overall; Holographic for free tier
- Official docs: https://hermes-agent.nousresearch.com/docs/memory-providers
- Holographic README: SQLite-based, FTS5, trust scoring, HRR
