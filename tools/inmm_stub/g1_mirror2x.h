#ifndef G1_MIRROR2X_H
#define G1_MIRROR2X_H

#include <windows.h>
#include <ddraw.h>
#include "g1_present_contract.h"

/* W60's opt-in, logical-800 / physical-1600 compositor helpers.  These
 * helpers are intentionally independent of the DirectDraw object lifetime so
 * they can be unit-tested without loading the game. */
BOOL g1_mirror2x_enabled(void);
BOOL g1_mirror2x_present_rect(DWORD destination_width, DWORD destination_height,
                              DWORD source_width, DWORD source_height,
                              DWORD x, DWORD y, const RECT *source_rect,
                              RECT *destination_rect, RECT *effective_source);
BOOL g1_mirror2x_input_point(LONG physical_x, LONG physical_y,
                             LONG *logical_x, LONG *logical_y);
BOOL g1_mirror2x_input_rect(const RECT *physical, RECT *logical);
BOOL g1_mirror2x_input_install(void);
BOOL g1_mirror2x_input_subclass(HWND window);
/* Bounded raw evidence for the input boundary. */
void g1_mirror2x_input_trace(const char *kind, HWND hwnd, UINT message,
                             LONG physical_x, LONG physical_y,
                             LONG logical_x, LONG logical_y,
                             WPARAM wparam, BOOL transformed);

/* One bounded, same-frame record for the W60 present probe.  The hashes are
 * FNV-1a over visible row bytes (padding excluded); the dumps are only the
 * first 32 visible bytes and are provenance samples, not a replacement for
 * the captured frame. */
typedef struct {
    BOOL attempted;
    BOOL success;
    DWORD source_width;
    DWORD source_height;
    DWORD source_stride;
    DWORD destination_width;
    DWORD destination_height;
    DWORD destination_stride;
    DWORD source_hash;
    DWORD destination_hash;
    DWORD nearest_matches;
    DWORD nearest_total;
    DWORD covered_pixels;
    DWORD stale_pixels;
    DWORD pause_snapshot_pixels;
    DWORD pause_restore_pixels;
    DWORD elapsed_ms;
    DWORD primitive_reinvoke_elapsed_ms_total;
    DWORD primitive_reinvoke_elapsed_ms_max;
    DWORD primitive_reinvoke_count;
    DWORD identity_pixels;
    DWORD identity_keys;
    DWORD identity_invalid_sources;
    DWORD identity_events;
    DWORD identity_lookup_hits;
    DWORD identity_lookup_misses;
    DWORD identity_cache_inserts;
    DWORD identity_cache_hits;
    DWORD identity_cache_misses;
    DWORD identity_cache_refreshes;
    DWORD identity_negative_lookup_attempts;
    DWORD identity_negative_lookup_misses;
    DWORD identity_key_mismatches;
    DWORD hd_mask_inside_diff_subpixels;
    DWORD hd_mask_outside_diff_subpixels;
    DWORD scale2x_blocks;
    DWORD scale2x_subpixel_differences;
    DWORD scale2x_palette_violations;
    char source_dump[65];
    char destination_dump[65];
} G1MirrorPresentMetrics;

/* 8-bit indexed nearest-neighbour compositor primitives.  src/dst strides
 * are bytes, not pixels.  The functions fail closed on invalid dimensions or
 * overlapping source/destination ranges. */
BOOL g1_mirror2x_nearest2x(const BYTE *src, DWORD src_stride,
                           BYTE *dst, DWORD dst_stride,
                           DWORD width, DWORD height);
DWORD g1_mirror2x_compose_sentinel(const BYTE *expected800,
                                   const BYTE *scratch_a,
                                   const BYTE *scratch_b,
                                   DWORD src_stride, BYTE *mirror1600,
                                   DWORD mirror_stride, DWORD width,
                                   DWORD height, LONG primitive_x,
                                   LONG primitive_y, DWORD primitive_width,
                                   DWORD primitive_height);
