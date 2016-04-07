/* This is special IO that handle SOURCE and SINK data for the task graph */

#include "tgsdp.h"

uint collectedPktOut = 0;				// will be increased when it receives data through SINK port
uchar nSrcTarget;						// how many target nodes the SOURCE will be serving to?
nodemap_t srcTarget[MAX_FAN];			// put those target nodes in this variable

/* handler for timer event */
void hTimer(uint tick, uint unused)
{
	simulationCntr++;
	// Then send packets to client nodes
	ushort i, j, k;
	uint data;
	for(i=0; i<nSrcTarget; i++) {
		// TODO: lanjutkan dakuuuuuu!!!!!!!
		packet.dest_addr = (srcTarget[i].x << 8) + srcTarget[i].y;
		for(j=0; j<srcTarget[i].optLen; j++) {	// for all pattern for the current srcTarget
			packet.seq = srcTarget[i].opt[j];	// seq contains the length of pattern-j, which is contained in the opt variable
			packet.length = sizeof(sdp_hdr_t)+sizeof(cmd_hdr_t)+packet.seq*sizeof(uint);
			for(k=0; k<packet.seq; k++){
				data = sark_rand();
				spin1_memcpy((void *)&packet.data[k*sizeof(uint)], (void *)&data, sizeof(uint));
			}
			spin1_send_sdp_msg(&packet, DEF_TIMEOUT);
			io_printf(IO_BUF, "Sending to node-%u at <%u,%u> with data: [ ", srcTarget[i].nodeID, srcTarget[i].x, srcTarget[i].y);
			for(k=0; k<packet.seq; k++) {
				spin1_memcpy((void *)&data, (void *)&packet.data[k*sizeof(uint)], sizeof(uint));
				io_printf(IO_BUF, "0x%x ", data);
			}
			io_printf(IO_BUF, "]\n");
		}
	}
}

