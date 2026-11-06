"""Tuya Cloud Lock: a Wi-Fi low-power Tuya lock (category jtmspro) through the Tuya cloud.

The lock sleeps and only connects to the cloud when woken (a key press, the bell key, an unlock),
so LocalTuya cannot reach it and it has no Bluetooth. The Tuya message service (Pulsar) delivers
what it reports while awake: every unlock and who made it, the bell key, alarms, battery.

Status only, nothing can be driven from here: the lock's remote unlock only works in the short
window its own bell key opens, which is not used. The lock has no locked/unlocked DP, so
sensor.<name> derives its state: "unlocked" for auto_lock_seconds after any unlock report, "open"
while gate_sensor (a Frigate state classifier watching the gate) says the gate is open, "jammed"
after a bolt alarm, "locked" otherwise.

Configured in configuration.yaml (imported into a config entry on startup, and re-imported
whenever the YAML changes):
  tuya_v2:
    client_id: !secret tuya_client_id
    client_secret: !secret tuya_client_secret
    region: us
    locks:
      - device_id: eb9e2652d395294ebbtv9e
        name: Pedestrian Gate
        gate_sensor: sensor.porch_main_door_camera_pedestrian_gate_classification  # optional
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field

import voluptuous as vol

from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import CONF_CLIENT_ID, CONF_CLIENT_SECRET, CONF_NAME, CONF_REGION, Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.typing import ConfigType

from .api import TuyaApiError, TuyaOpenApi, TuyaPulsar
from .const import (
    CONF_AUTO_LOCK_SECONDS,
    CONF_DEVICE_ID,
    CONF_GATE_SENSOR,
    CONF_LOCKS,
    DOMAIN,
    SIGNAL_UPDATE,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.EVENT]

LOCK_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_DEVICE_ID): cv.string,
        vol.Required(CONF_NAME): cv.string,
        vol.Optional(CONF_AUTO_LOCK_SECONDS, default=5): cv.positive_int,
        vol.Optional(CONF_GATE_SENSOR): cv.entity_id,
    }
)
CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_CLIENT_ID): cv.string,
                vol.Required(CONF_CLIENT_SECRET): cv.string,
                vol.Optional(CONF_REGION, default="us"): vol.In(["us", "eu", "cn", "in"]),
                vol.Required(CONF_LOCKS): vol.All(cv.ensure_list, [LOCK_SCHEMA]),
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

type TuyaCloudLockConfigEntry = ConfigEntry[TuyaCloudLockData]


@dataclass
class LockDevice:
    """One lock: its config, last known DP values and the time each DP last arrived."""

    device_id: str
    name: str
    auto_lock_seconds: int
    gate_sensor: str | None
    api: TuyaOpenApi
    product_name: str = ""
    dps: dict[str, object] = field(default_factory=dict)
    dp_times: dict[str, float] = field(default_factory=dict)

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.device_id)},
            name=self.name,
            manufacturer="Tuya",
            model=self.product_name or "Wi-Fi lock",
        )

    @callback
    def handle_status(self, status: list[dict]) -> list[str]:
        """Apply a status report from the cloud; returns the DP codes it carried."""
        codes = []
        for item in status:
            code, value = item.get("code"), item.get("value")
            if code is None:
                continue
            self.dps[code] = value
            self.dp_times[code] = time.monotonic()
            codes.append(code)
        return codes


@dataclass
class TuyaCloudLockData:
    api: TuyaOpenApi
    pulsar: TuyaPulsar
    locks: dict[str, LockDevice]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Import the YAML block into the config entry (creating or updating it)."""
    if DOMAIN in config:
        hass.async_create_task(
            hass.config_entries.flow.async_init(DOMAIN, context={"source": SOURCE_IMPORT}, data=config[DOMAIN])
        )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: TuyaCloudLockConfigEntry) -> bool:
    conf = entry.data
    session = async_get_clientsession(hass)
    api = TuyaOpenApi(session, conf[CONF_CLIENT_ID], conf[CONF_CLIENT_SECRET], conf[CONF_REGION])

    locks: dict[str, LockDevice] = {}
    for lock_conf in conf[CONF_LOCKS]:
        device = LockDevice(
            lock_conf[CONF_DEVICE_ID], lock_conf[CONF_NAME], lock_conf[CONF_AUTO_LOCK_SECONDS],
            lock_conf.get(CONF_GATE_SENSOR), api,
        )
        try:
            info = await api.get_device(device.device_id)
            device.product_name = info.get("product_name", "")
            device.handle_status(info.get("status", []))
        except TuyaApiError as err:
            _LOGGER.warning("Could not read %s from the Tuya cloud at startup: %s", device.name, err)
        locks[device.device_id] = device

    @callback
    def on_message(data: dict) -> None:
        device = locks.get(data.get("devId", ""))
        if device is None:
            return
        status = data.get("status")
        if status:
            codes = device.handle_status(status)
            _LOGGER.debug("%s reported %s", device.name, {c: device.dps[c] for c in codes})
            async_dispatcher_send(hass, SIGNAL_UPDATE.format(device.device_id), codes)
        elif data.get("bizCode") in ("online", "offline"):
            _LOGGER.debug("%s is %s", device.name, data["bizCode"])

    pulsar = TuyaPulsar(session, conf[CONF_CLIENT_ID], conf[CONF_CLIENT_SECRET], conf[CONF_REGION], on_message)
    pulsar.start()
    entry.async_on_unload(pulsar.stop)
    entry.async_on_unload(entry.add_update_listener(_async_reload))

    entry.runtime_data = TuyaCloudLockData(api, pulsar, locks)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: TuyaCloudLockConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_reload(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """The YAML changed and was re-imported: restart the entry with the new data."""
    await hass.config_entries.async_reload(entry.entry_id)
