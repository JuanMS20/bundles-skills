# NOVVA VALLE — Design Tokens (from prueba1 demo)

## Color Palette

```css
--teal: #1a9696;      /* Primary */
--teal-d: #0d6666;    /* Primary Dark */
--teal-l: #2ab8b8;    /* Primary Light */
--dark: #2d3748;      /* Secondary/Navy */
--dark-l: #4a5568;    /* Secondary Light */
--green: #10b981;     /* Success */
--red: #ef4444;       /* Error */
--gray-50: #f4f9f9;   /* Background */
--gray-100: #e8f4f4;  /* Surface */
--gray-200: #d1e8e8;  /* Border */
--gray-400: #7aaeae;  /* Text muted */
--gray-600: #3d7070;  /* Text secondary */
--gray-800: #1a3535;  /* Text primary */
```

## Typography

- **Primary**: Sora (300, 400, 500, 600, 700)
- **Mono**: DM Mono (400, 500) — for usernames, documents

## Border Radius

- Small: 8px (buttons, chips)
- Medium: 12px (cards, inputs) — `--r: 12px`
- Large: 24px (modals)
- Full: 99px (badges, pills)

## Shadows

```css
--shadow: 0 4px 24px rgba(26, 122, 122, 0.12);
--shadow-lg: 0 8px 40px rgba(26, 122, 122, 0.22);
```

## Component Patterns

### Topbar
- Height: 58px (desktop), 50px (mobile)
- Background: `--teal-d`
- Logo: SVG shield icon (32x32)
- User: avatar circle + name pill

### Nav Tabs
- Background: `--teal`
- Active: bottom border + gold/white color
- Icon + label layout

### Stat Cards
- 3-column grid
- Border-top: 3px solid (teal/gold/green)
- Number: 28px bold
- Label: 11px muted

### Contact/Leader Cards
- Avatar: 42-44px circle with gradient background + initials
- Badge: pill shape, uppercase, 10px
- Metadata: flex wrap with icons
- Border-left: 4px color-coded by status

### Modals
- Bottom sheet on mobile (border-radius top only)
- Centered on desktop (full border-radius)
- Slide-up animation: `translateY(40px)` → `0`
- Backdrop: `rgba(15, 34, 68, 0.6)` + blur(4px)

### Search Bar
- Icon: SVG lupa, absolute positioned left
- Padding-left: 40px (for icon)
- Focus: border-teal + box-shadow

### Filter Pills
- Pill shape (99px radius)
- Active: teal background, white text
- Inactive: white background, gray border

### Empty States
- Centered, 48px padding
- Icon: 48px emoji
- Title: 16px, teal-700
- Description: 13px, muted

### Toast
- Fixed bottom center
- Pill shape
- Dark background
- Auto-dismiss 3-4s

### Loading
- Full-screen overlay
- Backdrop blur
- Spinner: 32px, border-top-color teal
- Message below spinner

## Responsive Breakpoints

- Mobile: < 600px
  - Topbar: 50px height, compact
  - Modals: bottom sheet
  - Stats: smaller text
  - Nav: scroll horizontal
- Desktop: >= 600px
  - Full topbar
  - Centered modals
  - Max-width: 720px content
