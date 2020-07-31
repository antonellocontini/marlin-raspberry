import logging
import socketio
import time
from threading import Thread
from socketio.exceptions import ConnectionError
from websocket import WebSocketException

from marlin.Provider import Provider

class SocketController(socketio.ClientNamespace):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.boat = Provider().get_Boat()
        self.is_connected = False
        self.update_state_thread = Thread(target=self.update_loop)
        self.logger = logging.getLogger('marlin')

    def on_connect(self):
        self.emit('register_boat')
        print('register boat')
        self.is_connected = True
        if not self.update_state_thread.is_alive():
            self.update_state_thread.start()

    def on_start_autonomy(self, data):
        self.boat.start_autonomy(data)

    def on_stop_autonomy(self, data):
        self.boat.stop_autonomy()

    def on_set_speed(self, data):
        self.boat.set_speed(data)

    def on_set_heading(self, data):
        import json
        try:
            data = json.loads(data)
            Provider().get_heading().set_heading(data['heading'])
        except KeyError as e:
            pass
        except ValueError as e:
            pass
    
    def on_disconnect(self):
        self.is_connected = False

    def on_go_home(self, data):
        self.boat.go_home()
    
    def on_set_home(self, data):
        self.boat.set_home(data)
    
    def update_loop(self):
        while(True):
            if self.is_connected:
                try:
                     self.emit('state', self.boat.get_state())
                except ConnectionError as e:
                     self.logger.warning('failed to emit state')
                     #print("failed to send:", e)
                except WebSocketException as e:
                     self.logger.warning('WebSocketException: failed to emit state')
                except Exception as e:
                     self.logger.error('emit - generic exception: ' + e)
                     self.logger.warning('Retrying send...')
            time.sleep(1)

class SocketIOClient():
    def __init__(self, ip='localhost', port=5000):
        self.logger = logging.getLogger('marlin')
        self.sio = socketio.Client()
        self.sc = SocketController()
        self.sio.register_namespace(self.sc)
        #print('prova socketio')
        while True:
            try:
                self.sio.connect('http://{}:{}'.format(ip, port))
                self.logger.info('Connected to http://{}:{}'.format(ip, port))
                print('ok websocket')
                break
            except ConnectionError as e:
                self.logger.warning('Cannot connect -- retrying...')
                print('retrying websocket')
                time.sleep(1)
                continue
            
            break
    
    def start(self):
        self.sio.wait()
        print("websocket connection has been closed")


