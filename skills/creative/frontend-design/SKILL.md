---
name: frontend-design
description: |
  Generate distinctive, production-grade frontend interfaces that stand out from generic AI-generated designs.
  Establishes a design framework before coding — identifying purpose, audience, and a specific aesthetic direction.
  Avoids common patterns like generic system fonts, predictable purple gradients, and cookie-cutter components.
  Use when the user asks to build, create, or design any frontend interface, web page, dashboard,
  landing page, settings panel, or UI component. Do NOT use for backend-only tasks or CLI tools without UI.
---

# Frontend Design

8-phase workflow for distinctive, production-grade frontend interfaces.

## Quick Start

```
User: "Create a music streaming dashboard"
→ Phase 1: Purpose (discovery + playback), Audience (young adults), Aesthetic: Cyberpunk
→ Phase 2: Orbitron headings + Inter body, 64px hero
→ Phase 3: Dark bg (#0a0a0f), neon cyan (#00f0ff), neon pink (#ff00aa)
→ Phase 4: Asymmetric sidebar + floating player overlay
→ Phase 5: Album parallax, waveform animation, hover glow
→ Phase 6: Gradient orbs, glassmorphism player, noise texture
→ Phase 7: React + Tailwind (customized) + Framer Motion
→ Phase 8: Review contrast, mobile, accessibility
```

## Phase 1: Design Framework Establishment

**BEFORE writing any code**, establish:
- **Purpose**: dashboard? landing? e-commerce? admin?
- **Audience**: developers? executives? consumers? children?
- **Aesthetic Direction**: choose ONE explicitly from list below

### Aesthetic Directions (choose one, never default)

| Direction | Characteristics |
|-----------|----------------|
| Brutalist | Raw, bold typography, high contrast, exposed structure |
| Maximalist | Dense info, rich colors, multiple fonts, decorative |
| Retro-futuristic | 80s/90s tech, neon, grid backgrounds, pixel + modern |
| Luxury | Minimal premium, serif fonts, gold accent, whitespace |
| Playful | Rounded shapes, bright colors, illustrations, bouncy |
| Organic/Natural | Earth tones, organic shapes, nature textures, soft shadows |
| Cyberpunk | Dark mode, neon accents, glitch effects, monospace |
| Swiss/International | Grid-based, Helvetica, objective clarity, b/w/red |
| Editorial/Magazine | Large typography, asymmetric layouts, photo-heavy |

**NEVER default to generic corporate design.**

## Phase 2: Typography Strategy

- Choose unexpected pairings. Avoid Inter, Roboto, Arial as defaults
- Google Fonts, Adobe Fonts, or self-hosted
- Hierarchy: hero (48-96px), headings (24-48px), body (16-18px), captions (12-14px)
- Consider weights, letter-spacing, line-height per level

## Phase 3: Color & Visual Identity

- Create distinctive palette. AVOID AI clichés:
  - NO generic purple-to-blue gradients as primary
  - NO default Tailwind palette without customization
  - NO pure gray backgrounds as default
- Define: primary, secondary, accent, background, surface, text, error, success
- Consider dark mode from start if applicable

## Phase 4: Spatial Composition & Layout

- Use asymmetry and grid-breaking intentionally
- Avoid perfectly centered layouts unless aesthetic demands it
- CSS Grid with unexpected proportions (e.g., 1fr 2.5fr 0.5fr)
- Layer elements with z-index, overlapping cards, floating components
- Whitespace is active design element, not empty space

## Phase 5: Motion & Interactions

- Orchestrated animations, not random transitions
- Scroll-triggered interactions (IntersectionObserver, GSAP, Framer Motion)
- Micro-interactions: hover states, card lifts, input focus
- Intentional easing curves (e.g., cubic-bezier(0.16, 1, 0.3, 1))
- NO excessive animation that hurts usability or performance

## Phase 6: Visual Depth & Texture

- Gradients (non-generic), layered shadows, subtle textures
- Glassmorphism or neumorphism only if it fits the aesthetic
- Image treatments: duotone, overlays, masks, parallax

## Phase 7: Implementation

- Semantic HTML5
- Modern CSS: custom properties, container queries, clamp() for responsive typography
- Ensure responsive across breakpoints
- Test accessibility: contrast, keyboard nav, screen readers
- Optimize: lazy loading, image optimization, minimal reflows

## Phase 8: Polish & Review

- Visual consistency: spacing, colors, typography, animations
- Verify it stands out from generic AI-generated interfaces
- Test on real devices or dev tools
- Ask user for feedback and iterate

## Pitfalls

- **NEVER** use generic system fonts as primary without justification
- **NEVER** use predictable purple-to-blue gradients as default branding
- **NEVER** create cookie-cutter layouts (perfectly centered cards in 3-column grid)
- **NEVER** skip the design framework phase
- **NEVER** ignore accessibility. Distinctive must still be usable
- **NEVER** add motion that causes dizziness or hurts performance
- **NEVER** use default Tailwind/Bootstrap styling without customization
- **NEVER** forget dark mode if used in low-light environments

## Verification Checklist

```
[ ] Aesthetic direction chosen explicitly (not default corporate)
[ ] Typography is distinctive (not Inter/Roboto default)
[ ] Palette avoids AI clichés (no purple-blue gradients)
[ ] Layout uses unexpected proportions or asymmetry
[ ] Motion is orchestrated, not random
[ ] Depth added through non-generic gradients, shadows, textures
[ ] HTML semantic, CSS modern, responsive implemented
[ ] Accessibility tested (contrast, keyboard, screen reader)
[ ] Performance optimized (lazy load, image optimization)
[ ] Design stands out from generic AI output
```