HRESULT g1_mirror2x_copy_present(LPDIRECTDRAWSURFACE7 primary,
                                  LPDIRECTDRAWSURFACE7 source,
                                  const RECT *source_rect,
                                  const RECT *destination_rect);
void g1_mirror2x_last_present_metrics(G1MirrorPresentMetrics *metrics);

/* Runtime primitive detours are separately guarded by original bytes. */
BOOL g1_mirror2x_primitives_install(void);
void g1_mirror2x_primitives_detach(void);
void g1_mirror2x_panel_transfer(LPDIRECTDRAWSURFACE7 destination,
                               LPDIRECTDRAWSURFACE7 source, DWORD x, DWORD y,
                               const RECT *source_rect, HRESULT result,
                               BOOL destination_is_primary);
typedef struct {
    BOOL active;
    DWORD x, y, width, height;
} G1OverlayBlt;
BOOL g1_mirror2x_overlay_blt_begin(G1OverlayBlt *overlay,
                                   LPDIRECTDRAWSURFACE7 destination,
                                   LPDIRECTDRAWSURFACE7 source, DWORD x, DWORD y,
                                   const RECT *source_rect, DWORD flags,
                                   BOOL destination_is_primary);
void g1_mirror2x_overlay_blt_end(G1OverlayBlt *overlay,
                                 LPDIRECTDRAWSURFACE7 destination, HRESULT result);
DWORD g1_mirror2x_overlay_blt_mirrored_calls(void);
DWORD g1_mirror2x_overlay_blt_mirrored_pixels(void);
DWORD g1_mirror2x_overlay_blt_rejects(void);
BOOL g1_mirror2x_overlay_rect_blt_begin(G1OverlayBlt *overlay,
                                        LPDIRECTDRAWSURFACE7 destination,
                                        const RECT *destination_rect, DWORD flags,
                                        DWORD surface_width, DWORD surface_height);
void g1_mirror2x_overlay_rect_blt_end(G1OverlayBlt *overlay,
                                      LPDIRECTDRAWSURFACE7 destination, HRESULT result);
