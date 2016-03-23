#include "tgsdp.h"

/* the handler for SDP packet */
void hSDP(uint mBox, uint port)
{

}

void c_main()
{
    spin1_callback_on (SDP_PACKET_RX, hSDP, PRIORITY_SDP);
    spin1_start(SYNC_NOWAIT);
}

