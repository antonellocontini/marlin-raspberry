import logging
from datetime import datetime
import time

from threading import Thread
from marlin.Provider import Provider

class DataLogger:
    def __init__(self):
        self.logger = logging.getLogger('data')
        self.boat = Provider().get_Boat()
        self.loop_thread = Thread(target=self.log_loop)
        self.loop_thread.start()
        

    def log_loop(self):
        print('start logger')
        while True:
            state = self.boat.get_state()
            state['timestamp'] = datetime.now().timestamp()
            self.logger.info(state)
            time.sleep(1)
            
            





