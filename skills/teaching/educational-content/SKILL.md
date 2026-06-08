---
name: educational-content
description: Build self-contained educational demo kits with simulated backend, progressive demo scripts, slides, and video storyboard. Use when user says they're a teacher/professor, needs material for a class/workshop/video, wants to demonstrate a concept with working code, or asks for an "educational demo" or "teaching material."
---

# Educational Content

Build a complete, self-contained educational kit for teaching any technical concept. The goal is **zero operational overhead** for students: everything runs locally, no accounts, no real money, no external services beyond `pip install`.

## Architecture pattern

```
project/
├── core/                        # Pure domain model (no I/O, no UI, testable)
│   ├── __init__.py
│   ├── models.py                # Domain classes + state machine
│   ├── api.py                   # REST/HTTP layer (Flask, FastAPI, or stdlib)
│   └── presenter.py             # Console output (ANSI, JSON, or silent)
├── entrypoint.py                # Thin CLI entrypoint
├── demos/
│   ├── shared.py                # Shared helpers, base classes, ANSI constants
│   ├── demo-1-basics.py         # Progressive demos (3 recommended)
│   ├── demo-2-agent.py
│   └── demo-3-swarm.py
├── tests/
│   └── test_models.py           # Tests on the pure model (fast, deterministic)
├── slides.md                    # Presentation slides
├── storyboard.md                # Video timeline (minute-by-minute)
└── README.md                    # Quick start
```

## Layering rules

| Layer      | Depends on | Has I/O? | Testable?       |
|------------|-----------|----------|-----------------|
| models.py  | nothing   | NO       | ✅ Unit test    |
| api.py     | models    | HTTP     | Integration test|
| presenter.py | nothing (just prints) | stdout | Manual |
| demos/     | api (via HTTP) | HTTP+stdout | Demo run |
| tests/     | models    | NO       | ✅ Fast         |

**Models first** — pure classes with no prints, no Flask, no HTTP. The entire simulation logic lives here. Test immediately.

**API on top** — thin Flask layer that calls models and returns JSON. Presenter calls go here, not in models.

**Presenter extracted** — all ANSI/terminal output formatted here. One function per event type (block_mined, tx_sent, etc.). Keeps models testable.

**Entrypoint** — imports API + presenter, runs banner, starts server.

## Building order

1. **Models** — pure classes, zero I/O. Test immediately.
2. **API** — REST layer on top of models.
3. **Presenter** — extract all console output from step 1.
4. **Entrypoint** — banner + server start.
5. **Demos** — progressive: 1 = fundamentals, 2 = single agent, 3 = multi-agent.
6. **Tests** — unit tests on models (24+ cases recommended). Integration tests optional.
7. **Agent skill** — Hermes skill with curl commands. Use TDD vertical (see [agent-skill-tdd.md](references/agent-skill-tdd.md)): write integration tests against the live API FIRST, one behavior at a time, then document the verified behavior in the skill.
8. **Dashboard** — HTML page that polls the API for real-time state visualization.
   Use TDD vertical for the dashboard: write tests **first** covering structure (DOCTYPE, tags), JS behavior (endpoints, fetch, polling interval), CSS (dark theme, monospace, overflow), rendering (containers per data type, DOM manipulation functions), and visual feedback (highlight animation). Then build the HTML to make tests GREEN. See [dashboard-tdd.md](references/dashboard-tdd.md) for the full pattern.
9. **Materials** — slides + storyboard for video timing.

## Simulated backend pattern

Build a REST API server (Flask) that simulates the target environment:

- **Pre-loaded state**: Default accounts/data ready on startup
- **In-memory**: No persistence (resets on restart — ideal for classrooms)
- **REST endpoints**: CRUD operations the demos call via HTTP
- **Console output**: Show server-side activity as students watch
- **Reset endpoint**: POST /reset to wipe state between demos

The backend should be ~300 lines in 4 sections:
1. Domain models (pure logic, no prints, no framework)
2. Presenter (ANSI output formatting, separated from logic)
3. API routes (Flask, thin)
4. CLI entrypoint (banner + app.run())

## Progressive demo structure

Three-tier progression — each demo builds on the previous:

| Tier | What | Duration in video |
|------|------|------------------|
| 1 — Fundamentals | Basic concepts, no agents yet | ~3 min clip |
| 2 — Autonomous | Single agent perceive→decide→act loop | ~5 min clip |
| 3 — Swarm | Multiple agents coordinating via contracts | ~6 min clip |

