from constDef import *

def getChipXYfromID(TGmap, TGNodeId, table=CHIP_LIST_48):
    # map is a 1D list contains mapping from SPiNNaker-chipID to TG-nodeID
    # so, map might contains 48 elements and each element corresponds to one particular TG-nodeID
    # then using the index in the map, the corresponding <x,y> can be looked-up in CHIP_LIST_48
    for cIdx in range(len(TGmap)):
    # for cIdx in TGmap: -> it doesn't work because some items are negative
        if TGmap[cIdx]==TGNodeId:
            x=table[cIdx][0]
            y=table[cIdx][1]
            break
    return x,y

def experiment_dag0020():
    # Experiment with dag0020: --> this should be done via GUI :)
    # And let assume that aplx's are already there :)
    dag0020 = list()    # dag0020 is a list of cfg

    # Let's start with node-0
    cfg0 = list()        # NOTE: cfg is a list of dict()
    target = dict()
    target['nodeID'] = 0
    target['destID'] = 1
    target['nPkt'] = 3
    target['nDependant'] = 1
    target['dep0_srcID'] = DEF_SOURCE_ID
    target['dep0_nTriggerPkt'] = 4
    cfg0.append(target)
    target = dict()
    target['nodeID'] = 0
    target['destID'] = 2
    target['nPkt'] = 3
    target['nDependant'] = 1
    target['dep0_srcID'] = DEF_SOURCE_ID
    target['dep0_nTriggerPkt'] = 3
    cfg0.append(target)
    target = dict()
    target['nodeID'] = 0
    target['destID'] = 4
    target['nPkt'] = 2
    target['nDependant'] = 1
    target['dep0_srcID'] = DEF_SOURCE_ID
    target['dep0_nTriggerPkt'] = 2
    cfg0.append(target)
    dag0020.append(cfg0)

    # Then node-1
    cfg1 = list()
    target = dict()
    target['nodeID'] = 1
    target['destID'] = 3
    target['nPkt'] = 3
    target['nDependant'] = 1
    target['dep0_srcID'] = 0
    target['dep0_nTriggerPkt'] = 4
    cfg1.append(target)
    target = dict()
    target['nodeID'] = 1
    target['destID'] = 5
    target['nPkt'] = 2
    target['nDependant'] = 1
    target['dep0_srcID'] = 0
    target['dep0_nTriggerPkt'] = 3
    cfg1.append(target)
    target = dict()
    target['nodeID'] = 1
    target['destID'] = 6
    target['nPkt'] = 2
    target['nDependant'] = 1
    target['dep0_srcID'] = 0
    target['dep0_nTriggerPkt'] = 2
    cfg1.append(target)
    dag0020.append(cfg1)

    # Then node-2
    cfg2 = list()
    target = dict()
    target['nodeID'] = 2
    target['destID'] = 3
    target['nPkt'] = 1
    target['nDependant'] = 1
    target['dep0_srcID'] = 0
    target['dep0_nTriggerPkt'] = 5
    cfg2.append(target)
    target = dict()
    target['nodeID'] = 2
    target['destID'] = 5
    target['nPkt'] = 4
    target['nDependant'] = 1
    target['dep0_srcID'] = 0
    target['dep0_nTriggerPkt'] = 3
    cfg2.append(target)
    dag0020.append(cfg2)


    # Then node-3
    cfg3 = list()
    target = dict()
    target['nodeID'] = 3
    target['destID'] = 4
    target['nPkt'] = 2
    target['nDependant'] = 1
    target['dep0_srcID'] = 2
    target['dep0_nTriggerPkt'] = 3
    cfg3.append(target)
    target = dict()
    target['nodeID'] = 2
    target['destID'] = 8
    target['nPkt'] = 4
    target['nDependant'] = 2
    target['dep0_srcID'] = 2
    target['dep0_nTriggerPkt'] = 1
    target['dep1_srcID'] = 1
    target['dep1_nTriggerPkt'] = 4
    cfg3.append(target)
    dag0020.append(cfg3)

    # Then node-4
    cfg4 = list()
    target = dict()
    target['nodeID'] = 4
    target['destID'] = 5
    target['nPkt'] = 2
    target['nDependant'] = 1
    target['dep0_srcID'] = 3
    target['dep0_nTriggerPkt'] = 4
    cfg4.append(target)
    target = dict()
    target['nodeID'] = 4
    target['destID'] = 6
    target['nPkt'] = 3
    target['nDependant'] = 1
    target['dep0_srcID'] = 0
    target['dep0_nTriggerPkt'] = 3
    cfg4.append(target)
    dag0020.append(cfg4)

    # Then node-5
    cfg5 = list()
    target = dict()
    target['nodeID'] = 5
    target['destID'] = 6
    target['nPkt'] = 3
    target['nDependant'] = 1
    target['dep0_srcID'] = 4
    target['dep0_nTriggerPkt'] = 4
    cfg5.append(target)
    target = dict()
    target['nodeID'] = 5
    target['destID'] = 7
    target['nPkt'] = 2
    target['nDependant'] = 2
    target['dep0_srcID'] = 2
    target['dep0_nTriggerPkt'] = 3
    target['dep1_srcID'] = 4
    target['dep1_nTriggerPkt'] = 6
    cfg5.append(target)
    target = dict()
    target['nodeID'] = 5
    target['destID'] = 8
    target['nPkt'] = 1
    target['nDependant'] = 2
    target['dep0_srcID'] = 2
    target['dep0_nTriggerPkt'] = 4
    target['dep1_srcID'] = 1
    target['dep1_nTriggerPkt'] = 1
    cfg5.append(target)
    dag0020.append(cfg5)

    # Then node-6
    cfg6 = list()
    target = dict()
    target['nodeID'] = 6
    target['destID'] = 8
    target['nPkt'] = 6
    target['nDependant'] = 3
    target['dep0_srcID'] = 4
    target['dep0_nTriggerPkt'] = 3
    target['dep1_srcID'] = 1
    target['dep1_nTriggerPkt'] = 2
    target['dep2_srcID'] = 5
    target['dep2_nTriggerPkt'] = 1
    cfg6.append(target)
    dag0020.append(cfg6)

    # Then node-7
    cfg7 = list()
    target = dict()
    target['nodeID'] = 7
    target['destID'] = 8
    target['nPkt'] = 2
    target['nDependant'] = 1
    target['dep0_srcID'] = 5
    target['dep0_nTriggerPkt'] = 4
    cfg7.append(target)
    dag0020.append(cfg7)

    # Then node-8
    cfg8 = list()
    target = dict()
    target['nodeID'] = 8
    target['destID'] = DEF_SINK_ID
    target['nPkt'] = 2
    target['nDependant'] = 4
    target['dep0_srcID'] = 5
    target['dep0_nTriggerPkt'] = 3
    target['dep1_srcID'] = 3
    target['dep1_nTriggerPkt'] = 8
    target['dep2_srcID'] = 6
    target['dep2_nTriggerPkt'] = 1
    target['dep3_srcID'] = 7
    target['dep3_nTriggerPkt'] = 3
    cfg8.append(target)
    dag0020.append(cfg8)

    return dag0020

