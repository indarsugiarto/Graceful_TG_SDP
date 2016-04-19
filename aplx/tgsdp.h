#ifndef TGSDP_H
#define TGSDP_H

#include <spin1_api.h>

//#define DEF_SIMULATION_TIME		1	// in microseconds
//#define DEF_SIMULATION_TIME		100000	// ==0.5 second
//#define DEF_SIMULATION_TIME		2000000	// ==2 second
#define DEF_SIMULATION_TIME		100000	// ==1 second, since we use 10micro tick?
#define DEF_MINIMUM_TICK		10						// using 1micro seems too much?
#define DEF_PACKET_LENGTH		1

/* priority assignment for API callback */
#define PRIORITY_SDP			0
#define PRIORITY_REPORTING		3						// whoaaa, spin1_schedule_callback() DOESN'T work with priority 5????
#define PRIORITY_TIMER			-1
#define PRIORITY_PROCESSING		2

/* basic definitions */
#define APPID_TGSDP		16
#define APPID_SRCSINK	17
#define MAX_NODE_NUM	48								// assume that we're working with 48 boards (max is 47*24*5*10), with a special node for SOURCE and SINK in each board
#define MAX_X_SIZE		7								// max is 256 for the whole SpiNNaker big machine
#define MAX_Y_SIZE		7
#define MAX_FAN			10								// how many nodes can be connected to me?
#define MAX_WEIGHT		10								// how many data-per-link?
#define MAX_TARGET		10								// one node has, at most, MAX_TARGET output links
#define MAX_DEPENDENCY	10

/* for sdp mechanism */
#define TGPKT_PING					0x7179					// for debugging, why some chips produce WDOG???
#define DEF_TIMEOUT					10
#define TGPKT_NORMAL_ID				1
#define TGPKT_HOST_ASK_REPORT		0x2ead
#define TGPKT_CHIP_NODE_MAP			0xc01e
#define TGPKT_DEPENDENCY			0xdec1
#define TGPKT_SOURCE_TARGET			0x52ce
#define TGPKT_START_SIMULATION		0x6060
#define TGPKT_STOP_SIMULATION		0x7070
#define TGPKT_HOST_SEND_TICK		0x71c4
#define TGPKT_NODE_SEND_HIST_RPT	0x4127
#define TGPKT_NODE_SEND_HIST_IPTAG	1
#define DEF_CORE					1
#define DEF_SEND_PORT				1						// a node will send the packet out through this port
#define DEF_RECV_PORT				2						// a node will receive packet from others via this port
#define DEF_SENDACK_PORT			3						// a node will send an acknowledge to the sender via this port
#define DEF_RECVACK_PORT			4
#define DEF_CONF_PORT				7						// default configuration port used by the host to configure aplx
#define SOURCE_SINK_NODE_ID			0xFFFF


/* generic variables */
ushort			myNodeID;
sdp_msg_t		packet;										// packet data that will be sent out to other nodes
sdp_msg_t		histRpt;								// only task node will implement this
volatile uint	simulationTick;							// will be used by SOURCE node for its timer
volatile uint	simulationRunning;// = 0;			// INFO: karena aku pakai helper.c, inisialisasi di sini menyebabkan redundancy: multple definition of 'simulationRunning' first defined here (.bss+0x0)
uint			simulationCntr;

/*----------------------------------- Related with Global Node Mapping --------------------------------*/
// ushort CHIP_TO_NODE_MAP[MAX_X_SIZE][MAX_Y_SIZE];		// table that stores mapping from nodeID to chip_address
														// cannot be negative, since cmd_rc is ushort
														// the special case for SOURCE and SINK: 0xFFFF, SOURCE-port is 1, SINK-port is 2

typedef struct {
	ushort nodeID;
	ushort x;
	ushort y;
	ushort optLen;								// length of optional data
	ushort opt[6];								// optional data, eg. for carying payload for SOURCE node that contains sourcing patterns. 6 karena hanya pakai arg1, arg2 dan arg3
} nodemap_t;

nodemap_t	nodeMap[MAX_NODE_NUM];
ushort		nTotalNodes, nTaskNodes;
/*-----------------------------------------------------------------------------------------------------*/

/*----------------------------------- Related with Node Configuration ---------------------------------*/
typedef struct {
	ushort destID;										// destination node-ID
	ushort nPkt;										// number of packets it sends to the given destID-node at once
	uint pktCntr;										// to count how many packets have been generated for a specific output link
	ushort nDependant;									// number of dependant links (might helpful to count how many packets it has received)
	ushort nDependantReady;								// will count how many dependants have fullfil the dependency
														// if nDependantReady==nDependant, this target link will "fire" (and reset the nDependantReady counter)
	uint data[MAX_WEIGHT];								// the real data container to be sent out, should be in sysram or sdram (in the future)
} target_t;

typedef struct {
	ushort srcID;										// source node-ID
	ushort nTriggerPkt;									// total number of expected triggering packets from this dependant
	ushort pktCntr;										// the counter of current number of packets sent by srcID
														// everytime pktCntr==nTriggerPkt, the target_t.nDependantReady will be increased by one
	uint totalPktCntr;									// for diagnostic purpose, count how many packets have been received from this particular dependant
	uint data[MAX_WEIGHT*MAX_WEIGHT];					// the real data container to buffer the data from srcID, should be in sysram or sdram (in the future)
														// the number of data element is a "square" because it might receive a bunch of packets SEVERAL TIMES!!!
} dependency_t;

typedef struct {
	target_t target;
	dependency_t dependants[MAX_DEPENDENCY];
} output_t;

// each node may have one or several target_t data and each target data may require one or several dependeny_t data
// TODO: it might be better if it stored in sysram or sdram
// variable output basically represent the target links this node has
output_t output[MAX_TARGET];		// each node may have one or several target_t data and each target data may require one or several dependeny_t data
									// eg. output[2], means that *THIS* node is targeting the second node in its output list with given dependency data
ushort nOutput;// = 0;


/*------------------------------------------- forward declaration ---------------------------------------------*/
void hSDP(uint mBox, uint port);
void updateMyLinks();

//void getDestChip(short nodeID, ushort *x, ushort *y);	// get the actual chip<x,y> from the given nodeID
void printReport(uint reqType, uint arg1);
void printSOURCEtarget(uint arg0, uint arg1);
void initNode();
void checkAllInput(uint targetIndex, uint arg1);
// the following are in helper.c:
void splitUintToUshort(uint dIn, ushort *dLow, ushort *dHigh);
void printMap(uint arg0, uint arg1);
//ushort buildMap(sdp_msg_t *msg, nodemap_t *nodeMap);			// will return how many "task" nodes (excluding SOURCE/SINK) are found

/*------------------------------------------------------------------------------------------------------*/
#endif // TGSDP_H

