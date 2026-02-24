import asyncio
import json
import logging
import websockets
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .const import CONF_HOST, CONF_PORT

_LOGGER = logging.getLogger(__name__)


class OpenDTUCoordinator(DataUpdateCoordinator):

    def __init__(self, hass, entry):
        self.host = entry.data[CONF_HOST]
        self.port = entry.data[CONF_PORT]
        self._ws_task = None  # FIX: Task-Referenz

        super().__init__(
            hass,
            _LOGGER,
            name="OpenDTU WebSocket",
        )

        self.data = {}

    async def start(self):
        uri = f"ws://{self.host}:{self.port}/livedata"
        _LOGGER.info("Verbindung zu WebSocket: %s", uri)  # FIX: kein f-String im Logger

        while True:
            try:
                async with websockets.connect(uri) as ws:
                    _LOGGER.info("WebSocket verbunden mit %s", uri)

                    async for msg in ws:
                        raw = json.loads(msg)
                        new_data = self.flatten(raw)

                        if not isinstance(self.data, dict):
                            self.data = {}

                        for key, value in new_data.items():
                            if value.get("value") is not None:
                                self.data[key] = value

                        self.async_set_updated_data(self.data)

            except asyncio.CancelledError:
                # FIX: Sauberes Beenden wenn Task abgebrochen wird
                _LOGGER.info("WebSocket-Task wurde beendet.")
                return
            except Exception as e:
                _LOGGER.error("WebSocket Fehler: %s", e)  # FIX: kein f-String
                await asyncio.sleep(5)

    def flatten(self, data, prefix="", result=None):
        if result is None:
            result = {}

        if isinstance(data, dict):

            if "v" in data:
                result[prefix] = {
                    "value": data["v"],
                    "unit": data.get("u")
                }
                return result

            serial = data.get("serial")
            if serial:
                prefix = f"inverter_{serial}"

            for key, value in data.items():
                if key == "serial":
                    continue

                new_prefix = f"{prefix}_{key}" if prefix else key

                # FIX: Warnung bei Schlüsselkonflikten
                flat_key = new_prefix.lower()
                if flat_key in result:
                    _LOGGER.warning("Schlüsselkonflikt beim Flatten: %s wird überschrieben", flat_key)

                self.flatten(value, new_prefix.lower(), result)

        elif isinstance(data, list):
            for index, item in enumerate(data):
                if isinstance(item, dict) and "serial" in item:
                    self.flatten(item, prefix, result)
                else:
                    new_prefix = f"{prefix}_{index}"
                    self.flatten(item, new_prefix.lower(), result)

        return result
