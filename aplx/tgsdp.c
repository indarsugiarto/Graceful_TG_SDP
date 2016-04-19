/* NOTE:
 * - Ke depannya, apakah mau di buat routing adaptif? MUNGKIN!!!
 */
#include "tgsdp.h"

uint totalGeneratedPackets = 0;
uchar nodeIDinitialized = 0;	// 0 = uninitialized, 1 = initialized

/* Ada fungsi rtr_p2p_get() yang bisa digunakan untuk membaca rute tujuan. Dari sark.h:
 * /*!
   Gets a P2P table entry. Returns a value in the range 0 to 7.

   \param entry the entry number in the range 0..65535
   \return table entry (range 0 to 7)

   uint rtr_p2p_get (uint entry);
 * */

ushort buildMap(sdp_msg_t *msg)
{
	io_printf(IO_STD, "Node-%u at<%u,%u> builds the nodemap\n", myNodeID, sark_chip_id() >> 8, sark_chip_id() & 0xFF); //sark_delay_us(1000*sark_chip_id());
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

void buildDepList(sdp_msg_t *msg)
{
	ushort targetIdx, destID, nOutPkt, srcID, nExpInPkt, nodeID;
	ushort i, nDependant;

	targetIdx = msg->seq;	// target index in the "output" list/variable; this NOT the destID!!! but an index to an array in the "output" variable!!!

	splitUintToUshort(msg->arg1, &destID, &nodeID);		// get destID in low_arg1 and nodeID in high_arg1
	splitUintToUshort(msg->arg2, &nDependant, &nOutPkt);	// get nDependant in low_arg2 and nOutPkt in high_arg2

	/*
	nDependant = (ushort)msg->arg2;						// get nDependant from arg2
	splitUintToUshort(msg->arg1, &nOutPkt, &destID);	// get the nOutPkt and destID from arg1
	*/
	if(nodeIDinitialized==0) {
		nodeIDinitialized = 1;	// for debugging
		myNodeID = nodeID; //io_printf(IO_BUF, "\n============\nmyNodeID = %u\n============\n",myNodeID);
		//io_printf(IO_BUF, "Node-%u on <%d,%d>\n", myNodeID, sark_chip_id() >> 8, sark_chip_id() & 0xFF); spin1_delay_us(sark_chip_id()*1000);
		io_printf(IO_BUF, "Node-%u on <%d,%d>\n", myNodeID, msg->dest_addr >> 8, msg->dest_addr & 0xFF); // spin1_delay_us(sark_chip_id()*1000);
	}
//	myNodeID = nodeID; //io_printf(IO_BUF, "\n============\nmyNodeID = %u\n============\n",myNodeID);
	//io_printf(IO_BUF, "I'm node-%d with targetIdx = %d!\n", nodeID, targetIdx); return;
	output[targetIdx].target.destID = destID;
	output[targetIdx].target.nPkt = nOutPkt;
	output[targetIdx].target.nDependant = nDependant;
	output[targetIdx].target.nDependantReady = 0;		// reset the counter of nDependantReady

	// a target has at least one dependant
	splitUintToUshort(msg->arg3, &nExpInPkt, &srcID);	// get the first dependant from arg3
	output[targetIdx].dependants[0].srcID = srcID;
	output[targetIdx].dependants[0].nTriggerPkt = nExpInPkt;
	output[targetIdx].dependants[0].pktCntr = 0;		// reset the counter of packets sent by *this* dependant
	// output[targetIdx].dependant[0].data = somewhere in SDRAM, after allocation process using sark_xalloc()

	// optionally, when a target link has several dependants

	if(nDependant > 1) {
		/* dump the data:
					uint n;
					for(n=0; n<msg->length-24; n++) {
						io_printf(IO_BUF, "0x%x ", msg->data[n]);
					}
					io_printf(IO_BUF, "\n");
					*/
		for(i=1; i<nDependant; i++) {
			ushort srcID, nTriggerPkt;
			spin1_memcpy((void *)&srcID, (void *)&msg->data[(i-1)*4], sizeof(ushort));
			spin1_memcpy((void *)&nTriggerPkt, (void *)&msg->data[(i-1)*4+2], sizeof(ushort));
			//io_printf(IO_BUF, "Got srcID-%u, nTriggerPkt-%u\n", srcID, nTriggerPkt);
			output[targetIdx].dependants[i].srcID = srcID;
			output[targetIdx].dependants[i].nTriggerPkt = nTriggerPkt;
		}
	}
	nOutput++;
	// spin1_schedule_callback(printReport,msg->seq,0,PRIORITY_REPORTING); // --> ini bermasalah karena msg->seq di tgsdp.py digunakan untuk counting index target-nya
	spin1_schedule_callback(printReport,0,0,PRIORITY_REPORTING);
}

/* the handler for SDP packet */
void hSDP(uint mBox, uint port)
{
	sdp_msg_t *msg = (sdp_msg_t *)mBox;
	// it is a communication data with the host?
	if (port==DEF_CONF_PORT) {
		if(msg->cmd_rc==TGPKT_HOST_ASK_REPORT) {
			spin1_schedule_callback(printReport,msg->seq,0,PRIORITY_REPORTING);
		}
		else if(msg->cmd_rc==TGPKT_PING) {
			io_printf(IO_BUF, "Chip<%d,%d> receives TGPKT_PING from port-%d\n",msg->dest_addr>>8, msg->dest_addr & 0xFF, port);
		}
		// host send adjacency matrix? to fill up the CHIP_TO_NODE_MAP table.
		else if(msg->cmd_rc==TGPKT_CHIP_NODE_MAP) {
				//io_printf(IO_STD, "Node-%u at<%d,%d> recv something...\n", myNodeID, sark_chip_id() >> 8, sark_chip_id() & 0xFF); spin1_delay_us(1000*sark_chip_id());
				// spin1_msg_free(msg); return;

				nTaskNodes = buildMap(msg);
				nTotalNodes = nTaskNodes+1;
				// let's test it:
				spin1_schedule_callback(printMap, SOURCE_SINK_NODE_ID, 0, PRIORITY_REPORTING);
			}

		// host sends nodes dependency configuration? NOTE: it is not a broadcast,
		// so the host is responsible to determine where to send the data
		else if(msg->cmd_rc==TGPKT_DEPENDENCY) {
			// io_printf(IO_BUF, "Node-%u at<%d,%d> recv TGPKT_DEPENDENCY...\n", myNodeID, sark_chip_id() >> 8, sark_chip_id() & 0xFF); //spin1_delay_us(1000*sark_chip_id());
			buildDepList(msg);
		}
		//TGPKT_STOP_SIMULATION might be useful for debugging, eg. printing how many packets have been processed/delivered
		else if(msg->cmd_rc==TGPKT_STOP_SIMULATION){
			spin1_schedule_callback(printReport, 1, 0, PRIORITY_REPORTING);	// with initNode() inside reporting
		}
	}
	// receiving packets from other nodes?
	// assumption: no "wild" packets sent by "unknown" dependants!!!
	else if(port==DEF_RECV_PORT) {
		///*
		// step1: put to the data container "output"
		ushort srcID = msg->cmd_rc, nPkt = msg->seq;
		uint cek;	// debugging
		spin1_memcpy((void *)&cek, (void *)msg->data, sizeof(uint));
		//io_printf(IO_BUF, "Receiving %d-paket from srcID-%d: 0x%x\n", nPkt, srcID, cek);
		ushort target, deps, pos, sztotal;
		// scan for all target links in the list
		for(target=0; target<nOutput; target++) {
			// for each target, scan all dependency sources
			for(deps=0; deps<output[target].target.nDependant; deps++) {
				// it is sent by the known dependant? which one?
				if(output[target].dependants[deps].srcID == srcID) {

					// check if it is over?
					if(output[target].dependants[deps].pktCntr == output[target].dependants[deps].nTriggerPkt){
						// TODO: what should we do?
						continue;	// skip this deps?
						io_printf(IO_BUF, "[T-%u:D-%u] is full!\n", target, deps, srcID); //spin1_delay_us(1000*sark_chip_id());
					}
					else {					
						//io_printf(IO_BUF, "Adding the packet to target-%d, deps-%d\n",target,deps);
						// Assume that msg->seq is correctly equal with output[target].dependants[deps].nTriggerPkt
						sztotal = nPkt * sizeof(uint);
						pos = output[target].dependants[deps].pktCntr * sztotal;
						spin1_memcpy((void *)&output[target].dependants[deps].data[pos], (void *)msg->data, sztotal);
						// then update the counter
						output[target].dependants[deps].pktCntr++;
						output[target].dependants[deps].totalPktCntr++; // and keep the record of it
						//io_printf(IO_BUF, "Target-%u, dep-%u has collected %u packets\n", target, deps, output[target].dependants[deps].pktCntr); //spin1_delay_us(1000*sark_chip_id());
						// if the number of expected inputs is met, then mark the .nDependantReady and then call checkAllInput()
						if(output[target].dependants[deps].pktCntr == output[target].dependants[deps].nTriggerPkt) {
							//io_printf(IO_BUF, "Target-%u, dep-%u has collected enough %u packets\n", target, deps, output[target].dependants[deps].pktCntr); //spin1_delay_us(1000*sark_chip_id());
							output[target].target.nDependantReady++;
							spin1_schedule_callback(checkAllInput, target, 0, PRIORITY_PROCESSING);
						}
					}
				}
			}
		}
		//*/

	}
	spin1_msg_free(msg);
}

// since checkAllInput() is called within hSDP(), what if we put current target index on arg0
void checkAllInput(uint targetIndex, uint arg1)
{
	ushort i, k, l;
	uint data;
	ushort targetID = output[targetIndex].target.destID;
	ushort x,y;
	// if .nDependantReady is fullfiled, then generate output packets
	if(output[targetIndex].target.nDependantReady == output[targetIndex].target.nDependant) {
		uint pingout = spin1_send_sdp_msg(&histRpt, DEF_TIMEOUT);	// send a histogram ping
		/*
		if(pingout == SUCCESS)
			io_printf(IO_BUF, "Hist ping sent!\n");
		else
			io_printf(IO_BUF, "Hist ping fail!\n");
		*/
		for(i=0; i<nTotalNodes; i++) {
			if(nodeMap[i].nodeID == targetID) {
				x = nodeMap[i].x;
				y = nodeMap[i].y;
				break;
			}
		}
		// if valid, fill the data in the sdp (generated via random?)
		packet.dest_addr = ((ushort)x << 8) + (ushort)y;
		packet.cmd_rc = myNodeID;
		packet.seq = output[targetIndex].target.nPkt;
		for(l=0; l<packet.seq; l++) {
			// Well, actually the following k-loop comes from old implementation. It might not necessary to iterate packet.seq times for dummy data. Just to add some complexity :)
			for(k=0; k<packet.seq; k++){
				data = sark_rand();	// dummy data
				spin1_memcpy((void *)&packet.data[k*sizeof(uint)], (void *)&data, sizeof(uint));
			}
			packet.length = sizeof(sdp_hdr_t) + sizeof(cmd_hdr_t) + packet.seq*sizeof(uint);
			spin1_send_sdp_msg(&packet, DEF_TIMEOUT);
			output[targetIndex].target.pktCntr++;
			totalGeneratedPackets++;
		}
		// reset all counters
		for(i=0; i<output[targetIndex].target.nDependant; i++) {
			output[targetIndex].target.nDependantReady = 0;
			output[targetIndex].dependants[i].pktCntr = 0;
		}
	}
}

/* Print information requested by host. The type of information depends on the value of reqType.
 * eq. reqType 0: show target-dependants information of the node
 ***/
void printReport(uint reqType, uint arg1)
{
	if(reqType==0) {
		ushort t,d;
		io_printf(IO_BUF, "\n==================================================\nMy TGnodeID = %d\n-----------------------------------\n", myNodeID);
		io_printf(IO_BUF, "Number of output targets = %u\n\n", nOutput);
		for(t=0; t<nOutput; t++) {
			io_printf(IO_BUF, "Output target/links index-%u:\n", t);
			io_printf(IO_BUF, "Target node ID: %u\n", output[t].target.destID);
			io_printf(IO_BUF, "Target payload: %u\n", output[t].target.nPkt);
			io_printf(IO_BUF, "Number of dependant: %u\n", output[t].target.nDependant);
			io_printf(IO_BUF, "Data location: 0x%x\n", output[t].target.data);
			io_printf(IO_BUF, "Dependants:\n");
			for(d=0; d<output[t].target.nDependant; d++) {
				io_printf(IO_BUF, "\tDependant index-%u\n", d);
				io_printf(IO_BUF, "\tDependant node ID: %u\n", output[t].dependants[d].srcID);
				io_printf(IO_BUF, "\tDependant trigger amount: %u\n", output[t].dependants[d].nTriggerPkt);
				io_printf(IO_BUF, "\tDependant current #trigger: %u\n", output[t].dependants[d].pktCntr);
				io_printf(IO_BUF, "Data location: 0x%x\n\n", output[t].dependants[d].data);
			}
			io_printf(IO_BUF, "\n");
		}
		io_printf(IO_BUF, "============================================\n");
	}
	else if(reqType==1) {
		ushort t,d, srcID, reqPkt, nRecvPkt, targetID, nGenPkt;
		io_printf(IO_BUF, "\n====================\nReport on node-%u\n-------------------\n", myNodeID);
		// give info how many packets have been generated so far
		for(t=0; t<nOutput; t++) {
			targetID = output[t].target.destID;
			nGenPkt = output[t].target.pktCntr;
			io_printf(IO_BUF, "For target-%u:\n", targetID);
			for(d=0; d<output[t].target.nDependant; d++) {
				srcID = output[t].dependants[d].srcID;
				nRecvPkt = output[t].dependants[d].totalPktCntr;
				reqPkt = output[t].dependants[d].nTriggerPkt;
				io_printf(IO_BUF, "\tReceived packets from node-%u = %u out of %u\n", srcID, nRecvPkt, reqPkt);
			}
			io_printf(IO_BUF, "\tTotal generated packets = %u\n", nGenPkt);
		}
		initNode();
	}
}

void initNode(){
	// initialize output data (especially with dependency packet counter)
	ushort out, dep;
	for(out=0; out<MAX_TARGET; out++) {
		output[out].target.pktCntr = 0;
		for(dep=0; dep<MAX_DEPENDENCY; dep++) {
			output[out].dependants[dep].pktCntr = 0;			
		}
	}
	totalGeneratedPackets = 0;
}

void c_main()
{
	nOutput = 0;
	simulationTick = DEF_SIMULATION_TIME;
	sark_srand ((sark_chip_id () << 8) + sark_core_id() * sv->time_ms); // Init randgen, will be used to generate random data packet

	//io_printf(IO_STD, "tgsdp is running on core-%d with simulation tick-%d\n", sark_core_id(), simulationTick); spin1_delay_us(sark_core_id()*1000);
	/* initialize packet carrier*/
	//packet.cmd_rc = myNodeID;							// tell the receiver, who I am. Won't valid until sent by host
	packet.flags = 0x07;								// no reply is needed
	packet.tag = 0;										// for internal spinnaker machine
	packet.srce_port = (DEF_SEND_PORT << 5) | DEF_CORE;	// might be change during run-time?
	packet.srce_addr = (ushort)spin1_get_chip_id();
	packet.dest_port = (DEF_RECV_PORT << 5) | DEF_CORE;	// might be change during run-time?
	// items not yet set here: cmd_rc(myNodeID), length, dest_addr, seq, arg1, arg2, arg3, and the data (Note: arg1, arg2, and arg3 are not used!!!)

	// for reporting signal that can be used to build a histogram
	histRpt.flags = 0x07;
	histRpt.tag = TGPKT_NODE_SEND_HIST_IPTAG;			// send via iptag 1
	histRpt.srce_port = (DEF_SEND_PORT << 5) | DEF_CORE;	// might be change during run-time?
	histRpt.srce_addr = spin1_get_chip_id();
	histRpt.dest_port = PORT_ETH;
	histRpt.dest_addr = sv->dbg_addr;
	histRpt.length = sizeof(sdp_hdr_t);
	//histRpt.cmd_rc = TGPKT_NODE_SEND_HIST_RPT;
	//histRpt.seq = 0;
	//histRpt.length = sizeof(sdp_hdr_t) + sizeof(cmd_hdr_t);					// just send a ping


    spin1_callback_on (SDP_PACKET_RX, hSDP, PRIORITY_SDP);
	// test: why printReport is not executed? TIDAK MAU DENGAN PRIORITY 5
	// io_printf(IO_BUF, "Scheduling printReport...\n");
	// spin1_schedule_callback(printReport,0,0,PRIORITY_REPORTING);
	spin1_start(SYNC_NOWAIT);
}
