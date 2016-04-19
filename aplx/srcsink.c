/* This is special IO that handle SOURCE and SINK data for the task graph */

#include "tgsdp.h"

uint collectedPktOut = 0;				// will be increased when it receives data through SINK port
ushort nSrcTarget;						// how many target nodes the SOURCE will be serving to?
nodemap_t srcTarget[MAX_FAN];			// put those target nodes in this variable

uint sdpSendcntr = 0;

ushort buildMap(sdp_msg_t *msg, nodemap_t *nodeMap)
{
	io_printf(IO_STD, "Node-%u at<%u,%u> builds the nodemap\n", myNodeID, sark_chip_id() >> 8, sark_chip_id() & 0xFF); sark_delay_us(1000*sark_chip_id());
	ushort i;
	ushort nTaskNodes = msg->seq;
	nodeMap[0].nodeID = (ushort)msg->arg1;
	nodeMap[0].x = (ushort)msg->arg2;
	nodeMap[0].y = (ushort)msg->arg3;

	for(i=0; i<nTaskNodes; i++) {
		spin1_memcpy((void *)&nodeMap[i+1].nodeID, (void *)&msg->data[i*4], 2);
		nodeMap[i+1].x = msg->data[i*4+2];
		nodeMap[i+1].y = msg->data[i*4+3];
	}
	return nTaskNodes;
}

// generateData() should be a "virtual" function that depends on the application itself
void generateData(uchar *container, ushort N)
{
	ushort i;
	uint data;
	// in this experiment, let's generate N-random data
	for(i=0; i<N; i++) {
		data = sark_rand();
		spin1_memcpy((void *)&container[i*sizeof(uint)], (void *)&data, sizeof(uint));
	}
}

/* handler for timer event */
void hTimer(uint tick, uint unused)
{
	if(tick % simulationTick != 0) return;	// due to spin1_api mechanism
	simulationCntr++;
	// Then send packets to client nodes
	ushort i, j, k;
	uint data;
	// for all target nodes (maybe in different chips)
	for(i=0; i<nSrcTarget; i++) {
		packet.dest_addr = (srcTarget[i].x << 8) + srcTarget[i].y;
		//for(j=0; j<srcTarget[i].optLen; j++) {		// for all pattern for the current srcTarget
		for(j=0; j<1; j++) {	// NEW REVISION: one node target will receive only ONE packet at a time, and it is its responsible to distribute it to its output target
			//packet.seq = srcTarget[i].opt[j];	// seq contains the length of pattern-j, which is contained in the opt variable
			packet.seq = DEF_PACKET_LENGTH;				// NEW REVISION: every triggering might only send "1 uint" packet
			packet.length = sizeof(sdp_hdr_t)+sizeof(cmd_hdr_t)+packet.seq*sizeof(uint);
			generateData(packet.data, packet.seq);		// use "virtual" method to generate data!
			spin1_send_sdp_msg(&packet, DEF_TIMEOUT);
			sdpSendcntr++;	// just for debugging

			// The following is just for debugging -> will be removed later!
			if((simulationCntr * DEF_MINIMUM_TICK * simulationTick) % 1000000 == 0) {
				char *stream;
				stream = (char *)IO_STD;
				io_printf(stream, "[Sim-%u] Sending packet to node-%u at <%u,%u> with data: [ ", simulationCntr, srcTarget[i].nodeID, srcTarget[i].x, srcTarget[i].y); spin1_delay_us(1000);
				for(k=0; k<packet.seq; k++) {
					spin1_memcpy((void *)&data, (void *)&packet.data[k*sizeof(uint)], sizeof(uint));
					io_printf(stream, "0x%x ", data); spin1_delay_us(1000);
				}
				io_printf(stream, "]\n"); spin1_delay_us(1000);
			}
		}
	}
}

