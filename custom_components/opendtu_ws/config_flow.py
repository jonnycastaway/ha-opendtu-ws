import asyncio
import voluptuous as vol
import websockets
from homeassistant import config_entries
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from .const import DOMAIN, CONF_HOST, CONF_PORT


async def _test_connection(host: str, port: int) -> bool:
    """Verbindung testen bevor Entry erstellt wird."""
    uri = f"ws://{host}:{port}/livedata"
    try:
        async with websockets.connect(uri, open_timeout=5):
            return True
    except Exception:
        return False


class OpenDTUFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input:
            ok = await _test_connection(user_input[CONF_HOST], user_input[CONF_PORT])
            if ok:
                return self.async_create_entry(
                    title=f"OpenDTU ({user_input[CONF_HOST]})",
                    data=user_input,
                )
            else:
                errors["base"] = "cannot_connect"

        schema = vol.Schema({
            vol.Required(CONF_HOST): str,
            vol.Required(CONF_PORT, default=80): int,
            vol.Required(CONF_USERNAME, default="admin"): str,
            vol.Required(CONF_PASSWORD): str,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )
