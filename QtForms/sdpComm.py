from PyQt4 import QtCore, QtNetwork
import struct
from constDef import *
from helper import *
import time

class sdpComm(QtCore.QObject):
    histUpdate = QtCore.pyqtSignal(list)  # for cmd communication
    def __init__(self, parent=None):
        super(sdpComm, self).__init__(parent)
        self.RptSock = QtNetwork.QUdpSocket(self)
        self.initSDPReceiver()

    def sendSDP(self, flags, tag, dp, dc, dax, day, cmd, seq, arg1, arg2, arg3, bArray):
        """
        You know, the detail experiment with sendSDP() see mySDPinger.py
        the bArray can be constructed simply by using type casting. Ex:
        elements = [0, 200, 50, 25, 10, 255]
        bArray = bytearray(elements)        # byte must be in range(0, 256)
        Something wrong with bArray -> try to use list instead
        """
        da = (dax << 8) + day
        dpc = (dp << 5) + dc
        sa = 0
        spc = 255
        pad = struct.pack('2B',0,0)
        hdr = struct.pack('4B2H',flags,tag,dpc,spc,da,sa)
        scp = struct.pack('2H3I',cmd,seq,arg1,arg2,arg3)
        sdp = pad + hdr + scp
        """
        if bArray is not None:
            sdp = pad + hdr + scp + bArray
        else:
            sdp = pad + hdr + scp
        """
        if bArray is not None:
            for b in bArray:
                sdp += struct.pack('<B', b)
                #sdp += b


        CmdSock = QtNetwork.QUdpSocket()
        CmdSock.writeDatagram(sdp, QtNetwork.QHostAddress(DEF_HOST), DEF_SEND_PORT)
        time.sleep(DEF_SDP_TIMEOUT)
        return sdp


    def initSDPReceiver(self):
        print "Try opening port-{} for receiving report...".format(DEF_REPORT_PORT),
        #result = self.sock.bind(QtNetwork.QHostAddress.LocalHost, DEF.RECV_PORT) --> problematik dengan penggunaan LocalHost
        result = self.RptSock.bind(DEF_REPORT_PORT)
        if result is False:
            print 'failed! Cannot open UDP port-{}'.format(DEF_REPORT_PORT)
        else:
            print "done!"
            self.RptSock.readyRead.connect(self.readRptSDP)

    @QtCore.pyqtSlot()
    def readRptSDP(self):
        """
        For reading SDP data from SpiNNaker
        TODO: Terakhir disini!!!!!! 19 April 2016 jam 14:04
        """
        szData = self.RptSock.pendingDatagramSize()
        datagram, host, port = self.RptSock.readDatagram(szData)

        # See, where does it come from
        fmt = "<H4BH2B"
        pad, flags, tag, dp, sp, da, sax, say = struct.unpack(fmt, datagram)
        self.histUpdate.emit([sax, say])
        print "tick"

    def sendPing(self, map):
        for node in map:
            if node != -1:
                x,y = getChipXYfromID(map, node)
                self.sendSDP(NO_REPLY, DEF_SEND_IPTAG, DEF_SDP_CONF_PORT, DEF_SDP_CORE, x, y, TGPKT_PING, 0, 0, 0, 0, None)
                time.sleep(DEF_SDP_TIMEOUT)

    def sendSourceTarget(self, map, srcTarget):
        """
        to send it to the SOURCE node in spinnaker, we need to provide the target's chip coordinate as well!
        """
        # TODO: Ingat, kiriman ke SOURCE/SINK node harus dilengkapi dengan x_chip dan y_cTGPKT_PINGhip dari targetnya!!!!
        # Dan tidak perlu melibatkan trigger payload dari targetnya!
        xSrc, ySrc = getChipXYfromID(map, DEF_SOURCE_ID)    # get the x and y of SOURCE node
        bArray = list()
        for node in srcTarget:  # then node is the "key" in the dictionary
            x,y = getChipXYfromID(map, node)                # get the x and y of the target node of the SOURCE
            bArray.append(node)
            bArray.append(x)
            bArray.append(y)

        #print "Sending source target:",
        #print bArray
        seq = DEF_SOURCE_ID
        arg1 = len(srcTarget)
        self.sendSDP(NO_REPLY, 0, DEF_SDP_CONF_PORT, DEF_SDP_CORE, xSrc, ySrc, TGPKT_SOURCE_TARGET, seq, arg1, 0, 0, bArray)


    def sendConfig(self, map, cfg):
        """
        map is the mapping from nodeID to chip coordinate
        cfg is a list of dict() and REMEMBER: a dict is ordered!!!
        so, we have to find the chip coordinate from map and send the cfg to it

        """
        # print cfg
        nodeID = cfg[0]['nodeID']
        targetIdx = 0
        for target in cfg:  # each "target" is a dict
            destID = target['destID']
            # then find, where is it in SpiNNaker board
            dax,day = getChipXYfromID(map, nodeID)
            nPkt = target['nPkt']
            nDependant = target['nDependant']
            # since a node has at least one dependant
            srcID = target['dep0_srcID']
            nTriggerPkt  = target['dep0_nTriggerPkt']

            # then put to sdp header
            cmd = TGPKT_DEPENDENCY
            seq = targetIdx
            arg1 = (nodeID << 16) | destID      # arg1_high = nodeID, arg1_low = targetID
            arg2 = (nPkt << 16) | nDependant    # arg2_high = nPkt, arg2_los = nDependant
            # arg3_high = the first dependant node-ID, arg3_low = the expected number of triggers
            arg3 = (srcID << 16) | nTriggerPkt

            # if the node has more than one dependency
            if nDependant > 1:
                dep = list()    # build a list that will be translated into bytearray
                for d in range(nDependant-1):
                    srcIDkey = "dep{}_srcID".format(d+1)
                    srcID = target[srcIDkey]
                    s = struct.pack('<H',srcID)
                    l = struct.unpack('<BB',s)
                    for item in l:
                        dep.append(item)    # and with conversion to ushort


                    nTriggerPktkey = "dep{}_nTriggerPkt".format(d+1)
                    nTriggerPkt = target[nTriggerPktkey]
                    s = struct.pack('<H',nTriggerPkt)
                    l = struct.unpack('<BB',s)
                    for item in l:
                        dep.append(item)    # and with conversion to ushort
                #bArray = bytearray(dep)
                bArray = dep
            else:
                bArray = None

            # finally, send this particular output link to SpiNNaker
            #print "\nSend dep to <{},{}> with bArray = {}".format(dax,day,bArray)
            self.sendSDP(NO_REPLY, DEF_SEND_IPTAG, DEF_SDP_CONF_PORT, DEF_SDP_CORE, dax, day,\
                         cmd, seq, arg1, arg2, arg3, bArray)
            time.sleep(DEF_SDP_TIMEOUT)

            targetIdx += 1

    def sendChipMap(self, map):
        """
        Send TGnodes to SpiNN-chips map
        map is a 1D list contains mapping from SPiNNaker-chipID to TG-nodeID. In dag0020, it looks like:
        [65535,0,1,2,3,4,5,6,7,8,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]

        At 14.Apr.2016: I found: if the number of nodes is big, then it is not possible to put them in a single SDP
        """
        # first, build the list and count how many nodes are there
        xSrc, ySrc = getChipXYfromID(map, DEF_SOURCE_ID)
        nNode = 0
        lNode = list()
        for item in map:
            if item==DEF_SOURCE_ID or item==-1: # we skip SOURCE because it is already in arg
                continue
            else:
                nNode += 1
                x,y = getChipXYfromID(map, item)
                S = struct.pack('<HBB',item,x,y)
                L = struct.unpack('<BBBB',S)
                for l in L:
                    lNode.append(l)

        print "nNode =", nNode
        print "lNode =", lNode
        # print "Sending map as:", lNode
        # second, send to all nodes, including SOURCE/SINK
        for item in map:
            if item != -1:  # for all nodes, including SOURCE/SINK
                x,y = getChipXYfromID(map, item)
                #print "Sending nodeMap to <{},{}>".format(x,y)
                f = NO_REPLY
                t = DEF_SEND_IPTAG
                p = DEF_SDP_CONF_PORT
                c = DEF_SDP_CORE
                cmd_rc = TGPKT_CHIP_NODE_MAP
                seq = nNode
                arg1 = DEF_SOURCE_ID
                arg2 = xSrc
                arg3 = ySrc
                #self.sendSDP(f,t,p,c,x,y,cmd_rc,seq,arg1,arg2,arg3,None)
                self.sendSDP(NO_REPLY, DEF_SEND_IPTAG, DEF_SDP_CONF_PORT, DEF_SDP_CORE, x, y,
                         TGPKT_CHIP_NODE_MAP, nNode,DEF_SOURCE_ID,xSrc,ySrc,lNode)
                time.sleep(DEF_SDP_TIMEOUT)



    def sendSimTick(self, xSrc, ySrc, tick):
        self.sendSDP(NO_REPLY, DEF_SEND_IPTAG, DEF_SDP_CONF_PORT, DEF_SDP_CORE, xSrc, ySrc,
                     TGPKT_HOST_SEND_TICK,0,tick,0,0,None)

    def sendStartCmd(self, xSrc, ySrc):
        self.sendSDP(NO_REPLY, DEF_SEND_IPTAG, DEF_SDP_CONF_PORT, DEF_SDP_CORE, xSrc, ySrc, TGPKT_START_SIMULATION,0,0,0,0,None)

    def sendStopCmd(self, xSrc, ySrc, map=None):
        self.sendSDP(NO_REPLY, DEF_SEND_IPTAG, DEF_SDP_CONF_PORT, DEF_SDP_CORE, xSrc, ySrc, TGPKT_STOP_SIMULATION,0,0,0,0,None)
        # then, also to other nodes
        if map is not None:
            for item in map:
                if item==DEF_SOURCE_ID or item==-1:
                    continue
                else:
                    x,y = getChipXYfromID(map, item)
                    self.sendSDP(NO_REPLY, DEF_SEND_IPTAG, DEF_SDP_CONF_PORT, DEF_SDP_CORE, x, y, TGPKT_STOP_SIMULATION,0,0,0,0,None)

