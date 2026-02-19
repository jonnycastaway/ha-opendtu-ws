# Updated binary_sensor.py

# This file has been updated to fix the coordinator initialization and ensure safe data access.

class MyBinarySensor:
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self._attr_is_on = None

    @property
    def is_on(self):
        # Ensure safe data access by checking coordinator state
        if self.coordinator.data is not None:
            self._attr_is_on = self.coordinator.data['sensor_state'] == 'on'
        return self._attr_is_on