# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Two adult residents of one household, at home, using the Home Assistant companion app on
Android phones. Typical moments: walking into a room and wanting the lights or aircon changed,
checking the cats were fed, seeing who is home, glancing at temperature or air quality.

A wall-mounted tablet is planned. It will get its own dedicated view rather than the phone
layout; that view is not designed yet. (Confirmed 2026-10-07.)

No other audiences are confirmed. Guests and admin-only use are not design targets.

## Product Purpose

A single personal Home Assistant dashboard that is both a control surface and a status board,
with equal weight on each (confirmed). Success means the common actions take one or two taps,
and the household state is readable at a glance without opening device pages.

## Positioning

Not a product for others; a single-household dashboard. Its distinguishing mechanism is a
template-driven YAML source (button-card and decluttering-card templates with a neutral `app_`
prefix) that is published into Home Assistant's storage dashboard and mirrored to a public
GitHub repository with personal identifiers replaced by placeholders.

## Operating Context

- Home Assistant 2026.9 on Home Assistant OS; Zigbee devices through Zigbee2MQTT; MQTT broker.
- Rooms: Living Room, Master Bedroom, Bedroom, Master Bathroom. Floors: first and second.
- Devices: Zigbee bulbs and light groups; one Daikin aircon via a Faikin controller exposed as a
  hand-written MQTT climate entity (more aircons expected later, added with
  `bin/add_faikin_aircon.sh`); Xiaomi standing fans and an air purifier with sensors; two cat
  feeders and one pet fountain (a second was removed 2026-10-07); weather via OpenWeatherMap; speedtest, Zigbee bridge, AdGuard,
  backup and electricity-rate sensors; two gaming PCs with wake-on-LAN. Some devices are
  currently unavailable after the move (robot vacuum, TVs, speaker) and are shown
  conditionally.
- Dashboard pipeline: the default dashboard is a YAML dashboard reading `ui-lovelace.yaml` directly;
  touch that file and refresh to apply (see `dashboards/README.md`). HACS still manages resources. Edits in the
  UI are not written back to the files.
- HACS frontend plugins in use: Bubble Card (rows, pop-ups, separators), Mushroom (most cards and chips),
  auto-entities, button-card and decluttering-card (room cards, attention rows), stack-in-card, layout-card,
  navbar-card, card-mod, hass-swipe-navigation, upcoming-media-card. Meteocons SVGs (MIT) in `www/dashboard/weather`.
- Public mirror: github.com/rairulyle/hassio-config. A git clean/smudge filter swaps people,
  phone trackers, pet names, PC hostnames and Discord ids for placeholders on commit.

## Capabilities and Constraints

- Views: Home, Rooms (with one page per room), Climate, Pets, People, System; pop-ups for
  people, room settings, pet settings and upcoming TV; a bottom navbar.
- The Home Assistant header and sidebar stay visible; kiosk mode is not used. Secondary views
  are subviews so the header shows no tab bar. (Current choice, open to change.)
- Device control uses official Home Assistant cards where they fit (thermostat, tile); the
  aircon's Daikin-only fan and swing modes get friendly names through the MQTT entity because
  the official card cannot relabel options. (Current choice, open to change.)
- Removed on purpose and not to be re-added: a third person entity, the PC shutdown scripts,
  the water-shortage alert (flaky sensor), the second pet fountain (device removed), page-title toolbars,
  the old quick-actions row (the Lights and Fans rows with sub-buttons replaced it, by choice), and feeder fault alert cards.
- Three cats: Cat1, Cat2 and Cat3 (Cat3 joined 2026-10-07); one pet fountain.
- Spoken reminders use a playful Japanese-flavoured English voice; this is a TTS/automation
  trait, not a UI copy requirement.
- Undecided: the wall tablet's view and whether it runs full-screen; any desktop-specific layout.

## Brand Commitments

- Binding: neutral component naming. Templates, files, icons and URLs use the `app_` / `app:`
  prefix; no person's name or the upstream author's name in component names.
- Binding since 2026-10-07: stock cards (Bubble Card, Mushroom) over custom templates; see DESIGN.md.
- Current, not binding: the "Catppuccin Auto Latte Mocha Dashboard" theme (Catppuccin Latte/Mocha palettes with
  dashboard additions), the Inter typeface, and the custom `app:` icon set in
  `www/dashboard/app_icons.js`. Future design work may propose alternatives.
- The structure is adapted from johnkoht/hassio-config and credited in the README.

## Evidence on Hand

- The live instance and the YAML source in this folder are the ground truth.
- Screenshots for the README are to be added by the owner at `preview/overview.png` and
  `preview/master_bedroom.png` (mobile ratio). None exist in the repo yet.
- Entity lists before and after the owner's pruning are in `dashboard_backups/`.
- There are no testimonials, metrics or external evidence, and none should be invented.

## Product Principles

1. The common actions take one or two taps from the Home view.
2. Status and control carry equal weight; neither is demoted to a secondary page.
3. Prefer built-in Home Assistant behaviour and cards; add custom code only where the platform
   cannot do the job.
4. Components stay neutral and reusable; adding a room or an aircon means reusing a template,
   not writing a new one.
5. Public-safe by construction: nothing personal is needed in component names or files.
