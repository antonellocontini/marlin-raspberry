import logging

from singleton_decorator import singleton
from flask import Flask, jsonify, make_response
from threading import Lock


@singleton
class Provider:
    def __init__(self):
        self.mutex = {'RC':Lock(), 'MotorController':Lock(), 'APS':Lock()}
        self.instances = {}

    def get_ArduinoSerialParser(self):
        from marlin.ArduinoSerialReader import ArduinoSerialReader
        return self._get_instace('ArduinoSerialReader', ArduinoSerialReader,
                                 '/dev/arduino')

    def get_RC(self):
        self.mutex['RC'].acquire()
        from marlin.RCPi import RCPi
        rc = self._get_instace('RC', RCPi, '/dev/rc')
        self.mutex['RC'].release()
        return  rc

    def get_GPS(self):
        from marlin.GPSSensor import GPSSensor
        return self._get_instace('GPS', GPSSensor)

    def get_heading(self):
        from marlin.HeadingSensor import HeadingSensor
        return self._get_instace('heading', HeadingSensor)

    def get_AbsolutePositionSensor(self):
        self.mutex['APS'].acquire()
        from marlin.AbsolutePositionSensor import AbsolutePositionSensor
        aps = self._get_instace(
                'APS', AbsolutePositionSensor, '/dev/serial0', 18)
        self.mutex['APS'].release()
        return aps

    def get_ACS(self):
        from marlin.acs import ACS
        return self._get_instace('ACS', ACS)

    def get_Boat(self):
        from marlin.Boat import Boat
        return self._get_instace('Boat', Boat)

    def get_HttpController(self):
        from marlin.HttpController import HttpController
        app = Flask(__name__)
        HttpController.register(app)
        return app

    def get_SocketClient(self):
        from marlin.WebSocketController import SocketIOClient
        return self._get_instace('socketClient',
                                 SocketIOClient,
				 'wais.di.univr.it',
				 4000)
                                 #'wais.intcatch.eu',
                                 #4000)
                                 #'192.168.99.27',
                                 #4000)
                                 #'localhost',
                                 #5000)

    def get_Autonomy(self):
        from marlin.Autonomy import Autonomy
        return self._get_instace('Autonomy', Autonomy)
    
    def get_GoHome(self):
        from marlin.GoHome import GoHome
        return self._get_instace('GoHome', GoHome)

    def get_BlueBoxReader(self):
        from marlin.BlueBox import BlueBoxReader
        return self._get_instace(
                'BlueBoxReader', BlueBoxReader, '/dev/bluebox')

    def get_MotorController(self):
        self.mutex['MotorController'].acquire()
        from marlin.MotorController import MotorController
        mc = self._get_instace(
                'MotorController', MotorController)
        self.mutex['MotorController'].release()
        return mc

    def _get_instace(self, key, cls, *args, **kwargs):
        if key not in self.instances:
            self.instances[key] = cls(*args, **kwargs)

        return self.instances[key]
        
    def remove_instance(self, key):
        if key in self.instances:
            del self.instances[key]
            #print("instance removed")

    def close(self):
        if 'ArduinoSerialReader' in self.instances:
            self.instances['ArduinoSerialReader'].close()

