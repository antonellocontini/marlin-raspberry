import logging
import time
import os

from Adafruit_BNO055 import BNO055
from threading import Thread


class AbsolutePositionSensor:
    SENSOR_UDPDATE_TIME_S = 0.5

    def __init__(self, port, rst):
        self.logger = logging.getLogger(__name__)
        self.port = port
        self.rst = rst
        self.state = {
            'heading': 0,
            'roll': 0,
            'pitch': 0,
            'sys_cal': 0,
            'gyro_cal': 0,
            'accel_cal': 0,
            'mag_cal': 0
        }
        self.stop = False

        if os.getenv('NOPI') is not None:
            self.logger.warning('Absolute Position Sensor not working on this platform')
            return

        self.sensor = BNO055.BNO055(serial_port=port, rst=rst)
        self.setup()
        self.loop_thread = Thread(target=self.update_loop)
        self.loop_thread.start()

    def setup(self):
        while 1:
            try:
                self.sensor.begin()
                status, self_test, error = self.sensor.get_system_status()
                self.logger.debug('System status: {0}'.format(status))
                self.logger.debug(
                    'Self test result (0x0F is normal): 0x{0:02X}'.format(self_test))
                break
            except Exception as e:
                self.logger.warning(e)
                time.sleep(1)

        time.sleep(1)
        self.sensor.set_axis_remap(
                BNO055.AXIS_REMAP_Y,
                BNO055.AXIS_REMAP_Z,
                BNO055.AXIS_REMAP_X)
        self.logger.debug('APS axis remapped')
        time.sleep(1)

        # Print out an error if system status is in error mode.
        if status == 0x01:
            self.logger.error('System error: {0}'.format(error))
            self.logger.error('See datasheet section 4.3.59 for the meaning.')
        else:
            self.logger.info('APS OK')

    def update_loop(self):
        while not self.stop:
            (self.state['heading'], self.state['roll'],
             self.state['pitch']) = self.sensor.read_euler()
            self.state['heading'] = (self.state['heading']+90) % 360
            (self.state['sys_cal'], self.state['gyro_cal'],
             self.state['accel_cal'],
             self.state['mag_cal']) = self.sensor.get_calibration_status()

            # read sensor every SENSOR_UDPDATE_TIME_S
            time.sleep(time.time() % self.SENSOR_UDPDATE_TIME_S)

    def stop(self):
        self.stop = True
        self.logging.info('closing Absolute Position Sensor')
        self.loop_thread.join()
        self.sensor.close()

if __name__ == '__main__':
    import time
    a = AbsolutePositionSensor('/dev/serial0', 18)
    while True:
        print('---------------')
        print(a.sensor.get_calibration_status())
        time.sleep(1)

    a.stop = True


