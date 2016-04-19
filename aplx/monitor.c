/* SYNOPSIS:
 *   - I'm supposed to:
 *       1. monitor the traffic and do traffic management.
 *       2. do process migration, amelioration, etc
 *   - Where to put me? core-17?
 * */
#include "tgsdp.h"


void c_main()
{
	io_printf(IO_BUF, "monitor is running in core-%d\n", sark_core_id());
	spin1_start(SYNC_NOWAIT);
}
