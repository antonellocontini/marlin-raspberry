from bitstring import BitArray
import serial
import time

s = serial.Serial(port='/dev/rc', baudrate=100000, 
                  bytesize=serial.EIGHTBITS, parity=serial.PARITY_EVEN,
                  stopbits=serial.STOPBITS_ONE)
time.sleep(0.1)


def get_last_frame(data):
    bits = BitArray(data)
    frames = list(bits.findall(BitArray(hex='000f')))
    print(frames[-1]-frames[-2])
    return bits[frames[-2]:frames[-1]]


def read_data(frame):
    chs = [0]*16
    bytes_data = [frame[i*8:(i+1)*8] for i in range(2, 24)]

    chs[0]  = bytes_data[0].uint       | bytes_data[1].uint  << 8                        & 2047
    chs[1]  = bytes_data[1].uint  >> 3 | bytes_data[2].uint  << 5                        & 2047
    chs[2]  = bytes_data[2].uint  >> 6 | bytes_data[3].uint  << 3 | bytes_data[4].uint << 10  & 2047
    chs[3]  = bytes_data[4].uint  >> 1 | bytes_data[5].uint  << 7                        & 2047
    chs[4]  = bytes_data[5].uint  >> 4 | bytes_data[6].uint  << 4                        & 2047
    chs[5]  = bytes_data[6].uint  >> 7 | bytes_data[7].uint  << 1 | bytes_data[8].uint <<  9  & 2047
    chs[6]  = bytes_data[8].uint  >> 2 | bytes_data[9].uint  << 6                        & 2047
    chs[7]  = bytes_data[9].uint  >> 5 | bytes_data[10].uint << 3                        & 2047
    chs[8]  = bytes_data[11].uint      | bytes_data[12].uint << 8                        & 2047
    chs[9]  = bytes_data[12].uint >> 3 | bytes_data[13].uint << 5                        & 2047
    chs[10] = bytes_data[13].uint >> 3 | bytes_data[14].uint << 2 | bytes_data[15].uint << 10 & 2047
    chs[11] = bytes_data[15].uint >> 3 | bytes_data[16].uint << 7                        & 2047
    chs[12] = bytes_data[16].uint >> 3 | bytes_data[17].uint << 4                        & 2047
    chs[13] = bytes_data[17].uint >> 3 | bytes_data[18].uint << 1 | bytes_data[19].uint << 9  & 2047
    chs[14] = bytes_data[19].uint >> 3 | bytes_data[20].uint << 6                        & 2047
    chs[15] = bytes_data[20].uint >> 3 | bytes_data[21].uint << 3                        & 2047
    print(chs)

    return chs


while 1:
    data = s.read_all()
    frame = get_last_frame(data)
    print(read_data(frame))
    time.sleep(0.1)
