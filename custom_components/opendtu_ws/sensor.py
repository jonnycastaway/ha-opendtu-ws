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

        # Iteriere über jedes Inverter in den koordinierten Daten
        for inverter in coordinator.data.get("inverters", []):
            inverter_serial = inverter.get("serial", "unknown")
            inverter_name = inverter.get("name", "unknown")

            # Erstelle Entitäten für jedes Inverter
            for key, value in inverter.get("AC", {}).items():
                # Erstelle Sensor-Entitäten für AC-Werte (Power, Voltage, Current, etc.)
                for sensor_key, sensor_value in value.items():
                    entity = OpenDTUSensor(coordinator, inverter_serial, f"{inverter_name}_AC_{key}_{sensor_key}", sensor_value)
                    if entity.unique_id not in entities:
                        entities[entity.unique_id] = entity
                        new_entities.append(entity)

            for key, value in inverter.get("DC", {}).items():
                # Erstelle Sensor-Entitäten für DC-Werte (Power, Voltage, Current, etc.)
                for sensor_key, sensor_value in value.items():
                    entity = OpenDTUSensor(coordinator, inverter_serial, f"{inverter_name}_DC_{key}_{sensor_key}", sensor_value)
                    if entity.unique_id not in entities:
                        entities[entity.unique_id] = entity
                        new_entities.append(entity)

            # Hier kannst du noch weitere DC/AC-Werte hinzufügen, falls nötig

        if new_entities:
            async_add_entities(new_entities)

    # Füge Listener für Datenaktualisierungen hinzu
    coordinator.async_add_listener(_update)


class OpenDTUSensor(CoordinatorEntity, SensorEntity):

    def __init__(self, coordinator, inverter_serial, key, value):
        super().__init__(coordinator)
        self._inverter_serial = inverter_serial
        self._key = key
        self._value = value

        self._attr_unique_id = f"opendtu_{self._inverter_serial}_{self._key}"
        self._attr_name = f"OpenDTU {self._key}"
        self._attr_native_value = self._value
        self._attr_native_unit_of_measurement = value.get("u", "unknown")

    @property
    def native_value(self):
        return self.coordinator.data.get(self._key, {}).get("value", "unknown")

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self._inverter_serial)},
            name=f"OpenDTU {self._inverter_serial}",
            manufacturer="OpenDTU",
            model=self._key,
        )
