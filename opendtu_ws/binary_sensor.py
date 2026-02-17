from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .coordinator import OpenDTUCoordinator
from .utils import classify
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = OpenDTUCoordinator(hass, entry)
    created = set()
    entities = []

    async def update_entities():
        for key, val in coordinator.data.items():
            if key not in created and isinstance(val["value"], bool):
                entities.append(OpenDTUBinarySensor(coordinator, key))
                created.add(key)
        if entities:
            async_add_entities(entities)

    coordinator.async_add_listener(update_entities)

class OpenDTUBinarySensor(CoordinatorEntity, BinarySensorEntity):

    def __init__(self, coordinator, key):
        super().__init__(coordinator)
        self.key = key
        self._attr_unique_id = f"opendtu_{key}"
        self._attr_name = f"OpenDTU {key.replace('_', ' ')}"
        _, _, entity_category = classify(key, unit=None, is_bool=True)
        self._attr_entity_category = entity_category
        self._attr_entity_registry_enabled_default = False  # Diagnostik/Status standardmäßig deaktiviert

    @property
    def is_on(self):
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
        return {"identifiers": {(DOMAIN, identifier)}, "name": name, "manufacturer": "OpenDTU"}
