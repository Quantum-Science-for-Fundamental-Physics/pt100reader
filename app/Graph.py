import sys
import numpy as np
from PyQt6 import QtWidgets, QtCore
import pyqtgraph as pg

class RealTimePlot(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Real-Time Data Plot")

        # Create plot widget
        self.plot_widget = pg.PlotWidget(background='w')
        self.setCentralWidget(self.plot_widget)

        # Create a curve (the actual line on the graph)
        pen = pg.mkPen(color=(0, 100, 255), width=2)
        self.curve = self.plot_widget.plot(pen=pen)
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.setLabel('left', 'Value')
        self.plot_widget.setLabel('bottom', 'Time')

        # Data buffer
        self.xdata = np.linspace(0, 10, 1000)
        self.ydata = np.zeros(1000)

        # Timer to update the graph
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(20)  # update every 20 ms (50 FPS)

        self.phase = 0

    def update_plot(self, data):

        # Shift data left and append new value
        self.ydata = np.roll(self.ydata, -1)
        self.ydata[-1] = data

        # Update the curve
        self.curve.setData(self.xdata, self.ydata)


app = QtWidgets.QApplication(sys.argv)
win = RealTimePlot()
win.resize(800, 400)
win.show()
sys.exit(app.exec())