def showParsingResult(Handler):
    print "Link Payload (NodeID : TargetID (payload))"
    for nodes in Handler.Nodes:
        print nodes.Id, ":",
        for target in nodes.Target:
            print target.destId, "(", target.nPkt, ")",
        print
    print


    print "Target Dependency (NodeID : TargetID (Dependants)"
    for nodes in Handler.Nodes:
        print nodes.Id, ":",
        for target in nodes.Target:
            print target.destId, "(",
            for dep in target.Dep:
                print dep.srcId,
            print "), ",
        print

    print

    print "Detailed Target Dependency\n---------------------------"
    for n in range(Handler.NumberOfNodes):
        print "number of Targets for node-{} = {}".format(n, Handler.Nodes[n].numTarget)
        for t in range(Handler.Nodes[n].numTarget):
            print "\tnumber of Dependencies for Target-{} in Node-{} = {}".format(t, n, Handler.Nodes[n].Target[t].nDependant)
            for d in range(Handler.Nodes[n].Target[t].nDependant):
                print "\t\tSource-ID-idx-{} = {}".format(d,Handler.Nodes[n].Target[t].Dep[d].srcId),
            print
            for d in range(Handler.Nodes[n].Target[t].nDependant):
                print "\t\tnTriggerPkt-ID-idx-{} = {}".format(d,Handler.Nodes[n].Target[t].Dep[d].nTriggerPkt),
            print
        print "\n\n"
