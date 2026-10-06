# Home Assistant Configuration

Konnichiwassup! These are the configuration files behind my personal Home Assistant setup:
a YAML-defined mobile dashboard built on button-card / decluttering-card templates, a
Catppuccin Mocha theme, and the automations, scripts and MQTT entities that run the house.
Hopefully it gives you some ideas for your own configuration.

## Preview

| Overview | Master Bedroom |
| --- | --- |
| ![Overview](preview/overview.png) | ![Master Bedroom](preview/master_bedroom.png) |

## Dashboard

The default dashboard runs in UI/storage mode but is generated from the YAML under
[`dashboards/`](dashboards/). See [dashboards/README.md](dashboards/README.md) for the
structure, the publish workflow and the conventions used.

```
ui-lovelace.yaml              entry file (title, template includes, views)
dashboards/mobile/            views: home, rooms + room pages, climate, pets, people, system
dashboards/templates/         button_cards/, decluttering/, includes/ (card_mod, layouts, navbar)
themes/catppuccin-dashboard/  "Catppuccin Mocha Dashboard" theme
www/dashboard/                app_icons.js (custom icon set `app:`) and fonts.js (Inter)
```

HACS frontend plugins used: button-card, decluttering-card, stack-in-card, layout-card,
navbar-card, mini-graph-card, card-mod, Bubble Card, upcoming-media-card.

## Integrations & helpers

| File | Purpose |
| --- | --- |
| `configuration.yaml` | Core setup, theme/frontend options, hidden YAML source dashboard |
| `automations.yaml`, `scripts.yaml` | Pet feeding schedule, spoken reminders and greetings, theme switch |
| `mqtt.yaml`, `mqtt_templates/`, `bin/add_faikin_aircon.sh` | Hand-written MQTT climate entities for Faikin (Daikin) aircon controllers |
| `light.yaml` | Light groups (e.g. `light.all_lights`) |
| `rest.yaml`, `rest_command.yaml`, `switch.yaml` | Speedtest sensors, UpSnap wake-on-LAN, PC switches |
| `xiaomi.yaml` | Xiaomi MIoT translations |

Hosts, MAC addresses, URLs and tokens live in `secrets.yaml` (not committed). Discord ids in
`automations.yaml` are replaced with placeholders in this repository.

## Credits

- Dashboard structure and templates adapted from [johnkoht/hassio-config](https://github.com/johnkoht/hassio-config).
- Colours from [Catppuccin](https://github.com/catppuccin/home-assistant).
