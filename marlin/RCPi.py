import logging
import time
import serial
import os

from threading import Thread
from bitstring import BitArray, InterpretError
from marlin.utils import clip


class RCPi:
    def __init__(self, port):
        self.logger = logging.getLogger(__name__)
        self.name = 'RC'
        self.port = port
        self.state = {
            'trust': 0,  # throttle (1000-2000)
            'turn': 0,  # turn (1000-2000)
            'override': True,  # RC override
            'scale': 0,  # throttle scale (0-1)
        }

        if not os.path.exists(port):
            self.logger.warning('RC device {} not found'.format(port))
            self.serial = None
            return

        self.connect_serial(self.port)
        self.logger.info('RC OK')

    def connect_serial(self, port):
        try:
            self.serial = serial.Serial(port=port,
                                        baudrate=100000,
                                        bytesize=serial.EIGHTBITS,
                                        parity=serial.PARITY_EVEN,
                                        stopbits=serial.STOPBITS_ONE)
        except Exception as e:
            self.logger.warning(e)


    
    def read_all(self):
        buffer = []
        while True:
            data = self.serial.read(10000)
            buffer += data
            if len(data) < 10000:
                break
        return buffer

    def get_id(self):
        return 0

    def _get_last_frame(self):
        #data = self.read_all()
        data = self.serial.read_all()
        bits = BitArray(data)
        frames = list(bits.findall(BitArray(hex='000f')))
        if len(frames) < 2:
            return
        return bits[frames[-2]:frames[-1]]

    def _read_data(self, frame):
        if frame is None:
            return
        chs = [0,0, False, 0]
        bytes_data = [frame[i*8:(i+1)*8] for i in range(2, 24)]

        try:
            chs[0]  = bytes_data[0].uint       | bytes_data[1].uint  << 8                        & 2047
            chs[0] = RCPi.rc_to_motor_signal(chs[0])

            chs[1]  = bytes_data[1].uint  >> 3 | bytes_data[2].uint  << 5                        & 2047
            chs[1] = RCPi.rc_to_motor_signal(chs[1])

            chs[2]  = bytes_data[2].uint  >> 6 | bytes_data[3].uint  << 3 | bytes_data[4].uint << 10  & 2047
            chs[2] = chs[2] > 990

            chs[3]  = bytes_data[4].uint  >> 1 | bytes_data[5].uint  << 7                        & 2047
            chs[3] = clip((chs[3] - 172) * 0.00061, 0, 1)
        except Exception as e:
            self.logger.warning(e)
#        chs[4]  = bytes_data[5].uint  >> 4 | bytes_data[6].uint  << 4                        & 2047
#        chs[5]  = bytes_data[6].uint  >> 7 | bytes_data[7].uint  << 1 | bytes_data[8].uint <<  9  & 2047
#        chs[6]  = bytes_data[8].uint  >> 2 | bytes_data[9].uint  << 6                        & 2047
#        chs[7]  = bytes_data[9].uint  >> 5 | bytes_data[10].uint << 3                        & 2047
#        chs[8]  = bytes_data[11].uint      | bytes_data[12].uint << 8                        & 2047
#        chs[9]  = bytes_data[12].uint >> 3 | bytes_data[13].uint << 5                        & 2047
#        chs[10] = bytes_data[13].uint >> 3 | bytes_data[14].uint << 2 | bytes_data[15].uint << 10 & 2047
#        chs[11] = bytes_data[15].uint >> 3 | bytes_data[16].uint << 7                        & 2047
#        chs[12] = bytes_data[16].uint >> 3 | bytes_data[17].uint << 4                        & 2047
#        chs[13] = bytes_data[17].uint >> 3 | bytes_data[18].uint << 1 | bytes_data[19].uint << 9  & 2047
#        chs[14] = bytes_data[19].uint >> 3 | bytes_data[20].uint << 6                        & 2047
#        chs[15] = bytes_data[20].uint >> 3 | bytes_data[21].uint << 3                        & 2047

        return chs

    def rc_to_motor_signal(x):
        signal = (x - 990) * 0.61

        # remove noise from rest position
        if abs(signal) < 6:
            signal = 0

        # ensure value between -500 and 500
        return clip(signal, -500, 500)

    def update_state(self):
        try:
            data = self._read_data(self._get_last_frame())
        except Exception as e:
            self.logger.warning(e)
            self.connect_serial(self.port)
            data = [0,0,False,0]

        if data is not None:
            self.state = dict(zip(['trust','turn','override','scale'], data))

    def get_state(self):
        if self.serial is not None:
            self.update_state()

        return self.state

    def is_active(self):
        if self.serial is not None:
            self.update_state()
        return self.state['override']

    # def update_loop(self):
    #     while True:
    #         try:
    #             self.update_state()
    #             time.sleep(0.05)
    #         except Exception as e:
    #             self.logger.error(e)


if __name__ == '__main__':
    import time
    rc = RCPi('/dev/ttyUSB0')
    while 1:
        print(rc.is_active())
        print(rc.get_state())
        time.sleep(0.1)
    
