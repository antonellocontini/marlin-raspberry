import logging
import numpy as np
import utm
import time

from marlin.Provider import Provider
from marlin.utils import closestPointOnLine, directionError
from marlin.utils import clip, headingToVector, pointDistance
from simple_pid import PID


class Autonomy:
    def __init__(self, offset=4, min_distance=5):
        self.logger = logging.getLogger(__name__)
        self.is_running = False
        self.pid = (-1, 0, 0.5)
        self.coordinates = np.array([])
        self.coordinates_lat_long = []
        self.next_target = 0
        self.loop_thread = None
        self.pid_controller = PID(*self.pid)
        self.GPS = Provider().get_GPS()
        self.APS = Provider().get_AbsolutePositionSensor()
        self.heading_sensor = Provider().get_heading()
        self.offset = offset
        self.min_distance = min_distance
        self.speed = 30
        self.name = 'autonomy'
        self.is_go_home = False
        self.off_timestamp = time.time()

    def set_coordinates(self, coordinates, is_go_home=False):
        self.is_go_home = is_go_home
        self.coordinates_lat_long = coordinates
        self.coordinates = []
        for coord in coordinates:
            c = utm.from_latlon(coord['lat'], coord['lng'])[:2]
            self.coordinates.append(c)

        self.coordinates = np.array(self.coordinates)
        self.logger.debug('Set autonomy path to {}'.format(self.coordinates))
        self.next_target = 0

    def set_pid(self, pid):
        self.pid = pid

    def set_speed(self, speed):
        self.speed = clip(speed, 0, 100)
        self.logger.debug('Set speed to {}'.format(self.speed))

    def start(self):
        self.is_running = True
        self.pid_controller = PID(*self.pid)
        self.logger.info('Start autonomy')

    def stop(self):
        self.off_timestamp = time.time()
        self.is_running = False
        self.next_target = 0
        self.coordinates_lat_long = []
        self.coordinates = []
        self.is_go_home = False
        self.logger.info('Stop autonomy')

    def is_active(self):
        return self.is_running

    def get_id(self):
        if self.is_go_home:
            return 2
        else: 
            return 1
    
    def get_info(self):
        return {
            "speed": self.speed,
            "reached_point": self.next_target,
            "waypoints": self.coordinates_lat_long
        }

    def get_state(self):
        # if not running or reached last point
        boat_position = utm.from_latlon(self.GPS.state['lat'],
                                        self.GPS.state['lng'])[:2]

        # select next waypoint
        while True:
            # check that boat is running and there are point left
            if not self.is_running or self.next_target >= len(self.coordinates):
                self.logger.info('Last waypoint reached')
                self.stop()
                return {'trust': 0, 'turn': 0, 'scale': 0}

            # check if we reached waypoint
            waypoint = self.coordinates[self.next_target]
            if pointDistance(boat_position, waypoint) > self.min_distance:
                break

            self.next_target += 1
            self.logger.debug('Reached target {}'.format(self.next_target-1))

        target_position = self.coordinates[self.next_target]

        if not self.is_go_home and self.next_target > 0:
            target_position = closestPointOnLine(
                self.coordinates[self.next_target - 1],
                self.coordinates[self.next_target],
                boat_position, self.offset)

        #boat_direction = headingToVector(self.APS.state['heading'])
        boat_direction = headingToVector(self.heading_sensor.get_state())

        error = directionError(boat_position, target_position, boat_direction)
        correction = self.pid_controller(error)

        # if boat is point in opposite direction turn on the spot
        trust = 500*(1.0-error) if abs(error) < 0.5 else 0
        trust = trust * self.speed/100.0
        turn = 500 * clip(correction, -1, 1)
        return {'trust': trust, 'turn': turn, 'scale': 1}

