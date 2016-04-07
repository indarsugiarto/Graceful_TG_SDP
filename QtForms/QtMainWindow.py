# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'QtMainWindow.ui'
#
# Created: Wed Apr  6 11:38:14 2016
#      by: PyQt4 UI code generator 4.10.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_qtMainWindow(object):
    def setupUi(self, qtMainWindow):
        qtMainWindow.setObjectName(_fromUtf8("qtMainWindow"))
        qtMainWindow.resize(800, 631)
        self.centralwidget = QtGui.QWidget(qtMainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.mdiArea = QtGui.QMdiArea(self.centralwidget)
        self.mdiArea.setGeometry(QtCore.QRect(0, 0, 801, 551))
        self.mdiArea.setObjectName(_fromUtf8("mdiArea"))
        qtMainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(qtMainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 27))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menu_File = QtGui.QMenu(self.menubar)
        self.menu_File.setObjectName(_fromUtf8("menu_File"))
        self.menu_Tools = QtGui.QMenu(self.menubar)
        self.menu_Tools.setObjectName(_fromUtf8("menu_Tools"))
        self.menu_Simulation = QtGui.QMenu(self.menubar)
        self.menu_Simulation.setObjectName(_fromUtf8("menu_Simulation"))
        qtMainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(qtMainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        qtMainWindow.setStatusBar(self.statusbar)
        self.action_Load_XML = QtGui.QAction(qtMainWindow)
        self.action_Load_XML.setObjectName(_fromUtf8("action_Load_XML"))
        self.action_Quit = QtGui.QAction(qtMainWindow)
        self.action_Quit.setObjectName(_fromUtf8("action_Quit"))
        self.action_Visualiser = QtGui.QAction(qtMainWindow)
        self.action_Visualiser.setObjectName(_fromUtf8("action_Visualiser"))
        self.action_Send_and_Init = QtGui.QAction(qtMainWindow)
        self.action_Send_and_Init.setObjectName(_fromUtf8("action_Send_and_Init"))
        self.actionInspect_SpinConf = QtGui.QAction(qtMainWindow)
        self.actionInspect_SpinConf.setObjectName(_fromUtf8("actionInspect_SpinConf"))
        self.actionSet_Tick = QtGui.QAction(qtMainWindow)
        self.actionSet_Tick.setObjectName(_fromUtf8("actionSet_Tick"))
        self.actionStart = QtGui.QAction(qtMainWindow)
        self.actionStart.setObjectName(_fromUtf8("actionStart"))
        self.actionStop = QtGui.QAction(qtMainWindow)
        self.actionStop.setEnabled(False)
        self.actionStop.setObjectName(_fromUtf8("actionStop"))
        self.menu_File.addAction(self.action_Load_XML)
        self.menu_File.addAction(self.action_Send_and_Init)
        self.menu_File.addSeparator()
        self.menu_File.addAction(self.action_Quit)
        self.menu_Tools.addAction(self.action_Visualiser)
        self.menu_Tools.addSeparator()
        self.menu_Tools.addAction(self.actionInspect_SpinConf)
        self.menu_Simulation.addAction(self.actionSet_Tick)
        self.menu_Simulation.addAction(self.actionStart)
        self.menu_Simulation.addAction(self.actionStop)
        self.menubar.addAction(self.menu_File.menuAction())
        self.menubar.addAction(self.menu_Tools.menuAction())
        self.menubar.addAction(self.menu_Simulation.menuAction())

        self.retranslateUi(qtMainWindow)
        QtCore.QMetaObject.connectSlotsByName(qtMainWindow)

    def retranslateUi(self, qtMainWindow):
        qtMainWindow.setWindowTitle(_translate("qtMainWindow", "TGSDP - Traffic Generator Using SDP", None))
        self.menu_File.setTitle(_translate("qtMainWindow", "&File", None))
        self.menu_Tools.setTitle(_translate("qtMainWindow", "&Tools", None))
        self.menu_Simulation.setTitle(_translate("qtMainWindow", "&Simulation", None))
        self.action_Load_XML.setText(_translate("qtMainWindow", "&Load XML", None))
        self.action_Quit.setText(_translate("qtMainWindow", "&Quit", None))
        self.action_Visualiser.setText(_translate("qtMainWindow", "&Visualiser", None))
        self.action_Send_and_Init.setText(_translate("qtMainWindow", "&Send and Init", None))
        self.actionInspect_SpinConf.setText(_translate("qtMainWindow", "Inspect SpinConf", None))
        self.actionSet_Tick.setText(_translate("qtMainWindow", "Set Tick", None))
        self.actionStart.setText(_translate("qtMainWindow", "Start", None))
        self.actionStop.setText(_translate("qtMainWindow", "Stop", None))

