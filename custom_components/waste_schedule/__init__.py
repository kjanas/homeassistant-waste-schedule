import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, LOCATION_LEVELS
from .coordinator import WasteDataCoordinator

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

PLATFORMS = ["calendar"]


async def async_setup(hass: HomeAssistant, config: dict):
    return True


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    if entry.version == 1:
        # Version 1 stored a scraped cloud.fxsystems.com.pl URL identified by a
        # numeric gmina id. The new API is keyed by names only, and the id
        # cannot be translated back, so the entry has to be set up again.
        _LOGGER.error(
            "Waste Schedule entry '%s' uses the retired fxsystems endpoint. "
            "Remove it and add the integration again to pick the location from "
            "the new kiedysmieci.info API",
            entry.title,
        )
        return False

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    location = {level: entry.data[level] for level in LOCATION_LEVELS}

    coordinator = WasteDataCoordinator(hass, async_get_clientsession(hass), location)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
