#ifndef G1_CENSUS_H
#define G1_CENSUS_H

#include <windows.h>

/* P1 is measurement-only.  The census detours call the exact original
 * function and never write the renderer or surface buffers. */
BOOL g1_census_enabled(void);
/* Program state the census measures: PS3 unless SYW2_G1_CENSUS_STATE says otherwise. */
DWORD g1_census_target_state(void);
BOOL g1_census_install(void);
void g1_census_detach(void);

/* DirectDraw/GDI adapters are intentionally separate from primitive hooks so
 * their provenance can be recorded without changing the existing W60 path. */
void g1_census_record_surface_write(const char *method, DWORD self,
                                    DWORD source, DWORD destination_width,
                                    DWORD destination_height, DWORD source_width,
                                    DWORD source_height, DWORD program_state,
                                    DWORD game_tick, DWORD caller,
                                    BOOL destination_is_primary,
                                    DWORD destination_caps, DWORD source_caps);

/* Close a logical-frame attribution window at a primary DirectDraw present.
 * The call is measurement-only; it writes the selected writer map to the
 * diagnostic map stream and clears the window for the next present. */
void g1_census_present_boundary(DWORD destination_width,
                                DWORD destination_height,
                                DWORD source_width, DWORD source_height,
                                BOOL destination_is_primary,
                                DWORD program_state, DWORD game_tick,
                                DWORD source_surface, DWORD source_buffer,
                                DWORD source_pitch, BOOL source_locked);

void g1_census_record_surface_buffer(DWORD surface, DWORD buffer, DWORD pitch,
                                    DWORD width, DWORD height);
/* A destination surface smaller than the 800x600 screen buffer (e.g. the 101x40
 * text surface) cannot hold present pixels.  With SYW2_G1_CENSUS_RESIDUAL=1 such
 * Blts are counted apart instead of as missed captures; the default census
 * counts every Blt as before. */
void g1_census_surface_blt_attempt(DWORD destination_width, DWORD destination_height);
/* Residual diagnostics only: why an attempted surface Blt was not captured
 * (1 Blt rect invalid, 2 BltFast rect/lock, 3 Blt lock failed, 7 non-screen surface). */
void g1_census_surface_blt_skipped(DWORD reason);
BOOL g1_census_surface_blt_begin(DWORD buffer, DWORD pitch, DWORD height,
                                 DWORD left, DWORD top, DWORD right, DWORD bottom,
                                 const BYTE *pixels);
void g1_census_surface_blt_end(DWORD buffer, DWORD pitch, DWORD height,
                               DWORD left, DWORD top, DWORD right, DWORD bottom,
                               const BYTE *pixels);

#endif /* G1_CENSUS_H */
