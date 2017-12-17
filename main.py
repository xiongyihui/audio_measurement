#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
BLE SMURFS MONITOR
Plot realtime power comsumption of BLE SMURFS
"""

import sys
import datetime
from PySide.QtCore import QThread, Signal, Slot, Qt
from PySide.QtGui import QApplication, QMainWindow, QWidget, QHBoxLayout, QMessageBox, QKeyEvent
import pyqtgraph as pg
import numpy as np

from voice_engine.source import Source
from voice_engine.channel_picker import ChannelPicker
from voice_engine.file_sink import FileSink
from thd import THD

data = None

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle('Audio Measuring Experiment')
        self.resize(800, 500)
        self.cwidget = QWidget()
        self.setCentralWidget(self.cwidget)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.cwidget.setLayout(layout)
        self.plotwidget = pg.PlotWidget()
        layout.addWidget(self.plotwidget)
        
        self.plotwidget.setTitle(title="press 'space' to freeze/resume")

        self.plot = self.plotwidget.plot()
        self.plot.setPen((0, 255, 0))

        self.ff = pg.TextItem('fundamental frequency', anchor=(0, 0))
        self.plotwidget.addItem(self.ff)
        self.ff.setPos(100, 0)


        self.arrow = pg.ArrowItem(pos=(100, 0), angle=-45)
        self.plotwidget.addItem(self.arrow)
        

        plotitem = self.plotwidget.getPlotItem()
        # plotitem.hideAxis('left')
        # plotitem.hideAxis('bottom')
        
        self.freeze = False
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(50)

        self.src = Source(rate=48000, frames_size=4800)
        chx = ChannelPicker(channels=self.src.channels, pick=0)
        thd = THD(1000, self.src.rate)

        filename = '2.94dB1KHz.' + datetime.datetime.now().strftime("%Y%m%d.%H:%M:%S") + '.wav'

        sink = FileSink(filename, channels=self.src.channels, rate=self.src.rate)

        def on_data(d):
            global data

            data = d

        thd.on_data = on_data

        self.src.link(sink)
        self.src.pipeline(thd)

        self.src.pipeline_start()

    def update(self):
        global data

        if not self.freeze and data is not None:
            self.plot.setData(data)
            self.arrow.setPos(100, data[100])
            self.ff.setPos(100, 0)
            self.ff.setText(str(data[100]))
        
    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Space:
            self.freeze = not self.freeze
        elif key == Qt.Key_Escape:
            self.plotwidget.enableAutoRange()
            
        return True
        
    def closeEvent(self, event):
        self.src.pipeline_start()

        event.accept()


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
