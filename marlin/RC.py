import logging
import time

from marlin.Provider import Provider
from marlin.utils import clip


class RC:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.asp = Provider().get_ArduinoSerialParser()
        self.asp.add_sensor('RC', self.set_state)
        self.listeners = set()
        self.name = 'RC'
        self.off_timestamp = time.time()
        self.state = {
            'trust': 0,  # throttle (1000-2000)
            'turn': 0,  # turn (1000-2000)
            'override': False,  # RC override
            'scale': 0,  # throttle scale (0-1)
        }

    def set_state(self, data):
        old_override = self.state['override']
        try:
            self.state['trust'] = RC.rc_to_motor_signal(data['trust'])
            self.state['turn'] = RC.rc_to_motor_signal(data['turn'])
            self.state['override'] = data['override'] > 990
            self.state['scale'] = min((data['max_power'] - 172) * 0.00061, 1)
        except KeyError as e:
            self.logger.error(e)

        if old_override != self.state['override'] and old_override is True:
            self.off_timestamp = time.time()

    def rc_to_motor_signal(x):
        signal = (x - 990) * 0.61

        # remove noise from rest position
        if abs(signal) < 6:
            signal = 0

        # ensure value between -500 and 500
        return clip(signal, -500, 500)

    def get_state(self):
        return self.state

    def is_active(self):
        return self.state['override']
    
    def get_id(self):
        return 0
