import numpy as np

#Kalman filters
import filterpy as fp

#signal processing
import scipy as sp

#wavelet processing
#simport pywavelets

#Baysian filters
import pyprob

class KalmanFilter:
    #Linear Kalman Filter with filterpy
    def __init__(self, dim_x=2, dim_z=1):
        super.__init__()

        self.kf = fp.KalmanFilter(dim_x, dim_z)

        #State vector (x): This is the vector that represents the current state of the system. In our case, we might have position and velocity, so it's a 2D vector.
        #State covariance matrix (P): This represents the uncertainty in the state estimate.
        #State transition matrix (F): This describes how the state evolves from one time step to the next.
        #Measurement matrix (H): This relates the state vector to the measurements.
        #Measurement noise covariance (R): This represents the uncertainty in the measurements.
        #Process noise covariance (Q): This represents the uncertainty in the process model.

        # Initial State
        self.kf.x = np.zeros((dim_x, 1))

        # Initial uncertainty
        self.kf.P = np.eye(dim_x) * 1000 # Initial uncertainty is high

        # State transition matrix
        self.kf.F = np.eye(dim_x) * 1000

        # Measurement function

        self.kf.H = np.zeros((dim_X, 1))