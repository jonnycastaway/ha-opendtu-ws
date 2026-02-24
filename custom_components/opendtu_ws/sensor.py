from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceInfo
from .const import DOMAIN
from .utils import classify, friendly_name


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = {}

    def _update():
        if not coordinator.data:
            return

        new_entities = []

        for key in coordinator.data.keys():
            if key not in entities:
                # FIX: entry.entry_id in unique_id einbauen → keine Kollisionen bei mehreren Instanzen
                entity = OpenDTUSensor(coordinator, entry.entry_id, key)
                entities[key] = entity
                new_entities.append(entity)

        if new_entities:
            async_add_entities(new_entities)

    coordinator.async_add_listener(_update)


class OpenDTUSensor(CoordinatorEntity, SensorEntity):

    def __init__(self, coordinator, entry_id, key):
        super().__init__(coordinator)
        self._key = key
        self._entry_id = entry_id

        # FIX: entry_id als Teil der unique_id verhindert Kollisionen
        self._attr_unique_id = f"{entry_id}_{key}"
        self._attr_name = friendly_name(key)

        unit = coordinator.data.get(key, {}).get("unit")
        self._attr_native_unit_of_measurement = unit

        device_class, state_class, entity_category = classify(key, unit=unit)
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_entity_category = entity_category

    @property
    def native_value(self):
        return self.coordinator.data.get(self._key, {}).get("value")

    @property
    def device_info(self):
        key = self._key

        if "inverter_" in key:
            # Inverter-Seriennummer ist global eindeutig – kein Entry-ID-Prefix nötig
            parts = key.split("_")
            identifier = parts[1] if len(parts) > 1 else "unknown"
            name = f"Inverter {identifier}"
        elif "total" in key:
            # FIX: Entry-ID einbauen damit mehrere OpenDTU-Instanzen eigene Geräte haben
            identifier = f"{self._entry_id}_total"
            name = "OpenDTU Gesamtanlage"
        else:
            # hints_* und sonstige Keys → gehören zum OpenDTU-Gerät der jeweiligen Instanz
            identifier = f"{self._entry_id}_opendtu"
            name = "OpenDTU"

        return DeviceInfo(
            identifiers={(DOMAIN, identifier)},
            name=name,
            manufacturer="OpenDTU",
        )
