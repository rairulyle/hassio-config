#!/bin/sh
# Append a friendly-named MQTT climate entity for a Faikin (Daikin) controller to mqtt.yaml.
#
# Usage:  bin/add_faikin_aircon.sh "<Entity name>" <faikin-mqtt-id> <device-id>
# Example: bin/add_faikin_aircon.sh "Bedroom Aircon" bedroom-aircon D4059248ABCD
#
#   <faikin-mqtt-id>  the controller's MQTT id (its topics are state/<id> and command/<id>/...)
#   <device-id>       the hex id in its HA discovery topic homeassistant/climate/<device-id>/config
#
# Afterwards: run the "mqtt.reload" action (Developer Tools > Actions), then
#   1. disable the auto-discovered climate entity for that controller (Settings > Devices),
#   2. rename the new entity id if you want a short one (it defaults to
#      climate.<entity name>_<entity name> because the device carries the same name).
set -e
CONFIG_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATE="$CONFIG_DIR/mqtt_templates/faikin_climate.yaml"
TARGET="$CONFIG_DIR/mqtt.yaml"
NAME="$1"; ID="$2"; UID_="$3"
if [ -z "$NAME" ] || [ -z "$ID" ] || [ -z "$UID_" ]; then
  sed -n '2,13p' "$0"; exit 1
fi
if grep -q "unique_id: faikin_$UID_" "$TARGET" 2>/dev/null; then
  echo "mqtt.yaml already has an entry for device $UID_ - nothing added."; exit 1
fi
sed -e "s|__NAME__|$NAME|g" -e "s|__ID__|$ID|g" -e "s|__UID__|$UID_|g" "$TEMPLATE" >> "$TARGET"
echo "Added '$NAME' ($ID) to $TARGET. Now run the mqtt.reload action in Home Assistant."
