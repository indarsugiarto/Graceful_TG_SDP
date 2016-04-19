# For debugging:
SHOW_PARSING_RESULT     = False
SINGLE_SIMULATION       = True
DEF_MIN_TIMER_TICK      = 100               # in microsecond

DEF_HOST                = '192.168.240.1'   # since we need at least 10 chips
#DEF_HOST                = '192.168.240.253'   # since we need at least 10 chips
DEF_SEND_PORT           = 17893             # tidak bisa diganti dengan yang lain
DEF_TUBO_PORT           = 17892             # just for your info :)
DEF_TUBO_IPTAG          = 0
DEF_REPORT_PORT         = 17900             # for reading report data from SpiNNaker through iptag-1
DEF_REPORT_IPTAG        = 1                 # put this value in ybug!!!
DEF_SEND_IPTAG          = 0                 # for sending *into* SpiNNaker machine
DEF_SDP_CONF_PORT       = 7                 # Use port-7 for configuration
DEF_SDP_CORE            = 1                 # Let's use core-1 at the moment (future: configurable!)
DEF_SDP_TIMEOUT         = 0.025             # in second
WITH_REPLY              = 0x87
NO_REPLY                = 0x07

APPID_TGSDP		        = 16
APPID_SRCSINK	        = 17
APPID_MONITOR           = 255
TGPKT_CHIP_NODE_MAP     = 0xc01e
TGPKT_DEPENDENCY        = 0xdec1
TGPKT_HOST_ASK_REPORT   = 0x2ead
TGPKT_SOURCE_TARGET		= 0x52ce
TGPKT_START_SIMULATION	= 0x6060
TGPKT_STOP_SIMULATION	= 0x7070
TGPKT_HOST_SEND_TICK	= 0x71c4
TGPKT_PING              = 0x7179

DEF_SOURCE_ID = 0xFFFF
DEF_SOURCE_PORT = 1         # SOURCE will send through port-1
DEF_SINK_ID = 0xFFFF
DEF_SINK_PORT = 2           # SINK will receive through port-2
DEF_APP_CORE = 1
DEF_MON_CORE = 2            # cannot use core-17 because some chips don't have it (broken?)

# CHIP_LIST_48 contains 1D array of chipID, starting from 0 (==<0,0>) to 47(==<7,7,>)
CHIP_LIST_48 = [[0,0],[1,0],[2,0],[3,0],[4,0],\
                [0,1],[1,1],[2,1],[3,1],[4,1],[5,1],\
                [0,2],[1,2],[2,2],[3,2],[4,2],[5,2],[6,2],\
                [0,3],[1,3],[2,3],[3,3],[4,3],[5,3],[6,3],[7,3],\
                      [1,4],[2,4],[3,4],[4,4],[5,4],[6,4],[7,4],\
                            [2,5],[3,5],[4,5],[5,5],[6,5],[7,5],\
                                  [3,6],[4,6],[5,6],[6,6],[7,6],\
                                        [4,7],[5,7],[6,7],[7,7]]

# Let's generate static mapping from TGnodes to SpiNN-chips
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
# The following will produce: [65535, 0, 1, 2, 3, 4, 5, 6, 7, 8, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
smallmap = [-1 for _ in range(48)]
for mapItem in range(9):
    smallmap[mapItem+1] = mapItem    # we start from i+1 because chip<0,0> will be used for SOURCE and SINK
smallmap[0] = DEF_SOURCE_ID

bigmap = [-1 for _ in range(48)]
for mapItem in range(47):
    bigmap[mapItem+1] = mapItem    # we start from i+1 because chip<0,0> will be used for SOURCE and SINK
bigmap[0] = DEF_SOURCE_ID

map25 = [-1 for _ in range(48)]
for mapItem in range(25):
    map25[mapItem+1] = mapItem
map25[0] = DEF_SOURCE_ID

tg2spinMap = dict()
tg2spinMap['9Nodes'] = smallmap;
tg2spinMap['47Nodes'] = bigmap;
tg2spinMap['25Nodes'] = map25

