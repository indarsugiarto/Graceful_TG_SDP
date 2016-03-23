"""
This will handle both the main window and the UDP communication!
"""

from PyQt4 import QtGui, QtNetwork
from PyQt4.QtCore import *
import QtSpiNNProfilerMDI
from myTub import *
from myPlotterT import Twidget
from myPlotterU import Uwidget
from myPlotterF import Fwidget
from myCoreSwitch import Swidget
import constDef as DEF
import time # need sleep()
"""===============================================================================================
                                             MainGUI
-----------------------------------------------------------------------------------------------"""
class MainWindow(QtGui.QMainWindow, QtSpiNNProfilerMDI.Ui_QtSpiNNProfilerMDI):
    # The following signals MUST defined here, NOT in the init()
    sdpUpdate = QtCore.pyqtSignal('QByteArray')  # for streaming data
    tubUpdate = QtCore.pyqtSignal('QByteArray')  # for tubotron
    rplUpdate = QtCore.pyqtSignal('QByteArray')  # for cmd communication
    nChips = 4 # Can be changed by SelectBoard()

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.setCentralWidget(self.mdiArea);
        self.statusTxt = QtGui.QLabel("")
        self.statusBar().addWidget(self.statusTxt)

        self.connect(self.action_Tubotron, SIGNAL("triggered()"), SLOT("Tubotron()"))
        self.connect(self.action_Temperature, SIGNAL("triggered()"), SLOT("Temperature()"))
        self.connect(self.action_Utilization, SIGNAL("triggered()"), SLOT("Utilization()"))
        self.connect(self.action_Frequency, SIGNAL("triggered()"), SLOT("Frequency()"))
        self.connect(self.action_SaveData, SIGNAL("triggered()"), SLOT("SaveData()"))
        self.connect(self.action_SelectBoard, SIGNAL("triggered()"), SLOT("SelectBoard()"))
        self.connect(self.action_CoreSwitcher, SIGNAL("triggered()"), SLOT("CoreSwitch()"))

        self.TubSock = QtNetwork.QUdpSocket(self) # this is for Tubotron
        self.RptSock = QtNetwork.QUdpSocket(self) # this if for report streaming (temperature, utilization, etc)
        self.RplSock = QtNetwork.QUdpSocket(self) # this for generic reply for specific command request
        self.initRptSock(DEF.RECV_PORT)
        self.initRplSock(DEF.REPLY_PORT)
                
        self.uw = None
        self.tw = None
        self.fw = None
        self.sw = None
        # First, trigger the Board type and get the core map
        self.SelectBoard()

    """
    ######################### GUI callback ########################### 
    """
    @pyqtSlot()
    def Tubotron(self):
        if self.action_Tubotron.isChecked():
            #print "Tubotron is now checked, let's initiate the port-{} opening".format(DEF.TUBO_PORT)
            result = self.TubSock.bind(DEF.TUBO_PORT)
            if result is False:
                print 'Cannot open UDP port-{}'.format(DEF.TUBO_PORT)
                self.action_Tubotron.setChecked(False)
                return
    
            self.tub = Tubwidget(self)
            self.subWinTub = QtGui.QMdiSubWindow(self)
            self.subWinTub.setWidget(self.tub)
            self.mdiArea.addSubWindow(self.subWinTub)
            self.subWinTub.setGeometry(0,0,self.tub.width(),self.tub.height())
            self.tub.show()
            initialMsg = "Tubotron opened at port-%d" % DEF.TUBO_PORT
            self.tub.console.insertPlainText(initialMsg)
            self.TubSock.readyRead.connect(self.readTubSDP)
            self.tubUpdate.connect(self.tub.newData)
        else:
            self.tubUpdate.disconnect(self.tub.newData)
            self.tub.okToClose = True
            self.TubSock.close()
            self.tub.close()
            #self.mdiArea.removeSubWindow(self.subWinTub) -> this will create segmentation fault
            self.subWinTub.close()

    @pyqtSlot()
    def Temperature(self):
        if self.action_Temperature.isChecked():
            self.tw = Twidget(self.nChips, self); # let's try with 4 chips
            self.sdpUpdate.connect(self.tw.newData)     # when defining signal-slot in pyqt, the type can be omitted
            self.tw.cbMode.setCurrentIndex(1)
            self.subWinTw = QtGui.QMdiSubWindow(self)
            self.mdiArea.addSubWindow(self.subWinTw)
            self.subWinTw.setWidget(self.tw)
            self.subWinTw.setGeometry(400,0,600,400)
            self.tw.show()
        else:
            self.sdpUpdate.disconnect(self.tw.newData)     # when defining signal-slot in pyqt, the type can be omitted
            self.tw.okToClose = True
            self.tw.close()
            self.subWinTw.close()

    @pyqtSlot()
    def Utilization(self):
        if self.action_Utilization.isChecked():
            #self.uw = Uwidget(self.nChips, self); # let's try with 4 chips
            self.uw = Uwidget(self.nChips); # let's try with 4 chips
            self.sdpUpdate.connect(self.uw.newData)     # when defining signal-slot in pyqt, the type can be omitted
            self.uw.cbMode.setCurrentIndex(1)
            #self.subWinUw = QtGui.QMdiSubWindow()       # mo move it outside mdiArea because it is too big!!!
            #self.subWinUw = QtGui.QMdiSubWindow(self) #--> this will make it is contained in the main Window
            #self.mdiArea.addSubWindow(self.subWinUw)
            #self.subWinUw.setWidget(self.uw)
            #self.subWinUw.setGeometry(400,400,600,400)
            # Then give it the p2v coremap
            for i in range(self.nChips):
                cpuVal = self.p2vMap[i]
                self.uw.updateP2Vmap(i, cpuVal)
            self.uw.showMaximized()

        else:
            self.sdpUpdate.disconnect(self.uw.newData)     # when defining signal-slot in pyqt, the type can be omitted
            self.uw.okToClose = True
            self.uw.close()
            #self.subWinUw.close()

    @pyqtSlot()
    def Frequency(self):
        if self.action_Frequency.isChecked():
            self.fw = Fwidget(self.nChips, self); # let's try with 4 chips
            self.sdpUpdate.connect(self.fw.newData)     # when defining signal-slot in pyqt, the type can be omitted
            self.subWinFw = QtGui.QMdiSubWindow(self)
            self.mdiArea.addSubWindow(self.subWinFw)
            self.subWinFw.setWidget(self.fw)
            self.subWinFw.setGeometry(1000,0,800,1000)
            self.fw.show()
        else:
            self.sdpUpdate.disconnect(self.fw.newData)     # when defining signal-slot in pyqt, the type can be omitted
            self.fw.okToClose = True
            self.fw.close()
            self.subWinFw.close()

    @pyqtSlot()
    def SaveData(self):
        if self.action_SaveData.isChecked():
            print "SaveData is now checked"
        else:
            print "SaveData is now not checked"

    @pyqtSlot()
    def SelectBoard(self):
        msgBox = QtGui.QMessageBox()
        msgBox.setText("Select the SpiNNaker board.")
        msgBox.setInformativeText("Which board are you using?")
        bSpiNN3 = msgBox.addButton("SpiNN-3", QtGui.QMessageBox.ActionRole)
        bSpiNN5 = msgBox.addButton("SpiNN-5", QtGui.QMessageBox.ActionRole)
        bCancel = msgBox.addButton(QtGui.QMessageBox.Cancel)
        msgBox.exec_()
        if msgBox.clickedButton() == bSpiNN3:
            self.nChips = 4
            self.p2vMap = [list() for i in range(4)]   # Prepare the coremap list 
        elif msgBox.clickedButton() == bSpiNN5:
            self.nChips = 48
            self.p2vMap = [list() for i in range(48)]  # Prepare the coremap list
        else:
            print "Still using {}-chips".format(self.nChips)
            return
            
        #Display on status bar
        if self.nChips == 4:
            self.statusTxt.setText("Using SpiNN-3 board")
        else:
            self.statusTxt.setText("Using SpiNN-5 board")
        
        #Inform widgets
        if self.uw is not None:
            self.uw.updateNChips(self.nChips)
        if self.tw is not None:
            self.tw.updateNChips(self.nChips)
        if self.fw is not None:
            self.fw.updateNChips(self.nChips)
        if self.sw is not None:
            self.sw.updateNChips(self.nChips)

        #Send request for p2v
        self.askP2Vmap()

    @pyqtSlot()
    def CoreSwitch(self):
        if self.action_CoreSwitcher.isChecked():
            self.sw = Swidget(self.nChips, self); # let's try with 4 chips
            self.rplUpdate.connect(self.sw.newData)     # will be used for checking disabled-CPUs
            self.subWinSw = QtGui.QMdiSubWindow(self)
            self.mdiArea.addSubWindow(self.subWinSw)
            self.subWinSw.setWidget(self.sw)
            self.subWinSw.setGeometry(600,400,self.sw.width()+10,self.sw.height()+20)
            for i in range(self.nChips):
                cpuVal = self.p2vMap[i]
                self.sw.updateP2Vmap(i, cpuVal)
            self.sw.show()
        else:
            self.rplUpdate.disconnect(self.sw.newData)     # when defining signal-slot in pyqt, the type can be omitted
            self.sw.okToClose = True
            self.sw.close()
            self.subWinSw.close()
            

    """
    ############################ Reading Tubotron Socket ###########################
    """
    @pyqtSlot()
    def readTubSDP(self):
        while self.TubSock.hasPendingDatagrams():
            szData = self.TubSock.pendingDatagramSize()
            datagram, host, port = self.TubSock.readDatagram(szData)
            self.tubUpdate.emit(datagram)

    """
    ############################ Streaming Report Socket ###########################
    """
    def initRptSock(self, port):
        print "Try opening port-{} for streaming Profiler Report...".format(port),
        #result = self.sock.bind(QtNetwork.QHostAddress.LocalHost, DEF.RECV_PORT) --> problematik dengan penggunaan LocalHost
        result = self.RptSock.bind(port)
        if result is False:
            print 'failed! Cannot open UDP port-{}'.format(port)
        else:
            print "done!"
            self.RptSock.readyRead.connect(self.readRptSDP)

    @pyqtSlot()
    def readRptSDP(self):
        while self.RptSock.hasPendingDatagrams():
            szData = self.RptSock.pendingDatagramSize()
            datagram, host, port = self.RptSock.readDatagram(szData)
            self.sdpUpdate.emit(datagram)

    """
    ############################ CMD communication Socket ###########################
    """
    def initRplSock(self, port):
        print "Try opening port-{} for CMD communication...".format(port),
        result = self.RplSock.bind(port)
        if result is False:
            print 'failed! Cannot open UDP port-{}'.format(port)
        else:
            print "done!"
            self.RplSock.readyRead.connect(self.readRplSDP)

    @pyqtSlot()
    def readRplSDP(self):
        while self.RplSock.hasPendingDatagrams():
            szData = self.RplSock.pendingDatagramSize()
            datagram, host, port = self.RplSock.readDatagram(szData)
            self.rplUpdate.emit(datagram) # Let the other widget knows it as well, eq: disabledCPU
            # See if it contains core map
            if len(datagram)==DEF.HOST_REQ_CPU_MAP_REPLY_SIZE:
                #print "Receiving p2v core map with length-%d" % len(datagram)
                fmt = "<H4BH2B2H3I20B"
                pad, flags, tag, dp, sp, da, say, sax, cmd, seq, arg1, arg2, arg3, \
                cpu0, cpu1, cpu2, cpu3, cpu4, cpu5, cpu6, cpu7, cpu8, cpu9, cpu10, cpu11, \
                cpu12, cpu13, cpu14, cpu15, cpu16, cpu17, cpu18, cpu19 = struct.unpack(fmt, datagram)
                if cmd==DEF.HOST_REQ_CPU_MAP: # is it really the p2v core map?
                    if self.nChips==4:
                        cmap = DEF.CHIP_LIST_4
                    else:
                        cmap = DEF.CHIP_LIST_48
                    idx = self.getChipIndex(cmap, sax, say) # get linear chip-ID
                    cpuVal = [cpu0, cpu1, cpu2, cpu3, cpu4, cpu5, cpu6, cpu7, cpu8, cpu9, cpu10, cpu11, cpu12, cpu13, cpu14, cpu15, cpu16, cpu17]
                    self.p2vMap[idx] = cpuVal
                    if self.uw is not None:
                        self.uw.updateP2Vmap(idx, cpuVal) # only uw needs core map!!!
                    if self.sw is not None:
                        self.sw.updateP2Vmap(idx, cpuVal)
            
    """
    ############################# Misc. Functions ##################################
    askP2Vmap() : asks physical to virtual core map
    sendSDP()   : sending SDP packet to SpiNNaker
    closeEvent(): there's special treatment for uw
    """
    def askP2Vmap(self):
        if self.nChips==4:
            Coremap = DEF.CHIP_LIST_4
        else:
            Coremap = DEF.CHIP_LIST_48
        for i in range(self.nChips):
            #print "Asking p2v core map for chip<{},{}>".format(Coremap[i][0], Coremap[i][1])
            self.sendSDP(DEF.NO_REPLY, DEF.SEND_IPTAG, DEF.SDP_PORT, DEF.SDP_CORE, \
                         Coremap[i][0], Coremap[i][1], DEF.HOST_REQ_CPU_MAP, 0, 0, 0, 0, None)
            time.sleep(0.1)
            

    # We can use sendSDP to control frequency, getting virtual core map, etc
    def sendSDP(self,flags, tag, dp, dc, dax, day, cmd, seq, arg1, arg2, arg3, bArray):
        """
        The detail experiment with sendSDP() see mySDPinger.py
        """
        da = (dax << 8) + day
        dpc = (dp << 5) + dc
        sa = 0
        spc = 255
        pad = struct.pack('2B',0,0)
        hdr = struct.pack('4B2H',flags,tag,dpc,spc,da,sa)
        scp = struct.pack('2H3I',cmd,seq,arg1,arg2,arg3)
        if bArray is not None:
            sdp = pad + hdr + scp + bArray
        else:
            sdp = pad + hdr + scp

        CmdSock = QtNetwork.QUdpSocket()
        CmdSock.writeDatagram(sdp, QtNetwork.QHostAddress(DEF.HOST), DEF.SEND_PORT)
        return sdp

    def closeEvent(self, event):
        # Special treatment for uw
        if self.action_Utilization.isChecked():
            self.uw.okToClose = True
            self.uw.close()

    """
    ############################# Helper Functions ##################################
    """
    def getChipIndex(self, cmap, x, y):
        for i in range(self.nChips):
            if cmap[i][0]==x and cmap[i][1]==y:
                return i
            



