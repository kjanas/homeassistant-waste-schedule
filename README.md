# Waste schedule
For a given location (voivodeship, county, municipality and street/city), integration fetches waste collection events and creates calendar for each waste type/fraction. It is also possible to setup multiple locations.

Data comes from the public `kiedysmieci.info` schedule API.

To find this integration usable, your local goverment have to cooperate with author of "Kiedy śmieci" application.

## Installation
### Manual
Download [waste_schedule](https://github.com/kjanas/homeassistant-waste-schedule/releases/latest/download/waste_schedule.zip) file and extract it to your `homeassistant/config/custom_components` directory:

```
mkdir custom_components/waste_schedule
cd custom_components/waste_schedule
wget https://github.com/kjanas/homeassistant-waste-schedule/releases/latest/download/waste_schedule.zip
unzip waste_schedule.zip
rm waste_schedule.zip
```

Then you have to restart HomeAssistant.

### HACS (recommended)
- go to HACS
- find "Waste schedule" in available integrations
- in integration details, click [Download]
- restart HomeAssistant

## Setup
If you use "Kiedy śmieci" mobile application, just provide the same data as on your phone. The config flow walks through four steps: voivodeship (województwo), county (powiat), municipality (gmina) and finally street or locality (ulica). Every list is fetched live from the API, so only locations with a published schedule are offered. If you need more locations, simply setup as many as you need.

Once data fetched, integration creates waste collection calendars (one per each waste type/fraction). Each collection date is a full-day calendar event. Feel free to use this entities in automations or UI cards like [Trash card](https://github.com/idaho/hassio-trash-card)


## Upgrading from 1.x
Version 2.0.0 switches from scraping `cloud.fxsystems.com.pl` (retired, the
municipality picker no longer exists there) to the JSON API behind
`kiedysmieci.info`. The old config entries stored a numeric municipality id that
cannot be translated into the names the new API expects, so they cannot be
migrated automatically.

Remove the old integration entry **before** adding the new one - the calendar
entities are named the same way, so they keep their entity ids when the registry
slot is free.
