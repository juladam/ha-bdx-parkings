from datetime import timedelta
import logging

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
import requests

from .const import ( CONF_KEY, CONF_PKG_IDENT, ATTR_NOM, ATTR_ETAT, ATTR_LIBRE, ATTR_TOTAl, ATTR_CONNECTE)


_LOGGER = logging.getLogger(__name__)

DOMAIN = 'bdx_parkings'
SCAN_INTERVAL = timedelta(seconds=30*60)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_KEY): cv.string,
    vol.Required(CONF_PKG_IDENT, default='CUBPK80'): cv.string,
})

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Parkings platform."""
    entities = [ParkingsEntity(config)]
    add_entities(entities, True)


class ParkingsEntity(Entity):
    """Parkings Entity."""

    def __init__(self, config):
        """Init the Parkings Entity."""
        self._attr = {
            ATTR_NOM: {},
            ATTR_ETAT: {},
            ATTR_LIBRE: {},
            ATTR_TOTAl: {},
            ATTR_CONNECTE: {}
        }

        self.bdx_key = config[CONF_KEY]
        self.ident = config[CONF_PKG_IDENT]

    def update(self):
        """Update data."""
        self._attr = {
            ATTR_NOM: {},
            ATTR_ETAT: {},
            ATTR_LIBRE: {},
            ATTR_TOTAl: {},
            ATTR_CONNECTE: {}
        }

        url = "https://data.bordeaux-metropole.fr/geojson?key={}&typename=st_park_p".format(self.bdx_key)
        response = requests.get(url)
        data = response.json()
        for feature in data['features']:
            if feature['properties']['ident'] == self.ident:
                self._attr[ATTR_NOM] = feature['properties']['nom']
                self._attr[ATTR_ETAT] = feature['properties']['etat']
                self._attr[ATTR_LIBRE] = feature['properties']['libres']
                self._attr[ATTR_TOTAl] = feature['properties']['total']
                self._attr[ATTR_CONNECTE] = feature['properties']['connecte']
                break

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._attr[ATTR_NOM]

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._attr[ATTR_ETAT]

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._attr

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return 'mdi:parking'
