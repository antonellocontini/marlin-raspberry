import logging
import spidev
import os
from numpy import interp
from marlin.Provider import Provider

if os.getenv('NOPI') is None:
    import RPi.GPIO as GPIO

class Battery:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.value = 0
        self.unit = 'V'
        self.channel = 7
        self.spi = spidev.SpiDev()

        if os.getenv('NOPI') is not None:
            self.logger.warning('Battery sensor not available on this platform')
            return

        self.spi.open(0,0)
        self.spi.max_speed_hz = 1350000


    def get_state(self):
        if os.getenv('NOPI') is not None:
            return {'name': 'battery', 'value': -1, 'data': -1, 'unit': self.unit}

        adc = self.spi.xfer2([1,(8+self.channel)<<4,0])
        data = ((adc[1]&3)<<8) + adc[2]
        self.value = 0.1118 * data - 0.2548
        return {'name': 'battery',
                'value': self.value,
                'data':data,
                'unit': self.unit}


if __name__ == '__main__':
    import time
    b = Battery()
    for i in range(100):
        print(b.get_state())
        time.sleep(1)

