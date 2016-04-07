/* NOTE:
 * - Ke depannya, apakah mau di buat routing adaptif? MUNGKIN!!!
 */
#include "tgsdp.h"

/* Ada fungsi rtr_p2p_get() yang bisa digunakan untuk membaca rute tujuan. Dari sark.h:
 * /*!
   Gets a P2P table entry. Returns a value in the range 0 to 7.

   \param entry the entry number in the range 0..65535
   \return table entry (range 0 to 7)

   uint rtr_p2p_get (uint entry);
 * */


/* the handler for SDP packet */
void hSDP(uint mBox, uint port)
{
	sdp_msg_t *msg = (sdp_msg_t *)mBox;
	// it is a communication data with the host?
	if (port==DEF_CONF_PORT) {
		if(msg->cmd_rc==TGPKT_HOST_ASK_REPORT) {
			spin1_schedule_callback(printReport,msg->seq,0,PRIORITY_REPORTING);
		}
		// host send adjacency matrix? to fill up the CHIP_TO_NODE_MAP table.
		else if(msg->cmd_rc==TGPKT_CHIP_NODE_MAP) {
				ushort i;
				nTaskNodes = msg->seq;
				nTotalNodes = msg->seq+1;
				nodeMap[0].nodeID = (ushort)msg->arg1;	// node[0] is SOURCE/SINK node?
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
				spin1_schedule_callback(printMap, 0, 0, PRIORITY_REPORTING);
			}

		// host sends nodes dependency configuration? NOTE: it is not a broadcast,
		// so the host is responsible to determine where to send the data
		else if(msg->cmd_rc==TGPKT_DEPENDENCY) {
			ushort targetIdx, destID, nOutPkt, srcID, nExpInPkt, nodeID;
			ushort i, nDependant;

			targetIdx = msg->seq;	// target index in the "output" list/variable; this NOT the destID!!! but an index to an array in the "output" variable!!!

			splitUintToUshort(msg->arg1, &destID, &nodeID);		// get destID in low_arg1 and nodeID in high_arg1
			splitUintToUshort(msg->arg2, &nDependant, &nOutPkt);	// get nDependant in low_arg2 and nOutPkt in high_arg2

			/*
			nDependant = (ushort)msg->arg2;						// get nDependant from arg2
			splitUintToUshort(msg->arg1, &nOutPkt, &destID);	// get the nOutPkt and destID from arg1
			*/

			myNodeID = nodeID;
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
		}
	}
	// receiving packets from other nodes?
	else if(port==DEF_RECV_PORT) {
		/*
		if(msg->cmd_rc < SOURCE_SINK_NODE_ID) {	// it was sent by normal node, not a SOURCE
			// the length of the data will be carried on the arg1 parameter
			ushort idx, seq = msg->seq, dLen = msg->arg1;
			// first, get the index of the sender node in the linkIn table
			for(idx=0; idx<linkInCntr; idx++)
				if(linkIn[idx].srcdestID==msg->cmd_rc) break;	// then the index is idx
			// copy the data to pktIn buffer
			spin1_memcpy((void *)pktIn[idx].data[seq], (void *)msg->data, dLen);
			pktIn[idx].cntr++;
			// then check if all required input data are received
			if(checkAllInput())
				processOutput();
		}
		*/
		// let's dumpt it
		char *stream;
		//io_printf(IO_STD, "Receiving %u-packets from node-%u: [ ", msg->seq, msg->cmd_rc); spin1_delay_us(1000*(sark_chip_id()+1));

		if(simulationTick>100000){	// print to IO_STD
			stream = (char *)IO_STD;
		}
		else {	// print IO_BUF
			stream = (char *)IO_BUF;
		}
		io_printf(stream, "Receiving %u-packets from node-%u: [ ", msg->seq, msg->cmd_rc); //spin1_delay_us(1000*sark_chip_id());
		ushort i;
		for(i=0; i<msg->seq; i++){
			io_printf(stream, "0x%x ", msg->data[i*sizeof(uint)]); //spin1_delay_us(1000*sark_chip_id());
		}
		io_printf(stream, "]\n");	//spin1_delay_us(1000*sark_chip_id());

	}
	spin1_msg_free(msg);
}

int checkAllInput()
{
	int result = FALSE;
	// don't forget to clean the pktIn counter if done
	ushort i;
	for(i=0; i<MAX_FAN; i++) {

	}
	return result;
}

void processOutput()
{
	// don't forget to clean the pktOut counter if done
}

/* Print information requested by host. The type of information depends on the value of reqType.
 * eq. reqType 0: show target-dependants information of the node
 ***/
void printReport(uint reqType, uint arg1)
{
	io_printf(IO_BUF, "My TGnodeID = %d\n-----------------------------------\n", myNodeID);
	if(reqType==0) {
		ushort t,d;
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
	}
	io_printf(IO_BUF, "============================================\n");
}

void initNode(){
	// initialize output data (especially with dependency packet counter)
	ushort out, dep;
	for(out=0; out<MAX_TARGET; out++)
		for(dep=0; dep<MAX_DEPENDENCY; dep++)
			output[out].dependants[dep].pktCntr = 0;
}

void c_main()
{
	nOutput = 0;
	simulationTick = DEF_SIMULATION_TIME;
	io_printf(IO_BUF, "tgsdp is running on core-%d with simulation tick-%d\n", sark_core_id(), simulationTick);
	/* initialize packet carrier*/
	//packet.cmd_rc = myNodeID;							// tell the receiver, who I am. Won't valid until sent by host
	packet.flags = 0x07;								// no reply is needed
	packet.tag = 0;										// for internal spinnaker machine
	packet.srce_port = (DEF_SEND_PORT << 5) | DEF_CORE;	// might be change during run-time?
	packet.srce_addr = spin1_get_chip_id();
	packet.dest_port = (DEF_RECV_PORT << 5) | DEF_CORE;	// might be change during run-time?
	// items not yet set here: cmd_rc(myNodeID), length, dest_addr, seq, arg1, arg2, arg3, and the data

    spin1_callback_on (SDP_PACKET_RX, hSDP, PRIORITY_SDP);
	// test: why printReport is not executed? TIDAK MAU DENGAN PRIORITY 5
	// io_printf(IO_BUF, "Scheduling printReport...\n");
	// spin1_schedule_callback(printReport,0,0,PRIORITY_REPORTING);
	spin1_start(SYNC_NOWAIT);
}
