---
name: Household Dashboard
description: A Catppuccin-themed Home Assistant dashboard built from Bubble Card and Mushroom, with one idle grey and one tint rule everywhere.
colors:
  primary: "light-dark(#8839ef, #cba6f7)"
  page: "light-dark(#e6e9ef, #181825)"
  card: "light-dark(#eff1f5, #1e1e2e)"
  text: "light-dark(#4c4f69, #cdd6f4)"
  text-secondary: "light-dark(#5c5f77, #bac2de)"
  idle: "light-dark(#7c7f93, #6f6f6f)"
  light-on: "light-dark(#df8e1d, #f9e2af)"
  cat-accent: "light-dark(#b8860b, #f9e2af)"
  climate-cool: "light-dark(#1e66f5, #89b4fa)"
  climate-heat: "light-dark(#d20f39, #f38ba8)"
  climate-dry: "light-dark(#0b78a8, #89dceb)"
  climate-fan: "light-dark(#2b7a1d, #a6e3a1)"
  climate-auto: "light-dark(#179299, #94e2d5)"
  success: "light-dark(#2b7a1d, #a6e3a1)"
  warning: "light-dark(#a8690d, #f9e2af)"
  error: "light-dark(#d20f39, #f38ba8)"
  info: "light-dark(#0b78a8, #89b4fa)"
  backdrop: "light-dark(rgba(76, 79, 105, 0.45), rgba(17, 17, 27, 0.8))"
typography:
  display:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: "30px"
    fontWeight: 700
    lineHeight: 1.15
    letterSpacing: "-0.01em"
  headline:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: "18px"
    fontWeight: 700
    lineHeight: 1.1
  title:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: "14px"
    fontWeight: 600
    lineHeight: 1.15
  body:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.4
  label:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: "12px"
    fontWeight: 400
    lineHeight: 1.2
rounded:
  card: "14px"
  control: "12px"
  pill: "18px"
  disc: "50%"
spacing:
  xs: "6px"
  sm: "8px"
  md: "10px"
  lg: "12px"
  xl: "16px"
components:
  card:
    backgroundColor: "{colors.card}"
    rounded: "{rounded.card}"
  row-bubble:
    backgroundColor: "{colors.card}"
    textColor: "{colors.text}"
    rounded: "{rounded.card}"
  sub-button:
    backgroundColor: "rgba(76, 79, 105, 0.05)"
    textColor: "{colors.text}"
    rounded: "{rounded.control}"
    height: "36px"
  sub-button-on:
    backgroundColor: "rgba(136, 57, 239, 0.2)"
    textColor: "{colors.primary}"
    rounded: "{rounded.control}"
    height: "36px"
  chip:
    backgroundColor: "{colors.card}"
    textColor: "{colors.text}"
    rounded: "{rounded.pill}"
    height: "36px"
    padding: "0 10px"
  icon-disc:
    rounded: "{rounded.disc}"
    size: "42px"
  nav-bar:
    backgroundColor: "{colors.card}"
    rounded: "{rounded.card}"
    padding: "6px 8px"
  nav-item-active:
    backgroundColor: "transparent"
    textColor: "{colors.primary}"
    rounded: "{rounded.control}"
---

# Design System: Household Dashboard

## Overview

**Creative North Star: "The Quiet Control Panel"**

A phone dashboard for one household, read at a glance and worked with one thumb. It is an
Operate surface: every view starts with a row of status chips, then the cards you act on.
Nothing announces itself. State is carried by colour on an icon and a short line of text,
and the only strong colour on a screen is the one that means something is on.

The visual language is borrowed, deliberately, from two stock card libraries. Bubble Card
provides the status rows, sub-buttons, pop-ups and section separators; Mushroom provides
climate, fan, light, entity, person, media and chip cards. Hand-built button-card templates
survive only where no stock card fits (the room cards on the Rooms page and the attention
rows on Home), and they are styled to be indistinguishable from Mushroom. The theme is
Catppuccin, Latte in light mode and Mocha in dark, and it follows the phone's light/dark
setting.

**Key Characteristics:**
- One font (Inter), one card colour, one page colour, one idle grey.
- Icon discs and active fills are always the icon's own colour at 20%.
- Chips first on every view; no page titles; sections named by Bubble separators.
- Tap acts, hold opens the dialog, and status-only things open their dialog on tap.
- Sentence case, middle-dot separators, short relative times.

## Colors

Catppuccin Latte and Mocha, with a single accent and a few state colours that mean the same thing on every card.

### Primary
- **Mauve** (`{colors.primary}`): the dashboard accent. Any device that is on, any sensor icon, the active navbar item, Bubble's on-state tint, Mushroom's entity colour. It is the only "something is active" colour apart from the two exceptions below.

