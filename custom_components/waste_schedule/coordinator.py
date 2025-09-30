import aiohttp
import async_timeout
from datetime import datetime
import logging
import re
from bs4 import BeautifulSoup
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import DOMAIN, ENTITY_NAMES
from datetime import timedelta

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(hours=12)

class WasteDataCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, url: str):
        self.url = url
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)

    async def _async_update_data(self):
        try:
            async with async_timeout.timeout(15):
                async with aiohttp.ClientSession() as session:
                    async with session.get(self.url) as resp:
                        if resp.status != 200:
                            raise UpdateFailed(f"HTTP error {resp.status}")
                        html = await resp.text()
                        soup = BeautifulSoup(html, "html.parser")
                        today = datetime.today().date()
                        dates_by_type = {key: [] for key in ENTITY_NAMES.keys()}

                        for card in soup.select("div.termin.card"):
                            date_el = card.select_one(".naglowek")
                            type_el = card.select_one(".srodek.wysrodkowanie h3")
                            _LOGGER.debug("Processing card with date_el: %s and type_el: %s", date_el, type_el)
                            if not date_el or not type_el:
                                continue
                            date_text = date_el.get_text(strip=True).split("(")[0].strip()
                            type_text = type_el.get_text(strip=True).replace("ł", "l").replace("ś", "s").replace("ó", "o").replace("ą", "a").replace("ę", "e").replace("ć", "c").replace("ń", "n").replace("ź", "z").replace("ż", "z")
                            if type_text not in ENTITY_NAMES.values():
                                _LOGGER.warning("Unknown waste type: %s, please contact author", type_text)
                                continue
                            type_key = type_text.lower().replace(" ", "_")
                            m = re.search(r"(\d{4}\-\d{2}\-\d{2})", date_text)
                            if not m:
                                continue
                            yyyy, mm, dd = m.group(1).split("-")
                            dt = datetime(int(yyyy), int(mm), int(dd))
                            if dt.date() >= today:
                                dates_by_type[type_key].append(dt)

                        return {k: sorted(v) for k, v in dates_by_type.items() if v is not None and len(v) > 0}
        except Exception as err:
            raise UpdateFailed(f"Error fetching data: {err}") from err