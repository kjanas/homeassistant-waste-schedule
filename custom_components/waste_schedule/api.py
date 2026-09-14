"""Client for the kiedysmieci.info schedule proxy."""

import asyncio
import logging

import aiohttp
import async_timeout

from .const import (
    CONF_GMINA,
    CONF_POWIAT,
    CONF_ULICA,
    CONF_WOJEWODZTWO,
    SCHEDULE_API_URL,
)

_LOGGER = logging.getLogger(__name__)

REQUEST_TIMEOUT = 15

# Response key holding the option list for each level of the location cascade.
LIST_KEYS = {
    CONF_WOJEWODZTWO: "listaWojewodztw",
    CONF_POWIAT: "listaPowiatow",
    CONF_GMINA: "listaGmin",
    CONF_ULICA: "listaUlic",
}


class WasteApiError(Exception):
    """Raised when the schedule proxy cannot be queried."""


async def _async_request(session, request_type: str, params: dict) -> dict:
    query = {"type": request_type}
    query.update({key: value for key, value in params.items() if value})

    try:
        async with async_timeout.timeout(REQUEST_TIMEOUT):
            async with session.get(SCHEDULE_API_URL, params=query) as resp:
                payload = await resp.json(content_type=None)
    except (aiohttp.ClientError, asyncio.TimeoutError, ValueError) as err:
        raise WasteApiError(f"Error fetching data: {err}") from err

    if not isinstance(payload, dict) or not payload.get("ok"):
        message = ""
        if isinstance(payload, dict):
            message = payload.get("message") or ""
        raise WasteApiError(message or "Unexpected response from schedule proxy")

    data = payload.get("data")

    return data if isinstance(data, dict) else {}


def _option_names(items, level: str) -> list[str]:
    names = set()

    for item in items:
        if isinstance(item, str):
            name = item.strip()
        elif isinstance(item, dict):
            name = str(item.get(level) or "").strip()
        else:
            continue

        if name:
            names.add(name)

    return sorted(names)


async def async_fetch_options(session, level: str, selection: dict) -> list[str]:
    """Return the available values for one level of the location cascade."""
    data = await _async_request(session, "locations", selection)
    items = data.get(LIST_KEYS[level])

    if not isinstance(items, list):
        return []

    return _option_names(items, level)


async def async_fetch_terms(session, location: dict) -> list[dict]:
    """Return the raw collection terms for a fully qualified location."""
    data = await _async_request(session, "terms", location)
    terms = data.get("listaTerminow")

    return [term for term in terms if isinstance(term, dict)] if isinstance(terms, list) else []
