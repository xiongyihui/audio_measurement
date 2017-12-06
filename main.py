#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
BLE SMURFS MONITOR
Plot realtime power comsumption of BLE SMURFS
"""

import sys
from PySide.QtCore import QThread, Signal, Slot, Qt
from PySide.QtGui import QApplication, QMainWindow, QWidget, QHBoxLayout, QMessageBox, QKeyEvent
import pyqtgraph as pg
import numpy as np

from voice_engine.source import Source
from thd import THD

data = []

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


        self.point = pg.CurvePoint(self.plot)
        self.plotwidget.addItem(self.point)
        arrow = pg.ArrowItem(pos=(100, 0), angle=-45)
        arrow.setParentItem(self.point)

        plotitem = self.plotwidget.getPlotItem()
        # plotitem.hideAxis('left')
        # plotitem.hideAxis('bottom')
        
        self.freeze = False
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(50)

        self.src = Source(rate=48000, frames_size=4800)
        thd = THD(1000, self.src.rate)

        def on_data(d):
            global data

            data = d

        thd.on_data = on_data

        self.src.pipeline(thd)

        self.src.pipeline_start()

    def update(self):
        global data

        if not self.freeze:
            self.plot.setData(data)
            self.point.setPos(100.0 / 2400)
            self.ff.setPos(100, data[100])
            self.ff.setText(data[100])
        
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