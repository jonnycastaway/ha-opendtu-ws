from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
import voluptuous as vol

class OpenDTUConfigFlow(config_entries.ConfigFlow):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title=user_input[CONF_HOST],
                data=user_input
            )

        return self.async_show_form(
            step_id="user",
            data_schema=self._get_schema()
        )

    def _get_schema(self):
        return {
            vol.Required(CONF_HOST): str,
            vol.Required(CONF_PORT, default=80): int
        }
