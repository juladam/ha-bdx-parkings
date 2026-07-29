"""Config flow for Bordeaux Parkings integration."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import API_URL, CONF_KEY, CONF_PKG_IDENT, DEFAULT_PARKING_ID, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_KEY): str,
        vol.Required(CONF_PKG_IDENT, default=DEFAULT_PARKING_ID): str,
    }
)


async def validate_input(hass, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input by calling the API.

    Returns the parking name on success, or raises an exception.
    """
    session = async_get_clientsession(hass)
    url = API_URL.format(key=data[CONF_KEY])

    async with session.get(url) as response:
        if response.status == 401:
            raise InvalidApiKey
        if response.status != 200:
            raise CannotConnect

        json_data = await response.json(content_type=None)

    parking_id = data[CONF_PKG_IDENT].upper()
    for feature in json_data.get("features", []):
        if feature["properties"]["ident"] == parking_id:
            return {"title": feature["properties"]["nom"]}

    raise ParkingNotFound


class BdxParkingsConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Bordeaux Parkings."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Normalise l'identifiant parking en majuscules
            user_input[CONF_PKG_IDENT] = user_input[CONF_PKG_IDENT].strip().upper()

            # Évite les doublons (même parking)
            await self.async_set_unique_id(user_input[CONF_PKG_IDENT])
            self._abort_if_unique_id_configured()

            try:
                info = await validate_input(self.hass, user_input)
            except InvalidApiKey:
                errors["base"] = "invalid_api_key"
            except ParkingNotFound:
                errors[CONF_PKG_IDENT] = "parking_not_found"
            except (aiohttp.ClientError, TimeoutError):
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception during config flow")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )


class CannotConnect(Exception):
    """Error to indicate we cannot connect."""


class InvalidApiKey(Exception):
    """Error to indicate the API key is invalid."""


class ParkingNotFound(Exception):
    """Error to indicate the parking ID was not found."""
