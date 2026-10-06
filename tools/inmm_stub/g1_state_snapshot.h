#ifndef G1_STATE_SNAPSHOT_H
#define G1_STATE_SNAPSHOT_H

#include <windows.h>

BOOL g1_state_snapshot_enabled(void);
BOOL g1_state_snapshot_install(void);
void g1_state_snapshot_detach(void);

#endif
