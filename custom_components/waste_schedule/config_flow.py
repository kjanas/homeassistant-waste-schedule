import aiohttp
import async_timeout
import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN
from bs4 import BeautifulSoup

SCHEDULE_BASE_URL = "https://cloud.fxsystems.com.pl/OdbiorySmieci/HarmonogramOnline.dll"

async def fetch_municipalities():
    options = {}
    try:
        async with aiohttp.ClientSession() as session:
            async with async_timeout.timeout(15):
                async with session.get(SCHEDULE_BASE_URL) as resp:
                    html = await resp.text()
                    soup = BeautifulSoup(html, "html.parser")
                    select = soup.find("select", id="selGmina")
                    if select:
                        for opt in select.find_all("option"):
                            value = opt.get("value")
                            name = opt.text.strip()
                            if value:
                                options[value] = name
    except Exception:
        options = {}
    if not options:
        options = {"0": "Unable to fetch municipalities"}
    return options


async def fetch_streets(municipality_id):
    options = {}
    try:
        url = f"{SCHEDULE_BASE_URL}?gmina_id={municipality_id}"
        async with aiohttp.ClientSession() as session:
            async with async_timeout.timeout(15):
                async with session.get(url) as resp:
                    html = await resp.text()
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(html, "html.parser")
                    select = soup.find("select", id="selUlica")
                    if select:
                        for opt in select.find_all("option"):
                            text = opt.text.strip()
                            if text:
                                options[text] = text  
    except Exception:
        options = {}
    if not options:
        options = {"0": "No cities ot streets found"}
    return options


class WasteScheduleConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            municipality_id = user_input.get("municipality_id")
            self.context["municipality_id"] = municipality_id
            return await self.async_step_street()

        options = await fetch_municipalities()
        data_schema = vol.Schema({vol.Required("municipality_id"): vol.In(options)})
        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)

    async def async_step_street(self, user_input=None):
        errors = {}
        municipality_id = self.context.get("municipality_id")
        if user_input is not None:
            street_id = user_input.get("street_id")
            final_url = f"{SCHEDULE_BASE_URL}?gmina_id={municipality_id}&ulica={street_id}"
            return self.async_create_entry(title=f"Waste Schedule {street_id}", data={"url": final_url})

        options = await fetch_streets(municipality_id)
        data_schema = vol.Schema({vol.Required("street_id"): vol.In(options)})
        return self.async_show_form(step_id="street", data_schema=data_schema, errors=errors)