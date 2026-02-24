from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.helpers.entity import EntityCategory

# Übersetzungstabelle: Suffix des Keys → lesbarer Name
# Reihenfolge wichtig: längere/spezifischere Matches zuerst!
NAME_MAP = {
    # AC-Werte
    "ac_0_power":           "AC Leistung",
    "ac_0_voltage":         "AC Spannung",
    "ac_0_current":         "AC Strom",
    "ac_0_frequency":       "Netzfrequenz",
    "ac_0_powerfactor":     "Leistungsfaktor",
    "ac_0_reactivepower":   "Blindleistung",
    "ac_0_efficiency":      "Wirkungsgrad",
    "ac_0_yieldday":        "Ertrag heute",
    "ac_0_yieldtotal":      "Gesamtertrag",
    "ac_0_power_dc":        "DC Eingangsleistung",
    "ac_0_temperature":     "Temperatur",

    # Inverter-Gesamtwerte (inv_0_0_* – echte Keys aus flatten())
    "inv_0_0_efficiency":   "Wirkungsgrad",
    "inv_0_0_power_dc":     "DC Gesamtleistung",
    "inv_0_0_temperature":  "Temperatur",
    "inv_0_0_yieldday":     "Ertrag heute",
    "inv_0_0_yieldtotal":   "Gesamtertrag",
    "inv_0_efficiency":     "Wirkungsgrad",
    "inv_0_power_dc":       "DC Gesamtleistung",
    "inv_0_temperature":    "Temperatur",
    "inv_0_yieldday":       "Ertrag heute",
    "inv_0_yieldtotal":     "Gesamtertrag",

    # DC-Strings (0–3)
    "dc_0_power":           "DC Leistung String 1",
    "dc_0_voltage":         "DC Spannung String 1",
    "dc_0_current":         "DC Strom String 1",
    "dc_0_yieldday":        "Ertrag heute String 1",
    "dc_0_yieldtotal":      "Gesamtertrag String 1",
    "dc_0_irradiation":     "Einstrahlung String 1",

    "dc_1_power":           "DC Leistung String 2",
    "dc_1_voltage":         "DC Spannung String 2",
    "dc_1_current":         "DC Strom String 2",
    "dc_1_yieldday":        "Ertrag heute String 2",
    "dc_1_yieldtotal":      "Gesamtertrag String 2",
    "dc_1_irradiation":     "Einstrahlung String 2",

    "dc_2_power":           "DC Leistung String 3",
    "dc_2_voltage":         "DC Spannung String 3",
    "dc_2_current":         "DC Strom String 3",
    "dc_2_yieldday":        "Ertrag heute String 3",
    "dc_2_yieldtotal":      "Gesamtertrag String 3",
    "dc_2_irradiation":     "Einstrahlung String 3",

    "dc_3_power":           "DC Leistung String 4",
    "dc_3_voltage":         "DC Spannung String 4",
    "dc_3_current":         "DC Strom String 4",
    "dc_3_yieldday":        "Ertrag heute String 4",
    "dc_3_yieldtotal":      "Gesamtertrag String 4",
    "dc_3_irradiation":     "Einstrahlung String 4",

    # Inverter-Status
    "reachable":            "Erreichbar",
    "producing":            "Produziert",
    "poll_enabled":         "Abfrage aktiv",
    "limit_relative":       "Limit relativ",
    "limit_absolute":       "Limit absolut",
    "data_age":             "Datenalter",

    # Gesamtanlage
    "total_power":          "Gesamtleistung",
    "total_yieldday":       "Gesamtertrag heute",
    "total_yieldtotal":     "Gesamtertrag gesamt",

    # Hints / System
    "hints_time_sync":          "Zeitsynchronisation",
    "hints_radio_problem":      "Funkproblem",
    "hints_default_password":   "Standard-Passwort aktiv",
}


def friendly_name(key: str) -> str:
    """Gibt einen lesbaren Namen für einen OpenDTU-Datenpunkt zurück."""
    key_l = key.lower()

    # Exakter Match zuerst
    if key_l in NAME_MAP:
        return NAME_MAP[key_l]

    # Inverter-Prefix entfernen und Rest matchen
    # z.B. "inverter_123456_ac_0_power" → "ac_0_power"
    if key_l.startswith("inverter_"):
        parts = key_l.split("_", 2)  # ["inverter", "123456", "ac_0_power"]
        if len(parts) == 3:
            suffix = parts[2]
            if suffix in NAME_MAP:
                return NAME_MAP[suffix]

    # Fallback: Key lesbarer machen
    return key.replace("_", " ").title()


def classify(key, unit, is_bool=False):
    key_l = key.lower()
    device_class = None
    state_class = None
    entity_category = None

    if is_bool:
        if any(x in key_l for x in ["alarm", "fault", "error", "status", "connected", "charging",
                                      "reachable", "producing", "poll_enabled", "time_sync",
                                      "radio_problem", "default_password"]):
            entity_category = EntityCategory.DIAGNOSTIC
    else:
        if "power" in key_l and "factor" not in key_l:
            device_class = SensorDeviceClass.POWER
            state_class = SensorStateClass.MEASUREMENT
        elif "yieldday" in key_l or "yieldtotal" in key_l or "energy" in key_l:
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
        elif "frequency" in key_l:
            device_class = SensorDeviceClass.FREQUENCY
            state_class = SensorStateClass.MEASUREMENT
        elif "data_age" in key_l or "limit" in key_l or "irradiation" in key_l:
            entity_category = EntityCategory.DIAGNOSTIC

    if any(x in key_l for x in ["rssi", "signal", "uptime", "fw", "firmware", "data_age",
                                  "limit_relative", "limit_absolute", "poll_enabled",
                                  "time_sync", "radio_problem", "default_password"]):
        entity_category = EntityCategory.DIAGNOSTIC

    return device_class, state_class, entity_category
