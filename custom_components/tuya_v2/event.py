"""Event entities: every unlock (how, and which key/user id) and every alarm the lock raises."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.event import EventEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import ALARM_TYPES, DP_ALARM, DP_UNLOCK_CODES
from .entity import TuyaCloudLockEntity

if TYPE_CHECKING:
    from . import TuyaCloudLockConfigEntry


async def async_setup_entry(
    hass: HomeAssistant, entry: TuyaCloudLockConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    entities = []
    for device in entry.runtime_data.locks.values():
        entities += [UnlockEvent(device), AlarmEvent(device)]
    async_add_entities(entities)


class UnlockEvent(TuyaCloudLockEntity, EventEntity):
    """Fires once per unlock; event_type is the method, 'id' the key/user id on the lock."""

    _attr_name = "Unlock"
    _attr_icon = "mdi:lock-open-check"
    _attr_event_types = list(DP_UNLOCK_CODES.values())

    def __init__(self, device) -> None:
        super().__init__(device, "unlock")

    @callback
    def _handle_update(self, codes: list[str]) -> None:
        for code in codes:
            if code in DP_UNLOCK_CODES:
                self._trigger_event(DP_UNLOCK_CODES[code], {"id": self._device.dps.get(code)})
                self.async_write_ha_state()


class AlarmEvent(TuyaCloudLockEntity, EventEntity):
    _attr_name = "Alarm"
    _attr_icon = "mdi:shield-alert"
    _attr_event_types = ALARM_TYPES

    def __init__(self, device) -> None:
        super().__init__(device, "alarm")

    @callback
    def _handle_update(self, codes: list[str]) -> None:
        if DP_ALARM in codes and self._device.dps.get(DP_ALARM) in ALARM_TYPES:
            self._trigger_event(self._device.dps[DP_ALARM])
            self.async_write_ha_state()
