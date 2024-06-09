#Home Assistant Integration - Bordeaux Métropole - Parking hors voirie

Une clef est nécessaire pour interroger le webservice

https://data.bordeaux-metropole.fr/opendata/key


sensor:
  - platform: bdx_parkings
    bdx_data_key: !secret bdx_data_key
    parking_ids: 'CUBPK100'
    scan_interval: 3600
  - platform: bdx_parkings
    bdx_data_key: !secret bdx_data_key
    parking_ids: 'CUBPK80'
    scan_interval: 3600
  - platform: bdx_parkings
    bdx_data_key: !secret bdx_data_key
    parking_ids: 'CUBPK44'
    scan_interval: 3600
