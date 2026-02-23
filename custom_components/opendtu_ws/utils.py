from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.helpers.entity import EntityCategory

def classify(key, unit, is_bool=False):
    key_l = key.lower()
    device_class = None
    state_class = None
    entity_category = None

    if is_bool:
        if any(x in key_l for x in ["alarm","fault","error","status","connected","charging"]):
            entity_category = EntityCategory.DIAGNOSTIC
    else:
        if "power" in key_l:
            device_class = SensorDeviceClass.POWER
            state_class = SensorStateClass.MEASUREMENT
        elif "yield" in key_l or "energy" in key_l:
            device_class = SensorDeviceClass.ENERGY
            state_class = SensorStateClass.TOTAL_INCREASING
        elif "voltage" in key_l:
            device_class = SensorDeviceClass.VOLTAGE
            state_class = SensorStateClass.MEASUREMENT
        elif "current" in key_l:
            device_class = SensorDeviceClass.CURRENT
            state_class = SensorStateClass.MEASUREMENT
        elif "temperature" in key_l:
            device_class = SensorDeviceClass.TEMPERATURE
            state_class = SensorStateClass.MEASUREMENT

    if any(x in key_l for x in ["rssi","signal","uptime","fw","firmware"]):
        entity_category = EntityCategory.DIAGNOSTIC

    return device_class, state_class, entity_category
