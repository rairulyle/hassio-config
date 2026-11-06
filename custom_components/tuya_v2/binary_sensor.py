"""Binary sensor: the bell key on the keypad (a short pulse per press)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOORBELL_HOLD_SECONDS, DP_DOORBELL
from .entity import TuyaCloudLockEntity

if TYPE_CHECKING:
    from . import TuyaCloudLockConfigEntry


async def async_setup_entry(
    hass: HomeAssistant, entry: TuyaCloudLockConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    async_add_entities(DoorbellSensor(device) for device in entry.runtime_data.locks.values())


class DoorbellSensor(TuyaCloudLockEntity, BinarySensorEntity):
    """On for a few seconds each time the bell key on the keypad is pressed."""

    _attr_name = "Doorbell"
    _attr_icon = "mdi:bell-ring"
    _attr_is_on = False

    def __init__(self, device) -> None:
        super().__init__(device, "doorbell")
        self._off_cancel = None

    @callback
    def _handle_update(self, codes: list[str]) -> None:
        if DP_DOORBELL in codes and self._device.dps.get(DP_DOORBELL):
            self._attr_is_on = True
            if self._off_cancel:
                self._off_cancel()
            self._off_cancel = async_call_later(self.hass, DOORBELL_HOLD_SECONDS, self._turn_off)
        self.async_write_ha_state()

    @callback
    def _turn_off(self, _now) -> None:
        self._off_cancel = None
        self._attr_is_on = False
        self.async_write_ha_state()
