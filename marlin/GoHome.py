from threading import Thread
from collections import defaultdict
from simple_pid import PID
from marlin.Provider import Provider
from marlin.Astar import Node, A_star
from marlin.utils import headingToVector, directionError, clip, pointDistance

import utm
import time
import logging

from threading import Lock


class GoHome:
    UDPDATE_TIME_S = 0.1
    AUTOMATIC_START_S = 60

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.grid_map = defaultdict(lambda: defaultdict(lambda: None))
        self.home = None
        self.home_coords = None
        self.GPS = Provider().get_GPS()
        self.autonomy = Provider().get_Autonomy()
        self.path = None
        self.stop = False
        self.pause = False
        self.lock = Lock()

        self.loop_thread = Thread(target=self.update_loop)
        self.loop_thread.start()
        self.logger.info("Started GoHome service")

    def update_loop(self):
        while not self.stop:
            lat = self.GPS.state['lat']
            lng = self.GPS.state['lng']
            boat_position = utm.from_latlon(lat, lng)
            x, y = round(boat_position[0]/2), round(boat_position[1]/2)
            lat, lng = utm.to_latlon(x*2, y*2, boat_position[2], boat_position[3])

            self.lock.acquire()
            if self.grid_map[x][y] is None:
                self.grid_map[x][y] = Node(x, y, lat=lat, lng=lng)
            self.lock.release()

            if self.home_coords is None:
                self.home_coords = (x,y)
                self.home = self.grid_map[x][y]

            time.sleep(time.time() % self.UDPDATE_TIME_S)

    def calculate_path(self):
        lat = self.GPS.state['lat']
        lng = self.GPS.state['lng']
        boat_position = utm.from_latlon(lat, lng)
        x, y = round(boat_position[0]/2), round(boat_position[1]/2)
        self.lock.acquire()
        if self.grid_map[x][y] is None:
            self.grid_map[x][y] = Node(x, y, lat=lat, lng=lng)
        start = self.grid_map[x][y]
        self.find_closest_point_to_home()
        path = A_star(start, self.home, self.grid_map)
        self.lock.release()
        return path

    def set_home(self, lat, lng):
        self.home_coords = utm.from_latlon(lat, lng)[:2]
        self.home_coords = (self.home_coords[0]/2, self.home_coords[1]/2)
        self.logger.info("set home to {} {}".format(lat,lng))

    def find_closest_point_to_home(self):
        closest_home = None
        min_distance = 0

        for x in self.grid_map.keys():
            for y in self.grid_map[x].keys():
                if self.grid_map[x][y] is None:
                    continue
                home_distance = pointDistance(self.home_coords, (x,y))
                if closest_home is None or home_distance < min_distance:
                    closest_home = (x,y)
                    min_distance = home_distance
                    print(closest_home, min_distance)
        
        self.home = self.grid_map[closest_home[0]][closest_home[1]]
    
    def add_points(self, points):
        for x, y in points:
            x, y = round(x), round(y)
            if self.grid_map[x][y] is None:
                self.grid_map[x][y] = Node(x, y, 1, 2)

    def start(self):
        self.path = self.calculate_path().node_list
        coords = []
        for node in self.path:
            coords.append({'lat':node.lat, 'lng': node.lng})

        self.logger.info("Starting go home")
        self.autonomy.set_coordinates(coords, is_go_home=True)
        self.autonomy.start()
        

if __name__ == '__main__':
    import imageio
    import numpy as np
    import matplotlib.pyplot as plt

    image = imageio.imread('../../tmp/test.bmp')
    image = np.array(image)
    points = np.argwhere(image == 0)
    gh = GoHome()
    gh.add_points(points)
    gh.set_home((0,0))

    p = gh.calculate_path()
    image = np.expand_dims(image,2)
    image = np.repeat(image, 3, 2)
    for node in p.node_list:
        image[node.x, node.y] = [0,0,255]
    plt.imshow(image)
    plt.savefig('../../tmp/test_result.png')
