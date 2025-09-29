import aiohttp
import async_timeout
from datetime import timedelta, datetime
import logging
import re
import locale
from bs4 import BeautifulSoup
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(hours=12)

ENTITY_NAMES = {
    "opony": "opony",
    "odpady_wielkogabarytowe": "odpady wielkogabarytowe",
    "zmieszane": "zmieszane",
    "biodegradowalne": "biodegradowalne",
    "metale_i_tworzywa_sztuczne": "metale i tworzywa sztuczne",
    "papier_i_tektura": "papier i tektura",
}

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [WasteSensor(coordinator, key) for key in ENTITY_NAMES.keys()]
    async_add_entities(entities, True)

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
                            if not date_el or not type_el:
                                _LOGGER.debug("Missing date or type element in card, skipping")
                                continue
                            date_text = date_el.get_text(strip=True).split("(")[0].strip()
                            type_text = type_el.get_text(strip=True)
                            if type_text not in ENTITY_NAMES.values():
                                _LOGGER.debug("Unknown waste type: %s, skipping", type_text)
                                continue
                            type_key = type_text.lower().replace(" ", "_")
                            m = re.search(r"(\d{4}\-\d{2}\-\d{2})", date_text)
                            if not m:
                                _LOGGER.debug("Date format not recognized: %s, skipping", date_text)
                                continue
                            yyyy, mm, dd = m.group(1).split("-")
                            dt = datetime(int(yyyy), int(mm), int(dd))
                            if dt.date() >= today:
                                dates_by_type[type_key].append(dt)

                        result = {}
                        for key, date_list in dates_by_type.items():
                            if date_list:
                                sorted_dates = sorted(date_list, key=lambda x: x.date())
                                nearest = sorted_dates[0]
                                next_collection = sorted_dates[1] if len(sorted_dates) > 1 else None

                                weekday = nearest.strftime("%A")
                                
                                try:
                                    locale.setlocale(locale.LC_TIME, "")
                                except locale.Error:
                                    _LOGGER.warning("Locale setting failed, using default locale")
                                    pass
                                result[key] = {"date": nearest.date().isoformat(), "weekday": weekday, "next_collection": next_collection.date().isoformat() if next_collection else None}
                                
                        return result
        except Exception as err:
            raise UpdateFailed(f"Error fetching data: {err}") from err

class WasteSensor(SensorEntity):
    def __init__(self, coordinator: WasteDataCoordinator, key: str):
        self.coordinator = coordinator
        self.key = key
        self._attr_name = f"Waste {ENTITY_NAMES.get(key, key)}"
        self._attr_unique_id = f"{DOMAIN}_{key}"

    @property
    def native_value(self):
        entry = self.coordinator.data.get(self.key) if self.coordinator.data else None
        return entry["date"] if entry else None

    @property
    def extra_state_attributes(self):
        entry = self.coordinator.data.get(self.key) if self.coordinator.data else None
        return {
            "weekday": entry["weekday"],
            "next_collection": entry["next_collection"]
        } if entry else {}

    async def async_update(self):
        await self.coordinator.async_request_refresh()