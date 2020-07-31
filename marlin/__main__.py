import argparse
import time
import logging
import threading
import json
import os
import sys
import socketio # va sempre importato nel main thread
from websocket import WebSocketException
from marlin.utils import delete_old_log, get_log_name
from marlin.Boat import Boat
from marlin.Provider import Provider
from marlin.DataLogger import DataLogger
from flask import Flask, jsonify, make_response

def handle_unhandled_exception(exc_type, exc_value, exc_traceback):
    """Handler for unhandled exceptions that will write to the logs"""
    if issubclass(exc_type, KeyboardInterrupt):
        # call the default excepthook saved at __excepthook__
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger = logging.getLogger('marlin')
    logger.critical("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))

def patch_threading_excepthook():
    """Installs our exception handler into the threading modules Thread object
    Inspired by https://bugs.python.org/issue1230540
    """
    old_init = threading.Thread.__init__
    def new_init(self, *args, **kwargs):
        old_init(self, *args, **kwargs)
        old_run = self.run
        def run_with_our_excepthook(*args, **kwargs):
            try:
                old_run(*args, **kwargs)
            except WebSocketException:
                Provider().remove_instance('socketClient')
                print("failed to emit status - waiting 3 seconds before spawning new websocket...")
                time.sleep(3)
                print("spawning a new websocket")
                socket = Provider().get_SocketClient()
                socket.start()
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                sys.excepthook(*sys.exc_info())
        self.run = run_with_our_excepthook
    threading.Thread.__init__ = new_init

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', dest='debug', action='store_true', default=False)
    config = parser.parse_args()

    sys.excepthook = handle_unhandled_exception

    DATA_FOLDER = '/var/marlin/data'
    DATA_FILE = os.path.join(DATA_FOLDER, get_log_name())
    LOG_FOLDER = '/var/marlin/log'
    LOG_LEVEL = logging.INFO if not config.debug else logging.DEBUG
    LOG_FILE = os.path.join(LOG_FOLDER, get_log_name())
    LOG_FORMAT = '%(asctime)-15s  %(levelname)-8s %(name)s: %(message)s'

    os.makedirs(DATA_FOLDER, exist_ok=True)
    os.makedirs(LOG_FOLDER, exist_ok=True)
    delete_old_log(LOG_FOLDER)
    delete_old_log(DATA_FOLDER)

    # add log to console and file
    marlinFormatter = logging.Formatter(LOG_FORMAT)
    marlinFileHandler = logging.FileHandler(filename=LOG_FILE, mode='w')
    marlinFileHandler.setFormatter(marlinFormatter)
    marlinConsoleHandler = logging.StreamHandler()
    marlinConsoleHandler.setFormatter(marlinFormatter)

    logging.getLogger('marlin').addHandler(marlinConsoleHandler)
    logging.getLogger('marlin').addHandler(marlinFileHandler)
    logging.getLogger('marlin').setLevel(LOG_LEVEL)

    dataFormatter = logging.Formatter(LOG_FORMAT)
    dataFileHandler = logging.FileHandler(filename=DATA_FILE, mode='w')
    dataFileHandler.setFormatter(dataFormatter)
    logging.getLogger('data').addHandler(dataFileHandler)
    logging.getLogger('data').setLevel(logging.INFO)

    boat = Provider().get_Boat()
    dataLogger = DataLogger()

    # HTTP
    # app = Provider().get_HttpController()
    # app.run(port=5000, host='0.0.0.0')

    # SocketIO
    #print('prova prova')
    socket = Provider().get_SocketClient()
    socket.start()
    #logging.getLogger('marlin').info('socketIO started')
    #print('socketIO started')
    #print('__main__.py')

if __name__ == "__main__":
    patch_threading_excepthook()
    main()