DWORD g1_mirror2x_overlay_rect_blt_invocations(void);
DWORD g1_mirror2x_overlay_rect_blt_mirrored_calls(void);
DWORD g1_mirror2x_overlay_rect_blt_mirrored_pixels(void);
DWORD g1_mirror2x_overlay_rect_blt_changed_calls(void);
DWORD g1_mirror2x_overlay_rect_blt_clipped_calls(void);
DWORD g1_mirror2x_overlay_rect_blt_keysrc_calls(void);
DWORD g1_mirror2x_overlay_rect_blt_colorfill_calls(void);
DWORD g1_mirror2x_overlay_rect_blt_reject_bounds(void);
DWORD g1_mirror2x_overlay_rect_blt_reject_size(void);
DWORD g1_mirror2x_overlay_rect_blt_reject_lock(void);
DWORD g1_mirror2x_overlay_rect_blt_reject_target(void);
DWORD g1_mirror2x_overlay_rect_blt_reject_result(void);
DWORD g1_mirror2x_overlay_rect_blt_heal_presents(void);
DWORD g1_mirror2x_overlay_rect_blt_heal_pixels(void);
DWORD g1_mirror2x_overlay_rect_blt_heal2_presents(void);
DWORD g1_mirror2x_overlay_rect_blt_heal2_pixels(void);
DWORD g1_mirror2x_overlay_rect_blt_heal2_skipped(void);
DWORD g1_mirror2x_rect_fill_invocations(void);
DWORD g1_mirror2x_rect_fill_mirrored_calls(void);
DWORD g1_mirror2x_rect_fill_mirrored_pixels(void);
DWORD g1_mirror2x_rect_fill_reject_target(void);
DWORD g1_mirror2x_rect_fill_reject_size(void);
DWORD g1_mirror2x_rect_fill_reject_guard(void);
DWORD g1_mirror2x_cache_fill_invocations(void);
DWORD g1_mirror2x_cache_fill_mirrored_calls(void);
DWORD g1_mirror2x_cache_fill_mirrored_pixels(void);
DWORD g1_mirror2x_cache_fill_reject_target(void);
DWORD g1_mirror2x_cache_fill_unsupported(void);
DWORD g1_mirror2x_rect_border_invocations(void);
DWORD g1_mirror2x_rect_border_mirrored_calls(void);
DWORD g1_mirror2x_rect_border_mirrored_pixels(void);
DWORD g1_mirror2x_rect_border_reject_target(void);
DWORD g1_mirror2x_rect_border_reject_size(void);
DWORD g1_mirror2x_rect_border_reject_guard(void);
DWORD g1_mirror2x_rect_border7_invocations(void);
DWORD g1_mirror2x_rect_border7_mirrored_calls(void);
DWORD g1_mirror2x_rect_border7_mirrored_pixels(void);
DWORD g1_mirror2x_rect_border7_reject_target(void);
DWORD g1_mirror2x_rect_border7_reject_size(void);
DWORD g1_mirror2x_rect_border7_reject_guard(void);
DWORD g1_mirror2x_line_invocations(void);
DWORD g1_mirror2x_line_mirrored_calls(void);
DWORD g1_mirror2x_line_mirrored_pixels(void);
DWORD g1_mirror2x_line_reject_target(void);
DWORD g1_mirror2x_line_reject_size(void);
DWORD g1_mirror2x_line_reject_guard(void);
DWORD g1_mirror2x_rect_solid_invocations(void);
DWORD g1_mirror2x_rect_solid_mirrored_calls(void);
DWORD g1_mirror2x_rect_solid_mirrored_pixels(void);
DWORD g1_mirror2x_rect_solid_reject_target(void);
DWORD g1_mirror2x_rect_solid_reject_bounds(void);
DWORD g1_mirror2x_rect_solid_reject_size(void);
DWORD g1_mirror2x_rect_solid_reject_guard(void);
DWORD g1_mirror2x_rect_solid_wide_calls(void);
DWORD g1_mirror2x_rect_solid_ybound(void);
DWORD g1_mirror2x_flip_rle_invocations(void);
DWORD g1_mirror2x_flip_rle_mirrored_calls(void);
DWORD g1_mirror2x_flip_rle_mirrored_pixels(void);
DWORD g1_mirror2x_flip_rle_reject_target(void);
DWORD g1_mirror2x_flip_rle_reject_size(void);
DWORD g1_mirror2x_flip_rle_reject_guard(void);
DWORD g1_mirror2x_flip_rle_reject_bounds(void);
DWORD g1_mirror2x_flip_rle_clipped_calls(void);
DWORD g1_mirror2x_flip_rle_wrap_calls(void);
DWORD g1_mirror2x_flip_rle_keyed_calls(void);
DWORD g1_mirror2x_flip_rle_key_fallbacks(void);
DWORD g1_mirror2x_keyed_copy_invocations(void);
DWORD g1_mirror2x_keyed_copy_mirrored_calls(void);
DWORD g1_mirror2x_keyed_copy_mirrored_pixels(void);
DWORD g1_mirror2x_keyed_copy_changed_calls(void);
DWORD g1_mirror2x_keyed_copy_clipped_calls(void);
DWORD g1_mirror2x_keyed_copy_reject_target(void);
DWORD g1_mirror2x_keyed_copy_reject_bounds(void);
DWORD g1_mirror2x_keyed_copy_reject_size(void);
DWORD g1_mirror2x_keyed_copy_reject_guard(void);
DWORD g1_mirror2x_flip_clip_invocations(void);
DWORD g1_mirror2x_flip_clip_mirrored_calls(void);
DWORD g1_mirror2x_flip_clip_mirrored_pixels(void);
DWORD g1_mirror2x_flip_clip_reject_target(void);
DWORD g1_mirror2x_flip_clip_reject_size(void);
DWORD g1_mirror2x_flip_clip_reject_guard(void);
DWORD g1_mirror2x_flip_clip_reject_bounds(void);
DWORD g1_mirror2x_flip_clip_changed_calls(void);
DWORD g1_mirror2x_flip_clip_clipped_calls(void);
DWORD g1_mirror2x_flip_clip_wrap_calls(void);
DWORD g1_mirror2x_flip_clip_keyed_calls(void);
DWORD g1_mirror2x_flip_clip_key_fallbacks(void);
DWORD g1_mirror2x_shade_rle_invocations(void);
DWORD g1_mirror2x_shade_rle_mirrored_calls(void);
DWORD g1_mirror2x_shade_rle_mirrored_pixels(void);
DWORD g1_mirror2x_shade_rle_reject_target(void);
DWORD g1_mirror2x_shade_rle_reject_size(void);
DWORD g1_mirror2x_shade_rle_reject_guard(void);
DWORD g1_mirror2x_shade_rle_reject_bounds(void);
DWORD g1_mirror2x_shade_rle_changed_calls(void);
DWORD g1_mirror2x_shade_rle_clipped_calls(void);
DWORD g1_mirror2x_shade_rle_wrap_calls(void);
DWORD g1_mirror2x_shade_flip_invocations(void);
DWORD g1_mirror2x_shade_flip_mirrored_calls(void);
DWORD g1_mirror2x_shade_flip_mirrored_pixels(void);
DWORD g1_mirror2x_shade_flip_reject_target(void);
DWORD g1_mirror2x_shade_flip_reject_size(void);
DWORD g1_mirror2x_shade_flip_reject_guard(void);
DWORD g1_mirror2x_shade_flip_reject_bounds(void);
DWORD g1_mirror2x_shade_flip_changed_calls(void);
DWORD g1_mirror2x_shade_flip_clipped_calls(void);
DWORD g1_mirror2x_shade_flip_wrap_calls(void);
DWORD g1_mirror2x_shade_clip_invocations(void);
DWORD g1_mirror2x_shade_clip_mirrored_calls(void);
DWORD g1_mirror2x_shade_clip_mirrored_pixels(void);
DWORD g1_mirror2x_shade_clip_reject_target(void);
DWORD g1_mirror2x_shade_clip_reject_size(void);
DWORD g1_mirror2x_shade_clip_reject_guard(void);
DWORD g1_mirror2x_shade_clip_reject_bounds(void);
DWORD g1_mirror2x_shade_clip_changed_calls(void);
DWORD g1_mirror2x_shade_clip_clipped_calls(void);
DWORD g1_mirror2x_shade_clip_wrap_calls(void);
DWORD g1_mirror2x_blend_rle_invocations(void);
DWORD g1_mirror2x_blend_rle_mirrored_calls(void);
DWORD g1_mirror2x_blend_rle_mirrored_pixels(void);
DWORD g1_mirror2x_blend_rle_changed_calls(void);
DWORD g1_mirror2x_blend_rle_reject_target(void);
DWORD g1_mirror2x_blend_rle_reject_bounds(void);
DWORD g1_mirror2x_blend_rle_reject_size(void);
DWORD g1_mirror2x_blend_rle_reject_guard(void);
DWORD g1_mirror2x_blend_rle_keyed_calls(void);
DWORD g1_mirror2x_blend_rle_keyed_pixels(void);
DWORD g1_mirror2x_blend_rle_key_fallbacks(void);
DWORD g1_mirror2x_blend_rle_selfcheck_mismatches(void);
DWORD g1_mirror2x_blend_rle_selfcheck_pixels(void);
DWORD g1_mirror2x_blend_wrle_keyed_calls(void);
DWORD g1_mirror2x_blend_wrle_keyed_pixels(void);
DWORD g1_mirror2x_blend_wrle_key_fallbacks(void);
DWORD g1_mirror2x_blend_wrle_selfcheck_mismatches(void);
DWORD g1_mirror2x_blend_wrle_selfcheck_pixels(void);
DWORD g1_mirror2x_blend_clip_keyed_calls(void);
DWORD g1_mirror2x_blend_clip_keyed_pixels(void);
DWORD g1_mirror2x_blend_clip_key_fallbacks(void);
DWORD g1_mirror2x_blend_clip_selfcheck_mismatches(void);
DWORD g1_mirror2x_blend_clip_selfcheck_pixels(void);
DWORD g1_mirror2x_blend_clip_key_clip_cut(void);
DWORD g1_mirror2x_blend_clip_key_clip_empty(void);
DWORD g1_mirror2x_flip_blend_keyed_calls(void);
DWORD g1_mirror2x_flip_blend_keyed_pixels(void);
DWORD g1_mirror2x_flip_blend_key_fallbacks(void);
DWORD g1_mirror2x_flip_blend_selfcheck_mismatches(void);
DWORD g1_mirror2x_flip_blend_selfcheck_pixels(void);
DWORD g1_mirror2x_flip_blend_key_wrap_mismatches(void);
DWORD g1_mirror2x_blend_skip_keyed_calls(void);
DWORD g1_mirror2x_blend_skip_keyed_pixels(void);
DWORD g1_mirror2x_blend_skip_key_fallbacks(void);
DWORD g1_mirror2x_blend_skip_selfcheck_mismatches(void);
DWORD g1_mirror2x_blend_skip_selfcheck_pixels(void);
DWORD g1_mirror2x_blend_skip_key_clip_cut(void);
DWORD g1_mirror2x_blend_skip_key_clip_empty(void);
DWORD g1_mirror2x_blend_clip7_keyed_calls(void);
DWORD g1_mirror2x_blend_clip7_keyed_pixels(void);
DWORD g1_mirror2x_blend_clip7_key_fallbacks(void);
DWORD g1_mirror2x_blend_clip7_selfcheck_mismatches(void);
DWORD g1_mirror2x_blend_clip7_selfcheck_pixels(void);
DWORD g1_mirror2x_blend_clip7_key_clip_cut(void);
DWORD g1_mirror2x_blend_clip7_key_clip_empty(void);
DWORD g1_mirror2x_blend_clip7_key_level_rejects(void);
DWORD g1_mirror2x_blend_flip7_keyed_calls(void);
DWORD g1_mirror2x_blend_flip7_keyed_pixels(void);
DWORD g1_mirror2x_blend_flip7_key_fallbacks(void);
DWORD g1_mirror2x_blend_flip7_selfcheck_mismatches(void);
DWORD g1_mirror2x_blend_flip7_selfcheck_pixels(void);
DWORD g1_mirror2x_blend_flip7_key_clip_cut(void);
DWORD g1_mirror2x_blend_flip7_key_clip_empty(void);
DWORD g1_mirror2x_blend_flip7_key_level_rejects(void);
DWORD g1_mirror2x_blend_wrle_invocations(void);
DWORD g1_mirror2x_blend_wrle_mirrored_calls(void);
DWORD g1_mirror2x_blend_wrle_mirrored_pixels(void);
DWORD g1_mirror2x_blend_wrle_changed_calls(void);
DWORD g1_mirror2x_blend_wrle_clipped_calls(void);
DWORD g1_mirror2x_blend_wrle_reject_target(void);
DWORD g1_mirror2x_blend_wrle_reject_bounds(void);
DWORD g1_mirror2x_blend_wrle_reject_size(void);
DWORD g1_mirror2x_blend_wrle_reject_guard(void);
DWORD g1_mirror2x_blend_clip_invocations(void);
DWORD g1_mirror2x_blend_clip_mirrored_calls(void);
DWORD g1_mirror2x_blend_clip_mirrored_pixels(void);
DWORD g1_mirror2x_blend_clip_changed_calls(void);
DWORD g1_mirror2x_blend_clip_clipped_calls(void);
DWORD g1_mirror2x_blend_clip_reject_target(void);
DWORD g1_mirror2x_blend_clip_reject_bounds(void);
DWORD g1_mirror2x_blend_clip_reject_size(void);
DWORD g1_mirror2x_blend_clip_reject_guard(void);
DWORD g1_mirror2x_blend_clip_band_calls(void);
DWORD g1_mirror2x_blend_skip_invocations(void);
DWORD g1_mirror2x_blend_skip_mirrored_calls(void);
DWORD g1_mirror2x_blend_skip_mirrored_pixels(void);
DWORD g1_mirror2x_blend_skip_changed_calls(void);
DWORD g1_mirror2x_blend_skip_clipped_calls(void);
DWORD g1_mirror2x_blend_skip_reject_target(void);
DWORD g1_mirror2x_blend_skip_reject_bounds(void);
DWORD g1_mirror2x_blend_skip_reject_size(void);
DWORD g1_mirror2x_blend_skip_reject_guard(void);
DWORD g1_mirror2x_blend_skip_band_calls(void);
DWORD g1_mirror2x_blend_clip7_invocations(void);
DWORD g1_mirror2x_blend_clip7_mirrored_calls(void);
DWORD g1_mirror2x_blend_clip7_mirrored_pixels(void);
DWORD g1_mirror2x_blend_clip7_changed_calls(void);
DWORD g1_mirror2x_blend_clip7_clipped_calls(void);
DWORD g1_mirror2x_blend_clip7_reject_target(void);
DWORD g1_mirror2x_blend_clip7_reject_bounds(void);
DWORD g1_mirror2x_blend_clip7_reject_size(void);
DWORD g1_mirror2x_blend_clip7_reject_guard(void);
DWORD g1_mirror2x_flip_blend_invocations(void);
DWORD g1_mirror2x_flip_blend_mirrored_calls(void);
DWORD g1_mirror2x_flip_blend_mirrored_pixels(void);
DWORD g1_mirror2x_flip_blend_changed_calls(void);
DWORD g1_mirror2x_flip_blend_clipped_calls(void);
DWORD g1_mirror2x_flip_blend_reject_target(void);
DWORD g1_mirror2x_flip_blend_reject_bounds(void);
DWORD g1_mirror2x_flip_blend_reject_size(void);
DWORD g1_mirror2x_flip_blend_reject_guard(void);
DWORD g1_mirror2x_flip_blend_wrap_calls(void);
DWORD g1_mirror2x_blend_flip7_invocations(void);
DWORD g1_mirror2x_blend_flip7_mirrored_calls(void);
DWORD g1_mirror2x_blend_flip7_mirrored_pixels(void);
DWORD g1_mirror2x_blend_flip7_changed_calls(void);
DWORD g1_mirror2x_blend_flip7_clipped_calls(void);
DWORD g1_mirror2x_blend_flip7_reject_target(void);
DWORD g1_mirror2x_blend_flip7_reject_bounds(void);
DWORD g1_mirror2x_blend_flip7_reject_size(void);
DWORD g1_mirror2x_blend_flip7_reject_guard(void);
DWORD g1_mirror2x_flip_blend7_invocations(void);
DWORD g1_mirror2x_flip_blend7_mirrored_calls(void);
DWORD g1_mirror2x_flip_blend7_mirrored_pixels(void);
DWORD g1_mirror2x_flip_blend7_changed_calls(void);
DWORD g1_mirror2x_flip_blend7_reject_target(void);
DWORD g1_mirror2x_flip_blend7_reject_bounds(void);
DWORD g1_mirror2x_flip_blend7_reject_size(void);
DWORD g1_mirror2x_flip_blend7_reject_guard(void);
DWORD g1_mirror2x_blend_410_invocations(void);
DWORD g1_mirror2x_blend_410_changed_calls(void);
DWORD g1_mirror2x_blend_410_mirrored_calls(void);
DWORD g1_mirror2x_blend_410_mirrored_pixels(void);
DWORD g1_mirror2x_blend_410_reject_target(void);
DWORD g1_mirror2x_blend_410_reject_bounds(void);
DWORD g1_mirror2x_blend_410_reject_size(void);
DWORD g1_mirror2x_blend_410_reject_guard(void);
DWORD g1_mirror2x_blend_6d0_invocations(void);
DWORD g1_mirror2x_blend_6d0_changed_calls(void);
DWORD g1_mirror2x_drift_w_records(void);
DWORD g1_mirror2x_primitive_guard(void);
BOOL g1_mirror2x_drift_410_installed(void);
BOOL g1_mirror2x_drift_6d0_installed(void);
DWORD g1_mirror2x_drift_unattributed(DWORD index);
DWORD g1_mirror2x_textout_invocations(void);
BOOL g1_mirror2x_ret_range_diag_enabled(void);
DWORD g1_mirror2x_ret_diag_b_kills(void);
DWORD g1_mirror2x_ret_diag_b_idle(void);
DWORD g1_mirror2x_ret_diag_textout_kills(void);
DWORD g1_mirror2x_ret_diag_textout_idle(void);
DWORD g1_mirror2x_textout_mirrored_calls(void);
DWORD g1_mirror2x_textout_mirrored_pixels(void);
DWORD g1_mirror2x_textout_changed_calls(void);
DWORD g1_mirror2x_textout_reject_target(void);
DWORD g1_mirror2x_textout_reject_size(void);
DWORD g1_mirror2x_textout_screen_dc_calls(void);
DWORD g1_mirror2x_textout_reject_target_ps5(void);
DWORD g1_mirror2x_textout_reject_target_ps7(void);
DWORD g1_mirror2x_textout_reject_target_other(void);
DWORD g1_mirror2x_textout_reject_target_dc_screen(void);
DWORD g1_mirror2x_textout_reject_target_dc_buffer(void);
DWORD g1_mirror2x_textout_reject_target_dc_other(void);
DWORD g1_mirror2x_textout_reject_guard(void);
DWORD g1_mirror2x_textout_reject_align(void);
DWORD g1_mirror2x_textout_install_mismatch(void);
DWORD g1_mirror2x_textout_slot_installed(void);
DWORD g1_mirror2x_textout_slot_restored(void);
DWORD g1_mirror2x_panel_bound_transfers(void);
DWORD g1_mirror2x_panel_unbound_transfers(void);
DWORD g1_mirror2x_panel_lock_failures(void);
DWORD g1_mirror2x_panel_pointer_mismatches(void);
DWORD g1_mirror2x_panel_pitch_mismatches(void);
DWORD g1_mirror2x_panel_foreign_writer_calls(void);
DWORD g1_mirror2x_panel_frame_width(void);
DWORD g1_mirror2x_panel_frame_height(void);
const char *g1_mirror2x_panel_frame_sha256(void);
const char *g1_mirror2x_panel_asset_key(void);
BOOL g1_mirror2x_panel_hd_pack_loaded(void);
DWORD g1_mirror2x_panel_key_subpixels_emitted(void);
DWORD g1_mirror2x_panel_transfer_copied(void);
DWORD g1_mirror2x_panel_transfer_key_preserved(void);
DWORD g1_mirror2x_panel_transfer_mismatch_cleared(void);
DWORD g1_mirror2x_primitive_call_count(void);
DWORD g1_mirror2x_terrain_writer_calls(DWORD writer_index);
DWORD g1_mirror2x_tinted_writer_calls(DWORD writer_index);
DWORD g1_mirror2x_tinted_writer_covered(DWORD writer_index);
DWORD g1_mirror2x_writer_clip_mismatches(DWORD writer_index);
void g1_mirror2x_last_clip_mismatch(DWORD *writer, DWORD *origin_x,
                                    DWORD *origin_y, DWORD *width,
                                    DWORD *height, DWORD *pixel_x,
                                    DWORD *pixel_y, BYTE *screen_value,
                                    BYTE *replay_value);
