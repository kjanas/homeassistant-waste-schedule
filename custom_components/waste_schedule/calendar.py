from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.util import dt as dt_util
from datetime import timedelta
from .const import ENTITY_NAMES, DOMAIN


class WasteCalendar(CalendarEntity):
    def __init__(self, coordinator, key: str, street: str, entry_id: str):
        self.coordinator = coordinator
        self.key = key
        self.street = street
        self._attr_name = f"{ENTITY_NAMES.get(key, key)} - {street}"
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_{key}"

    @property
    def event(self):
        dates = self.coordinator.data.get(self.key) if self.coordinator.data else []
        if not dates:
            return None

        next_date = dates[0]
        start = dt_util.start_of_local_day(next_date)
        end = start + timedelta(days=1)

        return CalendarEvent(
            start=start,
            end=end,
            summary=f"{ENTITY_NAMES.get(self.key, self.key)}",
        )

    async def async_get_events(self, hass, start_date, end_date):
        result = []
        dates = self.coordinator.data.get(self.key) if self.coordinator.data else []

        for d in dates:
            start = dt_util.start_of_local_day(d)
            end = start + timedelta(days=1) - timedelta(seconds=1)
            if start_date <= start <= end_date:
                result.append(
                    CalendarEvent(
                        start=start,
                        end=end,
                        summary=f"{ENTITY_NAMES.get(self.key, self.key)}",
                    )
                )

        return result


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    street = entry.data.get("street", "unknown")

    entities = []
    if coordinator.data:
        for key in coordinator.data.keys():
            entities.append(WasteCalendar(coordinator, key, street, entry.entry_id))

    if entities:
        async_add_entities(entities, True)