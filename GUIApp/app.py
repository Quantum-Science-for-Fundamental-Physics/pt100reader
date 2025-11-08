import sys
import serial
import serial.tools.list_ports
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel
from PyQt6.QtCore import QTimer
import json
from Helper import *
import pyqtgraph as pg
import numpy as np
import time

# TODO: 
# --> add real time graph that updates temp data from pico!
#     |--> implement some way to pause until values is recieved from pico
# -->Calibration!

NUM_SENSORS = 8

class PicoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.__last_measured_temps = np.zeros((NUM_SENSORS))

        self.setWindowTitle("Pico JSON Serial Interface")

        layout = QVBoxLayout()
        self.status = QLabel("Not connected")
        layout.addWidget(self.status)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log)

        #real time graph widget
        self.plot_widget = pg.PlotWidget(background='w')
        layout.addWidget(self.plot_widget)

        #the actual line on the graph
        pen = pg.mkPen(color=(0, 100, 255), width=2)
        self.curve = self.plot_widget.plot(pen=pen)
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.setLabel('left', 'Value')
        self.plot_widget.setLabel('bottom', 'Time')

        # Data buffer
        self.xdata = np.linspace(0, 10, 1000)
        self.ydata = np.zeros(1000)

        #Temporary! Remove!
        self.plot_widget.setYRange(5150, 5250)

        # Timer to update the graph
        self.timer = QTimer()
        self.timer.timeout.connect(self.gather_data)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(20)  # update every 20 ms (50 FPS)

        self.phase = 0

        # Buttons
        self.btn_ping = QPushButton("Send PING")
        self.btn_ping.clicked.connect(lambda: self.send_json({"cmd": "PING"}))
        layout.addWidget(self.btn_ping)

        self.btn_temp = QPushButton("Get TEMPS")
        self.btn_temp.clicked.connect(lambda: self.send_json({"cmd": "TEMPS"}))
        layout.addWidget(self.btn_temp)

        self.btn_temp = QPushButton("Step through Temp Sensors")
        self.btn_temp.clicked.connect(lambda: self.send_json({"cmd": "STEP"}))
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
        print(msg)
        if type(msg.get("temp_values", "")) == list:
            self.__last_measured_temps[0] = msg.get("temp_values", "")[0]

    def closeEvent(self, event):
        if hasattr(self, 'serial_thread'):
            self.serial_thread.stop()
        event.accept()

    def gather_data(self):
        self.send_json({"cmd": "TEMPS"})

    def update_plot(self):

        # Shift data left and append new value
        self.ydata = np.roll(self.ydata, -1)
        self.ydata[-1] = self.__last_measured_temps[0]

        # Update the curve
        self.curve.setData(self.xdata, self.ydata)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PicoApp()
    window.show()
    sys.exit(app.exec())
