import asyncio
import json
import websockets
import logging
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .const import CONF_HOST, CONF_PORT

_LOGGER = logging.getLogger(__name__)

class OpenDTUCoordinator(DataUpdateCoordinator):

    def __init__(self, hass, entry):
        self.host = entry.data[CONF_HOST]
        self.port = entry.data[CONF_PORT]
        self.data = {}
        super().__init__(hass, logger=None, name="OpenDTU")

    async def _async_update_data(self):
        return self.data

    async def start(self):
        uri = f"ws://{self.host}:{self.port}/livedata"
        _LOGGER.info(f"Verbindung zu WebSocket: {uri}")

        while True:
            try:
                async with websockets.connect(uri) as ws:
                    _LOGGER.info(f"WebSocket verbunden mit {uri}")
                    async for msg in ws:
                        _LOGGER.debug(f"Empfangene Nachricht: {msg}")
                        try:
                            raw = json.loads(msg)
                            _LOGGER.debug(f"Parsed JSON: {raw}")
                            self.data = self.flatten(raw)
                            _LOGGER.debug(f"Flattened Data: {self.data}")
                            self.async_set_updated_data(self.data)
                        except json.JSONDecodeError as e:
                            _LOGGER.error(f"JSON Fehler: {e}")
            except Exception as e:
                _LOGGER.error(f"Fehler bei WebSocket-Verbindung: {e}")
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
