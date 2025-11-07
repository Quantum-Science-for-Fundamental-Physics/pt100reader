import sys
import serial
import serial.tools.list_ports
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel
from PyQt6.QtCore import QThread, pyqtSignal
import json

# Background thread to read from serial
class SerialReader(QThread):
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

class PicoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pico JSON Serial Interface")

        layout = QVBoxLayout()
        self.status = QLabel("Not connected")
        layout.addWidget(self.status)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log)

        # Buttons
        self.btn_ping = QPushButton("Send PING")
        self.btn_ping.clicked.connect(lambda: self.send_json({"cmd": "PING"}))
        layout.addWidget(self.btn_ping)

        self.btn_temp = QPushButton("Get TEMP")
        self.btn_temp.clicked.connect(lambda: self.send_json({"cmd": "TEMP"}))
        layout.addWidget(self.btn_temp)

        self.setLayout(layout)

        # Auto-detect Pico serial port
        ports = [p.device for p in serial.tools.list_ports.comports() if "Pico" in p.name or "USB Serial" in p.name or "MicroPython" in p.name or "ttyACM0" in p.name or "ttyUSB" in p.name]

        if not ports:
            self.log.append("No Pico found!")
            return
        port = ports[0]
        self.status.setText(f"Connected to {port}")

        self.serial_thread = SerialReader(port)
        self.serial_thread.data_received.connect(self.handle_data)
        self.serial_thread.start()

    def send_json(self, msg):
        if hasattr(self, 'serial_thread'):
            self.serial_thread.send(msg)
            self.log.append(f">> {json.dumps(msg)}")

    def handle_data(self, msg):
        self.log.append(f"<< {json.dumps(msg)}")

    def closeEvent(self, event):
        if hasattr(self, 'serial_thread'):
            self.serial_thread.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PicoApp()
    window.show()
    sys.exit(app.exec())
