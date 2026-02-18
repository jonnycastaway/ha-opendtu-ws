from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceInfo
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = {}

    def _update():
        if not coordinator.data:
            return

        new_entities = []

        for key in coordinator.data.keys():
            if key not in entities:
                entity = OpenDTUSensor(coordinator, key)
                entities[key] = entity
                new_entities.append(entity)

        if new_entities:
            async_add_entities(new_entities)

    coordinator.async_add_listener(_update)


class OpenDTUSensor(CoordinatorEntity, SensorEntity):

    def __init__(self, coordinator, key):
        super().__init__(coordinator)
        self._key = key

        self._attr_unique_id = f"opendtu_{key}"
        self._attr_name = f"OpenDTU {key}"

        unit = coordinator.data.get(key, {}).get("unit")
        self._attr_native_unit_of_measurement = unit

    @property
    def native_value(self):
        return self.coordinator.data.get(self._key, {}).get("value")

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, "opendtu")},
            name="OpenDTU",
            manufacturer="OpenDTU",
        )