DWORD g1_mirror2x_primitive_covered_pixels(void);
DWORD g1_mirror2x_stale_pixel_count(void);
DWORD g1_mirror2x_present_count(void);
DWORD g1_mirror2x_viewport_replay_count(void);
DWORD g1_mirror2x_cache_clip_attempts(void);
DWORD g1_mirror2x_cache_clip_verify_failures(void);
DWORD g1_mirror2x_cache_edge_unclipped_binds(void);
void g1_mirror2x_cache_clip_first_viewport(LONG viewport[4]);
DWORD g1_mirror2x_viewport_field_mutations(void);
DWORD g1_mirror2x_viewport_restore_failures(void);
DWORD g1_mirror2x_layer_compose_calls(void);
DWORD g1_mirror2x_layer_move_calls(void);
DWORD g1_mirror2x_layer_move_bytes(void);
DWORD g1_mirror2x_layer_move_unsupported(void);
DWORD g1_mirror2x_layer_transfer_calls(void);
DWORD g1_mirror2x_layer_covered_pixels(void);
DWORD g1_mirror2x_menu_copy_calls(void);
DWORD g1_mirror2x_menu_copy_pixels(void);
DWORD g1_mirror2x_menu_copy_hash_first(void);
DWORD g1_mirror2x_menu_copy_hash_last(void);
DWORD g1_mirror2x_menu_copy_hash_changes(void);
DWORD g1_mirror2x_partial_copy_calls(void);
DWORD g1_mirror2x_partial_copy_pixels(void);
DWORD g1_mirror2x_frame_copy_calls(void);
DWORD g1_mirror2x_frame_copy_pixels(void);
DWORD g1_mirror2x_frame_copy_rejects(void);
DWORD g1_mirror2x_pause_restore_total(void);
BOOL g1_mirror2x_primary_readback(LPDIRECTDRAWSURFACE7 destination, DWORD return_address,
                                  DWORD x, DWORD y, const RECT *src, BOOL color_keyed);
