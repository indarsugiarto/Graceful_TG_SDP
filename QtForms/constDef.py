DEF_HOST                = '192.168.240.1'   # since we need at least 10 chips
DEF_SEND_PORT           = 17893             # tidak bisa diganti dengan yang lain
DEF_TUBO_PORT           = 17892             # just for your info :)
DEF_SEND_IPTAG          = 0                 # for sending *into* SpiNNaker machine
DEF_SDP_CONF_PORT       = 7                 # Use port-7 for configuration
DEF_SDP_CORE            = 1                 # Let's use core-1 at the moment (future: configurable!)
DEF_SDP_TIMEOUT         = 0.025             # in second
WITH_REPLY              = 0x87
NO_REPLY                = 0x07

APPID_TGSDP		        = 16
APPID_SRCSINK	        = 17
TGPKT_CHIP_NODE_MAP     = 0xc01e
TGPKT_DEPENDENCY        = 0xdec1
TGPKT_HOST_ASK_REPORT   = 0x2ead
TGPKT_SOURCE_TARGET		= 0x52ce
TGPKT_START_SIMULATION	= 0x6060
TGPKT_STOP_SIMULATION	= 0x7070
TGPKT_HOST_SEND_TICK	= 0x71c4

DEF_SOURCE_ID = 0xFFFF
DEF_SOURCE_PORT = 1         # SOURCE will send through port-1
DEF_SINK_ID = 0xFFFF
DEF_SINK_PORT = 2           # SINK will receive through port-2

# CHIP_LIST_48 contains 1D array of chipID, starting from 0 (==<0,0>) to 47(==<7,7,>)
CHIP_LIST_48 = [[0,0],[1,0],[2,0],[3,0],[4,0],\
                [0,1],[1,1],[2,1],[3,1],[4,1],[5,1],\
                [0,2],[1,2],[2,2],[3,2],[4,2],[5,2],[6,2],\
                [0,3],[1,3],[2,3],[3,3],[4,3],[5,3],[6,3],[7,3],\
                      [1,4],[2,4],[3,4],[4,4],[5,4],[6,4],[7,4],\
                            [2,5],[3,5],[4,5],[5,5],[6,5],[7,5],\
                                  [3,6],[4,6],[5,6],[6,6],[7,6],\
                                        [4,7],[5,7],[6,7],[7,7]]