### Secondary
- **Light On** (`{colors.light-on}`): the Catppuccin yellow, matching Home Assistant's own light tiles. Used for lights only: the Lights row, light chips and light tiles when on. Mushroom's named "amber" is remapped to this value.
- **Cat Accent** (`{colors.cat-accent}`): goldenrod in light mode, Catppuccin yellow in dark. Used only for the cats' row icon. It sits at 2.9:1 in light mode, a deliberate exception for a decorative icon beside its label.

### Tertiary
- **Climate modes**: cool `{colors.climate-cool}`, heat `{colors.climate-heat}`, dry `{colors.climate-dry}`, fan-only `{colors.climate-fan}`, auto `{colors.climate-auto}`. The aircon chip, tile and card all use the same mapping, with a mode icon to match (snowflake, heat wave, water drop, fan, sun-snowflake).
- **Lock**: green when locked, amber when unlocked, red when jammed, idle grey when unavailable.

### Neutral
- **Page** (`{colors.page}`): the view background and the pop-up sheet.
- **Card** (`{colors.card}`): every card, Bubble row, chip and the floating navbar.
- **Text** (`{colors.text}`) and **Secondary text** (`{colors.text-secondary}`): names and states. Both exceed 4.5:1 on the card in each mode.
- **Idle** (`{colors.idle}`): Mushroom's disabled grey, used for every icon that is off or unavailable and for the disc behind it. Mushroom's named "grey" and "disabled" are remapped to it.
- **Backdrop** (`{colors.backdrop}`): the dim behind a pop-up, dark enough in light mode that the sheet reads as a sheet.

### Named Rules
**The Twenty Percent Rule.** A disc or active fill is never a new colour. It is the icon's colour at 20% opacity, via `color-mix(in srgb, currentColor 20%, transparent)` or `rgba(rgb, 0.2)`. Idle discs are the idle grey at 20%; idle sub-buttons are the text colour at 5%.

**The Sensor Is Never On Rule.** A sensor reading, humidity, temperature, air quality, gets no fill behind its sub-button or chip. Fills mean a switchable thing is switched on.

**The Three-to-One Rule.** Every icon colour reaches 3:1 on the card background in both modes. In light mode this is why Mushroom's named colours are remapped to darker Latte hues; the cat accent is the one recorded exception.

## Typography

**Display Font:** Inter (system-ui fallback)
**Body Font:** Inter
**Label Font:** Inter

**Character:** one neutral sans at five sizes, so hierarchy comes from weight and size alone and every card family looks like the same product.

### Hierarchy
- **Display** (700, 30px, 1.15): the Home greeting only. Two lines, "Good afternoon," then the signed-in person's name.
- **Headline** (700, 18px): room names on the Rooms page cards.
- **Title** (600, 14px): card and row names, chip text, tile names. This is Mushroom's primary size and Bubble rows and chips match it.
- **Body** (400, 15px): the greeting's weather line.
- **Label** (400, 12px): states and secondary lines under a name, tile states.

### Named Rules
**The Sentence Case Rule.** Copy follows Home Assistant: "Lunch tomorrow 12:00", "All off", "Schedule off". Never title case for a state.

**The Middle Dot Rule.** Compound states join with " · ": "Fed 4h ago · Lunch at 12:00", "Cool · 20°". Episode details join with " • ".

## Layout

A single column of cards at phone width with 16px gutters, following the Home Assistant masonry view. Every view opens with a chip row; there are no page-title toolbars because the Home Assistant header already shows the view name and a back arrow for subviews. On Home the greeting sits under the chips, then the two residents, then the status rows.

- **Chip rows** never wrap. They scroll sideways with the scrollbar hidden; a partly visible chip signals more. Room-page settings live as an icon-only action chip at the end of the row.
- **Grids** are two columns. A grid with exactly three short items uses three columns. Adjacent grids under one section are merged so cards fill both columns instead of leaving a lone card on a row.
- **Sections** are Bubble separators. A Devices section holds things you act on, grouped by type (fans together), never status or diagnostic rows; diagnostics live on the System page or in the device's dialog.
- **No repetition.** A page shows an entity once. The chips at the top carry a room's summary, so room cards have no status line under the name.
- **Floating navbar** is inset 12px from the edges and bottom, respects the safe area, and is the one control group without an active fill or labels.
- **Pop-ups** use Bubble's built-in header (avatar or icon, name, state) and the same card grids as pages. Group pop-ups are built by auto-entities and grouped by floor then room.

## Elevation & Depth

Flat. No card shadows and no borders; the theme sets both to none. Depth is tonal: page below card, card below the icon disc or control fill, and a dimmed backdrop below a pop-up sheet. The navbar floats on a 94% card colour with a 12px blur. Motion is limited to the swipe-navigation slide between views (250ms); a card entry animation was tried and removed because it re-fires on every state update.

### Named Rules
**The Flat-By-Default Rule.** Nothing casts a shadow. If a surface needs separation, change its tone, not its elevation.

