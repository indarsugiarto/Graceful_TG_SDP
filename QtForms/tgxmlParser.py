import xml.sax
import string

class cDep(object):
    def __init__(self):
        self.srcId = None
        self.nTriggerPkt = None

class cTarget(object):
    def __init__(self):
        self.destId = None
        self.nPkt = None
        self.nDependant = 0
        self.Dep = list()       # this will contain a list of cDep

class cNode(object):
    def __init__(self):
        self.Id = None
        self.numTarget = 0
        self.Target = list()    # this will contain a list of cTarget


#================================== Main Class for XML.SAX Handler ====================================
class tgxmlHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.CurrentElement = ""
        self.Nodes = list()
        self.NumberOfNodes = 0


    # call when an element starts
    def startElement(self, name, attrs):
        if name == "TrafficElement":        # this indicates a new node
            self.Nodes.append(cNode())      # add empty node list
            self.Targets = list()
            self.CurrentTarget = 0
        if name == "target":                # this indicates a new target
            self.Nodes[self.NumberOfNodes].numTarget += 1
            self.Targets.append(cTarget())  # add empty target list
            self.Dependencies = list()
            self.CurrentDep = 0
        if name == "dependency":
            self.Targets[self.CurrentTarget].nDependant += 1
            self.Dependencies.append(cDep)  # add emtpy dependency list
            self.D = cDep()

        self.CurrentElement = name

    # call when an element ends
    def endElement(self, name):
        if name == "TrafficElement":
            self.Nodes[self.NumberOfNodes].Target = self.Targets
            self.NumberOfNodes += 1
        if name == "target":
            self.Targets[self.CurrentTarget].Dep = self.Dependencies
            self.CurrentTarget += 1
        if name == "dependency":
            self.Dependencies[self.CurrentDep] = self.D
            self.CurrentDep += 1
        self.CurrentElement = ""

    # call when a character is read
    def characters(self, content):
        if self.CurrentElement == "nodeId":
            self.Nodes[self.NumberOfNodes].Id = int(content)
        if self.CurrentElement == "targetId":
            if string.upper(content)=='SINK':
                self.Targets[self.CurrentTarget].destId = 0xFFFF
            else:
                self.Targets[self.CurrentTarget].destId = int(content)
        if self.CurrentElement == "outputPackets":
            self.Targets[self.CurrentTarget].nPkt = int(content)
        if self.CurrentElement == "sourceId":
            if string.upper(content)=='SOURCE':
                self.D.srcId = 0xFFFF
            else:
                self.D.srcId = int(content)
        if self.CurrentElement == "triggerPackets":
            self.D.nTriggerPkt = int(content)

