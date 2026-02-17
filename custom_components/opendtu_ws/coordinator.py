import asyncio
import json
import websockets
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .const import CONF_HOST, CONF_PORT

class OpenDTUCoordinator(DataUpdateCoordinator):

    def __init__(self, hass, entry):
        self.host = entry.data[CONF_HOST]
        self.port = entry.data[CONF_PORT]
        self.data = {}
        super().__init__(hass, logger=None, name="OpenDTU")

    async def _async_update_data(self):
        return self.data

    async def start(self):
        # WebSocket URI auf "/livedata" setzen
        uri = f"ws://{self.host}:{self.port}/livedata"

        while True:
            try:
                async with websockets.connect(uri) as ws:
                    async for msg in ws:
                        raw = json.loads(msg)
                        self.data = self.flatten(raw)
                        self.async_set_updated_data(self.data)
            except Exception as e:
                # Fehlerbehandlung, wenn die Verbindung fehlschlägt
                _LOGGER.error(f"WebSocket Fehler: {e}")
                await asyncio.sleep(5)

    def flatten(self, data, prefix="", result=None):
        if result is None:
            result = {}

        if isinstance(data, dict):
            if "v" in data and isinstance(data["v"], (int, float, bool)):
                result[prefix] = {"value": data["v"], "unit": data.get("u")}
            else:
                for key, value in data.items():
                    new_prefix = f"{prefix}_{key}" if prefix else key
                    self.flatten(value, new_prefix.lower(), result)
        elif isinstance(data, (int, float, bool)):
            result[prefix] = {"value": data, "unit": None}

        return result
