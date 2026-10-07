# Dashboards

The default dashboard (`/lovelace`, sidebar "Home") runs in **YAML mode** and reads the files
under this folder directly. HACS keeps managing the frontend resources.

Layout:

```
ui-lovelace.yaml            entry file (title, templates, view includes)
dashboards/mobile/          views: home, rooms + room pages, climate, pets, more/people, more/system
dashboards/templates/       button_cards/ (button-card templates), decluttering/ (decluttering templates),
                            includes/ (card_mod snippets, layouts, navbar)
themes/catppuccin-dashboard/  "Catppuccin Auto Latte Mocha Dashboard" theme (light + dark modes) used by every view
www/dashboard/              app_icons.js (icon set app:app-*) and fonts.js (Inter)
```

Home Assistant resolves all the `!include`s from `ui-lovelace.yaml`, the entry file named in
`configuration.yaml`.

## Seeing YAML changes

The default dashboard (`/lovelace`) runs in YAML mode and reads `ui-lovelace.yaml` directly.

1. Edit the YAML files.
2. `touch ui-lovelace.yaml` (Home Assistant only re-reads YAML dashboards when the entry file changes).
3. Refresh the page.

Frontend resources (HACS plugins and `www/dashboard/*.js`) are still managed by HACS in
Settings > Dashboards > Resources; YAML mode applies to the dashboard only.

## Conventions

- Templates and icons use the neutral `app_` / `app:` prefix.
- Multi-line JavaScript (`[[[ ... ]]]`) must be a single line when passed as a decluttering variable.
- Every template key must be unique across `templates/button_cards` and `templates/decluttering`
  (`!include_dir_merge_named` silently lets the alphabetically later file win).
- In this repository the person and phone entity ids under `mobile/` are generic placeholders
  (`person.person1`, `device_tracker.person1_phone`, ...); a git clean/smudge filter maps them
  to the real ids on the Home Assistant host.

## Tile and chip behaviour

- Chip rows are plain `horizontal-stack`s styled with `card_mod` (flex, gap 10px, min-height 45px); `mod-card` wrappers paint seconds late, so avoid them for anything above the fold.
- Every device tile obeys one rule: **tap acts** (toggle, or the entity's own dialog when a toggle would be
  risky, e.g. all lights, the aircon, the door lock), **hold explains or navigates** (more-info or the page).
- Chips navigate or open the entity dialog; they never toggle except the plain device chip.
- State text is `<State> · <time> ago` with a middle dot everywhere; offline and unknown devices fade out.
- Switches that can disable something important (feeding schedule, unlocking the door) ask for confirmation
  or use the official card that asks for one.
- `light.all_lights` (light.yaml) carries its members, so chips and tiles bound to it count bulbs without a list.

## Adding another Faikin (Daikin) aircon

The official thermostat card cannot rename a device's fan/swing options, so each aircon gets a
hand-written MQTT climate entity with friendly names instead of the auto-discovered one:

```bash
bin/add_faikin_aircon.sh "Bedroom Aircon" bedroom-aircon D4059248ABCD
```

Arguments: entity name, the controller's MQTT id (topics are `state/<id>` and `command/<id>/...`),
and the device id from its discovery topic `homeassistant/climate/<device-id>/config`
(Settings > Devices > the Faikin device > MQTT info). The script appends a block to `mqtt.yaml`
from `mqtt_templates/faikin_climate.yaml`. Then run the `mqtt.reload` action, disable the
auto-discovered climate entity on that device, and rename the new entity id if wanted
(it defaults to `climate.<name>_<name>`).

Standard values (auto/low/medium/high, off/vertical/horizontal/both) keep Home Assistant's icons
and translations; Daikin-only modes show as Night, Low-Medium, Medium-High and Comfort.
