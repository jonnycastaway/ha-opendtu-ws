from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .utils import classify, friendly_name
from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    # FIX: Coordinator aus hass.data holen (nicht neu erstellen!)
    coordinator = hass.data[DOMAIN][entry.entry_id]
    created = set()

    def update_entities():
        entities = []
        for key, val in coordinator.data.items():
            if key not in created and isinstance(val.get("value"), bool):
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
        self._attr_name = friendly_name(key)
        _, _, entity_category = classify(key, unit=None, is_bool=True)
        self._attr_entity_category = entity_category
        self._attr_entity_registry_enabled_default = False

    @property
    def is_on(self):
        return self.coordinator.data.get(self.key, {}).get("value", False)

    @property
    def device_info(self):
        key = self.key

        if "total" in key:
            identifier = "total"
            name = "OpenDTU Gesamtanlage"
        elif "inverter_" in key:
            # FIX: sicheres Extrahieren der Serial – kein IndexError mehr
            parts = key.split("_")
            identifier = parts[1] if len(parts) > 1 else "unknown"
            name = f"Inverter {identifier}"
        else:
            identifier = "opendtu"
            name = "OpenDTU"

        return {
            "identifiers": {(DOMAIN, identifier)},
            "name": name,
            "manufacturer": "OpenDTU",
        }
