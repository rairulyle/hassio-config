"""Config flow: import-only. The integration is configured in configuration.yaml and the
YAML is imported into a single config entry so entities can belong to a device."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_CLIENT_ID

from .const import DOMAIN


class TuyaCloudLockConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_import(self, import_data: dict[str, Any]) -> ConfigFlowResult:
        await self.async_set_unique_id(import_data[CONF_CLIENT_ID])
        self._abort_if_unique_id_configured(updates=import_data)
        return self.async_create_entry(title="Tuya Cloud Lock", data=import_data)
