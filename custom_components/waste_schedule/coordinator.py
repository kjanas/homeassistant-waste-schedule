import aiohttp
import async_timeout
from datetime import date, datetime, timedelta
import logging
import re
from bs4 import BeautifulSoup
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .models import WasteType
from .const import DOMAIN

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
                        dates_by_type: dict[WasteType, list[date]] = {}

                        for card in soup.select("div.termin.card"):
                            date_el = card.select_one(".naglowek")
                            type_el = card.select_one(".srodek.wysrodkowanie h3")

                            if not date_el or not type_el:
                                continue

                            waste_type = WasteType(type_el.get_text(strip=True))

                            if waste_type not in dates_by_type:
                                dates_by_type[waste_type] = []

                            date_text = date_el.get_text(strip=True).split("(")[0].strip()
                            
                            m = re.search(r"(\d{4}\-\d{2}\-\d{2})", date_text)
                            
                            if not m:
                                continue

                            yyyy, mm, dd = m.group(1).split("-")
                            
                            dt = date(int(yyyy), int(mm), int(dd))
                            
                            if dt >= today:
                                dates_by_type[waste_type].append(dt)

                        return {
                            wt: sorted(list(set(dates)))
                            for wt, dates in dates_by_type.items()
                            if dates
                        }
        except Exception as err:
            raise UpdateFailed(f"Error fetching data: {err}") from err