Each demo is a self-contained Python script that:
- Imports from shared helpers (ANSI colors, step/pause helpers, base agent class)
- Connects to the running API
- Prints step-by-step with pauses for narration
- Ends with a summary of concepts demonstrated

### Agent base class pattern

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

## Creating slides

### When planning is already done

If the user loads the plan-sprint bundle (grill-with-docs / to-prd / to-issues) but the project already has complete planning artifacts (PRD, slides, storyboard, issues, demos), **skip the grilling phase**. Jump directly to building the materials. Confirm with the user: "Ya existe todo planeado — paso directo a construir los materiales." This avoids wasting the session on questions that were already answered.

### Two deliverables

Always produce **two separate files** — they serve different people:

1. **`guion.html`** — For the PRESENTER. Full narration text they read while recording. Includes timing per slide (~3-4 min each), visual cues, transitions between topics, embedded notes. Responsive for phone viewing during recording. Includes a built-in timer/stopwatch.

2. **`slides.html`** — For the STUDENTS (visual presentation). What appears on screen during the video. Minimal text, heavy on visuals. Slide-by-slide navigation like PowerPoint. White/minimalist background. Embed hand-drawn diagrams (Excalidraw style).

### Slide structure (~15 slides for 40-50 min video)

| Slide | Content | Duration |
|-------|---------|----------|
| 1 | Cover — topic, subtitle, context | ~2 min |
| 2 | Motivation — why this matters | ~3 min |
| 3 | Concepts — the 5 building blocks | ~4 min |
| 4 | Agent definition | ~3 min |
| 5 | Agent loop in context | ~3 min |
| 6 | Smart contracts / coordination | ~4 min |
| 7 | Tech stack diagram | ~2 min |
| 8-10 | What each demo shows | ~3-4 min each |
| 11 | Real-world use cases | ~3 min |
| 12 | Frameworks comparison | ~2 min |
| 13 | Conclusions | ~2 min |
| 14 | Resources + Q&A | ~1 min |

**Total: ~45-50 min** (leaves room for demo clips embedded in the video)

### Visual slides with hand-drawn diagrams (HTML)

