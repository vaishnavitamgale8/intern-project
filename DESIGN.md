# ImpactBridge AI — Design System

> **Note on the Figma MCP requirement:** The connected Figma MCP server
> (github.com/GLips/Figma-Context-MCP) is a **read-only** server — it can only
> *fetch* data from existing Figma files (`get_figma_data`,
> `download_figma_images`). It cannot create new design files. Because of this
> platform limitation, the visual design system is delivered as this document
> (the industry-standard "design tokens → components → screens" approach),
> and the frontend is implemented directly from these specifications.

---

## 1. Brand

| Token | Value |
|---|---|
| Brand name | **ImpactBridge AI** |
| Tagline | *Connecting People. Creating Impact.* |
| Support message | *Technology that connects communities, volunteers and meaningful change.* |
| Logo concept | A stylized bridge arc with two connected people shapes; a rising impact dot |
| Favicon | 32px rounded square, primary green `#0F5F4C`, white bridge mark |

## 2. Color System

| Token | Hex | Usage |
|---|---|---|
| `--primary-700` | `#0A3D31` | Dark green — headings, hero background |
| `--primary-600` | `#0F5F4C` | Primary green — primary buttons, links, active nav |
| `--primary-500` | `#167A62` | Hover state for primary buttons |
| `--primary-100` | `#E2F1EC` | Tinted backgrounds, badges, selected states |
| `--accent-500` | `#2E86AB` | Soft blue — secondary CTAs, info, links hover |
| `--accent-100` | `#E3F0F7` | Accent tinted backgrounds |
| `--teal-500` | `#14A38B` | Support accent — highlights, AI output headers |
| `--neutral-50` | `#F8F7F4` | Warm white — page background |
| `--neutral-100` | `#F1EFEA` | Card / section alternate background |
| `--neutral-200` | `#E5E2DB` | Borders, dividers |
| `--neutral-400` | `#9CA39F` | Muted text, placeholder |
| `--neutral-700` | `#3B3B3B` | Body text (dark charcoal) |
| `--neutral-900` | `#1F2320` | Strong text |
| `--success-500` | `#2E9E5B` | Success, approved |
| `--warning-500` | `#E8A33D` | Warning, pending |
| `--error-500` | `#D9534F` | Error, rejected |
| `--white` | `#FFFFFF` | Cards on tinted backgrounds |

**Contrast notes (WCAG AA):** text on neutral-50 uses neutral-900; text on
primary-700 uses white; badges use their 500 color on a 100 tint.

## 3. Typography

| Token | Value |
|---|---|
| Font stack | `'Inter', 'Segoe UI', system-ui, sans-serif` |
| Display | 700 weight, clamp(2rem, 5vw, 3.5rem) |
| H1 | 700, 2.25rem |
| H2 | 700, 1.75rem |
| H3 | 600, 1.375rem |
| Body | 400, 1rem / 1.6 |
| Small | 0.875rem |
| Caption | 0.75rem, letter-spacing 0.02em |
| Kicker | 0.75rem, uppercase, letter-spacing 0.14em, primary-600 |

## 4. Spacing & Radius

| Token | Value |
|---|---|
| Space scale | 4, 8, 12, 16, 24, 32, 48, 64, 96 px |
| Container max | 1200px |
| Card radius | 14px |
| Button radius | 10px |
| Input radius | 10px |
| Badge radius | 999px |
| Modal radius | 18px |

## 5. Shadows

| Token | Value |
|---|---|
| `--shadow-sm` | `0 1px 3px rgba(31,35,32,.08)` |
| `--shadow-md` | `0 6px 18px rgba(31,35,32,.10)` |
| `--shadow-lg` | `0 14px 40px rgba(31,35,32,.14)` |

## 6. Components

### Buttons
- **Primary:** bg primary-600, white text, radius 10, height 44, padding 0 24.
- **Secondary:** white bg, 1px neutral-300 border, primary-700 text.
- **Outline:** transparent, 1.5px primary-600 border, primary-600 text.
- **Danger:** bg error-500, white text.
- **Ghost:** transparent, neutral-700 text; hover bg neutral-100.
- Sizes: sm 36px, md 44px, lg 52px.

### Cards
- White bg, radius 14, shadow-sm, border 1px neutral-200, padding 24.
- **Project / Campaign / Event cards:** media top (16:9), body padding 20,
  kicker + title, meta row, footer row with CTA.

### Inputs & Forms
- Label 0.875rem 600; input height 44, radius 10, border 1px neutral-300;
  focus ring 3px primary-100 + border primary-500.
- Help text 0.8rem neutral-400. Error text 0.8rem error-500.
- Select and textarea match input styling.

### Navbar (public)
- Sticky, white/96 blur, 16px padding, logo left, links center/right,
  CTA "Become a Volunteer" right. Mobile: hamburger → slide-down panel.

### Admin Sidebar
- Desktop 260px fixed; tablet 72px collapsed; mobile drawer overlay.
- Items: icon 20px + label; active item = primary-100 pill, primary-700 text.

### Tables
- Header row neutral-100 uppercase caption; rows border-bottom neutral-200;
  hover row neutral-50; status badges inline.

### Badges
- PENDING → warning; APPROVED/ACTIVE/OPEN → success; REJECTED/CLOSED → error;
  Info → accent; pill radius.

### Modals / Toasts
- Modal: overlay rgba(15,19,17,.5); dialog radius 18, white, shadow-lg,
  title + body + footer buttons.
- Toast: fixed bottom-right stack, radius 12, shadow-md, auto-dismiss 4s.
  Success / warning / error / info variants.

### Charts
- Chart.js. Container card padding 24; legend bottom; no gridlines where possible.

### ImpactBot
- FAB bottom-right (56px, primary-600, chat icon, shadow-lg).
- Panel 380px wide, height 560px, white, radius 18, header primary-700.
- Messages: bot bubble neutral-100; user bubble primary-600 white text.
- Quick chips row; input with send button.

### States
- Empty: centered illustration icon + title + helper text + CTA.
- Loading: skeleton blocks (grey 200 pulse) or spinner.
- Error: error-100 tint card, icon, message, retry button.

## 7. Layout Grid

- 12-column grid, 24px gutters; breakpoints: 360 / 576 / 768 / 992 / 1200.
- Public content max 1200px; hero full-width tinted.
- Admin content padding 32px desktop / 16px mobile.

## 8. Motion

- Transitions 150–200ms ease.
- Fade-in-up on page load for hero (0.3s).
- Button hover lift 1px + shadow.
- Skeleton pulse 1.2s.
- No scrolljacking or heavy animation.

## 9. Accessibility

- Semantic landmarks (header/nav/main/footer/aside).
- All inputs labelled. Focus visible ring 2px primary-500 offset 2.
- Alt text on all images. Skip link to main content.
- Keyboard-operable modals and nav drawer.