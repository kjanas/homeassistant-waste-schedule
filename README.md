# Waste schedule
For given municipality (gmina) and street/city, integration fetches waste collection events and creates calendar for each waste type/fraction. It is also possible to setup multiple locations.

To find this integration usable, your local goverment have to cooperate with author of "Kiedy śmieci" application.

## Installation
### Manual
Download [wste_schedule](https://github.com/kjanas/homeassistant-waste-schedule/releases/latest/download/waste_schedule.zip) file and extract it to your `homeassistant/config/custom_components` directory:

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
If you use "Kiedy śmieci" mobile application, just provide the same data as on your phone - select municipality (gmina) and your city or street. If you need more locations, simply setup as many as you need.

Once data fetched, integration creates waste collection calendars (one per each waste type/fraction). Each collection date is a full-day calendar event. Feel free to use this entities in automations or UI cards like [Trash card](https://github.com/idaho/hassio-trash-card)