Build `slides.html` as a single-file HTML presentation with these features:
- **Full-viewport slides** with horizontal navigation (left/right arrows, swipe on mobile, click sides)
- **White/clean background** (students read content, not fancy backgrounds)
- **Hand-drawn (Excalidraw-style) diagrams** using [roughjs](https://roughjs.com/) — loads from CDN, no build step
- **Slide counter and progress indicator**
- **Keyboard shortcuts**: Arrow keys, Space, Home/End
- **Double-click** for fullscreen
- **Responsive**: works on projector, laptop, and mobile

#### roughjs integration pattern

```html
<script type="importmap">
{
  "imports": {
    "roughjs": "https://cdn.jsdelivr.net/npm/roughjs@4.6.6/bundled/rough.esm.js"
  }
}
</script>
<script type="module">
import rough from 'roughjs';

function draw(id, fn) {
  const svg = document.getElementById(id);
  if (!svg) return;
  svg.innerHTML = '';
  const rc = rough.svg(svg);
  fn(rc, svg);
}

// Draw a diagram into an SVG with viewBox
draw('diagram-1', (rc, svg) => {
  let box = rc.rectangle(20, 10, 350, 200, {
    stroke: '#ef4444', strokeWidth: 2, roughness: 1.5,
    fill: '#fef2f2', fillStyle: 'solid'
  });
  svg.appendChild(box);
  // Add text with regular SVG <text> elements
  const t = document.createElementNS('http://www.w3.org/2000/svg', 'text');
  t.setAttribute('x', '100'); t.setAttribute('y', '50');
  t.setAttribute('font-family', 'Inter, sans-serif');
  t.textContent = 'Hello';
  svg.appendChild(t);
});
</script>
```

#### Arrow workaround (roughjs has no native arrow)

```javascript
function drawArrow(rc, svg, x1, y1, x2, y2, opts = {}) {
  const line = rc.line(x1, y1, x2, y2, opts);
  svg.appendChild(line);
  const ang = Math.atan2(y2 - y1, x2 - x1);
  const hl = 10, ha = 0.4;
  const p1 = [x2 - hl * Math.cos(ang - ha), y2 - hl * Math.sin(ang - ha)];
  const p2 = [x2 - hl * Math.cos(ang + ha), y2 - hl * Math.sin(ang + ha)];
  const head = rc.polygon([[x2, y2], p1, p2], {
    stroke: opts.stroke, fill: opts.stroke,
    fillStyle: 'solid', roughness: 1, strokeWidth: 1
  });
  svg.appendChild(head);
  return line; // allows existing appendChild patterns to not error
}
```

#### Diagram types that work well for educational content

| Concept | Visual approach |
|---------|----------------|
| Comparison ("Sin vs Con") | Two side-by-side cards with colored outlines and pastel fills |
| Chain/sequence | Connected blocks with arrows showing hashes |
| Cycle (perceive→reason→act) | Boxes or circles arranged with directional arrows |
| Architecture stack | Stacked layers with decreasing width |
| Protocol flow | Actors on sides, contract/process in center, arrows showing interactions |
| Data/cards grid | Rectangles with color bars and compact text |

#### Navigation pattern (CSS + JS)

```css
#deck { display: flex; transition: transform 0.4s; }
.slide { min-width: 100vw; height: 100vh; }
```

```javascript
function goToSlide(idx) {
  deck.style.transform = `translateX(-${idx * 100}vw)`;
}
```

#### Guion narrator script (HTML)

Build `guion.html` as a scrollable single page:
- **Full narration text** (not bullet points) — the presenter reads this aloud
- **Timing annotations** per slide (~2-4 min)
- **Transitions** between slides ("→ Ahora veamos...")
- **Highlighted key terms** for emphasis while speaking
- **Visual cues** for the editor: when to show clip, when to transition
- **Built-in stopwatch timer** with pause/reset
- **Progress bar** and quick nav to any slide
- **Dark mode**, large font for phone reading
- **Space bar** toggles the timer

## Creating the video storyboard

Minute-by-minute timeline for ~55 min video:

| Block | Duration | Content |
|-------|----------|---------|
| Introduction | 5 min | Context, why this matters |
| Concepts | 10 min | Theory + Demo 1 clip |
| Autonomous agents | 12 min | Loop explanation + Demo 2 clip |
| Multi-agent | 12 min | Coordination + Demo 3 clip |
| Real cases | 10 min | Production projects + conclusions |
| Q&A | 5 min | Open |

Each row must specify: minute marker, what to say, what visual to show (slide or clip).

## Video format (slides + demo clips)

- **Slides**: Record first (with camera or voiceover)
- **Demos**: Record separately, just terminal + dashboard capture
- **Edit**: Interleave slides with demo clips
- **Tip**: If a demo fails mid-recording, only re-record that clip

### Split-screen recording (terminal + dashboard)

When the demo involves both a CLI agent and a live dashboard, record them simultaneously as split-screen:

```
┌─────────────────────┬─────────────────────┐
│ Terminal (left)     │ Dashboard (right)   │
│ 20+ px font, dark   │ Browser, full-width │
│ bg, light text      │ no address bar      │
├─────────────────────┴─────────────────────┤
│ Teacher voiceover (narration throughout)  │
└───────────────────────────────────────────┘
```

Each demo needs a **shot-by-shot script** mapping: what the teacher does → what's on screen → what students see → what concept it teaches. Use the [recording-demo-script.md](references/recording-demo-script.md) template for this.

Layout: terminal on LEFT, dashboard on RIGHT (standard video convention for Western reading direction).

### Step-by-step script structure

For each demo step, use a table:

```
| Paso | En pantalla | Qué hace/profesor | Qué ven estudiantes | Enseña |
|------|-------------|-------------------|---------------------|--------|
| N    | Terminal    | Action + exact    | Observable screen   | Single |
|      | or Dashboard| teacher line      | change with values  | concept|
```

This gives the editor exact cut points and the teacher a word-for-word script.

## One-command setup

```bash
pip install flask          # single dependency
python backend.py          # start the simulated environment
python demos/demo-1.py     # run progressive demos
```

## Pitfalls

- **Don't couple ANSI output to model logic.** It makes models untestable. Always extract a presenter layer.
- **Don't put global state in models module.** Use a registry in the API layer or pass instances explicitly. Put the single instance (e.g. `_chain_state`) in `api.py` and expose getter/setter.
- **Don't create agents as `__main__` blocks.** Extract agent base classes into `demos/shared.py` so demo-2 and demo-3 don't duplicate code.
- **Don't over-engineer the simulation.** Students don't need crypto-grade security — they need to see the concept. A `hashlib.sha256` that takes 200ns is fine for teaching; Proof of Work with difficulty=2 is visual enough.
- **Don't use real infrastructure.** No testnets, no faucets, no wallet setup, no gas fees. The entire point is zero setup friction.
- **Don't skip the storyboard.** A talk without timing runs over. Write the minute-by-minute script first, then build the demos to fit.
- **Keep the video realistic**: 1 hour of content needs ~45 min of slides and ~15 min of demo footage. Don't build more demo than the video can hold.
- **Don't forget raw video materials.** A working simulator without slides + storyboard is hard to film. Build them in the same session.
- **Unit tests on models first, integration later.** 24 fast tests > 10 slow integration tests for catching regressions.
- **Test API response shapes before documenting them in the skill.** What you *think* the API returns (e.g. `resp["tx_hash"]` at top level) is often wrong. Write a tracer bullet test that calls the actual endpoint and asserts the real structure. This catches response shape surprises before they reach the skill doc.
- **Avoid urllib for HTTP error testing when Flask returns 4xx.** Python's urllib can hang on `HTTPError.read()`. Use `curl` via `subprocess` for error-path integration tests instead.
- **Agents `from_balance` in POST /send response is the sender's balance, not the agent's.** Read `/balance/<agent_address>` after each action to get the correct post-transaction balance.
- **Skills created by writing files directly to the skills directory do not persist across sessions.** Always use `skill_manage(action='create')` to register a skill. Writing to `~/.claude/commands/<name>.md` also works for Matt Pocock-style local commands, but `skill_manage` is the canonical Hermes path that survives restarts.
- **SVG text in hand-drawn diagrams overflows if not centered properly.** When positioning text at the center of a box (e.g. `x = box.x + box.w/2`), always set `text-anchor='middle'` — use `txt.center()` from the `makeTxt` helper. Without centering, text extends right of the center point and spills outside the box.
- **SVGs can be too tall on small screens.** Add `max-height: 45vh` to diagram SVGs and `overflow-y: auto` to slides. Use `@media (max-height: 650px)` to tighten padding on short screens. See [roughjs-presentations.md](references/roughjs-presentations.md) for the full responsive recipe.
- **Test slides on mobile before finishing.** Desktop layout ≠ mobile layout. Open the HTML on a phone or resize the browser to <400px wide and <700px tall to catch overflow and text-spill bugs.

### Diagram positioning iteration loop

After writing a roughjs diagram, you WILL need to adjust positions. This is normal. Use this loop:

1. **Draw rough boxes first** — get the basic layout and dimensions.
2. **Add text labels** — use `txt()` for left-aligned, `txt.center()` for centered. Use the same `makeTxt(svg)` helper scoped to each `draw()` callback.
3. **Preview on mobile** (or resize browser to <400px wide, <700px tall).
4. **Fix overflow**: three levers (use in order):
   - **Shorter text** — "Transaction" → "Tx", "bal,estados,eventos" → condensed
   - **Smaller font** — inside boxes: '10'-'13' max
   - **Larger viewBox** — add 50-100px to viewBox height
5. **Fix centering** — if text at `box.x + box.w/2` spills right, it needs `txt.center()` not `txt()`. Check every call.
6. **Preview again** — repeat until all text fits inside boxes.
7. **Check ALL slides** — navigate through the full deck; the first slide always looks best because you tuned it most. Slide 6 (complex escrow/flow diagrams) and Slide 11 (multi-agent) tend to have the worst overflow.

## References

This skill has supporting reference files with concrete examples and domain knowledge:

- [py-chain-pattern.md](references/py-chain-pattern.md) — Simulated blockchain implementation with pure domain model, REST API, presenter separation. Template for blockchain educational demos.
- [blockchain-simulator-case-study.md](references/blockchain-simulator-case-study.md) — Full case study of the py-chain project: architecture evolution, lessons learned, video materials.
- [api-endpoints.md](references/api-endpoints.md) — Complete REST API reference for the simulated blockchain.
- [architecture.md](references/architecture.md) — Internal architecture: class hierarchy, mining, transaction lifecycle, smart contract execution.
- [hermes-agent-integration.md](references/hermes-agent-integration.md) — Pattern for integrating Hermes as a real LLM-powered agent interacting with the simulated blockchain via skill + curl.
- [agent-skill-tdd.md](references/agent-skill-tdd.md) — TDD vertical workflow for building/extending Hermes agent skills against simulated APIs. Use when starting a new issue that adds capabilities to an agent skill.
- [dashboard-tdd.md](references/dashboard-tdd.md) — TDD vertical workflow for static HTML dashboards: 12 tests covering structure, endpoints, CSS, rendering, and animation.
- [recording-demo-script.md](references/recording-demo-script.md) — Shot-by-shot split-screen recording script template with pedagogical mapping (screen × teacher × student × concept).
- [roughjs-presentations.md](references/roughjs-presentations.md) — Building HTML slide presentations with hand-drawn (Excalidraw-style) diagrams using roughjs: CDN integration, SVG viewBox approach, arrow workaround, diagram patterns for educational content.
