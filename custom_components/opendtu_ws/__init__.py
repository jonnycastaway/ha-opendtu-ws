import asyncio
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
import websockets
import json
import logging

_LOGGER = logging.getLogger(__name__)

class OpenDTUCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry):
        self.host = entry.data["host"]
        self.port = entry.data["port"]
        self.data = {}
        super().__init__(hass, logger=None, name="OpenDTU")

    async def _async_update_data(self):
        return self.data

    async def start(self):
        uri = f"ws://{self.host}:{self.port}/livedata"
        while True:
            try:
                async with websockets.connect(uri) as ws:
                    async for msg in ws:
                        raw = json.loads(msg)
                        self.data = self.flatten(raw)
                        self.async_set_updated_data(self.data)
            except Exception as e:
                _LOGGER.error(f"Fehler bei der WebSocket-Verbindung: {e}")
                await asyncio.sleep(5)

    def flatten(self, data, prefix="", result=None):
        if result is None:
            result = {}
        if "inverters" in data:
            for inverter in data["inverters"]:
                inverter_serial = inverter["serial"]
                if "AC" in inverter:
                    for ac_key, ac_value in inverter["AC"].items():
                        for sensor_key, sensor_data in ac_value.items():
                            if "v" in sensor_data:
                                new_key = f"ac_{inverter_serial}_{ac_key}_{sensor_key}"
                                result[f"{prefix}_{new_key}"] = {
                                    "value": sensor_data["v"],
                                    "unit": sensor_data["u"]
                                }
                if "DC" in inverter:
                    for dc_key, dc_value in inverter["DC"].items():
                        for sensor_key, sensor_data in dc_value.items():
                            if "v" in sensor_data:
                                new_key = f"dc_{inverter_serial}_{dc_key}_{sensor_key}"
                                result[f"{prefix}_{new_key}"] = {
                                    "value": sensor_data["v"],
                                    "unit": sensor_data["u"]
                                }
        if "total" in data:
            for key, value in data["total"].items():
                if "v" in value:
                    result[f"{prefix}_total_{key}"] = {
                        "value": value["v"],
                        "unit": value["u"]
                    }
        return result
    