#!/usr/bin/env python3

from absl import logging
from . import Sensor

import adafruit_lps28

class Lps28(Sensor):
  I2C_ADDRESS = 0x5C

  def __init__(self, remotestorage, localstorage, timesource, i2c, **kwargs):
    super().__init__(remotestorage, localstorage, timesource)
    self.sensor = adafruit_lps28.LPS28(i2c)
    self.name = "Lps28"

  def publish(self):
    logging.info('Publishing LPS28 Data')
    result = False

    try:
      # It is actually important that the try_write_to_remote happens before the result, otherwise
      # it will never be evaluated!
      result = self._try_write('LPS28', 'temperature_C', self.sensor.temperature) or result
    except Exception as err:
      self._try_write_error('LPS28', 'temperature_C', str(err))
      logging.error("Error getting data from LPS28.  Is this sensor correctly installed and the cable attached tightly:  " + str(err));
      result = self.name 

    try:
      # It is actually important that the try_write_to_remote happens before the result, otherwise
      # it will never be evaluated!
      result = self._try_write('LPS28', 'pressure_hPa', self.sensor.pressure) or result
    except Exception as err:
      self._try_write_error('LPS28', 'pressure_hPa', str(err))
      logging.error("Error getting data from LPS28.  Is this sensor correctly installed and the cable attached tightly:  " + str(err));
      result = self.name 

    return result
