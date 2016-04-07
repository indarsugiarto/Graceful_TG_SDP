from PyQt4 import QtCore, QtNetwork
import struct
from constDef import *
from helper import *
import time

class sdpComm(QtCore.QObject):
    def __init__(self, parent=None):
        super(sdpComm, self).__init__(parent)

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
        if bArray is not None:
            for b in bArray:
                sdp += struct.pack('B', b)

        CmdSock = QtNetwork.QUdpSocket()
        CmdSock.writeDatagram(sdp, QtNetwork.QHostAddress(DEF_HOST), DEF_SEND_PORT)
        return sdp

    def sendSourceTarget(self, map, srcTarget):
        """
        srcTarget is a dict of a list. Eg., in dag0020, it looks like: srcTarget = {0: [4,3,2]}
        to send it to the SOURCE node in spinnaker, we need to provide the target's chip coordinate as well!

cmd_rc = TGPKT_SOURCE_TARGET
seq = target node ID
arg1_high = x_chip dari target node
arg1_low = y_chip dari target node
arg2_high = unused
arg2_low = banyaknya payload (pola kiriman paket)
arg3_high = unused
arg3_low = unused
data[0:1] = pola/payload pertama
data[1:2] = pola/payload kedua
...dst
// Untuk saat ini dibatasi kalau satu node target hanya melayani hingga maximum MAX_FAN pola pengiriman
// IMPORTANT: sial, aku butuh informasi x_chip dan y_chip karena SOURCE/SINK chip tidak mengelola TGPKT_DEPENDENCY. tgsdp.py tidak mengirimkannya ke SOURCE/SINK chip!

        """
        # TODO: complete me!!!!!!!!
        # TODO: Ingat, kiriman ke SOURCE/SINK node harus dilengkapi dengan x_chip dan y_chip dari targetnya!!!!
        xSrc, ySrc = getChipXYfromID(map, DEF_SOURCE_ID)    # get the x and y of SOURCE node
        for node in srcTarget:  # then node is the "key" in the dictionary
            x,y = getChipXYfromID(map, node)                # get the x and y of the target node of the SOURCE
            arg1 = (x << 16) | y
            arg2 = len(srcTarget[node])

            bArray = list()                                 # contains the weight/payload for each link to the target
            for b in range(arg2):
                s = struct.pack('<H',srcTarget[node][b])    # convert to ushort
                L = struct.unpack('<BB',s)                  # split to two bytes
                for l in L:
                    bArray.append(l)    # and with conversion to ushort

            print "Sending source target ID-{} at <{},{}> :".format(node, x,y),
            print bArray
            self.sendSDP(NO_REPLY, DEF_SEND_IPTAG, DEF_SDP_CONF_PORT, DEF_SDP_CORE, xSrc, ySrc, TGPKT_SOURCE_TARGET,
                         node, arg1, arg2, 0, bArray)


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
            #print "bArray =", bArray
            self.sendSDP(NO_REPLY, DEF_SEND_IPTAG, DEF_SDP_CONF_PORT, DEF_SDP_CORE, dax, day,\
                         cmd, seq, arg1, arg2, arg3, bArray)
            time.sleep(DEF_SDP_TIMEOUT)

            targetIdx += 1

    def sendChipMap(self, map):
        """
        Send TGnodes to SpiNN-chips map
        map is a 1D list contains mapping from SPiNNaker-chipID to TG-nodeID. In dag0020, it looks like:
        [65535,0,1,2,3,4,5,6,7,8,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]
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
                S = struct.pack('<HHH',item,x,y)
                L = struct.unpack('<BBBBBB',S)
                for l in L:
                    lNode.append(l)

        # print "nNode =", nNode
        # print "Sending map as:", lNode
        # second, send to the SOURCE node
        self.sendSDP(NO_REPLY, DEF_SEND_IPTAG,DEF_SDP_CONF_PORT, DEF_SDP_CORE, xSrc, ySrc,
                     TGPKT_CHIP_NODE_MAP, nNode, DEF_SOURCE_ID, xSrc, ySrc, lNode)

        # then, also to other nodes
        for item in map:
            if item==DEF_SOURCE_ID or item==-1:
                continue
            else:
                x,y = getChipXYfromID(map, item)
                self.sendSDP(NO_REPLY, DEF_SEND_IPTAG, DEF_SDP_CONF_PORT, DEF_SDP_CORE, x, y,
                         TGPKT_CHIP_NODE_MAP, nNode,DEF_SOURCE_ID,xSrc,ySrc,lNode)


    def sendSimTick(self, xSrc, ySrc, tick):
        self.sendSDP(NO_REPLY, DEF_SEND_IPTAG, DEF_SDP_CONF_PORT, DEF_SDP_CORE, xSrc, ySrc,
                     TGPKT_HOST_SEND_TICK,0,tick,0,0,None)

    def sendStartCmd(self, xSrc, ySrc):
        self.sendSDP(NO_REPLY, DEF_SEND_IPTAG, DEF_SDP_CONF_PORT, DEF_SDP_CORE, xSrc, ySrc, TGPKT_START_SIMULATION,0,0,0,0,None)

    def sendStopCmd(self, xSrc, ySrc):
        self.sendSDP(NO_REPLY, DEF_SEND_IPTAG, DEF_SDP_CONF_PORT, DEF_SDP_CORE, xSrc, ySrc, TGPKT_STOP_SIMULATION,0,0,0,0,None)

