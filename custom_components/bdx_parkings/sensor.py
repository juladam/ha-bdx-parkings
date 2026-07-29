"""Sensor platform for Bordeaux Parkings."""

from __future__ import annotations

from datetime import timedelta
import logging

import aiohttp

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    API_URL,
    ATTR_CONNECTE,
    ATTR_ETAT,
    ATTR_LIBRE,
    ATTR_NOM,
    ATTR_TOTAL,
    CONF_KEY,
    CONF_PKG_IDENT,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=3600)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Bordeaux Parkings sensor from a config entry."""
    coordinator = BdxParkingsCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    async_add_entities([BdxParkingsSensor(coordinator, entry)])


class BdxParkingsCoordinator(DataUpdateCoordinator):
    """Coordinator to fetch parking data from the API."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self._api_key = entry.data[CONF_KEY]
        self._parking_id = entry.data[CONF_PKG_IDENT]
        self._session = async_get_clientsession(hass)

    async def _async_update_data(self) -> dict:
        """Fetch data from the Bordeaux Métropole API."""
        url = API_URL.format(key=self._api_key)
        try:
            async with self._session.get(url) as response:
                if response.status != 200:
                    raise UpdateFailed(
                        f"API returned HTTP {response.status}"
                    )
                json_data = await response.json(content_type=None)
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

        for feature in json_data.get("features", []):
            if feature["properties"]["ident"] == self._parking_id:
                props = feature["properties"]
                return {
                    ATTR_NOM: props.get("nom"),
                    ATTR_ETAT: props.get("etat"),
                    ATTR_LIBRE: props.get("libres"),
                    ATTR_TOTAL: props.get("total"),
                    ATTR_CONNECTE: props.get("connecte"),
                }

        raise UpdateFailed(f"Parking '{self._parking_id}' not found in API response")


class BdxParkingsSensor(CoordinatorEntity, SensorEntity):
    """Sensor representing a Bordeaux parking lot."""

    def __init__(
        self, coordinator: BdxParkingsCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = entry.data[CONF_PKG_IDENT]
        self._attr_icon = "mdi:parking"

    @property
    def name(self) -> str | None:
        """Return the name of the sensor (parking name from API)."""
        if self.coordinator.data:
            return self.coordinator.data.get(ATTR_NOM)
        return self._entry.data[CONF_PKG_IDENT]

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        if self.coordinator.data:
            return self.coordinator.data.get(ATTR_ETAT)
        return None

    @property
    def extra_state_attributes(self) -> dict | None:
        """Return extra state attributes."""
        return self.coordinator.data