/* handler for SDP event, especially for retrieving configuration and also in case of SINK data */
void hSDP(uint mBox, uint port)
{
	sdp_msg_t *msg = (sdp_msg_t *)mBox;
	if(port==DEF_CONF_PORT) {				// retrieve configuration (network map?) from host
		// host send adjacency matrix? to fill up the CHIP_TO_NODE_MAP table.
		if(msg->cmd_rc==TGPKT_CHIP_NODE_MAP) {
			ushort i;
			nTaskNodes = msg->seq;
			nTotalNodes = msg->seq+1;
			myNodeID = (ushort)msg->arg1;
			nodeMap[0].nodeID = (ushort)msg->arg1;
			nodeMap[0].x = (ushort)msg->arg2;
			nodeMap[0].y = (ushort)msg->arg3;
			// TODO: what happened if arg2 and arg3 != myChipID?

			for(i=0; i<nTaskNodes; i++) {
				spin1_memcpy((void *)&nodeMap[i+1].nodeID, (void *)&msg->data[i*6], 2);
				spin1_memcpy((void *)&nodeMap[i+1].x, (void *)&msg->data[i*6+2], 2);
				spin1_memcpy((void *)&nodeMap[i+1].y, (void *)&msg->data[i*6+4], 2);
				//CHIP_TO_NODE_MAP[x][y] = id;
			}
			// let's test it:
			spin1_schedule_callback(printMap, SOURCE_SINK_NODE_ID, 0, PRIORITY_REPORTING);
		}
		// if host send dependency map, then build the list of target nodes
		if(msg->cmd_rc==TGPKT_SOURCE_TARGET) {
			ushort i;
			if(nSrcTarget==0) {
				srcTarget[0].nodeID = msg->seq;
				srcTarget[0].optLen = (ushort)msg->arg2;
				//void splitUintToUshort(uint dIn, ushort *dLow, ushort *dHigh) {
				splitUintToUshort(msg->arg1, &srcTarget[0].y, &srcTarget[0].x);
				spin1_memcpy((void *)srcTarget[0].opt, (void *)msg->data, srcTarget[0].optLen*sizeof(ushort));
				nSrcTarget++;
			}
			else {
				uchar found = 0;
				for(i=0; i<nSrcTarget; i++) {
					if(srcTarget[i].nodeID == msg->seq) {
						splitUintToUshort(msg->arg1, &srcTarget[i].y, &srcTarget[i].x);
						srcTarget[i].optLen = (ushort)msg->arg2;
						spin1_memcpy((void *)srcTarget[i].opt, (void *)msg->data, srcTarget[i].optLen*sizeof(ushort));
						found = 1;
						break;
					}
				}
				if(found==0) {	// new data is sent by host
					srcTarget[nSrcTarget].nodeID = msg->seq;
					srcTarget[nSrcTarget].optLen = (ushort)msg->arg2;
					splitUintToUshort(msg->arg1, &srcTarget[nSrcTarget].y, &srcTarget[nSrcTarget].x);
					spin1_memcpy((void *)srcTarget[nSrcTarget].opt, (void *)msg->data, srcTarget[nSrcTarget].optLen*sizeof(ushort));
					nSrcTarget++;
				}
			}
			// let's test it
			spin1_schedule_callback(printSOURCEtarget, 0, 0, PRIORITY_REPORTING);
		}
		else if(msg->cmd_rc==TGPKT_HOST_SEND_TICK) {
			simulationTick = msg->arg1;
			spin1_set_timer_tick(simulationTick);
			if(simulationRunning==1) {
				spin1_callback_off(TIMER_TICK);
				spin1_callback_on(TIMER_TICK, hTimer, PRIORITY_TIMER);
			}
		}
		else if(msg->cmd_rc==TGPKT_START_SIMULATION) {
			simulationCntr = 0;
			collectedPktOut = 0;
			simulationRunning = 1;
			spin1_callback_on(TIMER_TICK, hTimer, PRIORITY_TIMER);
		}
		else if(msg->cmd_rc==TGPKT_STOP_SIMULATION) {
			simulationRunning = 0;
			spin1_callback_off(TIMER_TICK);
			io_printf(IO_BUF, "Have been running for %u simulation!\n", simulationCntr);
			io_printf(IO_BUF, "Have been receiving %u output packets!\n", collectedPktOut);	// do we need to send to host?
		}
	}
	else if(port==DEF_RECV_PORT) {			// work as a SINK

	}
	spin1_msg_free(msg);
}

void printSOURCEtarget(uint arg0, uint arg1)
{
	ushort i, j;
	for(i=0; i<nSrcTarget; i++) {
		io_printf(IO_BUF, "Source target-ID = %u at <%u,%u> : [ ", srcTarget[i].nodeID, srcTarget[i].x, srcTarget[i].y);
		for(j=0; j<srcTarget[i].optLen; j++) io_printf(IO_BUF, "%u ", srcTarget[i].opt[j]);
		io_printf(IO_BUF, "]\n\n");
	}
}

void c_main()
{
	simulationRunning = 0;
	simulationTick = DEF_SIMULATION_TIME;
	sark_srand ((sark_chip_id () << 8) + sark_core_id() * sv->time_ms); // Init randgen, will be used to generate random data packet
	io_printf(IO_STD, "srcsink is running in core-%d\n", sark_core_id());
	/* initialize packet carrier*/
	packet.cmd_rc = SOURCE_SINK_NODE_ID;				// tell the receiver, who I am
	packet.flags = 0x07;								// no reply is needed
	packet.tag = 0;										// for internal spinnaker machine
	packet.srce_port = (DEF_SEND_PORT << 5) | DEF_CORE;	// might be change during run-time?
	packet.srce_addr = spin1_get_chip_id();
	packet.dest_port = (DEF_RECV_PORT << 5) | DEF_CORE;	// might be change during run-time?
	// items not yet set here: length, dest_addr, seq, arg1, arg2, arg3, and the data

	spin1_set_timer_tick(simulationTick);
	spin1_callback_on(SDP_PACKET_RX, hSDP, PRIORITY_SDP);
	spin1_start(SYNC_NOWAIT);
}

