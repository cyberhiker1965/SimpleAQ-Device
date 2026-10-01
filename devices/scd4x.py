#!/usr/bin/env python3

from absl import logging
from . import Sensor

import adafruit_scd4x

class Scd4x(Sensor):
  I2C_ADDRESS = 0x62

  def __init__(self, remotestorage, localstorage, timesource, i2c, **kwargs):
    super().__init__(remotestorage, localstorage, timesource)
    self.sensor = adafruit_scd4x.SCD4X(i2c)
    self.name = "SCD4X"
    self.has_reported_serial = False

    self.serial_number = "".join(f"{word:04X}" for word in self.sensor.serial_number)
    self.sensor.start_periodic_measurement()

  def publish(self):
    logging.info('Publishing SCD4X Data')
    result = False

    if self.sensor.data_ready:
      if not self.has_reported_serial:
        try:
          # It is actually important that the try_write_to_remote happens before the result, otherwise
          # it will never be evaluated!
          result = self._try_write('SCD4X', 'serial_number', self.serial_number) or result
          self.has_reported_serial = True
        except Exception as err:
          self._try_write_error('SCD4X', 'serial_number', str(err))
          logging.error("Error getting data from SCD4X.  Is this sensor correctly installed and the cable attached tightly:  " + str(err));
          result = self.name

      try:
        # It is actually important that the try_write_to_remote happens before the result, otherwise
        # it will never be evaluated!
        result = self._try_write('SCD4X', 'temperature_C', self.sensor.temperature) or result
      except Exception as err:
        self._try_write_error('SCD4X', 'temperature_C', str(err))
        logging.error("Error getting data from SCD4X.  Is this sensor correctly installed and the cable attached tightly:  " + str(err));
        result = self.name 

      try:
        # It is actually important that the try_write_to_remote happens before the result, otherwise
        # it will never be evaluated!
        result = self._try_write('SCD4X', 'co2_ppm', self.sensor.CO2) or result
      except Exception as err:
        self._try_write_error('SCD4X', 'co2_ppm', str(err))
        logging.error("Error getting data from SCD4X.  Is this sensor correctly installed and the cable attached tightly:  " + str(err));
        result = self.name 

      try:
        # It is actually important that the try_write_to_remote happens before the result, otherwise
        # it will never be evaluated!
        result = self._try_write('SCD4X', 'relative_humidity_pct', self.sensor.relative_humidity) or result
      except Exception as err:
        self._try_write_error('SCD4X', 'relative_humidity_pct', str(err))
        logging.error("Error getting data from SCD4X.  Is this sensor correctly installed and the cable attached tightly:  " + str(err));
        result = self.name 

    return result
