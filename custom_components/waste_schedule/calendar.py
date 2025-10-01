from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.util import dt as dt_util
from datetime import timedelta
from .const import DOMAIN


class WasteCalendar(CalendarEntity):
    def __init__(self, coordinator, waste_type, street: str, entry_id: str):
        self.coordinator = coordinator
        self.waste_type = waste_type
        self.street = street
        self._attr_name = f"{self.waste_type.name} - {street}"
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_{self.waste_type.key}"

    @property
    def event(self):
        dates = self.coordinator.data.get(self.waste_type) if self.coordinator.data else []
        if not dates:
            return None

        next_date = dates[0]
        start = dt_util.start_of_local_day(next_date)
        end = start + timedelta(days=1)

        return CalendarEvent(
            start=start,
            end=end,
            summary=f"{self.waste_type.name}",
        )

    async def async_get_events(self, hass, start_date, end_date):
        result = []
        dates = self.coordinator.data.get(self.waste_type) if self.coordinator.data else []

        for d in dates:
            start = dt_util.start_of_local_day(d)
            end = start + timedelta(days=1) - timedelta(seconds=1)
            if start_date <= start <= end_date:
                result.append(
                    CalendarEvent(
                        start=start,
                        end=end,
                        summary=f"{self.waste_type.name}",
                    )
                )

        return result


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    street = entry.data.get("street", "unknown")

    entities = []
    if coordinator.data:
        for waste_type in coordinator.data.keys():
            entities.append(WasteCalendar(coordinator, waste_type, street, entry.entry_id))

    if entities:
        async_add_entities(entities, True)