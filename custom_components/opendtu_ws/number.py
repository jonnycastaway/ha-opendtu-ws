import aiohttp
import logging
from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from .const import DOMAIN, CONF_HOST, CONF_PORT

_LOGGER = logging.getLogger(__name__)

# 4 Limit-Entitäten pro Inverter
# limit_type gemäß OpenDTU API (aus ActivePowerControlCommand.h):
#   0 = relativ,  nicht-persistent (temporär, wird bei WR-Neustart zurückgesetzt)
#   1 = relativ,  persistent       (permanent, bleibt nach WR-Neustart erhalten)
#   2 = absolut,  nicht-persistent (temporär, wird bei WR-Neustart zurückgesetzt)
#   3 = absolut,  persistent       (permanent, bleibt nach WR-Neustart erhalten)
# limit_type gemäß OpenDTU API (verifiziert):
#   0 = Watt,  temporär
#   1 = %,     temporär
#   2 = Watt,  permanent
#   3 = %,     permanent
LIMIT_CONFIGS = [
    {
        "suffix":     "limit_relative_temporary",
        "source_key": "limit_relative",
        "name":       "Limit relativ (temporär)",
        "unit":       "%",
        "min":        2,
        "max":        100,
        "step":       1,
        "limit_type": 1,
    },
    {
        "suffix":     "limit_relative_persistent",
        "source_key": "limit_relative",
        "name":       "Limit relativ (permanent)",
        "unit":       "%",
        "min":        2,
        "max":        100,
        "step":       1,
        "limit_type": 3,
    },
    {
        "suffix":     "limit_absolute_temporary",
        "source_key": "limit_absolute",
        "name":       "Limit absolut (temporär)",
        "unit":       "W",
        "min":        0,
        "max":        99999,
        "step":       1,
        "limit_type": 0,
    },
    {
        "suffix":     "limit_absolute_persistent",
        "source_key": "limit_absolute",
        "name":       "Limit absolut (permanent)",
        "unit":       "W",
        "min":        0,
        "max":        99999,
        "step":       1,
        "limit_type": 2,
    },
]


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    created_serials = set()

    def update_entities():
        entities = []

        for key in coordinator.data.keys():
            if not key.startswith("inverter_"):
                continue
            if not (key.endswith("_limit_relative") or key.endswith("_limit_absolute")):
                continue

            serial = _extract_serial(key)
            if not serial or serial in created_serials:
                continue

            for config in LIMIT_CONFIGS:
                entities.append(OpenDTULimitNumber(coordinator, entry, serial, config))
            created_serials.add(serial)

        if entities:
            async_add_entities(entities)

    coordinator.async_add_listener(update_entities)


def _extract_serial(key: str) -> str | None:
    """Extrahiert die Seriennummer aus 'inverter_<serial>_limit_*'."""
    parts = key.split("_")
    if len(parts) >= 3:
        return parts[1]
    return None


class OpenDTULimitNumber(CoordinatorEntity, NumberEntity):

    def __init__(self, coordinator, entry, serial, config):
        super().__init__(coordinator)
        self._serial = serial
        self._config = config
        self._host = entry.data[CONF_HOST]
        self._port = entry.data[CONF_PORT]
        self._username = entry.data.get(CONF_USERNAME, "admin")
        self._password = entry.data.get(CONF_PASSWORD, "")
        self._source_key = f"inverter_{serial}_{config['source_key']}"

        self._attr_unique_id = f"{entry.entry_id}_{serial}_{config['suffix']}"
        self._attr_name = config["name"]
        self._attr_native_unit_of_measurement = config["unit"]
        self._attr_native_min_value = config["min"]
        self._attr_native_max_value = config["max"]
        self._attr_native_step = config["step"]
        self._attr_mode = NumberMode.BOX

    @property
    def native_value(self):
        return self.coordinator.data.get(self._source_key, {}).get("value")

    async def async_set_native_value(self, value: float) -> None:
        url = f"http://{self._host}:{self._port}/api/limit/config"
        payload = {
            "serial": self._serial,
            "limit_type": self._config["limit_type"],
            "limit_value": int(value),
        }
        _LOGGER.debug(
            "Sende Limit-Request: URL=%s | Payload=%s | limit_type=%s",
            url, payload, self._config["limit_type"]
        )
        try:
            async with aiohttp.ClientSession() as session:
                auth = aiohttp.BasicAuth(self._username, self._password)
                import json as _json
                form = aiohttp.FormData()
                form.add_field("data", _json.dumps(payload))
                async with session.post(
                    url,
                    data=form,
                    auth=auth,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    result = await resp.json()
                    _LOGGER.debug("Limit-Response: %s", result)
                    if result.get("type") == "success":
                        _LOGGER.info(
                            "Limit gesetzt (%s, type=%s): %s %s",
                            self._serial, self._config["limit_type"],
                            value, self._config["unit"],
                        )
                    else:
                        _LOGGER.error("Fehler beim Setzen des Limits: %s", result)
        except Exception as e:
            _LOGGER.error("HTTP-Fehler beim Setzen des Limits (%s): %s", self._source_key, e)

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self._serial)},
            name=f"Inverter {self._serial}",
            manufacturer="OpenDTU",
        )
