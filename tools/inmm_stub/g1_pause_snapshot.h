#ifndef G1_PAUSE_SNAPSHOT_H
#define G1_PAUSE_SNAPSHOT_H

/* H-PM2: program state 23 (Esc pause menu and its sub windows).  While paused
 * the game restores the whole screen buffer from a frozen world surface every
 * present, so a sub window that is closed leaves world pixels back on screen
 * but the HD mirror still holds the sub window's values.  The present loop
 * snapshots the HD state valid on the entering present and, while paused,
 * restores a pixel from it when the existing path would not show HD and the
 * screen pixel equals the snapshot's expected value. */
#define G1_PAUSE_PROGRAM_STATE 23u

enum {
    G1_PAUSE_PICK_NEAREST = 0,
    G1_PAUSE_PICK_EXISTING_HD = 1,
    G1_PAUSE_PICK_RESTORE = 2
};

enum {
    G1_PAUSE_ACTION_NONE = 0,
    G1_PAUSE_ACTION_CAPTURE = 1,
    G1_PAUSE_ACTION_INVALIDATE = 2
};

/* Existing HD (covered and expected == pixel) wins; otherwise a valid snapshot
 * entry equal to the pixel restores; everything else stays nearest. */
static inline int g1_pause_restore_pick(int covered, unsigned char expected,
                                        unsigned char pixel, int snap_valid,
                                        unsigned char snap_expected)
{
    if (covered && expected == pixel) return G1_PAUSE_PICK_EXISTING_HD;
    if (snap_valid && snap_expected == pixel) return G1_PAUSE_PICK_RESTORE;
    return G1_PAUSE_PICK_NEAREST;
}

static inline int g1_pause_snapshot_action(unsigned long previous_state,
                                           unsigned long state)
{
    if (state == G1_PAUSE_PROGRAM_STATE && previous_state != G1_PAUSE_PROGRAM_STATE)
        return G1_PAUSE_ACTION_CAPTURE;
    if (previous_state == G1_PAUSE_PROGRAM_STATE && state != G1_PAUSE_PROGRAM_STATE)
        return G1_PAUSE_ACTION_INVALIDATE;
    return G1_PAUSE_ACTION_NONE;
}

static inline int g1_pause_restore_active(unsigned long state, int snapshot_ready)
{
    return snapshot_ready && state == G1_PAUSE_PROGRAM_STATE;
}

#endif
