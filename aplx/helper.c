#include "tgsdp.h"

/*================================== Helper Functions ===================================*/
/* splitting an uint into two ushorts */
void splitUintToUshort(uint dIn, ushort *dLow, ushort *dHigh) {
	ushort temp[2];
	spin1_memcpy((void *)temp, (void *)&dIn, sizeof(uint));
	*dLow = temp[0];
	*dHigh = temp[1];
}

void printMap(uint arg0, uint arg1)
{
	ushort i,myX,myY;
	if(arg0==SOURCE_SINK_NODE_ID) {
		myX = sark_chip_id() >> 8;
		myY = sark_chip_id() & 0xFF;
		io_printf(IO_BUF, "SINK/SOURCE Id = %u, running at <%u,%u>\n", myNodeID, myX, myY);
	}
	for(i=0; i<nTotalNodes; i++) io_printf(IO_BUF, "Node-%u : <%u,%u>\n",nodeMap[i].nodeID, nodeMap[i].x, nodeMap[i].y);
}
/*
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
*/
