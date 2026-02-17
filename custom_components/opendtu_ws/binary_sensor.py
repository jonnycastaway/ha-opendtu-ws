from homeassistant.helpers.entity import Entity

class OpenDTUBinarySensor(Entity):
    def __init__(self, coordinator, name):
        self.coordinator = coordinator
        self.name = name
        self._state = None

    @property
    def state(self):
        return self._state

    async def async_update(self):
        self._state = self.coordinator.data.get(self.name, {}).get("value")
