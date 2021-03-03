import numpy as np
import glob
import os
import datetime


def pointDistance(x, y):
    d = (x[0]-y[0])**2 + (x[1]-y[1])**2
    return np.sqrt(d)


def clip(x, xmin, xmax):
    return min(max(x, xmin), xmax)


def closestPointOnLine(a, b, p, offset=0):
    ap = p - a
    ab = b - a

    # project point onto line
    result = a + np.dot(ap, ab) / np.dot(ab, ab) * ab

    # add offset
    result = result + (ab / np.linalg.norm(ab) * offset)

    # check if point outside line
    scale = np.dot(result - a, ab) / np.dot(ab, ab)
    if scale >= 1:
        return b

    return result


def directionError(position, goal, direction):
    d1 = goal - position
    d1 = d1/np.linalg.norm(d1)
    err = np.arccos(np.dot(d1, direction))*2/np.pi
    err *= np.sign(np.cross(d1, direction))
    return err


def headingToVector(heading):
    rad = heading*np.pi/180
    return np.array([np.sin(rad), np.cos(rad)])


class SensorExistsException(Exception):
    def __init__(self, sensor_name):
        super().__init__('sensor {} already exists'.format(sensor_name))


def delete_old_log(path, n=100):
    files = sorted(glob.glob(os.path.join(path,'*.log')))
    if len(files) > n:
        for f in files[:len(files)-n]:
            os.remove(f)

def get_log_name():
    now = datetime.datetime.now()
    return now.strftime('%Y%m%d-%H%M%S')+'.log'


class KalmanFilter(object):
    def __init__(self, F = None, B = None, H = None, Q = None, R = None, P = None, x0 = None):

        if(F is None or H is None):
            raise ValueError("Set proper system dynamics.")

        self.n = F.shape[1]
        self.m = H.shape[1]

        self.F = F
        self.H = H
        self.B = 0 if B is None else B
        self.Q = np.eye(self.n) if Q is None else Q
        self.R = np.eye(self.n) if R is None else R
        self.P = np.eye(self.n) if P is None else P
        self.x = np.zeros((self.n, 1)) if x0 is None else x0

    def predict(self, u = 0):
        self.x = np.dot(self.F, self.x) + np.dot(self.B, u)
        self.P = np.dot(np.dot(self.F, self.P), self.F.T) + self.Q
        return self.x

    def update(self, z):
        y = z - np.dot(self.H, self.x)
        S = self.R + np.dot(self.H, np.dot(self.P, self.H.T))
        K = np.dot(np.dot(self.P, self.H.T), np.linalg.inv(S))
        self.x = self.x + np.dot(K, y)
        I = np.eye(self.n)
        self.P = np.dot(np.dot(I - np.dot(K, self.H), self.P), 
            (I - np.dot(K, self.H)).T) + np.dot(np.dot(K, self.R), K.T)