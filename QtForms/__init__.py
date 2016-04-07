from PyQt4 import QtGui, QtCore
import sys
import QtMainWindow
from tgxmlParser import tgxmlHandler
import xml.sax
from tgsdpvis import visWidget
from sdpComm import sdpComm
import time

from constDef import *
from helper import *
from rig.machine_control import MachineController

class MainWindow(QtGui.QMainWindow, QtMainWindow.Ui_qtMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.setCentralWidget(self.mdiArea)
        self.statusTxt = QtGui.QLabel("")
        self.statusBar().addWidget(self.statusTxt)

        self.connect(self.action_Quit, QtCore.SIGNAL("triggered()"), QtCore.SLOT("Quit()"))
        self.connect(self.action_Load_XML, QtCore.SIGNAL("triggered()"), QtCore.SLOT("loadXML()"))
        self.connect(self.action_Visualiser, QtCore.SIGNAL("triggered()"), QtCore.SLOT("showVisualiser()"))
        self.connect(self.action_Send_and_Init, QtCore.SIGNAL("triggered()"), QtCore.SLOT("sendAndInit()"))
        self.connect(self.actionInspect_SpinConf, QtCore.SIGNAL("triggered()"), QtCore.SLOT("testSpin1()"))
        self.connect(self.actionSet_Tick, QtCore.SIGNAL("triggered()"), QtCore.SLOT("getSimulationTick()"))
        self.connect(self.actionStart, QtCore.SIGNAL("triggered()"), QtCore.SLOT("startSim()"))
        self.connect(self.actionStop, QtCore.SIGNAL("triggered()"), QtCore.SLOT("stopSim()"))

        self.output = None          # this is a list of list of dict that contains target dependency data
        self.srcTarget = dict()     # this similar to self.output, but just contains target for SOURCE node
                                    # (as a dict of a list), e.g: from dag0020, srcTarget = {0: [4,3,2]}
        self.sdp = sdpComm()
        self.mc = MachineController(DEF_HOST)

    @QtCore.pyqtSlot()
    def Quit(self):
        # TODO: clean up...
        self.close()

    @QtCore.pyqtSlot()
    def showVisualiser(self):
        self.vis = visWidget()
        self.vis.setGeometry(0,0,1024,1024)
        self.vis.show()


    @QtCore.pyqtSlot()
    def loadXML(self):
        print "Loading XML..."
        fullPathFileName = QtGui.QFileDialog.getOpenFileName(self, "Open XML file", "./", "*.xml")
        if not fullPathFileName:
            print "Cancelled!"
        else:
            print "Processing ", fullPathFileName
            parser = xml.sax.make_parser()

            # turn off namespace
            parser.setFeature(xml.sax.handler.feature_namespaces, 0)

            # override the default ContextHandler
            Handler = tgxmlHandler()
            parser.setContentHandler(Handler)
            parser.parse(str(fullPathFileName))

            """ Debugging:
            print "Link Payload"
            for nodes in Handler.Nodes:
                print nodes.Id, ":",
                for target in nodes.Target:
                    print target.destId, "(", target.nPkt, ")",
                print
            print


            print "Target Dependency"
            for nodes in Handler.Nodes:
                print nodes.Id, ":",
                for target in nodes.Target:
                    print target.destId, "(",
                    for dep in target.Dep:
                        print dep.srcId,
                    print "), ",
                print


            print "Target Dependency"
            for n in range(Handler.NumberOfNodes):
                print "nTarget for node-{} = {}".format(n, Handler.Nodes[n].numTarget)
                for t in range(Handler.Nodes[n].numTarget):
                    print "nDep for Target-{} in Node-{} = {}".format(t, n, Handler.Nodes[n].Target[t].nDependant)
                    for d in range(Handler.Nodes[n].Target[t].nDependant):
                        print "Source-ID-idx-{} = {}".format(d,Handler.Nodes[n].Target[t].Dep[d].srcId),
                    print
                    for d in range(Handler.Nodes[n].Target[t].nDependant):
                        print "nTriggerPkt-ID-idx-{} = {}".format(d,Handler.Nodes[n].Target[t].Dep[d].nTriggerPkt),
                    print
                print "\n\n"
            """

            """ Let's put the c-like struct as a list:
                Let's create a variable cfg, which is a list of a dict.
                Then, let's create a variable dag, which is a list of cfg. Hence, dag is a list of a list of a dict.
            """
            dag = list()
            for nodes in Handler.Nodes:
                cfg = list()
                srcPayload = list()
                srcFound = False
                for target in nodes.Target:
                    dct = dict()
                    dct['nodeID'] = nodes.Id
                    dct['destID'] = target.destId
                    dct['nPkt'] = target.nPkt
                    dct['nDependant'] = target.nDependant
                    for d in range(target.nDependant):
                        srcIDkey = "dep{}_srcID".format(d)
                        nTriggerPktkey = "dep{}_nTriggerPkt".format(d)
                        dct[srcIDkey] = target.Dep[d].srcId
                        dct[nTriggerPktkey] = target.Dep[d].nTriggerPkt
                        # also search for SOURCE dependant
                        if target.Dep[d].srcId==DEF_SOURCE_ID:
                            srcFound = True
                            srcPayload.append(target.Dep[d].nTriggerPkt)
                    cfg.append(dct)
                    # and put the payload to the current word in the dict
                if srcFound:
                    self.srcTarget[nodes.Id] = srcPayload
                dag.append(cfg)

            self.initMap()
            self.output = dag
            #self.output = experiment_dag0020()


            # for debugging:
            print "SpiNNaker usage  :", self.TGmap
            print "TG configuration :", self.output
            print "Source Target    :", self.srcTarget


    def initMap(self):
        # SOURCE and SINK send to chip<0,0>, since it is connected to ethernet
        # node-0, send to chip<1,0> == map[1] in the CHIP_LIST_48
        # node-1, send to chip<2,0> == map[2]
        # node-2, send to chip<3,0> == map[3]
        # node-3, send to chip<4,0> == map[4]
        # node-4, send to chip<0,1> == map[5]
        # node-5, send to chip<1,1> == map[6]
        # node-6, send to chip<2,1> == map[7]
        # node-7, send to chip<3,1> == map[8]
        # node-8, send to chip<4,1> == map[9]
        # let's put those in a "map" and "cfg" variables
        # TODO (future): use rig to find out the available chips (undead ones?)

        map = [-1 for _ in range(48)]
        for i in range(9):
            map[i+1] = i    # we start from i+1 because chip<0,0> will be used for SOURCE and SINK
        map[0] = DEF_SOURCE_ID
        self.TGmap = map

    @QtCore.pyqtSlot()
    def testSpin1(self):
        """
        send a request to dump tgsdp configuration data
        sendSDP(self, flags, tag, dp, dc, dax, day, cmd, seq, arg1, arg2, arg3, bArray):
        """
        f=NO_REPLY
        t=DEF_SEND_IPTAG
        p = DEF_SDP_CONF_PORT
        c = DEF_SDP_CORE
        m = TGPKT_HOST_ASK_REPORT

        for item in self.TGmap:
            if item != -1 and item != DEF_SOURCE_ID:
                x, y = getChipXYfromID(self.TGmap, item)
                #print "Sending a request to <{},{}:{}>".format(x,y,c)
                self.sdp.sendSDP(f,t,p,c,x,y,m,0,0,0,0,None)
                time.sleep(DEF_SDP_TIMEOUT)

    @QtCore.pyqtSlot()
    def sendAndInit(self):
        """
        will send aplx to corresponding chip and initialize/configure the chip
        Assuming that the board has been booted?
        """

        if self.output==None:
            QtGui.QMessageBox.information(self, "Information", "No valid network structure yet!")
            return

        # First, need to translate from node-ID to chip position <x,y>, including the SOURCE and SINK node
        # use self.TGmap
        print "Do translation from node to chip..."
        self.xSrc, self.ySrc = getChipXYfromID(self.TGmap, DEF_SOURCE_ID)
        appCores = dict()
        for item in self.TGmap:
            if item != -1 and item != DEF_SOURCE_ID:
                x, y = getChipXYfromID(self.TGmap, item)
                appCores[(x,y)] = [1]

        print "Application cores :", appCores

        # Second, send the aplx (tgsdp.aplx and srcsink.aplx) to the corresponding chip
        # example: mc.load_application("bla_bla_bla.aplx", {(0,0):[1,2,10,17]}, app_id=16)
        # so, the chip is a tupple and cores is in a list!!!
        # Do you want something nice? Use QFileDialog
        print "Send the aplx to the corresponding chip..."
        srcsinkaplx = "/local/new_home/indi/Projects/P/Graceful_TG_SDP_virtualenv/src/aplx/srcsink.aplx"
        tgsdpaplx = "/local/new_home/indi/Projects/P/Graceful_TG_SDP_virtualenv/src/aplx/tgsdp.aplx"
        self.mc.load_application(srcsinkaplx, {(self.xSrc, self.ySrc):[1]}, app_id=APPID_SRCSINK)
        self.mc.load_application(tgsdpaplx, appCores, app_id=APPID_TGSDP)

        # Third, send the configuration to the corresponding node
        print "Sending the configuration data to the corresponding chip..."

        for node in self.output: # self.output should be a list of a list of a dict
            self.sdp.sendConfig(self.TGmap, node)

        # TODO: send the source target list!!!
        self.sdp.sendSourceTarget(self.TGmap, self.srcTarget)   # butuh TGmap karena butuh xSrc dan ySrc

        print "Sending network map..."
        self.sdp.sendChipMap(self.TGmap)

    @QtCore.pyqtSlot()
    def getSimulationTick(self):
        simTick, ok = QtGui.QInputDialog.getInt(self, "Simulation Tick", "Enter Simulation Tick in microsecond", 1, 1, 10000000, 1)
        if ok is True:
            print "Sending tick {} microseconds".format(simTick)
            self.sdp.sendSimTick(self.xSrc, self.ySrc, simTick)

    @QtCore.pyqtSlot()
    def startSim(self):
        self.actionStop.setEnabled(True)
        self.actionStart.setEnabled(False)
        self.sdp.sendStartCmd(self.xSrc, self.ySrc)

    @QtCore.pyqtSlot()
    def stopSim(self):
        self.actionStop.setEnabled(False)
        self.actionStart.setEnabled(True)
        self.sdp.sendStopCmd(self.xSrc, self.ySrc)

