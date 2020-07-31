import eventlet
import socketio
import time
from threading import Thread

sio = socketio.Server()
app = socketio.WSGIApp(sio)
boat = None

@sio.event
def connect(sid, environ):
    print('connect', sid)

@sio.event
def disconnect(sid):
    print('disconnect ', sid)
    if sid == boat:
        boat == None

@sio.event
def register_boat(sid):
    print('register_boat')
    global boat
    boat = sid
    print(boat)

@sio.on('state')
def on_state(sid, data):
    print('state recived')
    sio.emit('state', data, skip_sid=sid)



@sio.event
def start_autonomy(sid, data):
    print('start autonomy', data)
    send_to_boat('start_autonomy', data, sid)

@sio.event
def stop_autonomy(sid):
    print('stop autonomy')
    send_to_boat('stop_autonomy', sid=sid)

@sio.event
def set_speed(sid, data):
    print('set_speed', data)
    send_to_boat('set_speed', data, sid)


def send_to_boat(event, data=None, sid=None):
    if boat is not None:
        if data is not None:
            sio.emit(event, data, room=boat)
        else:
            print('is None')
            sio.emit(event, room=boat)
        print('sent to boat')
    else:
        sio.emit('error','boat not connected', room=sid)
        print('boat not connected')



if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 4000)), app)
