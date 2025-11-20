import pyqtgraph as pg
from PyQt6.QtWidgets import QVBoxLayout, QWidget
import numpy as np

class RealTimeGraph(QWidget):
    def __init__(self,
                 settings,
                 background='#191919', 
                 pen=pg.mkPen(color=(0, 100, 255), width=2),
                 brush=pg.mkBrush(color=(0, 0, 139, 100)),
                ):
        super().__init__()
        self.settings = settings

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        #if dark mode, background black
        self.plot_widget = pg.PlotWidget(background='#191919') # #121212 is good. #1f1e1e is good but very subtle.

        self.curve = self.plot_widget.plot(pen=pen, brush=brush)
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.setLabel('left', 'Temp (\u00b0C)')
        self.plot_widget.setLabel('bottom', 'Time')
        self.layout.addWidget(self.plot_widget)
        
        # Data buffer
        self.xdata = np.linspace(0, 10, self.settings.get("gui/buffer_length", type=int))
        self.ydata = np.zeros(self.settings.get("gui/buffer_length", type=int))

    def add_data(self, data):
        #self.ydata = np.roll(self.ydata, -1)
        #self.ydata[-1] = value

        data = np.array(data)
        print(len(data))
        if len(data) < self.settings.get("gui/buffer_length", type=int):
            self.ydata = np.zeros(self.settings.get("gui/buffer_length", type=int) - len(data))
            self.ydata = np.concatenate((self.ydata, data))
        else:
            self.ydata = data
        #if ydata too big, start rolling.

    def update_plot(self):
        # Update the curve
        self.curve.setData(self.xdata, self.ydata)
        # Shade underneath curve
        self.curve.setFillLevel(0)