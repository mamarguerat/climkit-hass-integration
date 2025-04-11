import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import aiohttp_client
from .climkit_api import ClimkitAPI
from .const import DOMAIN

class ClimkitConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Climkit integration."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            username = user_input["username"]
            password = user_input["password"]

            # Validate credentials
            session = aiohttp_client.async_get_clientsession(self.hass)
            api = ClimkitAPI(username, password)
            try:
                await api.authenticate()
                sites = await api.get_site_id()
                if not sites:
                    errors["base"] = "no_sites"
                else:
                    return self.async_create_entry(
                        title="Climkit", data=user_input
                    )
            except Exception:
                errors["base"] = "auth_failed"

        data_schema = vol.Schema(
            {
                vol.Required("username"): str,
                vol.Required("password"): str,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return ClimkitOptionsFlow(config_entry)


class ClimkitOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Climkit."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        data_schema = vol.Schema(
            {
                vol.Optional("scan_interval", default=5): int,
            }
        )

        return self.async_show_form(step_id="init", data_schema=data_schema)