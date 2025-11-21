import pyqtgraph as pg
from PyQt6.QtWidgets import QVBoxLayout, QWidget
import numpy as np
import time
from PyQt6.QtCore import QEvent

class PlotWidgetWithReset(pg.PlotWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Store default view ranges
        self.defaultXRange = (0, 60)
        self.defaultYRange = None
        self.window_length = 60

        # Enable autopan X, auto-range Y
        # Set initial X range
        vb = self.getPlotItem().getViewBox()
        # Set initial X range
        vb.setXRange(*self.defaultXRange)
        vb.setAutoPan(x=True)
        vb.enableAutoRange(x=True, y=True)

        # Install event filter to catch double-click
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.MouseButtonDblClick:
            vb = self.getPlotItem().getViewBox()
            # Reset X range
            vb.setXRange(*self.defaultXRange, padding=0)
            vb.setAutoPan(x=True)
            vb.enableAutoRange(x=True, y=True)
            # Optionally reset Y range
            if self.defaultYRange:
                vb.setYRange(*self.defaultYRange)
            return True  # event handled
        return super().eventFilter(obj, event)
    
    def update(self, Xrange):
        self.getPlotItem().getViewBox().setXRange(Xrange[0], Xrange[1], padding=0)
        self.defaultXRange = Xrange


class RealTimeGraph(QWidget):
    def __init__(self,
                 settings,
                 background='#191919', 
                 pen=pg.mkPen(color=(0, 100, 255), width=2),
                 brush=pg.mkBrush(color=(0, 0, 139, 100)),
                ):
        super().__init__()

        print("Graph Initializing")

        #Initialize settings
        self.settings = settings
        self.graph_update_rate = self.settings.get("gui/graph_update_rate", type=int)
        self.buffer_length = self.settings.get("gui/buffer_length", type=int)

         # --- visual buffer (left space before data appears) ---
        self.start_buffer = self.buffer_length * self.graph_update_rate  # ms

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        #if dark mode, background black
        self.plot_widget = PlotWidgetWithReset(background='#191919') # #121212 is good. #1f1e1e is good but very subtle.

        self.curve = self.plot_widget.plot(pen=pen, brush=brush)
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.setLabel('left', 'Temp (\u00b0C)')
        self.plot_widget.setLabel('bottom', 'Time', units='s')
        self.layout.addWidget(self.plot_widget)
        
        # Data
        self.data = np.zeros(1)
        self.times = np.array([time.perf_counter()])

    def add_data(self, data):
        self.data = np.array(data)
        self.times = np.append(self.times, time.perf_counter())

    def update_plot(self):
        # Update the curve
        self.curve.setData(self.times[1:] - self.times[0], self.data)
        # Shade underneath curve
        self.curve.setFillLevel(0)
    


        if self.times[-1] - self.times[0] - self.plot_widget.window_length < 0:
            self.plot_widget.setXRange(self.times[-1] - self.times[0] - self.plot_widget.window_length, self.times[-1] - self.times[0])
            self.plot_widget.update((0, self.times[-1] - self.times[0]))
        else:
            self.plot_widget.update((self.times[-1] - self.times[0] - self.plot_widget.window_length, self.times[-1] - self.times[0]))

        #solution to problem:
        #record exact time that we update the time graph and make array of times