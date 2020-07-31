import logging
import time
import os

from marlin.Provider import Provider
from marlin.utils import clip
from threading import Thread
from datetime import datetime

RIGHT_MOTOR_PIN = 17
LEFT_MOTOR_PIN = 27
MAX_SPEED = 2000
MIN_SPEED = 1000
IS_PI = False


if os.getenv('NOPI') is None:
    import pigpio


class MotorController:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.dataLogger = logging.getLogger('data')
        self.left_motor = None
        self.right_motor = None
        self.controllers = [Provider().get_RC(),Provider().get_Autonomy()]

        self.on = False
        self.stop = False
        self.driving_mode = -1
        self.state = {'speed': 0, 'turn': 0, 'scale': 0}

        if os.getenv('NOPI') is None:
            self.pi = pigpio.pi()

        self.setup()
        self.turn_on()
        self.loop_thread = Thread(target=self.update_loop)
        self.loop_thread.start()

    def setup(self):
        if os.getenv('NOPI') is None:
            self.pi.set_mode(RIGHT_MOTOR_PIN, pigpio.OUTPUT)
            self.pi.set_mode(LEFT_MOTOR_PIN, pigpio.OUTPUT)
            self.pi.set_pull_up_down(RIGHT_MOTOR_PIN, pigpio.PUD_OFF)
            self.pi.set_pull_up_down(LEFT_MOTOR_PIN, pigpio.PUD_OFF)

    def set_engine_state(self, speed, turn, scale):
        self.state = {'speed': speed, 'turn': turn, 'scale': scale}
        l_speed = r_speed = speed
        l_speed += turn / 2
        r_speed -= turn / 2

        offset = 0
        top_limit = max(l_speed, r_speed)
        bottom_limit = min(l_speed, r_speed)

        if top_limit > 500:
            offset = top_limit - 500
        if bottom_limit < -500:
            offset = bottom_limit + 500

        l_speed = (l_speed - offset) * scale + 1500
        r_speed = (r_speed - offset) * scale + 1500
        l_speed = clip(l_speed, 1000, 2000)
        r_speed = clip(r_speed, 1000, 2000)

        data = {'left_motor':(l_speed-1500)/500,
                'right_motor':(r_speed-1500)/500,
                'timestamp':datetime.now().timestamp()}

        self.dataLogger.info(data)

        if os.getenv('NOPI') is None:
            self.pi.set_servo_pulsewidth(LEFT_MOTOR_PIN, l_speed)
            self.pi.set_servo_pulsewidth(RIGHT_MOTOR_PIN, r_speed)

    def turn_on(self):
        if os.getenv('NOPI') is None:
            self.pi.set_servo_pulsewidth(RIGHT_MOTOR_PIN, 1500)
            self.pi.set_servo_pulsewidth(LEFT_MOTOR_PIN, 1500)

        # wait 2 second for motors to start
        time.sleep(2)
        self.on = True

    def update_loop(self):
        while not self.stop:
            active_controller = False
            for controller in self.controllers:
                if controller.is_active():
                    #self.logger.info("active controller: " + controller.name)
                    state = controller.get_state()
                    self.set_engine_state(state['trust'],
                                          state['turn'],
                                          state['scale'])
                    active_controller = True
                    self.driving_mode = controller.get_id()
                    break
            if not active_controller:
                    self.set_engine_state(0, 0, 0)
                    self.driving_mode = -1
            time.sleep(0.05)
