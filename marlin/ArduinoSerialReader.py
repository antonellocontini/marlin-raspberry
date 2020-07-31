import logging
import serial
import json
import time

from threading import Thread
from marlin.utils import SensorExistsException
logging.basicConfig(level=logging.DEBUG)


class ArduinoSerialReader:
    def __init__(self, serial_port, boud_rate=115200, timeout=5):
        self.logger = logging.getLogger(__name__)
        self.serial_port = serial_port
        self.boud_rate = boud_rate
        self.serial_connection = serial.Serial(
            self.serial_port, self.boud_rate, timeout=timeout)
        self.sensors = {}

        self.loop_thread = Thread(target=self._read_loop)
        self.stop = False
        self.loop_thread.start()

    def add_sensor(self, sensor_name, callback):
        if sensor_name in self.sensors:
            raise SensorExistsException(sensor_name)

        self.sensors[sensor_name] = callback

    def remove_sensor(self, sensor_name):
        if sensor_name in self.sensors:
            del self.sensors[sensor_name]
        else:
            self.logger.info('{} not register'.format(sensor_name))

    def _notify_sensor(self, sensor_name, data):
        if sensor_name not in self.sensors:
            return

        self.sensors[sensor_name](data)

    def _read_loop(self):
        line = ''
        while not self.stop:
            try:
                line = self.serial_connection.readline().decode()
                data = json.loads(line)
                self._notify_sensor(data['sensor'], data['data'])
            except json.JSONDecodeError as e:
                self.logger.debug(e)
            except KeyError as e:
                self.logger.debug(e)
            except TypeError as e:
                self.logger.debug(e)
            except UnicodeDecodeError as e:
                self.logger.debug(e)

    def close(self):
        self.stop = True
        self.logger.info('waiting for serial to close')
        self.serial_connection.close()
        self.loop_thread.join(timeout=60)
        if self.loop_thread.is_alive():
            self.logger.info('failed to close serial connection')
        else:
            self.logger.info('serial connection closed')


if __name__ == '__main__':
    port = '/dev/ttyACM1'
    a = ArduinoSerialReader(port)
    a.add_sensor('RC', lambda x: print('RC -> {}'.format(x)))
    time.sleep(5)
    a.close()
