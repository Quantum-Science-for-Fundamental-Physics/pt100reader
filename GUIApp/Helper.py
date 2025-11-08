from PyQt6.QtCore import QThread, pyqtSignal
import serial
import json

class SerialReader(QThread):
    '''background thread to read from serial'''
    data_received = pyqtSignal(object)

    def __init__(self, port, baud=115200):
        super().__init__()
        self.ser = serial.Serial(port, baud, timeout=1)
        self.running = True

    def run(self):
        while self.running:
            if self.ser.in_waiting:
                line = self.ser.readline().decode(errors='ignore').strip()
                if not line:
                    continue
                try:
                    msg = json.loads(line)
                    self.data_received.emit(msg)
                except json.JSONDecodeError:
                    # malformed line
                    self.data_received.emit({"error": "Invalid JSON: " + line})

    def send(self, cmd: dict):
        self.ser.write((json.dumps(cmd) + "\n").encode())

    def stop(self):
        self.running = False
        self.ser.close()