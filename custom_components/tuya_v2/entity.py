"""Base entity: one per lock, refreshed by the dispatcher signal the Pulsar listener sends."""

from __future__ import annotations

from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import Entity

from . import LockDevice
from .const import DOMAIN, SIGNAL_UPDATE


class TuyaCloudLockEntity(Entity):
    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, device: LockDevice, key: str) -> None:
        self._device = device
        self._attr_unique_id = f"{DOMAIN}_{device.device_id}_{key}"
        self._attr_device_info = device.device_info

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(self.hass, SIGNAL_UPDATE.format(self._device.device_id), self._handle_update)
        )

    @callback
    def _handle_update(self, codes: list[str]) -> None:
        """Called with the DP codes of each report the lock sends; override to react."""
        self.async_write_ha_state()