DWORD g1_mirror2x_primary_readback_calls(void);
DWORD g1_mirror2x_primary_readback_converted(void);
DWORD g1_mirror2x_primary_readback_rejects(void);
DWORD g1_mirror2x_primary_readback_dest_hash(void);
DWORD g1_mirror2x_primary_readback_source_hash(void);
DWORD g1_mirror2x_primary_readback_return_address(void);
DWORD g1_mirror2x_bar_copy_calls(void);
DWORD g1_mirror2x_bar_copy_mirrored(void);
DWORD g1_mirror2x_bar_copy_rejects(void);
DWORD g1_mirror2x_bar_copy_pixels(void);
void g1_mirror2x_scratch_bltfast_adopt(LPDIRECTDRAWSURFACE7 back, BOOL has_record);
DWORD g1_mirror2x_scratch_bltfast_calls(void);
DWORD g1_mirror2x_scratch_bltfast_recorded(void);
DWORD g1_mirror2x_scratch_bltfast_rejects(void);
DWORD g1_mirror2x_scratch_bltfast_flush_applied(void);
DWORD g1_mirror2x_scratch_bltfast_flush_pixels(void);
DWORD g1_mirror2x_scratch_bltfast_adopts(void);
DWORD g1_mirror2x_scratch_bltfast_adopt_skipped_record(void);
DWORD g1_mirror2x_scratch_bltfast_overflow(void);
DWORD g1_mirror2x_scratch_bltfast_other_site_calls(void);
DWORD g1_mirror2x_scratch_bltfast_site_calls(DWORD index); /* 0..6 = known call sites */
DWORD g1_mirror2x_briefing_compose_calls(void);
DWORD g1_mirror2x_briefing_compose_mirrored(void);
DWORD g1_mirror2x_briefing_compose_pixels(void);
DWORD g1_mirror2x_briefing_compose_rejects(void);
DWORD g1_mirror2x_briefing_compose_reject_gate(void);
DWORD g1_mirror2x_briefing_compose_reject_lock(void);
DWORD g1_mirror2x_briefing_compose_reject_surface(void);
DWORD g1_mirror2x_briefing_compose_last_dest(void);
DWORD g1_mirror2x_briefing_compose_last_geometry(DWORD index); /* width, height, pitch, bpp */
BOOL g1_mirror2x_frame_blt_copy(LPDIRECTDRAWSURFACE7 destination,
                                LPDIRECTDRAWSURFACE7 source);
BOOL g1_mirror2x_primitives_installed(void);
BOOL g1_mirror2x_s3_pattern_enabled(void);
BOOL g1_mirror2x_s3_pattern_applied(void);
DWORD g1_mirror2x_s3_pattern_pixel_count(void);

#endif /* G1_MIRROR2X_H */
