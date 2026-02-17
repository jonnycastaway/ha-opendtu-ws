from homeassistant.helpers.entity import Entity
from .coordinator import OpenDTUCoordinator

class OpenDTUSensor(Entity):
    def __init__(self, coordinator: OpenDTUCoordinator, name: str):
        self.coordinator = coordinator
        self.name = name
        self._state = None

    @property
    def state(self):
        return self._state

    @property
    def device_state_attributes(self):
        return {
            "value": self.coordinator.data.get(self.name, {}).get("value"),
            "unit": self.coordinator.data.get(self.name, {}).get("unit")
        }

    async def async_update(self):
        self._state = self.coordinator.data.get(self.name, {}).get("value")
