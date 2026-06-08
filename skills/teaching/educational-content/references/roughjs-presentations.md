# HTML slides with hand-drawn diagrams (roughjs / Excalidraw style)

Build responsive HTML slide presentations with hand-drawn (Excalidraw-like) diagrams using the [roughjs](https://roughjs.com) library.

## When to use this instead of PowerPoint

- Student-facing slides need **visual engagement** — text-only slides bore students after 30 seconds
- You want **hand-drawn diagrams** without hiring a designer
- The content benefits from **embedded code**, **live data**, or **animations**
- You want **zero dependencies** — single HTML file, no build tools
- The presentation should work on **any device** (projector, laptop, phone)

## Roughjs CDN integration

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
// rc = rough.svg(svgElement)  →  SVG renderer
// rc.rectangle(x, y, w, h, opts)  →  <g> node
// rc.ellipse(x, y, w, h, opts)
// rc.line(x1, y1, x2, y2, opts)
// rc.circle(x, y, d, opts)
// rc.polygon(points, opts)
// rc.linearPath(points, opts)
</script>
```

Key roughjs options for Excalidraw look:
- `roughness: 1.3–1.6` — higher = wobblier lines
- `strokeWidth: 1.5–2.5`
- `fill: '#pastelhex'` with `fillStyle: 'solid'`
- `stroke: '#color'`
- `strokeLineDash: [8, 6]` for dashed borders (contracts, constraints)

## SVG structure

Each diagram is an `<svg>` with a `viewBox` for responsive scaling:

```html
<div class="diagram-wrap">
  <svg id="diag-concept" viewBox="0 0 800 300"></svg>
</div>
<style>
.diagram-wrap { width: 100%; max-width: 800px; margin: 16px auto; }
.diagram-wrap svg { width: 100%; height: auto; display: block; }
</style>
```

## Adding text to roughjs drawings

roughjs doesn't have text support. Add regular SVG `<text>` elements via a `makeTxt(svg)` factory:

```javascript
function makeTxt(svg) {
  const ns = 'http://www.w3.org/2000/svg';
  const create = (x, y, content, opts = {}) => {
    const t = document.createElementNS(ns, 'text');
    t.setAttribute('x', x); t.setAttribute('y', y);
    t.setAttribute('font-family', 'Inter, sans-serif');
    t.setAttribute('font-size', opts.size || '13');
    t.setAttribute('fill', opts.c || opts.color || '#334155');
    t.setAttribute('font-weight', opts.w || opts.weight || '400');
    if (opts.center || opts.a === 'm') t.setAttribute('text-anchor', 'middle');
    t.textContent = content;
    return t;
  };
  // Shortcut: txt.center(...) wraps text-anchor='middle'
  create.center = (x, y, content, opts = {}) => create(x, y, content, {...opts, a: 'm'});
  return create;
}
```

Usage:

```javascript
const txt = makeTxt(svg);
svg.appendChild(txt(50, 50, 'Left-aligned text', {c: '#475569'}));
svg.appendChild(txt.center(200, 80, 'Centered text', {size: '16', w: '700'}));
```

Always define `txt` at the top of each `draw()` callback so each diagram has its own text helper scoped to the correct SVG document.

## Arrow workaround

roughjs has no native arrow. Use this helper:

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
  return line; // so existing appendChild calls don't crash
}
```

## Diagram patterns for educational content

| Concept | Layout | Elements |
|---------|--------|----------|
| **Comparison** (Sin vs Con) | Two side-by-side boxes (~350x270 each) | Colored outlines (red/green), pastel fills, emoji markers |
| **Chain** (blocks) | 3+ blocks connected by arrows (~180x140 each) | Hash text, transaction list, highlighted current block |
| **Cycle** (perceive→reason→act) | 3 boxes in a row with arrows, or triangle layout | Step number, description, emoji icon |
| **Architecture stack** | 4 stacked layers, decreasing width | Emoji per layer, primary color accent, sub-description |
| **Protocol / escrow** | Actors on sides, contract in center | Dashed border on contract, arrows labeled with action |
| **Terminal/CLI demo** | Dark terminal rectangle, green prompt | Monospace text, output lines, optional split-screen line |
| **Card grid** | 2×3 or 3×2 grid of cards | Color bar on left, bold name, compact description, tag badge |

## Slide deck HTML structure

```html
<div id="deck">
  <div class="slide" data-idx="0">...</div>
  <div class="slide" data-idx="1">...</div>
  ...
</div>
<div id="controls">
  <button onclick="prevSlide()">◀</button>
  <span>1 / 15</span>
  <button onclick="nextSlide()">▶</button>
</div>
```

```css
#deck { display: flex; transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1); }
.slide { min-width: 100vw; height: 100vh; overflow-y: auto; }
```

```javascript
let currentSlide = 0;
function goToSlide(idx) {
  currentSlide = Math.max(0, Math.min(idx, totalSlides - 1));
  deck.style.transform = `translateX(-${currentSlide * 100}vw)`;
}
```

### Navigation features

- **Keyboard**: ArrowRight/Space/PageDown → next, ArrowLeft/PageUp → prev, Home → first, End → last
- **Touch**: Swipe left/right (>50px, dominant horizontal)
- **Mouse**: Click right 30% → next, left 30% → prev
- **Wheel**: Horizontal scroll
- **Fullscreen**: Double-click toggles fullscreen
- **Slide dots**: Right edge, vertical indicator

## Responsive SVG constraints

SVGs can be too tall on small screens, pushing content out of view. Constrain them:

```css
.diagram-wrap svg {
  width: 100%;
  height: auto;
  display: block;
  max-height: 45vh;          /* prevent tall diagrams from dominating small screens */
}
@media (max-height: 700px) {
  .diagram-wrap svg { max-height: 35vh; }
}
```

For short screens, also adjust slide padding and vertical alignment:

```css
@media (max-height: 650px) {
  .slide { padding: 10px 20px; justify-content: flex-start; }
}
```

## Text overflow debugging

When text spills outside its box in hand-drawn diagrams:

1. **Check `text-anchor`** — if the x position is the center of a box but `text-anchor` is not `'middle'`, the text extends right of center and may overflow. Use `txt.center()` or pass `{a: 'm'}` or `{center: true}`.

2. **Shorten labels** — use compact abbreviations:
   - "Blockchain" → "Chain", "Transaction" → "Tx", "Smart Contract" → "Contract"
   - Hash previews: "0x9d2e...c4f7" (10 chars) not full hashes
   - Descriptions: at most 2 short lines, ~25 chars per line

3. **Reduce font size** — inside SVG boxes use size '10'-'13' for sublabels, '13'-'16' for titles. Outside diagrams, slide body text can stay at '16'-'18'.

4. **Increase viewBox** — if the diagram is cramped, expand the viewBox (e.g. 800×300 → 800×350) and spread elements further apart.

5. **Add `max-height` to the SVG** — prevents the diagram from compressing vertically on small screens (see section above).

6. **Make slides scrollable** — on `.slide` set `overflow-y: auto` so if content exceeds viewport height the user can scroll. This is a safety net; the goal is still to fit in one view.

## Color palette for hand-drawn diagrams

```css
/* Diagram accent colors */
blue:   #3b82f6 / fill: #eff6ff
green:  #10b981 / fill: #f0fdf4
orange: #f59e0b / fill: #fffbeb
red:    #ef4444 / fill: #fef2f2
purple: #8b5cf6 / fill: #f5f3ff
teal:   #06b6d4 / fill: #ecfeff
```

Pastel fills with distinct colored strokes give the Excalidraw feel. Use emoji sparingly to mark key concepts.

## Working with viewBox

All roughjs coordinates are absolute within the viewBox space. The SVG scales automatically:

```html
<!-- All positions in 800x400 coordinate space -->
<svg viewBox="0 0 800 400" style="min-height:200px">
```

The viewBox approach means:
- Elements don't need repositioning when window resizes
- Mobile and projector get the same layout
- `min-height` prevents collapse before JS renders

## Common pitfalls

- **`rc.arrow()` does not exist** — always use `drawArrow()` helper
- **SVG elements must be appended** — roughjs returns raw SVG nodes, you need `svg.appendChild(node)`
- **Module scripts run async** — diagram code may execute after non-module scripts
- **Importmap needs modern browser** — Chrome 89+, Firefox 108+, Safari 16.4+
- **Don't use `checkVisibility()`** — off-screen slides may return false; always just check `if (!svg) return`
- **Avoid `rc.path()` for simple shapes** — `rectangle()`, `ellipse()`, `polygon()` give more consistent hand-drawn wobble
