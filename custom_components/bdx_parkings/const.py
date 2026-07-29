"""Constants for BDX Parkings Platform."""

DOMAIN = "bdx_parkings"

CONF_KEY = "bdx_data_key"
CONF_PKG_IDENT = "parking_ids"

DEFAULT_PARKING_ID = "CUBPK80"

ATTR_NOM = "nom"
ATTR_ETAT = "etat"
ATTR_LIBRE = "libre"
ATTR_TOTAL = "total"
ATTR_CONNECTE = "connecte"

API_URL = "https://data.bordeaux-metropole.fr/geojson?key={key}&typename=st_park_p"
