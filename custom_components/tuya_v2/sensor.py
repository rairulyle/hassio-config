"""Sensors: the gate's state (locked / unlocked / open / jammed) and the battery.

The lock has no locked/unlocked DP and cannot be driven from here (its remote unlock only works in
the short window its own bell key opens), so the state is a read-only sensor derived from:

* every unlock the lock reports (fingerprint, code, card, app, inside handle): the bolt springs back
  after a few seconds, so "unlocked" for auto_lock_seconds after any of them;
* the optional gate sensor (a Frigate state classifier on the camera that sees the gate leaf):
  "open" while the leaf is open;
* a bolt alarm from the lock (the tongue did not come out): "jammed" until the next unlock.

A closed gate with the bolt out and no bolt alarm is "locked".
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.const import PERCENTAGE, STATE_UNAVAILABLE, STATE_UNKNOWN, EntityCategory
from homeassistant.core import Event, EventStateChangedData, HomeAssistant, callback
from homeassistant.helpers.event import async_call_later, async_track_state_change_event
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import DP_ALARM, DP_BATTERY, DP_UNLOCK_CODES, JAMMED_ALARMS
from .entity import TuyaCloudLockEntity

if TYPE_CHECKING:
    from . import TuyaCloudLockConfigEntry

_LOGGER = logging.getLogger(__name__)

LOCKED, UNLOCKED, OPEN, JAMMED = "locked", "unlocked", "open", "jammed"
GATE_OPEN, GATE_CLOSED = "open", "closed"
ATTR_GATE = "gate"
ICONS = {LOCKED: "mdi:lock", UNLOCKED: "mdi:lock-open-variant", OPEN: "mdi:gate-open", JAMMED: "mdi:lock-alert"}


async def async_setup_entry(
    hass: HomeAssistant, entry: TuyaCloudLockConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    entities = []
    for device in entry.runtime_data.locks.values():
        entities += [GateStateSensor(device), BatterySensor(device)]
    async_add_entities(entities)


class GateStateSensor(TuyaCloudLockEntity, RestoreEntity, SensorEntity):
    """Read-only state of the gate: locked, unlocked, open or jammed (see the module docstring)."""

    _attr_name = None  # takes the device name: sensor.<device>
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = [LOCKED, UNLOCKED, OPEN, JAMMED]

    def __init__(self, device) -> None:
        super().__init__(device, "state")
        self._bolt_locked = True
        self._jammed = False
        self._gate: str | None = None  # last confirmed gate position from the gate sensor
        self._relock_cancel = None

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        if (last := await self.async_get_last_state()) and last.attributes.get(ATTR_GATE) in (GATE_OPEN, GATE_CLOSED):
            self._gate = last.attributes[ATTR_GATE]  # the Frigate sensor does not survive a restart; we do
        if sensor := self._device.gate_sensor:
            self._set_gate(self.hass.states.get(sensor))
            self.async_on_remove(async_track_state_change_event(self.hass, sensor, self._gate_changed))

    @property
    def native_value(self) -> str:
        if self._gate == GATE_OPEN:
            return OPEN
        if self._jammed:
            return JAMMED
        return LOCKED if self._bolt_locked else UNLOCKED

    @property
    def icon(self) -> str:
        return ICONS[self.native_value]

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {ATTR_GATE: self._gate}

    @callback
    def _gate_changed(self, event: Event[EventStateChangedData]) -> None:
        self._set_gate(event.data["new_state"])
        self.async_write_ha_state()

    def _set_gate(self, state) -> None:
        """Only "open" and "closed" are positions; "unknown" (someone in the crop, or the
        Frigate sensor fresh after a restart) and unavailable keep the last confirmed one."""
        value = state.state.lower() if state else STATE_UNKNOWN
        if value in (GATE_OPEN, GATE_CLOSED):
            self._gate = value
        elif value not in (STATE_UNKNOWN, STATE_UNAVAILABLE):
            _LOGGER.warning("%s is not a gate position, expected open/closed", state.state)

    @callback
    def _handle_update(self, codes: list[str]) -> None:
        if any(code in DP_UNLOCK_CODES for code in codes):
            self._jammed = False
            self._bolt_locked = False
            if self._relock_cancel:
                self._relock_cancel()
            self._relock_cancel = async_call_later(self.hass, self._device.auto_lock_seconds, self._relock)
        if DP_ALARM in codes and self._device.dps.get(DP_ALARM) in JAMMED_ALARMS:
            self._jammed = True
        self.async_write_ha_state()

    @callback
    def _relock(self, _now) -> None:
        self._relock_cancel = None
        self._bolt_locked = True
        self.async_write_ha_state()


class BatterySensor(TuyaCloudLockEntity, SensorEntity):
    _attr_name = "Battery"
    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, device) -> None:
        super().__init__(device, "battery")

    @property
    def native_value(self) -> int | None:
        value = self._device.dps.get(DP_BATTERY)
        return int(value) if value is not None else None