/* handler for SDP event, especially for retrieving configuration and also in case of SINK data */
void hSDP(uint mBox, uint port)
{
	//io_printf(IO_STD, "Node-%u at<%d,%d> recv something...\n", myNodeID, sark_chip_id() >> 8, sark_chip_id() & 0xFF); spin1_delay_us(1000*sark_chip_id());
	sdp_msg_t *msg = (sdp_msg_t *)mBox;
	if(port==DEF_CONF_PORT) {				// retrieve configuration (network map?) from host
		// host send adjacency matrix? to fill up the CHIP_TO_NODE_MAP table.
		if(msg->cmd_rc==TGPKT_PING) {
			io_printf(IO_BUF, "Chip<%d,%d> receives TGPKT_PING from port-%d\n",msg->dest_addr>>8, msg->dest_addr & 0xFF, port);
		}
		else if(msg->cmd_rc==TGPKT_CHIP_NODE_MAP) {
			//io_printf(IO_STD, "Node-%u at<%d,%d> recv something...\n", myNodeID, sark_chip_id() >> 8, sark_chip_id() & 0xFF); spin1_delay_us(1000*sark_chip_id());
			//spin1_msg_free(msg); return;

			nTaskNodes = buildMap(msg, nodeMap);
			nTotalNodes = nTaskNodes+1;
			// let's test it:
			spin1_schedule_callback(printMap, SOURCE_SINK_NODE_ID, 0, PRIORITY_REPORTING);
		}
		// if host send the list of target nodes
		else if(msg->cmd_rc==TGPKT_SOURCE_TARGET) {
			ushort i;
			myNodeID = msg->seq;
			io_printf(IO_STD, "srcsink is running in chip<%d,%d> with ID-%u\n", sark_chip_id() >> 8, sark_chip_id() & 0xFF, myNodeID);
			nSrcTarget = msg->arg1;
			for(i=0; i<nSrcTarget; i++) {
				srcTarget[i].nodeID = (ushort)msg->data[i*3];
				srcTarget[i].x = (ushort)msg->data[i*3+1];
				srcTarget[i].y = (ushort)msg->data[i*3+2];
			}
			// let's test it
			spin1_schedule_callback(printSOURCEtarget, 0, 0, PRIORITY_REPORTING);
		}
		else if(msg->cmd_rc==TGPKT_HOST_SEND_TICK) {
			simulationTick = msg->arg1/DEF_MINIMUM_TICK;
		}
		else if(msg->cmd_rc==TGPKT_START_SIMULATION) {
			simulationRunning = 1;
			spin1_callback_on(TIMER_TICK, hTimer, PRIORITY_TIMER);
		}
		else if(msg->cmd_rc==TGPKT_STOP_SIMULATION) {
			simulationRunning = 0;
			spin1_callback_off(TIMER_TICK);
			io_printf(IO_BUF, "Have been running for %u simulation!\n", simulationCntr);
			io_printf(IO_BUF, "Have been receiving %u output packets!\n", collectedPktOut);	// do we need to send to host?
			// reset counter
			simulationCntr = 0;
			collectedPktOut = 0;
			sdpSendcntr = 0;
		}
	}
	else if(port==DEF_RECV_PORT) {			// work as a SINK
		io_printf(IO_BUF, "Receiving %u-packets from node-%u\n", msg->seq, msg->cmd_rc);
		collectedPktOut++;
	}
	spin1_msg_free(msg);
}

void printSOURCEtarget(uint arg0, uint arg1)
{
	ushort i, j;
	for(i=0; i<nSrcTarget; i++) {
		io_printf(IO_STD, "Source target-ID %u is at <%u,%u>\n", srcTarget[i].nodeID, srcTarget[i].x, srcTarget[i].y); spin1_delay_us(1000);
	}
}

void c_main()
{
	simulationRunning = 0;
	simulationTick = DEF_SIMULATION_TIME;
	sark_srand ((sark_chip_id () << 8) + sark_core_id() * sv->time_ms); // Init randgen, will be used to generate random data packet
	//io_printf(IO_STD, "srcsink is running in core-%d\n", sark_core_id());
	/* initialize packet carrier*/
	packet.cmd_rc = SOURCE_SINK_NODE_ID;				// tell the receiver, who I am
	packet.flags = 0x07;								// no reply is needed
	packet.tag = 0;										// for internal spinnaker machine
	packet.srce_port = (DEF_SEND_PORT << 5) | DEF_CORE;	// might be change during run-time?
	packet.srce_addr = spin1_get_chip_id();
	packet.dest_port = (DEF_RECV_PORT << 5) | DEF_CORE;	// might be change during run-time?
	// items not yet set here: length, dest_addr, seq, arg1, arg2, arg3, and the data

	spin1_set_timer_tick(DEF_MINIMUM_TICK);	// due to spin1_api that doesn't allow time scalling during runtime
	spin1_callback_on(SDP_PACKET_RX, hSDP, PRIORITY_SDP);
	spin1_start(SYNC_NOWAIT);
}

