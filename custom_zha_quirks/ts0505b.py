"""Moes ZB-TDA9-RCW-E27-MS - Tuya TS0505B RGB+CCT bulb."""

from typing import Any, Final

import zigpy.types as t
from zigpy.zcl.clusters.lighting import Color
from zigpy.zcl.foundation import BaseAttributeDefs, ZCLAttributeDef, ZCLCommandDef

from zhaquirks import LocalDataCluster
from zhaquirks.builder import QuirkBuilder
from zhaquirks.clusters import CustomCluster


class TuyaColorPowerOn(t.enum8):
    """Color and brightness to use when power comes back."""

    Initial = 0x00
    Previous = 0x01


class TuyaLightColorCluster(CustomCluster, Color):
    """Color cluster with the Tuya startup commands (as used by Z2M)."""

    class ServerCommandDefs(Color.ServerCommandDefs):
        """Server command definitions."""

        tuya_on_start_up: Final = ZCLCommandDef(
            id=0xF9,
            schema={"mode": t.uint16_t, "data": t.List[t.uint8_t]},
            is_manufacturer_specific=False,
        )
        tuya_do_not_disturb: Final = ZCLCommandDef(
            id=0xFA,
            schema={"enable": t.uint8_t},
            is_manufacturer_specific=False,
        )


class TuyaLightConfigCluster(LocalDataCluster):
    """Local cluster holding the write-only Tuya startup settings."""

    cluster_id = 0xFBFE
    ep_attribute = "tuya_light_config"

    class AttributeDefs(BaseAttributeDefs):
        """Attribute definitions."""

        power_outage_memory: Final = ZCLAttributeDef(id=0x0000, type=t.Bool)
        color_power_on: Final = ZCLAttributeDef(id=0x0001, type=TuyaColorPowerOn)

    _DEFAULT_VALUES = {
        AttributeDefs.power_outage_memory.id: t.Bool.false,
        AttributeDefs.color_power_on.id: TuyaColorPowerOn.Initial,
    }

    async def write_attributes(
        self,
        attributes: dict[str | int | ZCLAttributeDef, Any],
        **kwargs,
    ) -> list:
        """Send the matching Tuya command, then cache the value locally."""
        color = self.endpoint.light_color

        for attr, value in attributes.items():
            attr_id = self.find_attribute(attr).id
            if attr_id == self.AttributeDefs.power_outage_memory.id:
                # "Do not disturb": off = always turn on, on = restore last on/off
                await color.tuya_do_not_disturb(enable=int(bool(value)))
            elif attr_id == self.AttributeDefs.color_power_on.id:
                await color.tuya_on_start_up(mode=int(value) << 8, data=[0] * 10)

        return await super().write_attributes(attributes, **kwargs)


(
    QuirkBuilder("_TZ3210_wxa85bwk", "TS0505B")
    .friendly_name(manufacturer="Moes", model="ZB-TDA9-RCW-E27-MS")
    .replaces(TuyaLightColorCluster)
    .adds(TuyaLightConfigCluster)
    .switch(
        TuyaLightConfigCluster.AttributeDefs.power_outage_memory.name,
        TuyaLightConfigCluster.cluster_id,
        translation_key="power_outage_memory",
        fallback_name="Power outage memory",
    )
    .enum(
        TuyaLightConfigCluster.AttributeDefs.color_power_on.name,
        TuyaColorPowerOn,
        TuyaLightConfigCluster.cluster_id,
        translation_key="color_power_on",
        fallback_name="Power-on color",
    )
    .add_to_registry()
)
