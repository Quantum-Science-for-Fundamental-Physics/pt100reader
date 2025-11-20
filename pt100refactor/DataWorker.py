from PyQt6.QtCore import QObject, pyqtSignal
import time
import random

class DataWorker(QObject):
    '''This class handles storing and real time filtering the data acquired by Serial Reader'''
    data_updated = pyqtSignal(float, int)

    def __init__(self, sensor_id, filter=None):
        super().__init__()
        self.sensor_id = sensor_id
        self.filter = filter
        
        #Each DataWorker listens to SerialReader's output.

    def set_interval(self, filter):
        self.filter = filter  # called when settings change
    
    def handle_data(self, values):
        self.data_updated.emit(values['temp_values'][self.sensor_id], self.sensor_id)
        
