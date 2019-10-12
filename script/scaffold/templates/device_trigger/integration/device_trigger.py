"""Provides device automations for NEW_NAME."""
from typing import List
import voluptuous as vol

from homeassistant.const import (
    CONF_DOMAIN,
    CONF_TYPE,
    CONF_PLATFORM,
    CONF_DEVICE_ID,
    CONF_ENTITY_ID,
    STATE_ON,
    STATE_OFF,
)
from homeassistant.core import HomeAssistant, CALLBACK_TYPE
from homeassistant.helpers import entity_registry
from homeassistant.helpers.typing import ConfigType
from homeassistant.components.automation import state, AutomationActionType
from homeassistant.components.device_automation import TRIGGER_BASE_SCHEMA
from . import DOMAIN

# TODO specify your supported trigger types.
TRIGGER_TYPES = {"turned_on", "turned_off"}

TRIGGER_SCHEMA = TRIGGER_BASE_SCHEMA.extend(
    {vol.Required(CONF_TYPE): vol.In(TRIGGER_TYPES)}
)


async def async_get_triggers(hass: HomeAssistant, device_id: str) -> List[dict]:
    """List device triggers for NEW_NAME devices."""
    registry = await entity_registry.async_get_registry(hass)
    triggers = []

    # TODO Read this comment and remove it.
    # This example shows how to iterate over the entities of this device
    # that match this integration. If your triggers instead rely on
    # events fired by devices without entities, do something like:
    # zha_device = await _async_get_zha_device(hass, device_id)
    # return zha_device.device_triggers

    # Get all the integrations entities for this device
    for entry in entity_registry.async_entries_for_device(registry, device_id):
        if entry.domain != DOMAIN:
            continue

        # Add triggers for each entity that belongs to this integration
        # TODO add your own triggers.
        triggers.append(
            {
                CONF_PLATFORM: "device",
                CONF_DEVICE_ID: device_id,
                CONF_DOMAIN: DOMAIN,
                CONF_ENTITY_ID: entry.entity_id,
                CONF_TYPE: "turned_on",
            }
        )
        triggers.append(
            {
                CONF_PLATFORM: "device",
                CONF_DEVICE_ID: device_id,
                CONF_DOMAIN: DOMAIN,
                CONF_ENTITY_ID: entry.entity_id,
                CONF_TYPE: "turned_off",
            }
        )

    return triggers


async def async_attach_trigger(
    hass: HomeAssistant,
    config: ConfigType,
    action: AutomationActionType,
    automation_info: dict,
) -> CALLBACK_TYPE:
    """Attach a trigger."""
    config = TRIGGER_SCHEMA(config)

    # TODO Implement your own logic to attach triggers.
    # Generally we suggest to re-use the existing state or event
    # triggers from the automation integration.

    if config[CONF_TYPE] == "turned_on":
        from_state = STATE_OFF
        to_state = STATE_ON
    else:
        from_state = STATE_ON
        to_state = STATE_OFF

    return state.async_attach_trigger(
        hass,
        {
            CONF_ENTITY_ID: config[CONF_ENTITY_ID],
            state.CONF_FROM: from_state,
            state.CONF_TO: to_state,
        },
        action,
        automation_info,
        platform_type="device",
    )
