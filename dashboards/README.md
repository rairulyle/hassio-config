# Dashboards

The default dashboard (`/lovelace`, sidebar "Home") runs in **UI/storage mode**, so it is
editable in the Home Assistant UI and HACS manages its resources.

The YAML under this folder is the **source** it was built from:

```
ui-lovelace.yaml            entry file (title, templates, view includes)
dashboards/mobile/          views: home, rooms + room pages, climate, pets, more/people, more/system
dashboards/templates/       button_cards/ (button-card templates), decluttering/ (decluttering templates),
                            includes/ (card_mod snippets, layouts, navbar)
themes/catppuccin-dashboard/  "Catppuccin Mocha Dashboard" theme used by every view
www/dashboard/              app_icons.js (icon set app:app-*) and fonts.js (Inter)
```

The same YAML is also served as a hidden admin-only dashboard at `/dashboard-source`
(defined in `configuration.yaml`), which is how Home Assistant resolves all the `!include`s.

## Publishing YAML changes to the default dashboard

1. Edit the YAML files.
2. `touch ui-lovelace.yaml` (Home Assistant only re-reads YAML dashboards when the entry file changes).
3. Open `/dashboard-source` once to check it renders.
4. Copy the resolved config to the default dashboard. From a browser console on the HA page:

```js
const hass = document.querySelector('home-assistant').hass;
const cfg = await hass.callWS({ type: 'lovelace/config', url_path: 'dashboard-source', force: true });
await hass.callWS({ type: 'lovelace/config/save', url_path: null, config: cfg });
location.reload();
```

Alternatively open `/dashboard-source`, use the raw configuration editor to copy the YAML,
and paste it into the raw configuration editor of the default dashboard.

Edits made directly in the UI on the default dashboard are **not** written back to these files.

## Conventions

- Templates and icons use the neutral `app_` / `app:` prefix.
- Multi-line JavaScript (`[[[ ... ]]]`) must be a single line when passed as a decluttering variable.
- Every template key must be unique across `templates/button_cards` and `templates/decluttering`
  (`!include_dir_merge_named` silently lets the alphabetically later file win).
- In this repository the person and phone entity ids under `mobile/` are generic placeholders
  (`person.person1`, `device_tracker.person1_phone`, ...); a git clean/smudge filter maps them
  to the real ids on the Home Assistant host.

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
