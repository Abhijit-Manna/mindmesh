---
version: alpha
name: Notion
description: "Notion's marketing surface is clean, editorial and near-monochrome: crisp white canvases carry near-black ink with a warm-grey muted tier, letting content and product imagery breathe. Typography leans on the Inter-based NotionInter for UI and headings — from oversized display down to compact captions — with Lyon Text serif for pull-quotes. A single confident blue is the interactive accent, joined by warm yellow, red and green as illustrative surface pops. Corners are softly rounded (4–12px, pills for chips), elevation is delicate multi-layer shadow, and hairlines are faint black-on-white."
colors:
  primary: "#0075DE"
  primary-strong: "#005BAB"
  primary-alt: "#097FE8"
  primary-surface: "#E6F3FE"
  ink: "#000000"
  ink-secondary: "#615D59"
  muted: "#A39E98"
  on-primary: "#FFFFFF"
  surface: "#FFFFFF"
  surface-subtle: "#F6F5F4"
  surface-dark: "#111111"
  accent-yellow: "#FFB110"
  accent-yellow-strong: "#E89D01"
  accent-red: "#F64932"
  accent-red-strong: "#E32D14"
  accent-green: "#1AAE39"
  accent-green-surface: "#D0F4D8"
typography:
  hero-display:
    fontFamily: NotionInter
    fontSize: 96px
    fontWeight: 600
    lineHeight: 1.05
    letterSpacing: -4.6px
  display-lg:
    fontFamily: NotionInter
    fontSize: 72px
    fontWeight: 500
    lineHeight: 1.2
    letterSpacing: -2px
  display-md:
    fontFamily: NotionInter
    fontSize: 54px
    fontWeight: 700
    lineHeight: 1.05
    letterSpacing: -1.87501px
  title-xl:
    fontFamily: NotionInter
    fontSize: 40px
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: normal
  title-lg:
    fontFamily: NotionInter
    fontSize: 24px
    fontWeight: 500
    lineHeight: 0.85
    letterSpacing: normal
  title-md:
    fontFamily: NotionInter
    fontSize: 22px
    fontWeight: 700
    lineHeight: 1.25
    letterSpacing: -0.25px
  title-sm:
    fontFamily: NotionInter
    fontSize: 20px
    fontWeight: 600
    lineHeight: 1.4
    letterSpacing: -0.125px
  body:
    fontFamily: NotionInter
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: normal
  body-medium:
    fontFamily: NotionInter
    fontSize: 16px
    fontWeight: 500
    lineHeight: 1.5
    letterSpacing: normal
  body-strong:
    fontFamily: NotionInter
    fontSize: 16px
    fontWeight: 700
    lineHeight: 1.5
    letterSpacing: normal
  body-sm:
    fontFamily: NotionInter
    fontSize: 14px
    fontWeight: 500
    lineHeight: 1.45
    letterSpacing: normal
  body-sm-regular:
    fontFamily: NotionInter
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.45
    letterSpacing: normal
  caption:
    fontFamily: NotionInter
    fontSize: 12px
    fontWeight: 500
    lineHeight: 1.35
    letterSpacing: 0.125px
  quote-serif:
    fontFamily: Lyon Text
    fontSize: 18px
    fontWeight: 400
    lineHeight: 1.55
    letterSpacing: normal
rounded:
  sm: 4px
  md: 8px
  lg: 12px
  pill: 9999px
