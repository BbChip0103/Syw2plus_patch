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
DWORD g1_hd_asset_identity_cache_bytes(void);
DWORD g1_hd_asset_identity_evictions(void);
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
/* Pointer-free HD pack (SYW2_G1_HD_PACK): per-key counters of the first attempt. */
BOOL g1_hd_asset_pack_enabled(void);
DWORD g1_hd_asset_pack_hits(void);
DWORD g1_hd_asset_pack_misses(void);
DWORD g1_hd_asset_pack_rejects(void);
DWORD g1_hd_asset_pack_skipped_aux(void);
DWORD g1_hd_asset_pack_lookup_blocks(void);
DWORD g1_hd_asset_pack_lut_hits(void);
DWORD g1_hd_asset_pack_lut_rejects(void);
DWORD g1_hd_asset_pack_lut_key_color(void);
DWORD g1_hd_asset_pack_lut_nonidentity(void);
/* H-HDU0/H-HDU1: 0x466B50 and the clip-box 0x466BE0 (left/right flipped remap RLE) as an identity key; SYW2_G1_HD_PACK_FLIP=0 keeps the diff mirror. */
BOOL g1_hd_asset_flip_key_path(void);
/* H-HDB0/H-HDB1: 0x4672E0 (50% translucent logo RLE) and 0x467580 (weighted translucent RLE) as identity keys; SYW2_G1_HD_PACK_BLEND=0 keeps the diff mirror. */
BOOL g1_hd_asset_blend_key_path(void);
/* H-HDB3: the flipped translucent writers 0x467FD0 and 0x4685C0; they also follow SYW2_G1_HD_PACK_FLIP=0 (diff mirror only). */
BOOL g1_hd_asset_blend_flip_key_path(void);
const BYTE *g1_hd_asset_current_pack_frame(DWORD *hd_width, DWORD *hd_height);
/* H-HDN0: frames found under the extended (prefix length) name when the plain name collides; SYW2_G1_HD_PACK_EXT=0 disables the lookup. */
DWORD g1_hd_asset_pack_ext_hits(void);
DWORD g1_hd_asset_pack_ext_misses(void);
DWORD g1_hd_asset_pack_ext_rejects(void);
DWORD g1_hd_asset_pack_blend_hits(void);
DWORD g1_hd_asset_pack_blend_misses(void);
DWORD g1_hd_asset_pack_blend_rejects(void);
DWORD g1_hd_asset_pack_flip_hits(void);
DWORD g1_hd_asset_pack_flip_misses(void);
DWORD g1_hd_asset_pack_flip_rejects(void);
/* Whole-screen raw picture (SYW2_G1_HD_PACK_FULLSCREEN): key = FNV-1a of all width*height 1x bytes; NULL = no pack frame. */
const BYTE *g1_hd_asset_fullscreen_frame(DWORD hash, DWORD width, DWORD height);
DWORD g1_hd_asset_fullscreen_hits(void);
DWORD g1_hd_asset_fullscreen_misses(void);
DWORD g1_hd_asset_fullscreen_rejects(void);
DWORD g1_hd_asset_fullscreen_loads(void);
/* H-HDPAL: pack frames live in <pack>\<pal8>\<name>; pal8 = FNV-1a of the 768 R,G,B bytes of the renderer PALETTEENTRY array, or of start*4 (+0x419A0) when the screen is only a darkened imjin2. */
DWORD g1_hd_asset_palette_digest(void);
DWORD g1_hd_asset_palette_family(void);   /* 1 = the screen is a darkened start-up palette (imjin2 family) */
DWORD g1_hd_asset_palette_changes(void);
DWORD g1_hd_asset_pack_pal_misses(void);
/* Shaded terrain (SYW2_G1_HD_PACK_SHADE): reasons 0 aux, 1 table, 2 range, 3 source, 4 selfcheck, 5 refresh. */
DWORD g1_hd_asset_pack_shade_hits(void);
DWORD g1_hd_asset_pack_shade_rejects(void);
DWORD g1_hd_asset_pack_shade_rejects_by_reason(DWORD reason);
DWORD g1_hd_asset_pack_shade_selfcheck_pixels(void);
DWORD g1_hd_asset_pack_shade_multi_keys(void);
DWORD g1_hd_asset_pack_shade_key_color(void);
DWORD g1_hd_asset_pack_shade_lut_bytes(void);
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
