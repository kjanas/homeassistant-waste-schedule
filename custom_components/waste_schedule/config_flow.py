import aiohttp
import async_timeout
import voluptuous as vol
from homeassistant import config_entries
from bs4 import BeautifulSoup
from .const import DOMAIN, SCHEDULE_BASE_URL

async def fetch_municipalities():
    try:
        async with aiohttp.ClientSession() as session:
            async with async_timeout.timeout(15):
                async with session.get(SCHEDULE_BASE_URL) as resp:
                    html = await resp.text()
                    soup = BeautifulSoup(html, "html.parser")
                    select = soup.find("select", id="selGmina")
                    if not select:
                        return {}
                    return {
                        opt.get("value"): opt.text.strip()
                        for opt in select.find_all("option")
                        if opt.get("value")
                    }
    except Exception:
        return {}

async def fetch_streets(municipality_id):
    try:
        url = f"{SCHEDULE_BASE_URL}?gmina_id={municipality_id}"
        async with aiohttp.ClientSession() as session:
            async with async_timeout.timeout(15):
                async with session.get(url) as resp:
                    html = await resp.text()
                    soup = BeautifulSoup(html, "html.parser")
                    select = soup.find("select", id="selUlica")
                    if not select:
                        return {}
                    return {
                        opt.text.strip(): opt.text.strip()
                        for opt in select.find_all("option")
                        if opt.text.strip()
                    }
    except Exception:
        return {}

class WasteScheduleConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1

    async def async_step_user(self, user_input=None):
        return await self.async_step_municipality(user_input)

    async def async_step_municipality(self, user_input=None):
        errors = {}

        if user_input is not None:
            municipality_id = user_input["municipality_id"]
            self.context["municipality_id"] = municipality_id
            return await self.async_step_street()

        options = await fetch_municipalities()
        
        if not options:
            errors["base"] = "cannot_connect"
            return self.async_show_form(step_id="user", errors=errors)

        data_schema = vol.Schema(
            {vol.Required("municipality_id"): vol.In(options)}
        )
        
        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    async def async_step_street(self, user_input=None):
        errors = {}
        municipality_id = self.context.get("municipality_id")

        if user_input is not None:
            street_id = user_input["street_id"]
            final_url = f"{SCHEDULE_BASE_URL}?gmina_id={municipality_id}&ulica={street_id}"

            await self.async_set_unique_id(f"{municipality_id}_{street_id}")
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=f"Waste Schedule {street_id}",
                data={"url": final_url, "street": street_id},
            )

        options = await fetch_streets(municipality_id)
        
        if not options:
            errors["base"] = "cannot_connect"
            return self.async_show_form(step_id="street", errors=errors)

        data_schema = vol.Schema({vol.Required("street_id"): vol.In(options)})
        
        return self.async_show_form(
            step_id="street", data_schema=data_schema, errors=errors
        )