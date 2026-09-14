from datetime import date, datetime, timedelta
import logging

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import WasteApiError, async_fetch_terms
from .const import DOMAIN, NO_SCHEDULE_MARKER
from .models import WasteType

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(hours=12)


class WasteDataCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, session, location: dict):
        self.session = session
        self.location = location
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)

    async def _async_update_data(self):
        try:
            terms = await async_fetch_terms(self.session, self.location)
        except WasteApiError as err:
            raise UpdateFailed(str(err)) from err

        today = datetime.today().date()
        dates_by_type: dict[WasteType, set[date]] = {}

        for term in terms:
            # A location without a published schedule gets a single placeholder
            # term instead of real dates.
            if str(term.get("dzienTygodnia", "")).strip().lower() == NO_SCHEDULE_MARKER:
                continue

            name = str(term.get("nazwaTypuSmieci") or "").strip()
            raw_date = str(term.get("dataOdbioru") or "").strip()

            if not name or not raw_date:
                continue

            try:
                dt = date.fromisoformat(raw_date)
            except ValueError:
                _LOGGER.debug("Skipping term with unparsable date %r", raw_date)
                continue

            if dt < today:
                continue

            dates_by_type.setdefault(WasteType(name), set()).add(dt)

        return {wt: sorted(dates) for wt, dates in dates_by_type.items() if dates}
