import sys
from PyQt6.QtWidgets import QScrollArea, QApplication, QVBoxLayout, QLabel, QTextEdit, QMainWindow, QToolBar, QToolButton, QWidget
from PyQt6.QtCore import QTimer, QThread, QSize
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
import qdarktheme
from SettingsManager import SettingsManager
import numpy as np
from DataWorker import DataWorker
from SerialReader import SerialReader
import serial
import serial.tools.list_ports
from RealTimeGraph import RealTimeGraph
from SettingsDialog import SettingsDialog
from SensorSettings import SensorSettings

class MainWindow(QMainWindow):
    '''
    This is the main part of the GUI.
    It does not store most of the data. Most of the data read is handled by 
    DataWorker.py. It only stores the last N datapoints to display in the graph.
    These datapoints are overwritten if the user selectes a different filter mode.
    '''
    def __init__(self):
        super().__init__()

        self.settings = SettingsManager()

        self.settings.settings_changed.connect(self.apply_settings)

        if self.settings.get("user/theme") == "dark":
            self.setStyleSheet(qdarktheme.load_stylesheet())
        
        #Find a nice font?
        #self.setStyleSheet("font-family: 'Helvetica'")

        self.setWindowTitle("Pico JSON Serial Interface")

        #Create a central widget
        self.central = QWidget()
        self.setCentralWidget(self.central)

        # Now create the layout for the central widget
        layout = QVBoxLayout()
        self.central.setLayout(layout)

        # Menu bar
        menu = self.menuBar().addMenu("&Settings")
        settings_action = QAction("Preferences", self)
        settings_action.triggered.connect(self.open_settings)
        menu.addAction(settings_action)

        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)

        # Settings button for toolbar

        settings_btn = QToolButton()
        settings_btn.setIcon(QIcon.fromTheme("preferences-system"))  # system theme icon
        settings_btn.setToolTip("Open Settings")
        settings_btn.clicked.connect(self.open_settings)
        toolbar.addWidget(settings_btn)

        btn_list = QToolButton()
        btn_list.setIcon(QIcon.fromTheme("view-list"))  # or a custom icon
        btn_list.setToolTip("Select Sensor Graphs")
        btn_list.clicked.connect(self.open_checkbox_dialog)
        toolbar.addWidget(btn_list)


        self.status = QLabel("Not connected")
        if self.settings.get("gui/display_connection_status", type=bool):
            layout.addWidget(self.status)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        if self.settings.get("gui/display_log", type=bool):
            layout.addWidget(self.log)

        self.data_buffers = np.zeros((self.settings.get("hardware/NUM_SENSORS", type=int), self.settings.get("gui/buffer_length", type=int)))

        # Auto-detect Pico serial port
        ports = [p.device for p in serial.tools.list_ports.comports() if "Pico" in p.name or "USB Serial" in p.name or "MicroPython" in p.name or "ttyACM0" in p.name or "ttyUSB" in p.name]

        if not ports:
            self.log.append("No Pico found!")
            port = None
            picoFound = False
        else:
            port = ports[0]
            self.status.setText(f"Connected to {port}")
            picoFound = True
            
        if picoFound:
            self.serial_reader_worker = SerialReader(port)
        
        self.data_workers = []
        self.threads = []

        for i in range(self.settings.get("hardware/NUM_SENSORS", type=int)):
            thread = QThread()
            worker = DataWorker(i, self.settings, filter="lowpass")
            worker.moveToThread(thread)
            self.data_workers.append(worker)
            self.threads.append(thread)
        print("Workers Initialized")


        #Connecting the pico serial reader to the data workers
        if picoFound:
            for worker in self.data_workers:
                self.serial_reader_worker.data_received.connect(worker.handle_data)

        #Connecting the data workers to the GUI
        for worker in self.data_workers:
            worker.data_updated.connect(self.add_data)

         # Timer to refresh graphs
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_graphs)
        self.timer.start(self.settings.get("gui/graph_update_rate", type=int))  # 20 FPS

         # ---- Scroll Area ----
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        layout.addWidget(scroll)

        # ---- Container inside the Scroll Area ----
        container = QWidget()
        scroll.setWidget(container)

        self.container_layout = QVBoxLayout()
        self.container_layout.setSpacing(12)
        container.setLayout(self.container_layout)

        # ---- Now add your RealTimeGraphs inside the scrollable container ----
        self.graphs = []

        num_sensors = self.settings.get("hardware/NUM_SENSORS", type=int)
        for i in range(num_sensors):
            graph = RealTimeGraph(self.settings)
            graph.setMinimumHeight(200)     # prevents 0-height collapse
            self.container_layout.addWidget(graph)
            self.graphs.append(graph)

        self.container_layout.addStretch()       # pushes graphs to top

        for thread in self.threads:
            thread.start()

        if picoFound:
            print("Pico found! Starting serial thread.")
            self.serial_reader_worker.start()
        else:
            print("Pico not found!")

        dialog = SensorSettings(self.settings)
        dialog.load_graphs()

        self.central.setLayout(layout)
        self.central.show()

    def add_data(self, value, sensor_id):
        """Receive new data from worker thread."""
        self.graphs[sensor_id].add_data(value)

    def update_graphs(self):
        """Refresh the plot in the GUI thread."""
        for graph in self.graphs:
            graph.update_plot()

    def apply_settings(self, setting, value):
        if setting == "user/theme":
            if self.settings.get("user/theme")=="dark":
                self.setStyleSheet(qdarktheme.load_stylesheet())
            else:
                self.setStyleSheet("")
        for i in range(self.settings.get("hardware/NUM_SENSORS", type=int)):
            if setting == f"hardware/temp_sensors/{i}" and not self.settings.get(f"hardware/temp_sensors/{i}", type=bool):
                self.graphs[i].hide()
                print(f"Hiding graph for Sensor {i}")
            if setting == f"hardware/temp_sensors/{i}" and self.settings.get(f"hardware/temp_sensors/{i}", type=bool):
                self.graphs[i].show()

    def open_settings(self):
        dialog = SettingsDialog(self.settings)
        if dialog.exec():
            # Apply changes (e.g., refresh rate)
            dark_mode = self.settings.get("user/theme")
            if dark_mode=="dark":
                print("Dark Mode on")
            else:
                print("Dark Mode off")
        dialog.close()
    
    def open_checkbox_dialog(self):
        dialog = SensorSettings(self.settings)
        dialog.load_graphs()
        if dialog.exec():  # User pressed OK
            dialog.load_graphs()
        dialog.close()
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
