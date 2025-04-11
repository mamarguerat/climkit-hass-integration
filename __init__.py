DOMAIN = "climkit"

import logging
from datetime import timedelta

import voluptuous as vol
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_time_interval
import homeassistant.helpers.config_validation as cv

from .climkit_api import ClimkitAPI

_LOGGER = logging.getLogger(__name__)

CONF_USERNAME = "username"
CONF_PASSWORD = "password"

CONFIG_SCHEMA = vol.Schema(
  {
    DOMAIN: vol.Schema(
      {
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
      }
    )
  },
  extra=vol.ALLOW_EXTRA,
)

SCAN_INTERVAL = timedelta(minutes=5)

async def async_setup(hass, config):
  conf = config[DOMAIN]
  username = conf[CONF_USERNAME]
  password = conf[CONF_PASSWORD]

  api = ClimkitAPI(username, password)
  await api.authenticate()

  site_id = await api.get_site_id()
  if not site_id:
    _LOGGER.error("No site ID found.")
    return False

  meters = await api.get_meter_list(site_id)

  async def update_sensors(now):
    for meter in meters:
      meter_id = meter["id"]
      meter_type = meter.get("type")
      meter_mode = meter.get("mode")
      meter_name = meter.get("name")
      address = meter.get("site_address", meter_name or meter_id)

      # Create unique sensor name
      sensor_name = f"sensor.{address.lower().replace(' ', '_')}_{meter_type}_{meter_mode}_{meter_id}"

      # Determine device class and unit
      if meter_type in ["electricity", "heating"]:
        device_class = "energy"
        unit = "kWh"
      elif meter_type in ["cold_water", "hot_water"]:
        device_class = "water"
        unit = "m³"
      else:
        device_class = None
        unit = None

      data = await api.get_meter_data(site_id, meter_id)
      value = data.get("value", 0)  # Adjust based on actual API response structure

      sensor = ClimkitSensor(sensor_name, value, device_class, unit, meter)
      hass.states.async_set(sensor_name, value, sensor.extra_state_attributes)

  async_track_time_interval(hass, update_sensors, SCAN_INTERVAL)
  await update_sensors(None)

  return True

async def async_setup_entry(hass, config_entry):
    """Set up Climkit from a config entry."""
    conf = config_entry.data
    username = conf["username"]
    password = conf["password"]

    api = ClimkitAPI(username, password)
    await api.authenticate()

    sites = await api.get_site_id()
    if not sites:
        _LOGGER.error("No sites found.")
        return False

    async def update_sensors(now):
        for site in sites:
            site_id = site["site_id"]
            meters = await api.get_meter_list(site_id)

            for meter in meters:
                meter_id = meter["id"]
                meter_type = meter.get("type")
                meter_mode = meter.get("mode")
                meter_name = meter.get("name")
                address = meter.get("site_address", meter_name or meter_id)

                # Create unique sensor name
                sensor_name = f"sensor.{address.lower().replace(' ', '_')}_{meter_type}_{meter_mode}_{meter_id}"

                # Determine device class and unit
                if meter_type in ["electricity", "heating"]:
                    device_class = "energy"
                    unit = "kWh"
                elif meter_type in ["cold_water", "hot_water"]:
                    device_class = "water"
                    unit = "m³"
                else:
                    device_class = None
                    unit = None

                data = await api.get_meter_data(site_id, meter_id)
                value = data.get("value", 0)  # Adjust based on actual API response structure

                sensor = ClimkitSensor(sensor_name, value, device_class, unit, meter)
                hass.states.async_set(sensor_name, value, sensor.extra_state_attributes)

    async_track_time_interval(hass, update_sensors, SCAN_INTERVAL)
    await update_sensors(None)

    return True

class ClimkitSensor(Entity):
  def __init__(self, name, value, device_class, unit, meter):
    self._name = name
    self._state = value
    self._device_class = device_class
    self._unit = unit
    self._meter = meter

  @property
  def name(self):
    return self._name

  @property
  def state(self):
    return self._state

  @property
  def device_class(self):
    return self._device_class

  @property
  def unit_of_measurement(self):
    return self._unit

  @property
  def state_class(self):
    return "total_increasing"

  @property
  def extra_state_attributes(self):
    return {
      "integration": DOMAIN,
      "mode": self._meter.get("mode"),
      "type": self._meter.get("type"),
      "meter_id": self._meter.get("id"),
      "is_rule_meter": self._meter.get("is_rule_meter"),
    }
