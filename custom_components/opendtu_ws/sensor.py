from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceInfo
from .coordinator import OpenDTUCoordinator
from .utils import classify
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = OpenDTUCoordinator(hass, entry)
    hass.loop.create_task(coordinator.start())
    created = set()
    entities = []

    async def update_entities():
        for key, val in coordinator.data.items():
            if key not in created and isinstance(val["value"], (int, float)):
                entities.append(OpenDTUSensor(coordinator, key))
                created.add(key)
        if entities:
            async_add_entities(entities)

    coordinator.async_add_listener(update_entities)

class OpenDTUSensor(CoordinatorEntity, SensorEntity):

    def __init__(self, coordinator, key):
        super().__init__(coordinator)
        self.key = key
        self._attr_unique_id = f"opendtu_{key}"
        self._attr_name = f"OpenDTU {key.replace('_', ' ')}"
        unit = coordinator.data[key]["unit"]
        device_class, state_class, entity_category = classify(key, unit)
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_entity_category = entity_category

        # Aktiv nur für relevante Werte (Power/Energy/Voltage/Current/Temperature)
        self._attr_entity_registry_enabled_default = device_class is not None or state_class is not None

    @property
    def native_value(self):
        return self.coordinator.data[self.key]["value"]

    @property
    def device_info(self):
        if "total" in self.key:
            identifier = "total"
            name = "OpenDTU Gesamtanlage"
        elif "inverters_" in self.key:
            identifier = self.key.split("_")[2]
            name = f"Inverter {identifier}"
        else:
            identifier = "opendtu"
            name = "OpenDTU"
        return DeviceInfo(
            identifiers={(DOMAIN, identifier)},
            name=name,
            manufacturer="OpenDTU",
        )
