from PyQt6.QtCore import QObject, pyqtSignal
import time
import random
from scipy.signal import butter, filtfilt


class DataWorker(QObject):
    '''This class handles storing and real time filtering the data acquired by Serial Reader'''
    data_updated = pyqtSignal(list, int)

    def __init__(self, sensor_id, settings, filter=None):
        super().__init__()
        self.sensor_id = sensor_id
        self.filter = filter
        self.cutoff = 5 #hz
        self.fs = 100 #hz- guesstimate. Just find a nice value.
        self.raw_data = []

        self.settings = settings
        self.VREF = settings.get("hardware/VREF", type=float)
        self.IREF = settings.get("hardware/IREF", type=float)
        self.ALPHA = settings.get("hardware/ALPHA", type=float)
        self.WIRE_RESISTANCE = 0.5



    def lowpass_filter(self, data, cutoff, fs, order=5):
        """
        Apply a low-pass Butterworth filter.

        Parameters:
            data : 1D array of samples
            cutoff : float, cutoff frequency in Hz
            fs : float, sampling frequency in Hz
            order : int, filter order
        """
        if len(data) <= 18:
            return data
        
        nyquist = 0.5 * fs
        normal_cutoff = cutoff / nyquist
        b, a = butter(order, normal_cutoff, btype='lowpass', analog=False)
        filtered_data = filtfilt(b, a, data)
        return filtered_data
    
    def convert_raw_to_temperature(self, raw_data):
        measuredVoltage = (raw_data / 65535) * self.VREF
        measuredResistance = ( measuredVoltage / self.IREF )
        return (measuredResistance - self.WIRE_RESISTANCE - 100)/(self.ALPHA * 10**2)

    def set_interval(self, filter):
        self.filter = filter  # called when settings change
    
    def handle_data(self, values):
        self.raw_data.append(self.convert_raw_to_temperature(values['temp_values'][self.sensor_id]))
        if self.filter == "lowpass":
            self.data_updated.emit(self.lowpass_filter(self.raw_data, self.cutoff, self.fs), self.sensor_id)
        else:
            self.data_updated.emit(self.raw_data, self.sensor_id)