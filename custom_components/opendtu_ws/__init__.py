from .const import DOMAIN
from .coordinator import OpenDTUCoordinator

PLATFORMS = ["sensor"]

async def async_setup_entry(hass, entry):
    coordinator = OpenDTUCoordinator(hass, entry)

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # WebSocket im Hintergrund starten (NICHT awaiten!)
    hass.async_create_task(coordinator.start())

    # Plattformen laden (Plural!)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass, entry):
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
