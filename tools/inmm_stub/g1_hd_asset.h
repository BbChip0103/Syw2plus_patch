#ifndef G1_HD_ASSET_H
#define G1_HD_ASSET_H

#include <windows.h>

/* P2 identity source: the original primitive has already decoded the
 * source frame into the sentinel mask/value pair.  This module only records
 * the stable source key and marks pixels produced by that frame; it never
 * reads or writes the game's renderer buffer. */
BOOL g1_hd_asset_enabled(void);
const char *g1_hd_asset_source_name(void);
void g1_hd_asset_reset(void);
BOOL g1_hd_asset_begin(const BYTE *source, DWORD writer,
                       DWORD width, DWORD height, LONG origin_x, LONG origin_y);
BOOL g1_hd_asset_begin_with_aux(const BYTE *source, DWORD writer,
                                const BYTE *auxiliary, DWORD auxiliary_digest,
                                DWORD width, DWORD height,
                                LONG origin_x, LONG origin_y);
BOOL g1_hd_asset_needs_identity_frame(void);
BOOL g1_hd_asset_current_ready(void);
BOOL g1_hd_asset_compare_visible_frame(const BYTE *frame, DWORD frame_stride,
                                       DWORD width, DWORD height);
BOOL g1_hd_asset_compare_visible_frame_in_viewport(
    const BYTE *frame, DWORD frame_stride, DWORD width, DWORD height,
    LONG viewport_left, LONG viewport_top, LONG viewport_right,
    LONG viewport_bottom);
BOOL g1_hd_asset_verify_unclipped_frame(const BYTE *screen_frame,
                                        const BYTE *unclipped_frame,
                                        DWORD frame_stride,
                                        DWORD unclipped_stride,
                                        DWORD width, DWORD height);
BOOL g1_hd_asset_verify_unclipped_frame_in_viewport(
    const BYTE *screen_frame, const BYTE *unclipped_frame,
    DWORD frame_stride, DWORD unclipped_stride, DWORD width, DWORD height,
    LONG viewport_left, LONG viewport_top, LONG viewport_right,
    LONG viewport_bottom);
BOOL g1_hd_asset_bind_identity_frame(const BYTE *frame, DWORD frame_stride,
                                     const BYTE *written, DWORD written_stride,
                                     DWORD width, DWORD height);
BOOL g1_hd_asset_lookup_identity_block(DWORD logical_pixel,
                                       BYTE *top_left, BYTE *top_right,
                                       BYTE *bottom_left, BYTE *bottom_right);
BOOL g1_hd_asset_lookup_identity_block_at(DWORD x, DWORD y,
                                          BYTE *top_left, BYTE *top_right,
                                          BYTE *bottom_left, BYTE *bottom_right);
BOOL g1_hd_asset_probe_negative_key_mismatch(void);
void g1_hd_asset_mark(DWORD logical_pixel);
void g1_hd_asset_end(void);
DWORD g1_hd_asset_identity_pixels(void);
DWORD g1_hd_asset_identity_keys(void);
DWORD g1_hd_asset_identity_invalid_sources(void);
DWORD g1_hd_asset_identity_events(void);
DWORD g1_hd_asset_identity_lookup_hits(void);
DWORD g1_hd_asset_identity_lookup_misses(void);
DWORD g1_hd_asset_identity_cache_inserts(void);
DWORD g1_hd_asset_identity_cache_hits(void);
DWORD g1_hd_asset_identity_cache_misses(void);
DWORD g1_hd_asset_identity_cache_refreshes(void);
DWORD g1_hd_asset_identity_negative_lookup_attempts(void);
DWORD g1_hd_asset_identity_negative_lookup_misses(void);
DWORD g1_hd_asset_identity_key_mismatches(void);
DWORD g1_hd_asset_scale2x_blocks(void);
DWORD g1_hd_asset_scale2x_subpixel_differences(void);
DWORD g1_hd_asset_scale2x_palette_violations(void);
DWORD g1_hd_asset_full_frame_calls(void);
DWORD g1_hd_asset_bbox_calls(void);
DWORD g1_hd_asset_clipped_calls(void);
DWORD g1_hd_asset_cache_hit_bytes(void);
DWORD g1_hd_asset_cache_insert_bytes(void);
DWORD g1_hd_asset_cache_refresh_bytes(void);
DWORD g1_hd_asset_clip_replay_mismatches(void);
void g1_hd_asset_last_clip_mismatch(DWORD *x, DWORD *y,
                                   BYTE *screen_value, BYTE *replay_value);

#endif /* G1_HD_ASSET_H */
