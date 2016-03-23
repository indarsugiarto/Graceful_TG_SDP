#!/usr/bin/env python
"""
SYNOPSIS:
    Simple framework to do experiment with core frequency, utilization, and chip temperature. 
    Created on 2 Nov 2015
    @author: indi

TODO:
12.01.2016:
- Ask SpiNNaker to send the physical to virtual core map. Don't start if we don't have the core map!
"""

from PyQt4 import Qt
from QtForms import MainWindow
import sys

if __name__=='__main__':
    myApp = Qt.QApplication(sys.argv)
    myMainWindow = MainWindow()
    myMainWindow.showMaximized()
    sys.exit(myApp.exec_())
