import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, CONF_API_TOKEN, CONF_STROOM_PROVIDER, CONF_GAS_PROVIDER, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, PROVIDERS

_LOGGER = logging.getLogger(__name__)

class EneverConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            token = user_input.get(CONF_API_TOKEN)
            stroom_prov = user_input.get(CONF_STROOM_PROVIDER)
            gas_prov = user_input.get(CONF_GAS_PROVIDER)

            if not token: 
                errors[CONF_API_TOKEN] = "required"

            if not errors:
                return self.async_create_entry(
                    title=f"Enever (Stroom: {PROVIDERS.get(stroom_prov, stroom_prov)} / Gas: {PROVIDERS.get(gas_prov, gas_prov)})",
                    data={
                        CONF_API_TOKEN: token,
                        CONF_STROOM_PROVIDER: stroom_prov,
                        CONF_GAS_PROVIDER: gas_prov
                    },
                    options={CONF_SCAN_INTERVAL: DEFAULT_SCAN_INTERVAL},
                )

        data_schema = vol.Schema({
            vol.Required(CONF_API_TOKEN): str,
            vol.Required(CONF_STROOM_PROVIDER, default="EE"): vol.In(PROVIDERS),
            vol.Required(CONF_GAS_PROVIDER, default="EE"): vol.In(PROVIDERS),
        })
        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return OptionsFlowHandler()

class OptionsFlowHandler(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options_schema = vol.Schema({
            vol.Required(CONF_SCAN_INTERVAL, default=self.config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)): int,
        })
        return self.async_show_form(step_id="init", data_schema=options_schema)