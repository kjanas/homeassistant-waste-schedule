import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import WasteApiError, async_fetch_options
from .const import (
    CONF_GMINA,
    CONF_POWIAT,
    CONF_ULICA,
    CONF_WOJEWODZTWO,
    DOMAIN,
    LOCATION_LEVELS,
)


class WasteScheduleConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 2

    def __init__(self):
        self._location: dict[str, str] = {}

    async def _async_step_level(self, level: str, step_id: str, user_input=None):
        """Show one level of the wojewodztwo -> powiat -> gmina -> ulica cascade."""
        errors = {}

        if user_input is not None:
            self._location[level] = user_input[level]
            return await self._async_next_step(level)

        session = async_get_clientsession(self.hass)

        try:
            options = await async_fetch_options(session, level, self._location)
        except WasteApiError:
            options = []
            errors["base"] = "cannot_connect"

        if not options:
            errors.setdefault("base", "no_options")
            return self.async_show_form(step_id=step_id, errors=errors)

        return self.async_show_form(
            step_id=step_id,
            data_schema=vol.Schema({vol.Required(level): vol.In(options)}),
            errors=errors,
        )

    async def _async_next_step(self, level: str):
        next_index = LOCATION_LEVELS.index(level) + 1

        if next_index == len(LOCATION_LEVELS):
            return await self._async_create_entry()

        next_level = LOCATION_LEVELS[next_index]

        return await getattr(self, f"async_step_{next_level}")()

    async def _async_create_entry(self):
        await self.async_set_unique_id("|".join(self._location[l] for l in LOCATION_LEVELS))
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=f"{self._location[CONF_ULICA]} ({self._location[CONF_GMINA]})",
            data=dict(self._location),
        )

    async def async_step_user(self, user_input=None):
        return await self._async_step_level(CONF_WOJEWODZTWO, "user", user_input)

    async def async_step_powiat(self, user_input=None):
        return await self._async_step_level(CONF_POWIAT, "powiat", user_input)

    async def async_step_gmina(self, user_input=None):
        return await self._async_step_level(CONF_GMINA, "gmina", user_input)

    async def async_step_ulica(self, user_input=None):
        return await self._async_step_level(CONF_ULICA, "ulica", user_input)
