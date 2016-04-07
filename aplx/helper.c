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