spacing:
  xxs: 3px
  xs: 6px
  sm: 8px
  md: 12px
  lg: 16px
  xl: 24px
  2xl: 32px
  3xl: 64px
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    typography: "{typography.body-sm}"
    rounded: "{rounded.md}"
    padding: 8px 16px
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    typography: "{typography.body-sm}"
    rounded: "{rounded.md}"
    borderColor: "{colors.ink}"
    borderWidth: 1px
  card:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.lg}"
    boxShadow: rgba(0, 0, 0, 0.01) 0px 0.175px 1.041px 0px, rgba(0, 0, 0, 0.02) 0px 0.8px 2.925px 0px, rgba(0, 0, 0, 0.027) 0px 2.025px 7.847px 0px, rgba(0, 0, 0, 0.04) 0px 4px 18px 0px
    padding: 24px
  card-elevated:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.lg}"
    boxShadow: rgba(0, 0, 0, 0.008) 0px 0.667px 3.502px 0px, rgba(0, 0, 0, 0.016) 0px 2.933px 7.252px 0px, rgba(0, 0, 0, 0.02) 0px 7.2px 14.462px 0px, rgba(0, 0, 0, 0.024) 0px 13.867px 28.348px 0px, rgba(0, 0, 0, 0.03) 0px 23.333px 52.123px 0px, rgba(0, 0, 0, 0.04) 0px 36px 89px 0px
  chip:
    backgroundColor: "{colors.surface-subtle}"
    textColor: "{colors.ink-secondary}"
    typography: "{typography.caption}"
    rounded: "{rounded.pill}"
    padding: 6px 12px
  input:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.md}"
    borderColor: "{colors.muted}"
    borderWidth: 1px
    padding: 8px 12px
  link:
    textColor: "{colors.primary}"
    typography: "{typography.body}"
  navbar:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    height: 64px
    borderColor: "{colors.ink}"
    borderWidth: 0px
    position: relative
  nav-link:
    textColor: "{colors.ink}"
    typography: "{typography.body}"
  footer:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    height: 396px
    borderColor: rgba(0, 0, 0, 0.1)
    borderWidth: 0px
    columns: "4"
  footer-link:
    textColor: "{colors.ink}"
    typography: "{typography.body}"
  blockquote:
    textColor: "{colors.ink-secondary}"
    typography: "{typography.quote-serif}"
---

# Notion

## Overview

Notion's marketing surface is editorial and near-monochrome: crisp white canvases (`{colors.surface}` — #FFFFFF) carry near-black ink (`{colors.ink}` — #000000), with a warm-grey muted tier for supporting text. The personality is confident and product-led B2B — bold oversized display type set against playful accents (a green 'Ship' pill, cartoon avatar badges) and a logo-wall of enterprise names. Approachable, but credible.

Density is generous rather than packed. Content breathes inside roomy card padding (`{spacing.xl}` — 24px is the workhorse) and a base-8 rhythm. Hierarchy is built almost entirely through **type scale and weight**, not color — a 96px hero drops to 16px body, and a single confident blue is the only interactive accent. Elevation is deliberately restrained: flat light-grey surfaces with 1px hairlines carry most of the structure, and delicate multi-layer shadows are reserved for floating product mockups.

The result reads like a well-made document: lots of white space, strong typographic contrast, and color used sparingly and purposefully.

**Key Characteristics:**
- Near-monochrome palette: black ink on white, warm-grey mutes, one interactive blue.
- Type does the hierarchy work — display sizes from 96px down to 12px captions.
- Two typefaces only: NotionInter for everything UI/heading, Lyon Text for pull-quotes.
- Softly rounded geometry: 4–12px corners, pills for chips and avatars.
- Elevation from surface change and hairlines, not heavy shadows.
- Warm accent pops (yellow, red, green) used only as illustrative surfaces.
- Base-8 spacing scale with tight, consistent card padding.
- Modular rounded-card grid that collapses cleanly to a single mobile column.

## Colors

The palette is near-monochrome by design: black ink on white, a warm-grey muted tier, and one confident blue for interaction. Warm accents appear only as illustrative surface pops. There are no gradients on this surface.