## Shapes

Three radii and a circle. Cards, Bubble rows, pop-up sheets and the navbar use the card radius (14px). Controls, Mushroom's mode buttons, Bubble sub-buttons and navbar items, use 12px. Chips are pills (18px on a 36px height). Icon discs are circles, 42px on cards and rows, 36px inside chips. Avatars are circular and replace the disc on person cards and pop-up headers.

## Components

### Chips (Mushroom chips card)
- **Style:** card-coloured pill, 36px tall, entity icon plus a short state, title weight.
- **Colour:** icon only. Lights-on yellow, climate mode colour, lock colour, mauve for a device that is on, idle grey otherwise. No fill.
- **Navigation chips** end with " ›" and navigate on tap, open the dialog on hold.
- **Sensor chips** show one decimal and a degree sign, or a dash when unavailable.
- **Action chip:** icon-only dots at the end of a room row, opens that room's settings pop-up.

### Status rows (Bubble button)
- **Shape:** card colour, card radius, 42px icon disc on the left, name over state.
- **Icon:** colour by state, disc at 20% of that colour.
- **Sub-buttons:** 12px corners, 36px tall, idle fill text-at-5%; when on, primary at 20% with the icon and text in solid primary. Sensors have `state_background: false`. Fans show "On"/"Off" text so state is never colour alone.
- **Actions:** the icon opens the entity dialog; the rest of the row navigates or opens a pop-up.

### Cards (Mushroom entity, fan, climate, light, person, media, vacuum)
- **Corner Style:** card radius.
- **Background:** card colour, no shadow, no border.
- **Icons:** the entity's own icon, never hand-picked unless the icon encodes state. Mushroom's icon shape is the 20% disc.
- **Controls:** collapsible sliders, mode and preset dropdowns through Home Assistant card features.
- **Number cards** hide the state subtitle since the stepper shows the value.
- **Status-only devices** (the air purifier) open their dialog on tap and never toggle.

### Room cards (button-card, Rooms page only)
- Chips row, then room icon disc + room name + temperature (and humidity when known), then a device tile row.
- **Device tiles** follow Mushroom's vertical card: 42px disc, name (600/14), state (400/12). Lights use the light colour, the aircon its mode colour, the lock its lock colour, everything else mauve when active. Hover and press feedback is a neutral text-colour ripple at 4% and 8%.

### Navigation (navbar-card)
- **Bar:** card colour at 94% with blur, card radius, inset 12px, no labels.
- **Items:** idle grey icon; the active item is a solid mauve icon with no fill.
- **More menu:** card-coloured pills with 14px corners, stretched to the widest label.

### Pop-ups (Bubble pop-up)
- **Header:** built-in, with the entity's avatar or an icon, the name and state; close button on the right.
- **Sheet:** page colour, over the dimmed backdrop. Content uses the same grids and Mushroom cards as pages.
- **Group pop-ups:** auto-entities per room, under floor separators and room sub-headings, in the group's own member order.

### Greeting (Markdown card, Home only)
- Transparent, aligned to the card edges. Display heading on two lines, a body line with condition and outside temperature, and a Meteocons illustration (MIT, in `www/dashboard/weather/`) on the right chosen by condition and time of day.

## Do's and Don'ts

### Do:
- **Do** reach for Bubble Card or Mushroom first; add a button-card template only when no stock card can do the job.
- **Do** start every view with the chip row and let the Home Assistant header be the title.
- **Do** derive every disc and active fill from the icon colour at 20%, and keep sensors unfilled.
- **Do** use the entity's default icon; override only when the icon encodes state (aircon mode, lock).
- **Do** keep Devices sections to controls, grouped by type, and merge adjacent grids so columns fill.
- **Do** give every control a tap and a hold: tap acts, hold opens the dialog; dangerous actions (feeding the cats) confirm first.
- **Do** write states in sentence case with " · " between parts, and show "—" rather than NaN or 0.0 when a sensor is unavailable.
- **Do** verify in the browser after a theme change, and reload themes (Developer tools › YAML › Themes) for theme edits; touch `ui-lovelace.yaml` and refresh for dashboard edits.

### Don't:
- **Don't** fill the active navbar item or show navbar labels; the navbar is the one exception to the control styling.
- **Don't** paint a sub-button solid; the solid colour goes on the icon and text, the fill stays at 20%.
- **Don't** use Bubble's horizontal-buttons-stack for inline rows; it is a fixed footer.
- **Don't** add an entry animation to all cards via card-mod; it re-fires on every state update.
- **Don't** repeat an entity on a page, put a page title above the chips, or put status rows (filters, batteries, "Status") in a Devices section.
- **Don't** show more than one decimal on a temperature, or a unit on a chip when the degree sign will do.
- **Don't** rely on colour alone for on/off where the icon is identical; add the state word.
