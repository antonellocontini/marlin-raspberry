import logging
import time
import os

if os.getenv('NOPI') is None:
    import pigpio

from threading import Thread
from marlin.Provider import Provider


class ACS:
    S1_PIN = 23
    S2_PIN = 24
    SLEEP_TIME = 0.25

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.stop = False
        if os.getenv('NOPI') is None:
            self.pi = pigpio.pi()
        self.APS = Provider().get_AbsolutePositionSensor()
        self.loop_thread = Thread(target=self.update_loop)
        #self.loop_thread.start()
        self.calibrate()

    def setup(self):
        if os.getenv('NOPI') is not None:
            return

        self.pi.set_mode(self.S1_PIN, pigpio.OUTPUT)
        self.pi.set_mode(self.S2_PIN, pigpio.OUTPUT)
        self.pi.set_pull_up_down(self.S1_PIN, pigpio.PUD_OFF)
        self.pi.set_pull_up_down(self.S2_PIN, pigpio.PUD_OFF)

    def update_loop(self):
        self.logger.info('Start ACS')
        while not self.stop:
            if self.APS.state['mag_cal'] < 3:
                self.calibrate()
            time.sleep(1)

    def calibrate(self):
        if os.getenv('NOPI') is not None:
            return

        self.logger.debug('Start compass calibration procedure')
        # move first servo
        self.pi.set_servo_pulsewidth(self.S1_PIN, 1500)
        self.pi.set_servo_pulsewidth(self.S1_PIN, 1000)
        time.sleep(self.SLEEP_TIME)
        self.pi.set_servo_pulsewidth(self.S1_PIN, 2000)
        time.sleep(self.SLEEP_TIME)
        self.pi.set_servo_pulsewidth(self.S1_PIN, 1500)
        time.sleep(self.SLEEP_TIME)
        self.pi.set_servo_pulsewidth(self.S1_PIN, 0)

        # move second servo
        self.pi.set_servo_pulsewidth(self.S2_PIN, 1500)
        self.pi.set_servo_pulsewidth(self.S2_PIN, 1000)
        time.sleep(self.SLEEP_TIME)
        self.pi.set_servo_pulsewidth(self.S2_PIN, 2000)
        time.sleep(self.SLEEP_TIME)
        self.pi.set_servo_pulsewidth(self.S2_PIN, 1500)
        time.sleep(self.SLEEP_TIME)
        self.pi.set_servo_pulsewidth(self.S2_PIN, 0)


    def stop(self):
        self.stop = True
        self.logging.info('closing ACS')
        self.loop_thread.join()