### Brand & Accent
- **Action Blue** (`{colors.primary}` — #0075DE): the single interactive accent — buttons, links, active states. Evidence shows it used exclusively for interactive roles.
- **Action Blue Strong** (`{colors.primary-strong}` — #005BAB): pressed/hover-darker variant for the blue.
- **Action Blue Alt** (`{colors.primary-alt}` — #097FE8): a slightly brighter blue seen in text/surface contexts.
- **Blue Surface** (`{colors.primary-surface}` — #E6F3FE): pale blue tint for interactive highlight backgrounds.
- **On Primary** (`{colors.on-primary}` — #FFFFFF): text/icon color on blue fills.

### Illustrative Accents
These never carry text weight — they are surface pops inside mockups and illustrations.
- **Sunny Yellow** (`{colors.accent-yellow}` — #FFB110) and **Yellow Strong** (`{colors.accent-yellow-strong}` — #E89D01).
- **Signal Red** (`{colors.accent-red}` — #F64932) and **Red Strong** (`{colors.accent-red-strong}` — #E32D14).
- **Ship Green** (`{colors.accent-green}` — #1AAE39) with **Green Surface** (`{colors.accent-green-surface}` — #D0F4D8) for the pale green pill.

### Surface
- **Paper White** (`{colors.surface}` — #FFFFFF): the primary canvas.
- **Warm Grey Surface** (`{colors.surface-subtle}` — #F6F5F4): flat light-grey card fills that create depth without shadow.
- **Near-Black Surface** (`{colors.surface-dark}` — #111111): dark section/inverse block backgrounds.

### Text
- **Ink** (`{colors.ink}` — #000000): primary text, the dominant color by weight.
- **Warm Grey Ink** (`{colors.ink-secondary}` — #615D59): secondary and supporting copy, blockquotes.
- **Muted** (`{colors.muted}` — #A39E98): de-emphasized captions, placeholder text, input borders.

No dark-mode token block is provided; a single `{colors.surface-dark}` value exists for inverse sections but there is no full dark theme to mirror. Build for the light canvas only.

## Typography

Two families, no more. NotionInter carries all UI and headings; Lyon Text is reserved exclusively for serif pull-quotes.

### Font Family
- **NotionInter** — the Inter-based workhorse for everything from the 96px hero to 12px captions. UI, headings, body, buttons.
- **Lyon Text** — a serif used only for blockquotes/pull-quotes at 18px, adding editorial warmth.

### Hierarchy

| Token | Size | Weight | Line Height | Letter Spacing | Use |
|---|---|---|---|---|---|
| `{typography.hero-display}` | 96px | 600 | 1.05 | -4.6px | Hero H1 |
| `{typography.display-lg}` | 72px | 500 | 1.2 | -2px | Large display headings |
| `{typography.display-md}` | 54px | 700 | 1.05 | -1.875px | Section headers (H2) |
| `{typography.title-xl}` | 40px | 400 | 1.5 | normal | Light large titles |
| `{typography.title-lg}` | 24px | 500 | 0.85 | normal | Compact titles |
| `{typography.title-md}` | 22px | 700 | 1.25 | -0.25px | Bold subheads (H2) |
| `{typography.title-sm}` | 20px | 600 | 1.4 | -0.125px | Small titles |
| `{typography.body}` | 16px | 400 | 1.5 | normal | Body copy, nav/footer links |
| `{typography.body-medium}` | 16px | 500 | 1.5 | normal | Emphasized body |
| `{typography.body-strong}` | 16px | 700 | 1.5 | normal | Bold body, inline H3 |
| `{typography.body-sm}` | 14px | 500 | 1.45 | normal | Button labels, small UI |
| `{typography.body-sm-regular}` | 14px | 400 | 1.45 | normal | Small regular text |
| `{typography.caption}` | 12px | 500 | 1.35 | 0.125px | Chips, captions, legal |
| `{typography.quote-serif}` | 18px | 400 | 1.55 | normal | Lyon Text pull-quotes |

### Principles
- **Weights span 400–700**, chosen per role rather than uniformly — hero is 600, display-lg is 500, display-md and title-md are 700. There is no single canonical heading weight; the ladder mixes deliberately.
- **Negative letter-spacing scales with size**: tighter as type grows (-4.6px at 96px, easing to normal by 24px). Small text at 12px gets a slight positive +0.125px to aid legibility.
- **Line-height tightens for display** (1.05 for the biggest sizes) and opens to 1.5 for body — big type wants to be compact, reading copy wants air. Note `{typography.title-lg}` at 0.85 is intentionally ultra-tight for single-line compact labels.
- **NotionInter dominates**; Lyon Text is a single accent for quotes — do not add a third family.

## Layout

### Spacing System
The system is base-8 with fine-grained small steps. Scale: `{spacing.xxs}` (3px), `{spacing.xs}` (6px), `{spacing.sm}` (8px), `{spacing.md}` (12px), `{spacing.lg}` (16px), `{spacing.xl}` (24px), `{spacing.2xl}` (32px), `{spacing.3xl}` (64px). The 8px step is by far the most used, with 24px the standard card padding and section rhythm.

### Grid & Container
The hero is a centered single column. Below it, feature content flows through a modular card grid — two-column capture/find blocks, then full-width automate sections, with an asymmetric rhythm. A horizontal logo marquee runs full-bleed. The header stands 64px tall; the footer is 396px with a four-column link layout. Exact container max-widths and gutter values were not measured — treat the grid as a modular card system with generous, consistent padding rather than a fixed pixel grid.

### Whitespace Philosophy
White space is a primary tool. Cards get roomy `{spacing.xl}` (24px) interiors, sections separate with large vertical gaps, and the near-monochrome palette lets content and product imagery breathe. Density stays low so that oversized display type and product mockups carry the eye without visual competition.

## Elevation & Depth

| Level | Treatment | Use |
|---|---|---|
| Flat | `{colors.surface-subtle}` (#F6F5F4) fill on white, no shadow | Default feature cards, surface layering |
| Hairline | 1px border at `{colors.ink}` or rgba(0,0,0,0.1) | Card/section separation, inputs, footer top rule |
| Soft shadow | `{components.card}` boxShadow — 4 stacked low-alpha layers (0.01–0.04), max 18px blur | Standard elevated cards |
| Deep shadow | `{components.card-elevated}` boxShadow — 6 stacked layers up to 89px blur | Floating product mockups, chat bubbles, dashboard panels |

**Shadow philosophy.** Elevation comes primarily from surface change and hairlines, not shadows. Most cards are flat light-grey rectangles on white, separated by 1px borders. When depth is needed, it is delivered through finely-tuned multi-layer shadows — 4 to 6 stacked rgba(0,0,0) layers at very low opacity (0.008–0.04) that read as soft, realistic ambient light rather than a hard drop. The heavy `{components.card-elevated}` treatment is reserved for floating UI mockups that need to lift off the page.

## Shapes

### Border Radius Scale

| Token | Value | Use |
|---|---|---|
| `{rounded.sm}` | 4px | Small chips, tight inner elements |
| `{rounded.md}` | 8px | Buttons, inputs — the most-used radius |
| `{rounded.lg}` | 12px | Cards and larger containers |
| `{rounded.pill}` | 9999px | Chips, tags, the green 'Ship' pill, circular avatars |

The geometry is consistently soft: rounded rectangles everywhere, medium-to-large radii, nothing sharp. 8px is the default corner (buttons, inputs), stepping up to 12px for cards. Pills and full circles appear for chips, tags, and avatar badges — the friendly counterpoint to the otherwise square grid blocks. The rounding is restrained enough to stay professional but consistent enough to feel like a single, approachable family.

## Components

### Navigation
- **`navbar`** — 64px tall, `{colors.surface}` (#FFFFFF) background with `{colors.ink}` text, `position: relative` (not sticky), no backdrop blur. Border width is 0px — the header sits flush on white with no visible rule. Links use `{typography.body}` (16px/400) in black; the evidence counts many nav entries (a full mega-menu structure). The header **does** carry a CTA button (`hasCtaButton: true`) — a primary Action Blue action at the right.
- **`nav-link`** — `{colors.ink}` text in `{typography.body}` (16px regular). Understated, monochrome; the blue CTA provides the only color contrast.

### Buttons
- **`button-primary`** — `{colors.primary}` (#0075DE) fill, `{colors.on-primary}` white text, `{typography.body-sm}` (14px/500) label, `{rounded.md}` (8px) corners, 8px×16px padding. The primary call to action; reserve the blue fill for it.
- **`button-secondary`** — `{colors.surface}` white fill, `{colors.ink}` text, 1px `{colors.ink}` border, same `{typography.body-sm}` label and `{rounded.md}` radius. The outlined companion to the primary.

### Cards & Containers
- **`card`** — `{colors.surface}` background, `{rounded.lg}` (12px) corners, `{spacing.xl}` (24px) padding, and the soft 4-layer `boxShadow`. Standard feature card.
- **`card-elevated`** — same surface and radius with the deep 6-layer shadow (up to 89px blur) for floating mockups that must lift off the page.

### Inputs & Forms
- **`input`** — `{colors.surface}` background, `{colors.ink}` text, `{rounded.md}` (8px) corners, 1px `{colors.muted}` (#A39E98) border, 8px×12px padding. Muted warm-grey border keeps forms quiet until focused.

### Badges & Chips
- **`chip`** — `{colors.surface-subtle}` (#F6F5F4) fill, `{colors.ink-secondary}` text, `{typography.caption}` (12px/500), `{rounded.pill}` fully-rounded corners, 6px×12px padding. Used for tags and category markers.

### Links & Quotes
- **`link`** — `{colors.primary}` (#0075DE) text in `{typography.body}`. The blue is the interactive signal.
- **`blockquote`** — `{colors.ink-secondary}` text in `{typography.quote-serif}` (Lyon Text 18px). The one place the serif appears.

### Footer
- **`footer`** — `{colors.surface}` white background, 396px tall, four link columns, with a faint rgba(0,0,0,0.1) top hairline (borderWidth token 0px but color present). Contains ~24 links in `{typography.body}` (16px/400) black via `footer-link`, no CTA button. Legal/caption text drops to `{typography.caption}` treatment. Static positioning.

## Do's and Don'ts

### Do
- Reserve `{colors.primary}` (#0075DE) strictly for interactive elements — buttons, links, CTAs (evidence shows it used only in interactive roles).
- Keep the two-typeface split: `NotionInter` for UI/headings, `Lyon Text` for quotes only — never add a third family.
- Build hierarchy with the type scale and weight, not color — go from `{typography.hero-display}` down to `{typography.caption}`.
- Layer depth with `{colors.surface-subtle}` fills and 1px hairlines first; reach for `{components.card}` shadow only when a card must lift.
- Use `{rounded.md}` (8px) for buttons/inputs and `{rounded.lg}` (12px) for cards to keep geometry consistent.
- Keep warm accents (`{colors.accent-yellow}`, `{colors.accent-red}`, `{colors.accent-green}`) as illustrative surface pops, never as text or primary UI color.

### Don't
- Don't tint body text with the accent colors — text is `{colors.ink}` or `{colors.ink-secondary}` only.
- Don't add heavy single drop-shadows; elevation is the delicate multi-layer `{components.card}` / `{components.card-elevated}` stacks.
- Don't introduce gradients — this surface has none.
- Don't fill secondary buttons with color — `{components.button-secondary}` is white with a 1px `{colors.ink}` border.
- Don't make the navbar sticky or add a backdrop blur — it is `position: relative` with no blur.
- Don't crowd content; preserve the generous `{spacing.xl}` (24px) card padding and base-8 rhythm.

## Responsive Behavior

This is a two-viewport analysis (desktop and mobile captures); no intermediate breakpoint pixel values were measured, so treat exact thresholds as unknown.

On desktop the hero is a centered single column above a mixed grid — two-column capture/find blocks and full-width automate sections — with a horizontal logo marquee. On mobile the same modules collapse to a strict single-column stack, preserving the rounded-card rhythm and module order. The component system is clearly designed to reflow: cards keep their `{rounded.lg}` corners and `{spacing.xl}` padding at both sizes.

Touch targets are supported by the token padding: `{components.button-primary}` at 8px×16px and `{components.input}` at 8px×12px give adequately tappable controls, and chips at 6px×12px stay legible. The 64px header height leaves room for a comfortable mobile bar. Beyond this stacking behavior, finer responsive tuning (column-count changes, gutter shifts) was not directly measured.

## Iteration Guide

1. **Change interactive color once, at the token.** All CTAs, links, and active states derive from `{colors.primary}`; edit that token (and its `{colors.primary-strong}` / `{colors.primary-alt}` companions) rather than per-component hexes.
2. **Add new text styles inside the existing ladder.** Slot between `{typography.hero-display}` and `{typography.caption}` and match the letter-spacing-scales-with-size rule; do not introduce a new font family beyond NotionInter and Lyon Text.
3. **Button and input variants live in `{components.button-primary}`, `{components.button-secondary}`, and `{components.input}`** — keep `{rounded.md}` corners and `{typography.body-sm}` labels consistent across them.
4. **Elevation is a two-tier choice**: flat surface + hairline, or `{components.card}` shadow, with `{components.card-elevated}` for floating mockups only. Don't invent a mid shadow.
5. **Keep accents illustrative.** `{colors.accent-yellow}`, `{colors.accent-red}`, `{colors.accent-green}` belong to imagery/surface pops — never migrate them into text or core UI chrome.
6. **Respect the base-8 spacing scale.** Use the `{spacing}` tokens; avoid off-grid values like 10px or 15px even though a few appear in raw captures.
7. **Unbreakable boundaries**: near-monochrome canvas (white surface, black ink), one blue accent, two typefaces, soft rounded geometry. Breaking any of these breaks the Notion feel.

## Known Gaps

- **Single page captured.** Only the homepage (`notion.com/`) was analyzed; interior product, pricing, and template pages may introduce patterns not represented here.
- **No hover/focus/pressed states observed.** Variants like `{colors.primary-strong}` are inferred as interactive-darker states but were not captured live.
- **Two-viewport responsive only.** Exact breakpoints, container max-widths, and gutter values were not measured — the responsive section describes stacking behavior, not thresholds.
- **No dark theme.** A single `{colors.surface-dark}` / `{colors.surface}` inverse exists for dark sections, but no full dark-mode token set was found; do not assume one.
- **Animation and motion** (marquee scroll speed, transitions, mockup parallax) could not be evaluated from static evidence.
- **Navbar mega-menu contents** — the header reports 23 link references suggesting a dropdown structure, but the expanded menu design was not captured.
- **Auth-walled surfaces** (the actual Notion app UI) are outside this marketing extraction entirely.
- No values were dropped during grounding, so token coverage of the captured page is complete.
