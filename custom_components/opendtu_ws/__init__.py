from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from . import config_flow

async def async_setup(hass: HomeAssistant, config: dict):
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    return True
