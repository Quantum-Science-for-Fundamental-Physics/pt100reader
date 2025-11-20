from PyQt6.QtCore import QThread, pyqtSignal
import serial
import json
import time

class SerialReader(QThread):
    '''background thread to read from serial'''
    data_received = pyqtSignal(object)

    def __init__(self, port, baud=115200):
        print("Serial Reader Initializing")
        super().__init__()
        self.ser = serial.Serial(port, baud, timeout=1)
        self.ser.flush()
        self.running = True

    def run(self):
        while self.running:
            try:
                self.send({"cmd": "TEMPS"})
                #time.sleep(0.1)
            except:
                pass
            if self.ser.in_waiting:
                while True:
                    try:
                        line = self.ser.readline().decode(errors='ignore').strip()
                        break
                    except serial.SerialException as e:
                        print(f"Serial exception: {e}")
                if not line:
                    continue
                try:
                    msg = json.loads(line)
                    self.data_received.emit(msg)
                except json.JSONDecodeError:
                    # malformed line
                    #self.data_received.emit({"error": "Invalid JSON: " + line})
                    pass

    def send(self, cmd: dict):
        self.ser.write((json.dumps(cmd) + "\n").encode())

    def stop(self):
        self.running = False
        self.ser.close()