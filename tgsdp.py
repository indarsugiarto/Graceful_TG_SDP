#!/usr/bin/env python
"""
SYNOPSIS:
    Simple framework to do experiment with traffic generator using sdp mechanism. 
    Created on 2 Nov 2015
    @author: indar.sugiarto@manchester.ac.uk
"""

from PyQt4 import Qt
from QtForms import MainWindow
import sys

if __name__=='__main__':
    myApp = Qt.QApplication(sys.argv)
    myMainWindow = MainWindow()
    myMainWindow.show()
    sys.exit(myApp.exec_())
