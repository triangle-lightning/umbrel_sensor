"""Platform for sensor integration."""
from __future__ import annotations
from typing import Dict
import requests

from homeassistant.components.sensor import (
    SensorEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

# TODO Setup configuration file vars
HOST = 'http://CHANGEME'  # < ------------------------------ Set to local IP Address
PASSWORD = 'CHANGEME'     # < ------------------------------ Set to umbrel password

def post(url: str, body: Dict) -> Dict:
    r = requests.post(url, data=body)
    return r.json()

def get(url: str, headers: Dict) -> Dict:
    r = requests.get(url,headers=headers)
    return r.json()


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None
) -> None:
    """Set up the sensor platform."""
    add_entities([UmbrelExchangeSensor(), UmbrelBTCSensor()])


class UmbrelExchangeSensor(SensorEntity):
    """Representation of a Sensor."""

    _attr_name = "Umbrel BTC Exchange Rate"
    _attr_native_unit_of_measurement = "USD"
    _attr_icon = "mdi:currency-btc"

    def update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        api = UmbrelApi(HOST, PASSWORD)
        btc_data = UmbrelExachange(api)
        print(btc_data.data)        
        self._attr_native_value = btc_data.data['USD']

class UmbrelBTCSensor(SensorEntity):
    """Representation of a Sensor."""

    _attr_name = "Umbrel BTC Sync Status"
    _attr_native_unit_of_measurement = "%"
    _attr_icon = "mdi:cloud-percent-outline"

    def update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        api = UmbrelApi(HOST, PASSWORD)
        btc_data = UmbrelBTC(api)
        print(btc_data.data)        
        self._attr_native_value = btc_data.data['percent'] * 100


class UmbrelApi:
    def __init__(self, base_url: str, password: str) -> None:
        self.base_url = base_url
        self.password = password
        self.jwt = self.get_jwt()

    def get(self, url_ending: str):
        headers = {'Authorization': f'JWT {self.jwt}'}
        response = get(self.base_url+url_ending, headers)
        return response


    def get_jwt(self):
        body = {"password": self.password, "otpToken": ""}
        response = post(self.base_url+'/manager-api/v1/account/login', body)
        return response['jwt']


class UmbrelExachange:
    def __init__(self, session: UmbrelApi) -> None:
       self.data = session.get('/manager-api/v1/external/price') 
       
class UmbrelBTC:
    def __init__(self, session: UmbrelApi) -> None:
       self.data = session.get('/api/v1/bitcoind/info/sync')       