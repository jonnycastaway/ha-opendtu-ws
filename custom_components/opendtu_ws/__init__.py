from .const import DOMAIN
from .coordinator import OpenDTUCoordinator

PLATFORMS = ["sensor", "binary_sensor", "number"]  # FIX: binary_sensor ergänzt


async def async_setup_entry(hass, entry):
    coordinator = OpenDTUCoordinator(hass, entry)

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # WebSocket im Hintergrund starten – asyncio.ensure_future() verhindert
    # dass HA den Task beim Bootstrap trackt und in einen Timeout läuft
    import asyncio
    task = asyncio.ensure_future(coordinator.start())
    coordinator._ws_task = task

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass, entry):
    coordinator = hass.data[DOMAIN].get(entry.entry_id)

    # FIX: WebSocket-Task sauber abbrechen
    if coordinator and hasattr(coordinator, "_ws_task"):
        coordinator._ws_task.cancel()
        try:
            await coordinator._ws_task
        except Exception:
            pass

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
