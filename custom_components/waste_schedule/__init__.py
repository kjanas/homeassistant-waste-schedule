from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN
from .sensor import WasteDataCoordinator

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the integration from YAML (optional)."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up integration from Config Flow entry."""
    url = entry.data["url"]

    # Create a coordinator for this entry
    coordinator = WasteDataCoordinator(hass, url)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Forward setup to sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True