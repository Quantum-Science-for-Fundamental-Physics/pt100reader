import sys
import serial
import serial.tools.list_ports
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel
from PyQt6.QtCore import QTimer, QSettings
import json
from pt100refactor.SerialReader import *
import numpy as np
import qdarktheme
import Graph
import DefaultSettings
import os

config_folder = os.path.relpath("../pt100_controller_config")
if not os.path.exists(config_folder):
    os.makedirs(config_folder, exist_ok=True)  # create folder if it doesn't exist
    config_file = os.path.join(config_folder, "settings.ini")
    settings = QSettings(config_file, QSettings.Format.IniFormat)
    DefaultSettings.generate_default_settings(settings)
else:
    config_file = os.path.join(config_folder, "settings.ini")
    settings = QSettings(config_file, QSettings.Format.IniFormat)

NUM_SENSORS = int(settings.value("hardware/NUM_SENSORS", type=int))
# standard PT100 (IEC 60751 Class B) constant:
ALPHA = settings.value("hardware/ALPHA", type=float)
VREF = settings.value("hardware/VREF", type=float)
IREF = settings.value("hardware/IREF", type=float)
WIRE_RESISTANCE = 0.5

# TODO: 
# --> implement some way to halt updating graph until values are recieved from pico
# --> Calibration!
# --> Add "wire resistance vector"
# --> Add "constant resistance vector"

#Problem: gather_data should preceed update_graph (this isn't enforced in code). Gathering data should trigger an update plot.
#Gathering data is the responsibility of picoApp, not the graph. 

class PicoApp(QWidget):
    def __init__(self):
        super().__init__() 
        self.__last_measured_temps = np.zeros((NUM_SENSORS))

        if settings.value("user/theme") == "dark":
            self.setStyleSheet(qdarktheme.load_stylesheet())
        
        #Find a nice font?
        #self.setStyleSheet("font-family: 'Helvetica'")

        self.setWindowTitle("Pico JSON Serial Interface")

        layout = QVBoxLayout()

        self.status = QLabel("Not connected")
        if settings.value("gui/display_connection_status", type=bool):
            layout.addWidget(self.status)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        if settings.value("gui/display_log", type=bool):
            layout.addWidget(self.log)

        #real time graph widget
        self.graph = Graph.RealTimeGraph()
        layout.addWidget(self.graph)
        
        # Timer to update graphs
        self.timer = QTimer()
        self.timer.timeout.connect(self.gather_data)
        self.timer.timeout.connect(self.graph.update_plot)
        self.timer.start(20)  # update every 20 ms (50 FPS)

        # Buttons
        self.btn_ping = QPushButton("Send PING")
        self.btn_ping.clicked.connect(lambda: self.send_json({"cmd": "PING"}))
        self.btn_temp = QPushButton("Get TEMPS")
        self.btn_temp.clicked.connect(lambda: self.send_json({"cmd": "TEMPS"}))
        self.btn_step = QPushButton("Step through Temp Sensors")
        self.btn_step.clicked.connect(lambda: self.send_json({"cmd": "STEP"}))
        if settings.value("gui/display_debug_buttons", type=bool):
            layout.addWidget(self.btn_ping)
            layout.addWidget(self.btn_temp)
            layout.addWidget(self.btn_step)        
            

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

    def convert_raw_to_temperature(raw_data):
        measuredVoltage = (raw_data / 65535) * VREF
        measuredResistance = ( measuredVoltage / IREF )
        #print((measuredResistance - WIRE_RESISTANCE - 100)/(ALPHA * 10**2))
        return (measuredResistance - WIRE_RESISTANCE - 100)/(ALPHA * 10**2)

    def handle_data(self, msg):
        self.log.append(f"<< {json.dumps(msg)}")
        print(msg)
        if type(msg.get("temp_values", "")) == list:
            self.__last_measured_temps = PicoApp.convert_raw_to_temperature(np.array(msg.get("temp_values", "")))

    def closeEvent(self, event):
        if hasattr(self, 'serial_thread'):
            self.serial_thread.stop()
        event.accept()

    def gather_data(self):
        self.send_json({"cmd": "TEMPS"})
        self.graph.next_data = self.__last_measured_temps[0]

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PicoApp()
    window.show()
    sys.exit(app.exec())
 