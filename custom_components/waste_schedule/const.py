DOMAIN = "waste_schedule"

SCHEDULE_API_URL = "https://kiedysmieci.info/schedule-proxy.php"

CONF_WOJEWODZTWO = "wojewodztwo"
CONF_POWIAT = "powiat"
CONF_GMINA = "gmina"
CONF_ULICA = "ulica"

LOCATION_LEVELS = (CONF_WOJEWODZTWO, CONF_POWIAT, CONF_GMINA, CONF_ULICA)

# The API answers with a single placeholder term when a location has no
# published schedule yet.
NO_SCHEDULE_MARKER = "brak harmonogramu"
