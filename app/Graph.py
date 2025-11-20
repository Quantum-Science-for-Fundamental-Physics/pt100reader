import pyqtgraph as pg
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QComboBox
from PyQt6.QtCore import Qt
import sys
import numpy as np

#Kalman filters
from filterpy.common import kinematic_kf, Q_continuous_white_noise
import scipy as sp

BUFFER_LENGTH = 1000

class CheckableComboBox(QComboBox):
    def __init__(self):
        super().__init__()
        self.setModel(QStandardItemModel(self))
        self.view().pressed.connect(self.handle_item_pressed)
        self.checked_items = []

    def addItem(self, text, data=None):
        item = QStandardItem(text)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        item.setData(Qt.CheckState.Unchecked, Qt.ItemDataRole.CheckStateRole)
        if data is None:
            data = text
        item.setData(data)
        self.model().appendRow(item)

    def handle_item_pressed(self, index):
        item = self.model().itemFromIndex(index)
        if item.checkState() == Qt.CheckState.Checked:
            item.setCheckState(Qt.CheckState.Unchecked)
        else:
            item.setCheckState(Qt.CheckState.Checked)
        self.update_checked_items()

    def update_checked_items(self):
        self.checked_items = []
        for i in range(self.model().rowCount()):
            item = self.model().item(i)
            if item.checkState() == Qt.CheckState.Checked:
                self.checked_items.append(item.text())
        # For demo, update the display text
        self.setCurrentText(", ".join(self.checked_items))

#Update Plot Must wait for data to be returned!
class RealTimeGraph(QWidget):
    def __init__(self,
                 background='#191919', 
                 pen=pg.mkPen(color=(0, 100, 255), width=2),
                 brush=pg.mkBrush(color=(0, 0, 139, 100)),
                 ):
        super().__init__()
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        #if dark mode, background black
        self.plot_widget = pg.PlotWidget(background='#191919') # #121212 is good. #1f1e1e is good but very subtle.

        #Per-graph settings - Checkable combo box for graph styles
        self.plot_items = {}
        self.combo = CheckableComboBox()
        for style in ["Orange", "Blue", "Green"]:
            self.combo.addItem(style)
        #self.layout.addWidget(self.combo)

        self.curve = self.plot_widget.plot(pen=pen, brush=brush)
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.setLabel('left', 'Temp (\u00b0C)')
        self.plot_widget.setLabel('bottom', 'Time')
        self.layout.addWidget(self.plot_widget)
        
        self.combo.model().dataChanged.connect(self.on_combo_changed)

        # Data stuff:

        ORDER = 3
        self.__kf = kinematic_kf(dim=1, order=ORDER, dim_z=1, dt=1.0)
        self.__kf.Q = Q_continuous_white_noise(dim=(ORDER + 1))
        self.__kf.R = 1000

        # Data buffer
        self.xdata = np.linspace(0, 10, 1000)
        self.ydata = np.zeros(1000)

        #Implement way to handle range

        self.next_data = 0
        self.phase = 0

    def on_combo_changed(self):
        styles = self.combo.checked_items
        self.update_plot(styles)

    def update_plot_settings(self, styles):
        # Remove plots that are no longer selected
        for style in list(self.plot_items.keys()):
            if style not in styles:
                self.plot_widget.removeItem(self.plot_items[style])
                del self.plot_items[style]

        # Add or update selected styles
        for style in styles:
            if style not in self.plot_items:
                if style == "Orange":
                    plot = self.plot_widget.plot(self.data, pen='o')
                elif style == "Blue":
                    plot = self.plot_widget.plot(self.data, symbol='b')
                elif style == "Green":
                    plot = self.plot_widget.plot(self.data, pen='g')
                self.plot_items[style] = plot

    #def update_filter(self):


    def update_plot(self):

        # Predict next point according to kalman filter
        #self.__kf.predict()
        #print(f"Kalman Estimate: {self.__kf.x[0]}")

        # Update prediction
        #self.__kf.update(self.next_data)

        # Shift data left and append new value
        self.ydata = np.roll(self.ydata, -1)
        self.ydata[-1] = self.next_data

        # The initial data has a buffer of zeros in front. Our filter should not see this. 
        # The filter should be initialized with the first avalible data.

        # Update the curve
        self.curve.setData(self.xdata, self.ydata)
        # Shade underneath curve
        self.curve.setFillLevel(0)