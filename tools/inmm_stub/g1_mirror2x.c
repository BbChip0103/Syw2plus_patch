/* W60 logical-800 / physical-1600 mirror compositor.
 *
 * This file is deliberately Win32/no-CRT like the existing diagnostic DLL.
 * It does not patch the EXE on disk.  Runtime detours are installed only
 * after exact old-byte checks against the pinned PE32 build. */

#include "g1_mirror2x.h"
#include "g1_hd_asset.h"
#include "g1_perf_sections.h"
#include "g1_scale2x_core.h"
#include "g1_scratch_bounds.h"
#include "g1_mirror_frame.h"
#include "g1_hd_pack.h"
#include "g1_blend_key.h"
#include "g1_panel_layer.h"
#include "g1_overlay_blt.h"
#include "g1_frame_copy.h"
#include "g1_pause_snapshot.h"
#include "g1_primary_readback.h"
#include "g1_bar_copy.h"
#include "g1_briefing_compose.h"
#include "g1_scratch_bltfast.h"
#include "g1_rect_fill.h"
#include "g1_cache_fill.h"
#include "g1_stale_mask.h"
#include "g1_layer_drift.h"
#include "g1_screen_watch.h"

#define G1_MIRROR_ENV "SYW2_G1_MIRROR2X"
#define G1_S3_PATTERN_ENV "SYW2_G1_S3_PATTERN"
#define G1_PAUSE_SNAPSHOT_ENV "SYW2_G1_PAUSE_SNAPSHOT"
#define G1_PRIMARY_READBACK_ENV "SYW2_G1_PRIMARY_READBACK"
#define G1_BAR_COPY_ENV "SYW2_G1_BAR_COPY"
#define G1_RECT_SOLID_WIDE_ENV "SYW2_G1_RECT_SOLID_WIDE"
#define G1_TEXTOUT_SCREEN_DC_ENV "SYW2_G1_TEXTOUT_SCREEN_DC"
#define G1_BRIEFING_COMPOSE_ENV "SYW2_G1_BRIEFING_COMPOSE"
#define G1_SCRATCH_BLTFAST_ENV "SYW2_G1_SCRATCH_BLTFAST_MIRROR"
#define G1_STALE_MASK_ENV "SYW2_G1_STALE_MASK"
#define G1_STALE_MASK_STATE_ENV "SYW2_G1_STALE_MASK_STATE"
#define G1_STALE_MASK_PATH "C:\\inmm_g1_stale_mask.bin"
#define G1_LAYER_DRIFT_ENV "SYW2_G1_LAYER_DRIFT"
#define G1_DRIFT_SAMPLES_ENV "SYW2_G1_DRIFT_SAMPLES"
#define G1_LAYER_DRIFT_PATH "C:\\inmm_g1_layer_drift.jsonl"
#define G1_LAYER_DRIFT_HEARTBEAT 50u
#define G1_PROGRAM_STATE_VA 0x004ED818u
#define G1_GAME_TICK_VA 0x009B5210u
#define G1_RENDERER_VA 0x00E5BF18u
#define G1_RENDERER_BUFFER 0x1514u
#define G1_RENDERER_STRIDE 0x10u
#define G1_RENDERER_HEIGHT 0x08u
#define G1_RENDERER_YBOUND 0x14u
#define G1_RENDERER_VIEWPORT 0x4D0u
#define G1_TARGET_A 0x00466D50u
#define G1_TARGET_B 0x004664D0u
#define G1_TERRAIN_RLE 0x00468C30u
#define G1_TERRAIN_SHADE 0x00468CC0u
#define G1_TERRAIN_CHECKER 0x00468E10u
#define G1_TERRAIN_CLIP 0x00468F00u
#define G1_TERRAIN_CLIP_SHADE 0x004690A0u
#define G1_PANEL_RLE 0x004663E0u
#define G1_TINTED_RLE 0x00466EA0u
#define G1_TINTED_CLIP_RLE 0x00466540u
#define G1_RECT_FILL 0x00466070u
#define G1_RECT_BORDER 0x00465B30u
#define G1_RECT_BORDER7 0x00465CA0u
#define G1_LINE 0x004659B0u
#define G1_RECT_SOLID 0x00465E80u
#define G1_FLIP_RLE 0x00466B50u
#define G1_FLIP_CLIP 0x00466BE0u
#define G1_SHADE_RLE 0x004687F0u
#define G1_SHADE_FLIP 0x004689C0u
#define G1_SHADE_CLIP 0x00468870u
#define G1_BLEND_RLE 0x004672E0u
#define G1_BLEND_WRLE 0x00467580u
#define G1_BLEND_CLIP 0x00467B00u
#define G1_BLEND_SKIP 0x004685C0u
#define G1_BLEND_CLIP7 0x004678C0u
#define G1_FLIP_BLEND 0x00467FD0u
#define G1_BLEND_FLIP7 0x00468360u
#define G1_FLIP_BLEND7 0x00467E60u
#define G1_BLEND_410 0x00467410u
#define G1_BLEND_6D0 0x004676D0u
#define G1_PANEL_HD_PACK_ENV "SYW2_G1_HD_PACK"
#define G1_CACHE_MOVE 0x004DB1D0u
#define G1_CACHE_COPY 0x00466280u
/* H-RS2: PS26 banner prepare 0x4C7D00 calls the renderer blit wrapper 0x469300
 * (selector 1 = BltFast on renderer+0x1520) with the primary surface [0xE5D434]
 * as source.  The destination is the flip-chain back buffer, which the game got
 * from GetAttachedSurface, so the DirectDraw surface hooks never see the call. */
#define G1_RENDERER_BLIT 0x00469300u
#define G1_PRIMARY_READBACK_SITE 0x004C7EE6u
#define G1_PRIMARY_SURFACE_VA 0x00E5D434u
#define G1_RENDERER_BACK_BUFFER 0x1520u
/* H-RS3: the PS29 result table draws its gradient bars with 0x468BB0 (thiscall,
 * ret 0x28, ten stack arguments), called from one site, 0x4B5493. */
#define G1_BAR_COPY_FUNC 0x00468BB0u
#define G1_BAR_COPY_SITE 0x004B5493u
/* H-SC2: the PS20 briefing frame 0x4B2320 calls 0x4D4620 (thiscall, one stack argument,
 * ret 4) from 0x4B23B5 with the flip-chain back buffer [0xE5D438] as destination; it
 * colorkey-copies the body layer, portraits and buttons there. */
#define G1_BRIEFING_COMPOSE_FUNC 0x004D4620u
#define G1_BRIEFING_COMPOSE_SITE 0x004B23B5u
#define G1_BACK_BUFFER_VA 0x00E5D438u
#define G1_CACHE_FILL 0x00465FC0u
#define G1_CACHE_FILL_LEN 5u
#define G1_RENDERER_BPP 0x0Cu
#define G1_CACHE_BASE 0x00BA3D30u
#define G1_CACHE_WIDTH G1_MIRROR_CACHE_WIDTH
#define G1_CACHE_HEIGHT 512u
#define G1_CACHE_BYTES (G1_CACHE_WIDTH * G1_CACHE_HEIGHT)
#define G1_TARGET_A_LEN 7u
#define G1_TARGET_B_LEN 8u
#define G1_TERRAIN_RLE_LEN 8u
#define G1_TERRAIN_SHADE_LEN 5u
#define G1_TERRAIN_CHECKER_LEN 5u
#define G1_TERRAIN_CLIP_LEN 8u
#define G1_TERRAIN_CLIP_SHADE_LEN 5u
#define G1_PANEL_RLE_LEN 6u
#define G1_TINTED_RLE_LEN 7u
#define G1_TINTED_CLIP_RLE_LEN 8u
#define G1_RECT_FILL_LEN 5u
#define G1_RECT_BORDER_LEN 8u
#define G1_RECT_BORDER7_LEN 9u
#define G1_LINE_LEN 7u
#define G1_RECT_SOLID_LEN 5u
#define G1_FLIP_RLE_LEN 8u
#define G1_FLIP_CLIP_LEN 5u
#define G1_SHADE_RLE_LEN 5u
#define G1_SHADE_FLIP_LEN 5u
#define G1_SHADE_CLIP_LEN 7u
#define G1_BLEND_RLE_LEN 6u
#define G1_BLEND_WRLE_LEN 6u
#define G1_BLEND_CLIP_LEN 5u
#define G1_BLEND_SKIP_LEN 5u
#define G1_BLEND_CLIP7_LEN 5u
#define G1_FLIP_BLEND_LEN 5u
#define G1_BLEND_FLIP7_LEN 5u
#define G1_FLIP_BLEND7_LEN 5u
#define G1_BLEND_410_LEN 5u
#define G1_BLEND_6D0_LEN 5u
#define G1_TEXTOUT_SLOT 0x004E502Cu
#define G1_PANEL_SURFACE_GLOBAL 0x0104F814u
#define G1_PANEL_WIDTH 800u
#define G1_PANEL_MAX_HEIGHT 203u
#define G1_PANEL_HD_STRIDE 1600u
#define G1_MAX_STRIDE 2048u
#define G1_MAX_HEIGHT 1200u
#define G1_MAX_BUFFER (G1_MAX_STRIDE * G1_MAX_HEIGHT)
#define G1_EXE_BASE 0x00400000u
#define G1_USER32_NAME "USER32.dll"
#define G1_HD_NEGATIVE_ENV "SYW2_G1_HD_NEGATIVE_MISMATCH"
#define G1_BLEND_SIZE_REJECT_DIAG_ENV "SYW2_G1_BLEND_SIZE_REJECT_DIAG"
/* H-E2611G1-1 (diagnostic only, default off): counts primitive B (0x4664D0) and TextOutA calls
 * whose return address lies in the official 2610/2611 `.kills` / `.idle` sections. */
#define G1_RET_RANGE_DIAG_ENV "SYW2_G1_RET_RANGE_DIAG"
#define G1_RET_RANGE_KILLS_BASE 0x0115B000u
#define G1_RET_RANGE_IDLE_BASE 0x01157000u
#define G1_RET_RANGE_SIZE 0x1000u
/* lap1141 H-TM1: 0x466480 (thiscall, ret 0x14; x y w h src) copies an 8-bit 0xFE-colorkey
 * rectangle into the screen buffer; the title menu's user-registration popup panel is drawn
 * with it.  SYW2_G1_KEYED_COPY=0 turns the mirror off (default on). */
#define G1_KEYED_COPY 0x00466480u
#define G1_KEYED_COPY_LEN 6u
#define G1_KEYED_COPY_ENV "SYW2_G1_KEYED_COPY"

typedef DWORD (__attribute__((thiscall)) *G1PrimitiveFn)(void *, DWORD, DWORD,
                                                         DWORD, DWORD, DWORD);
typedef DWORD (__attribute__((thiscall)) *G1Primitive4Fn)(void *, DWORD, DWORD,
                                                           DWORD, DWORD);
typedef DWORD (__attribute__((thiscall)) *G1Primitive6Fn)(void *, DWORD, DWORD,
                                                           DWORD, DWORD, DWORD,
                                                           DWORD);
typedef DWORD (__attribute__((thiscall)) *G1Primitive7Fn)(void *, DWORD, DWORD,
                                                           DWORD, DWORD, DWORD,
                                                           DWORD, DWORD);

static volatile LONG g_primitive_guard = 0;
static volatile LONG g_primitives_installed = 0;
static G1PrimitiveFn g_original_a = NULL;
static G1PrimitiveFn g_original_b = NULL;
static G1Primitive4Fn g_original_terrain_rle = NULL;
static G1Primitive6Fn g_original_terrain_shade = NULL;
static G1PrimitiveFn g_original_terrain_checker = NULL;
static G1PrimitiveFn g_original_terrain_clip = NULL;
static G1Primitive6Fn g_original_terrain_clip_shade = NULL;
static G1Primitive6Fn g_original_tinted_rle = NULL;
static G1Primitive6Fn g_original_tinted_clip_rle = NULL;
typedef DWORD (__attribute__((thiscall)) *G1PanelRleFn)(void *, DWORD, DWORD,
                                                        DWORD, DWORD, DWORD);
static G1PanelRleFn g_original_panel_rle = NULL;
static G1PrimitiveFn g_original_rect_fill = NULL;
static G1PrimitiveFn g_original_cache_fill = NULL;
static G1PrimitiveFn g_original_rect_border = NULL;
static G1Primitive7Fn g_original_rect_border7 = NULL;
static G1PrimitiveFn g_original_line = NULL;
static G1PrimitiveFn g_original_rect_solid = NULL;
static G1Primitive6Fn g_original_flip_rle = NULL;
static G1Primitive6Fn g_original_flip_clip = NULL;
static G1Primitive6Fn g_original_shade_rle = NULL;
static G1Primitive6Fn g_original_shade_flip = NULL;
static G1Primitive6Fn g_original_shade_clip = NULL;
static G1PrimitiveFn g_original_blend_rle = NULL;
static G1PrimitiveFn g_original_blend_wrle = NULL;
static G1PrimitiveFn g_original_blend_clip = NULL;
static G1PrimitiveFn g_original_blend_skip = NULL;
static G1Primitive7Fn g_original_blend_clip7 = NULL;
static G1PrimitiveFn g_original_flip_blend = NULL;
static G1Primitive7Fn g_original_blend_flip7 = NULL;
static G1Primitive7Fn g_original_flip_blend7 = NULL;
static G1Primitive7Fn g_original_blend_410 = NULL;
static G1PrimitiveFn g_original_blend_6d0 = NULL;
static BYTE *g_scratch_a = NULL;
static BYTE *g_scratch_b = NULL;
static BYTE *g_mirror = NULL;
static BYTE *g_covered = NULL;
static BYTE *g_expected_snapshot = NULL;
/* H-PM2: PS23 entry-present HD snapshot (optional; NULL keeps the old behaviour). */
static BYTE *g_pause_valid = NULL;
static BYTE *g_pause_expected = NULL;
static BYTE *g_pause_hd = NULL;
static DWORD g_pause_state_prev = 0u;
static DWORD g_pause_snapshot_pixels = 0u;
static DWORD g_pause_restore_total = 0u;
static BOOL g_pause_snapshot_enabled = TRUE;
/* H-RS2: last presented logical 800x600 frame handed back to primary readbacks. */
static BYTE *g_last_frame = NULL;
static BOOL g_last_frame_valid = FALSE;
static DWORD g_last_frame_source_hash = 0u;
static BOOL g_primary_readback_enabled = TRUE;
static DWORD g_primary_readback_calls = 0u;
static DWORD g_primary_readback_converted = 0u;
static DWORD g_primary_readback_rejects = 0u;
static DWORD g_primary_readback_dest_hash = 0u;
static DWORD g_primary_readback_source_hash = 0u;
static DWORD g_primary_readback_return = 0u;
static BOOL g_bar_copy_enabled = TRUE;
static BOOL g_rect_solid_wide_enabled = TRUE;
static BOOL g_textout_screen_dc_enabled = TRUE;
static DWORD g_textout_screen_dc_calls = 0u;
static DWORD g_bar_copy_calls = 0u;
static DWORD g_bar_copy_mirrored = 0u;
static DWORD g_bar_copy_rejects = 0u;
static DWORD g_bar_copy_pixels = 0u;
static BOOL g_briefing_compose_enabled = TRUE;
static BYTE g_briefing_compose_before[G1_BRIEFING_MIN_WIDTH * G1_BRIEFING_HEIGHT];
static BYTE g_briefing_compose_tile[G1_OVERLAY_MAX_WIDTH * G1_OVERLAY_MAX_HEIGHT];
static DWORD g_briefing_compose_calls = 0u;
static DWORD g_briefing_compose_mirrored = 0u;
static DWORD g_briefing_compose_changed_pixels = 0u;
static DWORD g_briefing_compose_rejects = 0u;
static DWORD g_briefing_compose_reject_gate = 0u;
static DWORD g_briefing_compose_reject_lock = 0u;
static DWORD g_briefing_compose_reject_surface = 0u;
static DWORD g_briefing_compose_last_dest = 0u;
static DWORD g_briefing_compose_last_geometry[4];
static BOOL g_scratch_bltfast_enabled = TRUE;
typedef HRESULT (WINAPI *G1ScratchBltFastFn)(LPDIRECTDRAWSURFACE7 self, DWORD x, DWORD y,
                                             LPDIRECTDRAWSURFACE7 source, LPRECT src,
                                             DWORD flags);
static G1ScratchBltFastFn g_scratch_original_blt_fast = NULL;
static IDirectDrawSurface7Vtbl *g_scratch_clone = NULL;
static LPDIRECTDRAWSURFACE7 g_scratch_surface = NULL;
static G1ScratchQueue g_scratch_queue;
static BYTE g_scratch_before[G1_OVERLAY_SCREEN_WIDTH * G1_OVERLAY_SCREEN_HEIGHT];
static BYTE g_scratch_tile[G1_OVERLAY_MAX_WIDTH * G1_OVERLAY_MAX_HEIGHT];
static DWORD g_scratch_calls = 0u;
static DWORD g_scratch_recorded = 0u;
static DWORD g_scratch_rejects = 0u;
static DWORD g_scratch_site_calls[G1_SCRATCH_BLTFAST_SITE_COUNT + 1u];
static DWORD g_scratch_adopts = 0u;
static DWORD g_scratch_adopt_skipped_record = 0u;
static DWORD g_scratch_flush_applied = 0u;
static DWORD g_scratch_flush_pixels = 0u;
static BYTE *g_layer_mirror = NULL;
static BYTE *g_layer_covered = NULL;
static BYTE *g_layer_expected = NULL;
static BYTE *g_panel_expected = NULL;
static BYTE *g_panel_covered = NULL;
static BYTE *g_panel_mirror = NULL;
static BYTE *g_panel_pack = NULL;
static BYTE *g_panel_bound_buffer = NULL;
static DWORD g_panel_bound_pitch = 0u;
static DWORD g_panel_bound_height = 0u;
static DWORD g_panel_frame_width = 0u;
static DWORD g_panel_frame_height = 0u;
static char g_panel_frame_sha256[65];
static char g_panel_asset_key_name[64];
static BOOL g_panel_hd_pack_loaded = FALSE;
static DWORD g_panel_key_subpixels = 0u;
static DWORD g_panel_bound_transfer_count = 0u;
static DWORD g_panel_unbound_transfer_count = 0u;
static DWORD g_panel_lock_failures = 0u;
static DWORD g_panel_pointer_mismatches = 0u;
static DWORD g_panel_pitch_mismatches = 0u;
static DWORD g_panel_foreign_writer_count = 0u;
static DWORD g_panel_transfer_copied = 0u;
static DWORD g_panel_transfer_key_preserved = 0u;
static DWORD g_panel_transfer_mismatch_cleared = 0u;
static DWORD g_overlay_blt_mirrored_calls = 0u;
static DWORD g_overlay_blt_mirrored_pixels = 0u;
static DWORD g_overlay_blt_rejects = 0u;
static BYTE g_overlay_before[G1_OVERLAY_MAX_WIDTH * G1_OVERLAY_MAX_HEIGHT];
static BYTE g_overlay_scratch[G1_OVERLAY_SCRATCH_BYTES];
static BYTE g_rect_blt_before[G1_OVERLAY_MAX_WIDTH * G1_OVERLAY_MAX_HEIGHT];
static DWORD g_rect_blt_invocations = 0u;
static DWORD g_rect_blt_mirrored_calls = 0u;
static DWORD g_rect_blt_mirrored_pixels = 0u;
static DWORD g_rect_blt_changed_calls = 0u;
static DWORD g_rect_blt_clipped_calls = 0u;
static DWORD g_rect_blt_keysrc_calls = 0u;
static DWORD g_rect_blt_colorfill_calls = 0u;
static DWORD g_rect_blt_reject_bounds = 0u;
static DWORD g_rect_blt_reject_size = 0u;
static DWORD g_rect_blt_reject_lock = 0u;
static DWORD g_rect_blt_reject_target = 0u;
static DWORD g_rect_blt_reject_result = 0u;
static BOOL g_rect_blt_heal_active = FALSE;
static DWORD g_rect_blt_heal_x = 0u, g_rect_blt_heal_y = 0u;
static DWORD g_rect_blt_heal_w = 0u, g_rect_blt_heal_h = 0u;
static DWORD g_rect_blt_heal_quiet = 0u;
static DWORD g_rect_blt_heal_presents = 0u;
static DWORD g_rect_blt_heal_pixels = 0u;
static DWORD g_rect_blt_heal2_presents = 0u;
static DWORD g_rect_blt_heal2_pixels = 0u;
static DWORD g_rect_blt_heal2_skipped = 0u;
static DWORD g_rect_solid_reject_logged = 0u;
static DWORD g_rect_border_reject_logged = 0u;
static BYTE g_rect_fill_before[G1_OVERLAY_MAX_WIDTH * G1_OVERLAY_MAX_HEIGHT];
static DWORD g_rect_fill_invocations = 0u;
static DWORD g_rect_fill_mirrored_calls = 0u;
static DWORD g_rect_fill_mirrored_pixels = 0u;
static DWORD g_rect_fill_reject_target = 0u;
static DWORD g_rect_fill_reject_size = 0u;
static DWORD g_rect_fill_reject_guard = 0u;
static DWORD g_cache_fill_invocations = 0u;
static DWORD g_cache_fill_mirrored_calls = 0u;
static DWORD g_cache_fill_mirrored_pixels = 0u;
static DWORD g_cache_fill_reject_target = 0u;
static DWORD g_cache_fill_unsupported = 0u;
static BYTE g_rect_border_before[G1_OVERLAY_SCREEN_WIDTH * G1_OVERLAY_SCREEN_HEIGHT];
static BYTE g_rect_border_tile[G1_OVERLAY_MAX_WIDTH * G1_OVERLAY_MAX_HEIGHT];
static DWORD g_rect_border_invocations = 0u;
static DWORD g_rect_border_mirrored_calls = 0u;
static DWORD g_rect_border_mirrored_pixels = 0u;
static DWORD g_rect_border_reject_target = 0u;
static DWORD g_rect_border_reject_size = 0u;
static DWORD g_rect_border_reject_guard = 0u;
static BYTE g_rect_border7_before[G1_OVERLAY_SCREEN_WIDTH * G1_OVERLAY_SCREEN_HEIGHT];
static BYTE g_rect_border7_tile[G1_OVERLAY_MAX_WIDTH * G1_OVERLAY_MAX_HEIGHT];
static DWORD g_rect_border7_invocations = 0u;
static DWORD g_rect_border7_mirrored_calls = 0u;
static DWORD g_rect_border7_mirrored_pixels = 0u;
static DWORD g_rect_border7_reject_target = 0u;
static DWORD g_rect_border7_reject_size = 0u;
static DWORD g_rect_border7_reject_guard = 0u;
static BYTE g_line_before[G1_OVERLAY_SCREEN_WIDTH * G1_OVERLAY_SCREEN_HEIGHT];
static BYTE g_line_tile[G1_OVERLAY_MAX_WIDTH * G1_OVERLAY_MAX_HEIGHT];
static DWORD g_line_invocations = 0u;
static DWORD g_line_mirrored_calls = 0u;
static DWORD g_line_mirrored_pixels = 0u;
static DWORD g_line_reject_target = 0u;
static DWORD g_line_reject_size = 0u;
static DWORD g_line_reject_guard = 0u;
static BYTE g_rect_solid_before[G1_OVERLAY_SCREEN_WIDTH * G1_OVERLAY_SCREEN_HEIGHT];
static BYTE g_rect_solid_tile[G1_OVERLAY_MAX_WIDTH * G1_OVERLAY_MAX_HEIGHT];
static DWORD g_rect_solid_wide_calls = 0u;
static DWORD g_rect_solid_invocations = 0u;
static DWORD g_rect_solid_mirrored_calls = 0u;
static DWORD g_rect_solid_mirrored_pixels = 0u;
static DWORD g_rect_solid_reject_target = 0u;
static DWORD g_rect_solid_reject_bounds = 0u;
static DWORD g_rect_solid_reject_size = 0u;
static DWORD g_rect_solid_reject_guard = 0u;
static DWORD g_rect_solid_ybound = 0u;
static BYTE g_flip_rle_before[G1_OVERLAY_MAX_WIDTH * G1_OVERLAY_MAX_HEIGHT];
static DWORD g_flip_rle_invocations = 0u;
static DWORD g_flip_rle_mirrored_calls = 0u;
static DWORD g_flip_rle_mirrored_pixels = 0u;
static DWORD g_flip_rle_reject_target = 0u;
static DWORD g_flip_rle_reject_size = 0u;
static DWORD g_flip_rle_reject_guard = 0u;
static DWORD g_flip_rle_reject_bounds = 0u;
static DWORD g_flip_rle_clipped_calls = 0u;
static DWORD g_flip_rle_wrap_calls = 0u;
static DWORD g_flip_rle_keyed_calls = 0u;
static DWORD g_flip_rle_key_fallbacks = 0u;
/* Set by mirror_reinvoke: the asset key was ready when the composition ran (a flip call then needs no diff). */
static BOOL g_reinvoke_composed = FALSE;
/* H-TM1: 0x466480 unclipped colorkey rectangle copy; diffed in tiles from a screen-sized
 * before copy (the popup panel is taller than G1_OVERLAY_MAX_HEIGHT). */
static G1PrimitiveFn g_original_keyed_copy = NULL;
static BOOL g_keyed_copy_enabled = TRUE;
static BYTE g_keyed_copy_before[G1_OVERLAY_SCREEN_WIDTH * G1_OVERLAY_SCREEN_HEIGHT];
static BYTE g_keyed_copy_tile[G1_OVERLAY_MAX_WIDTH * G1_OVERLAY_MAX_HEIGHT];
static DWORD g_keyed_copy_invocations = 0u;
static DWORD g_keyed_copy_mirrored_calls = 0u;
static DWORD g_keyed_copy_mirrored_pixels = 0u;
static DWORD g_keyed_copy_changed_calls = 0u;
static DWORD g_keyed_copy_clipped_calls = 0u;
static DWORD g_keyed_copy_reject_target = 0u;
static DWORD g_keyed_copy_reject_bounds = 0u;
static DWORD g_keyed_copy_reject_size = 0u;
static DWORD g_keyed_copy_reject_guard = 0u;
static BYTE g_flip_clip_before[G1_OVERLAY_MAX_WIDTH * G1_OVERLAY_MAX_HEIGHT];
static DWORD g_flip_clip_invocations = 0u;
static DWORD g_flip_clip_mirrored_calls = 0u;
static DWORD g_flip_clip_mirrored_pixels = 0u;
static DWORD g_flip_clip_reject_target = 0u;
static DWORD g_flip_clip_reject_size = 0u;
static DWORD g_flip_clip_reject_guard = 0u;
static DWORD g_flip_clip_reject_bounds = 0u;
static DWORD g_flip_clip_changed_calls = 0u;
static DWORD g_flip_clip_clipped_calls = 0u;
static DWORD g_flip_clip_wrap_calls = 0u;
static DWORD g_flip_clip_keyed_calls = 0u;
static DWORD g_flip_clip_key_fallbacks = 0u;
static BYTE g_shade_rle_before[G1_OVERLAY_MAX_WIDTH * G1_OVERLAY_MAX_HEIGHT];
static DWORD g_shade_rle_invocations = 0u;
static DWORD g_shade_rle_mirrored_calls = 0u;
static DWORD g_shade_rle_mirrored_pixels = 0u;
static DWORD g_shade_rle_reject_target = 0u;
static DWORD g_shade_rle_reject_size = 0u;
static DWORD g_shade_rle_reject_guard = 0u;
static DWORD g_shade_rle_reject_bounds = 0u;
static DWORD g_shade_rle_changed_calls = 0u;
static DWORD g_shade_rle_clipped_calls = 0u;
static DWORD g_shade_rle_wrap_calls = 0u;
static BYTE g_shade_flip_before[G1_OVERLAY_MAX_WIDTH * G1_OVERLAY_MAX_HEIGHT];
static DWORD g_shade_flip_invocations = 0u;
static DWORD g_shade_flip_mirrored_calls = 0u;
static DWORD g_shade_flip_mirrored_pixels = 0u;
static DWORD g_shade_flip_reject_target = 0u;
static DWORD g_shade_flip_reject_size = 0u;
static DWORD g_shade_flip_reject_guard = 0u;
static DWORD g_shade_flip_reject_bounds = 0u;
static DWORD g_shade_flip_changed_calls = 0u;
static DWORD g_shade_flip_clipped_calls = 0u;
static DWORD g_shade_flip_wrap_calls = 0u;
static BYTE g_shade_clip_before[G1_OVERLAY_MAX_WIDTH * G1_OVERLAY_MAX_HEIGHT];
static DWORD g_shade_clip_invocations = 0u;
static DWORD g_shade_clip_mirrored_calls = 0u;
static DWORD g_shade_clip_mirrored_pixels = 0u;
static DWORD g_shade_clip_reject_target = 0u;
static DWORD g_shade_clip_reject_size = 0u;
static DWORD g_shade_clip_reject_guard = 0u;
static DWORD g_shade_clip_reject_bounds = 0u;
static DWORD g_shade_clip_changed_calls = 0u;
static DWORD g_shade_clip_clipped_calls = 0u;
static DWORD g_shade_clip_wrap_calls = 0u;
static BYTE g_blend_rle_before[G1_OVERLAY_MAX_WIDTH * G1_OVERLAY_MAX_HEIGHT];
static DWORD g_blend_rle_invocations = 0u;
static DWORD g_blend_rle_mirrored_calls = 0u;
static DWORD g_blend_rle_mirrored_pixels = 0u;
static DWORD g_blend_rle_changed_calls = 0u;
static DWORD g_blend_rle_reject_target = 0u;
static DWORD g_blend_rle_reject_bounds = 0u;
static DWORD g_blend_rle_reject_size = 0u;
static DWORD g_blend_rle_reject_guard = 0u;
/* H-HDB0/H-HDB1: HD key path of the translucent RLE writers 0x4672E0 and 0x467580 (decode, self check, pack blend).
 * The planes cover a whole stream rectangle (at most the screen); covered/hd_before/v* only its screen window. */
#define G1_BLEND_KEY_MAX_PIXELS (G1_OVERLAY_SCREEN_WIDTH * G1_OVERLAY_SCREEN_HEIGHT)
typedef struct {
    DWORD keyed_calls;
    DWORD keyed_pixels;
    DWORD key_fallbacks;
    DWORD selfcheck_mismatches;
    DWORD selfcheck_pixels;
    DWORD key_clip_cut;       /* H-HDB2: keyed calls whose renderer clip was narrower than the screen intersection */
    DWORD key_clip_empty;     /* H-HDB2: calls whose renderer clip left nothing of the screen intersection (no key try) */
    DWORD key_wrap_mismatches; /* H-HDB3: self-check mismatches of a 0x467FD0 call whose rectangle wraps past the stride/screen */
    DWORD key_level_rejects;  /* H-HDB4: 7-arg calls refused before any decode (level outside the 10 table slices, entry beyond int16, no remap) */
} G1BlendKeyStats;
static G1BlendKeyStats g_blend_rle_key;
static G1BlendKeyStats g_blend_wrle_key;
static G1BlendKeyStats g_blend_clip_key;
static G1BlendKeyStats g_flip_blend_key;   /* H-HDB3: 0x467FD0 */
static G1BlendKeyStats g_blend_skip_key;   /* H-HDB3: 0x4685C0 */
static G1BlendKeyStats g_blend_clip7_key;  /* H-HDB4: 0x4678C0 */
static G1BlendKeyStats g_blend_flip7_key;  /* H-HDB4: 0x468360 */
static BYTE g_blend_clip_key_before[G1_BLEND_KEY_MAX_PIXELS];
static BYTE g_blend_key_idx[G1_BLEND_KEY_MAX_PIXELS];
static BYTE g_blend_key_mask[G1_BLEND_KEY_MAX_PIXELS];
static BYTE g_blend_key_vidx[G1_BLEND_KEY_MAX_PIXELS];
static BYTE g_blend_key_vmask[G1_BLEND_KEY_MAX_PIXELS];
/* H-HDB4: the 7-arg writers hand their remap table and level to blend_key_apply through these (set right before the call). */
static const BYTE *g_blend_key_remap = NULL;
static DWORD g_blend_key_remap_digest = 0u;
static int32_t g_blend_key_level = 0;
static BYTE g_blend_key_vsrc[G1_BLEND_KEY_MAX_PIXELS];
static int16_t g_blend_key_level_weights[G1_BLEND_WEIGHT_ENTRIES];
static BYTE g_blend_key_covered[G1_BLEND_KEY_MAX_PIXELS];
static BYTE g_blend_key_hd_before[G1_BLEND_KEY_MAX_PIXELS * 4u];
/* H-W330: 0x467580 and 0x467B00 mirror up to the whole screen (lap1083 330x200 was
 * reject_size) in <=320x160 tiles from a screen-sized before copy. */
static BYTE g_blend_wrle_before[G1_OVERLAY_SCREEN_WIDTH * G1_OVERLAY_SCREEN_HEIGHT];
static BYTE g_blend_wrle_tile[G1_OVERLAY_MAX_WIDTH * G1_OVERLAY_MAX_HEIGHT];
static DWORD g_blend_wrle_invocations = 0u;
static DWORD g_blend_wrle_mirrored_calls = 0u;
static DWORD g_blend_wrle_mirrored_pixels = 0u;
static DWORD g_blend_wrle_changed_calls = 0u;
static DWORD g_blend_wrle_clipped_calls = 0u;
static DWORD g_blend_wrle_reject_target = 0u;
static DWORD g_blend_wrle_reject_bounds = 0u;
static DWORD g_blend_wrle_reject_size = 0u;
static DWORD g_blend_wrle_reject_guard = 0u;
static BYTE g_blend_clip_before[G1_OVERLAY_SCREEN_WIDTH * G1_OVERLAY_SCREEN_HEIGHT];
static BYTE g_blend_clip_tile[G1_OVERLAY_MAX_WIDTH * G1_OVERLAY_MAX_HEIGHT];
/* H-D2r: 0x4685C0 still mirrors rects up to the full screen height in row bands. */
static BYTE g_blend_skip_before[G1_OVERLAY_MAX_WIDTH * G1_OVERLAY_SCREEN_HEIGHT];
static BYTE g_blend_clip7_before[G1_OVERLAY_MAX_WIDTH * G1_OVERLAY_MAX_HEIGHT];
static DWORD g_blend_clip7_invocations = 0u;
static DWORD g_blend_clip7_mirrored_calls = 0u;
static DWORD g_blend_clip7_mirrored_pixels = 0u;
static DWORD g_blend_clip7_changed_calls = 0u;
static DWORD g_blend_clip7_clipped_calls = 0u;
static DWORD g_blend_clip7_reject_target = 0u;
static DWORD g_blend_clip7_reject_bounds = 0u;
static DWORD g_blend_clip7_reject_size = 0u;
static DWORD g_blend_clip7_reject_guard = 0u;
static BYTE g_flip_blend_before[G1_OVERLAY_MAX_WIDTH * G1_OVERLAY_MAX_HEIGHT];
static DWORD g_flip_blend_invocations = 0u;
static DWORD g_flip_blend_mirrored_calls = 0u;
static DWORD g_flip_blend_mirrored_pixels = 0u;
static DWORD g_flip_blend_changed_calls = 0u;
static DWORD g_flip_blend_clipped_calls = 0u;
static DWORD g_flip_blend_reject_target = 0u;
static DWORD g_flip_blend_reject_bounds = 0u;
static DWORD g_flip_blend_reject_size = 0u;
static DWORD g_flip_blend_reject_guard = 0u;
static DWORD g_flip_blend_wrap_calls = 0u;
static BYTE g_blend_flip7_before[G1_OVERLAY_MAX_WIDTH * G1_OVERLAY_MAX_HEIGHT];
static DWORD g_blend_flip7_invocations = 0u;
static DWORD g_blend_flip7_mirrored_calls = 0u;
static DWORD g_blend_flip7_mirrored_pixels = 0u;
static DWORD g_blend_flip7_changed_calls = 0u;
static DWORD g_blend_flip7_clipped_calls = 0u;
static DWORD g_blend_flip7_reject_target = 0u;
static DWORD g_blend_flip7_reject_bounds = 0u;
static DWORD g_blend_flip7_reject_size = 0u;
static DWORD g_blend_flip7_reject_guard = 0u;
/* H-L2: 0x467E60 has no clip, so the rect (up to the screen) is diffed in tiles. */
static BYTE g_flip_blend7_before[G1_OVERLAY_SCREEN_WIDTH * G1_OVERLAY_SCREEN_HEIGHT];
static BYTE g_flip_blend7_tile[G1_OVERLAY_MAX_WIDTH * G1_OVERLAY_MAX_HEIGHT];
static DWORD g_flip_blend7_invocations = 0u;
static DWORD g_flip_blend7_mirrored_calls = 0u;
static DWORD g_flip_blend7_mirrored_pixels = 0u;
static DWORD g_flip_blend7_changed_calls = 0u;
static DWORD g_flip_blend7_reject_target = 0u;
static DWORD g_flip_blend7_reject_bounds = 0u;
static DWORD g_flip_blend7_reject_size = 0u;
static DWORD g_flip_blend7_reject_guard = 0u;
static DWORD g_blend_clip_invocations = 0u;
static DWORD g_blend_clip_mirrored_calls = 0u;
static DWORD g_blend_clip_mirrored_pixels = 0u;
static DWORD g_blend_clip_changed_calls = 0u;
static DWORD g_blend_clip_clipped_calls = 0u;
static DWORD g_blend_clip_reject_target = 0u;
static DWORD g_blend_clip_reject_bounds = 0u;
static DWORD g_blend_clip_reject_size = 0u;
static DWORD g_blend_clip_reject_guard = 0u;
static DWORD g_blend_clip_band_calls = 0u;
static DWORD g_blend_skip_invocations = 0u;
static DWORD g_blend_skip_mirrored_calls = 0u;
static DWORD g_blend_skip_mirrored_pixels = 0u;
static DWORD g_blend_skip_changed_calls = 0u;
static DWORD g_blend_skip_clipped_calls = 0u;
static DWORD g_blend_skip_reject_target = 0u;
static DWORD g_blend_skip_reject_bounds = 0u;
static DWORD g_blend_skip_reject_size = 0u;
static DWORD g_blend_skip_reject_guard = 0u;
static DWORD g_blend_skip_band_calls = 0u;
static BYTE g_textout_before[G1_OVERLAY_MAX_WIDTH * G1_OVERLAY_MAX_HEIGHT];
static DWORD g_textout_invocations = 0u;
static DWORD g_textout_mirrored_calls = 0u;
static DWORD g_textout_mirrored_pixels = 0u;
static DWORD g_textout_changed_calls = 0u;
static DWORD g_textout_reject_target = 0u;
static DWORD g_textout_reject_target_ps5 = 0u;
static DWORD g_textout_reject_target_ps7 = 0u;
static DWORD g_textout_reject_target_other = 0u;
static DWORD g_textout_reject_target_dc_screen = 0u;
static DWORD g_textout_reject_target_dc_buffer = 0u;
static DWORD g_textout_reject_target_dc_other = 0u;
static DWORD g_textout_reject_logged_ps5 = 0u;
static DWORD g_textout_reject_logged_ps7 = 0u;
static DWORD g_last_present_screen = 0u;
static DWORD g_textout_reject_size = 0u;
static DWORD g_textout_reject_guard = 0u;
static DWORD g_textout_reject_align = 0u;
static DWORD g_textout_install_mismatch = 0u;
static DWORD g_textout_slot_restored = 0u;
static BYTE *g_s3_mask = NULL;
static DWORD g_primitive_calls = 0;
static DWORD g_covered_pixels = 0;
static DWORD g_stale_pixels = 0;
static DWORD g_present_count = 0;
static G1StaleMaskSpec g_stale_mask_spec;
static BYTE *g_stale_mask_buffer = NULL;
static DWORD g_stale_mask_state = 3u;
static DWORD g_stale_mask_ordinal = 0u;
static DWORD g_stale_mask_dumps = 0u;
static DWORD g_primitive_reinvoke_elapsed_ms_total = 0;
static DWORD g_primitive_reinvoke_elapsed_ms_max = 0;
static DWORD g_primitive_reinvoke_count = 0;
static DWORD g_writer_call_counts[7];
static DWORD g_tinted_writer_calls[2];
static DWORD g_tinted_writer_covered[2];
static DWORD g_layer_compose_calls = 0u;
static DWORD g_layer_move_calls = 0u;
static DWORD g_layer_move_bytes = 0u;
static DWORD g_layer_move_unsupported = 0u;
static DWORD g_layer_transfer_calls = 0u;
static DWORD g_layer_covered_pixels = 0u;
static DWORD g_menu_copy_calls = 0u;
static DWORD g_menu_copy_pixels = 0u;
static DWORD g_menu_copy_hash_first = 0u;
static DWORD g_menu_copy_hash_last = 0u;
static DWORD g_menu_copy_hash_changes = 0u;
static DWORD g_partial_copy_calls = 0u;
static DWORD g_partial_copy_pixels = 0u;
static DWORD g_frame_copy_calls = 0u;
static DWORD g_frame_copy_pixels = 0u;
static DWORD g_frame_copy_rejects = 0u;
static DWORD g_writer_clip_mismatch_counts[7];
static DWORD g_last_clip_mismatch_writer = 0u;
static DWORD g_last_clip_mismatch_origin_x = 0u;
static DWORD g_last_clip_mismatch_origin_y = 0u;
static DWORD g_last_clip_mismatch_width = 0u;
static DWORD g_last_clip_mismatch_height = 0u;
static DWORD g_last_clip_mismatch_x = 0u;
static DWORD g_last_clip_mismatch_y = 0u;
static BYTE g_last_clip_screen_value = 0u;
static BYTE g_last_clip_replay_value = 0u;
static DWORD g_viewport_replay_count = 0u;
static DWORD g_viewport_field_mutations = 0u;
static DWORD g_viewport_restore_failures = 0u;
static DWORD g_cache_clip_attempts = 0u;
static DWORD g_cache_clip_verify_failures = 0u;
static BOOL g_cache_clip_viewport_seen = FALSE;
static LONG g_cache_clip_first_viewport[4];
static DWORD g_cache_edge_unclipped_binds = 0u;
static BOOL g_s3_pattern_applied = FALSE;
static BOOL g_s3_overlay_done = FALSE;
static DWORD g_s3_pattern_pixels = 0;
static G1MirrorPresentMetrics g_last_present;

static void s3_overlay_at_present(const BYTE *source, DWORD source_stride);
static void s3_overlay_destination(const BYTE *source, DWORD source_stride,
                                   BYTE *destination, DWORD destination_stride);

typedef struct {
    BYTE *target;
    BYTE original[16];
    BYTE patched[16];
    DWORD length;
    BYTE *trampoline;
    BOOL installed;
} G1HookState;

static G1HookState g_hook_a;
static G1HookState g_hook_b;
static G1HookState g_hook_terrain_rle;
static G1HookState g_hook_terrain_shade;
static G1HookState g_hook_terrain_checker;
static G1HookState g_hook_terrain_clip;
static G1HookState g_hook_terrain_clip_shade;
static G1HookState g_hook_panel_rle;
static G1HookState g_hook_tinted_rle;
static G1HookState g_hook_tinted_clip_rle;
static G1HookState g_hook_rect_fill;
static G1HookState g_hook_cache_fill;
static G1HookState g_hook_rect_border;
static G1HookState g_hook_rect_border7;
static G1HookState g_hook_line;
static G1HookState g_hook_rect_solid;
static G1HookState g_hook_flip_rle;
static G1HookState g_hook_keyed_copy;
static G1HookState g_hook_flip_clip;
static G1HookState g_hook_shade_rle;
static G1HookState g_hook_shade_flip;
static G1HookState g_hook_shade_clip;
static G1HookState g_hook_blend_rle;
static G1HookState g_hook_blend_wrle;
static G1HookState g_hook_blend_clip;
static G1HookState g_hook_blend_skip;
static G1HookState g_hook_blend_clip7;
static G1HookState g_hook_flip_blend;
static G1HookState g_hook_blend_flip7;
static G1HookState g_hook_flip_blend7;
static G1HookState g_hook_blend_410;
static G1HookState g_hook_blend_6d0;
typedef BOOL (WINAPI *G1TextOutA)(HDC, int, int, LPCSTR, int);
typedef BOOL (WINAPI *G1TextExtentA)(HDC, LPCSTR, int, LPSIZE);
typedef UINT (WINAPI *G1TextAlign)(HDC);
typedef BOOL (WINAPI *G1GdiFlush)(void);
static G1TextOutA g_real_textout = NULL;
static G1TextExtentA g_textout_extent = NULL;
static G1TextAlign g_textout_align = NULL;
static G1GdiFlush g_textout_flush = NULL;
static BOOL g_textout_slot_active = FALSE;
static G1HookState g_hook_cache_copy;
static G1HookState g_hook_primary_readback;
static G1HookState g_hook_bar_copy;
static G1HookState g_hook_briefing_compose;
static G1HookState g_hook_cache_moves[8];
static G1PrimitiveFn g_original_cache_copy = NULL;
typedef void *(__cdecl *G1MemmoveFn)(void *, const void *, DWORD);
static G1MemmoveFn g_original_cache_move = NULL;
typedef BOOL (WINAPI *G1GetCursorPosFn)(LPPOINT);
typedef BOOL (WINAPI *G1SetCursorPosFn)(int, int);
typedef BOOL (WINAPI *G1ClipCursorFn)(const RECT *);
static G1GetCursorPosFn g_get_cursor_pos = NULL;
static G1SetCursorPosFn g_set_cursor_pos = NULL;
static G1ClipCursorFn g_clip_cursor = NULL;
static volatile LONG g_input_installed = 0;
static HWND g_input_window = NULL;
static WNDPROC g_input_original_wndproc = NULL;
static LONG g_input_window_area = 0;
static volatile LONG g_env_state = 0;
static BOOL g_mirror_enabled = FALSE;
/* H-S2d (SYW2_G1_LAYER_DRIFT): cache-layer drift diagnostic state. */
typedef struct {
    BOOL valid;
    DWORD writer, present, result;
    LONG origin_x, origin_y;
    DWORD width, height;
} G1DriftEvent;
static BOOL g_layer_drift_enabled = FALSE;
static HANDLE g_drift_file = INVALID_HANDLE_VALUE;
static DWORD g_drift_present = 0u;
static DWORD g_drift_calls[G1_LAYER_DRIFT_RECTS][G1_DRIFT_CALL_REASONS];
static DWORD g_drift_px[G1_LAYER_DRIFT_RECTS][G1_DRIFT_PX_RESULTS];
static DWORD g_drift_guard_bypass = 0u;
static DWORD g_drift_cur_writer = 0u;
static LONG g_drift_cur_x = 0, g_drift_cur_y = 0;
static DWORD g_drift_cur_w = 0u, g_drift_cur_h = 0u;
static G1DriftEvent g_drift_event[G1_LAYER_DRIFT_RECTS];
static char g_drift_last_sample[G1_LAYER_DRIFT_RECTS][320];
static char g_drift_last_rect[G1_LAYER_DRIFT_RECTS][320];
/* H-B2: per-call write attribution of the three screen sample points. */
static DWORD g_drift_w_records = 0u;
static DWORD g_blend_410_invocations = 0u;
static DWORD g_blend_410_changed_calls = 0u;
/* H-D2k-s1: 0x467410 diff mirror (production). */
static BYTE g_blend_410_before[G1_OVERLAY_MAX_WIDTH * G1_OVERLAY_MAX_HEIGHT];
static DWORD g_blend_410_mirrored_calls = 0u;
static DWORD g_blend_410_mirrored_pixels = 0u;
static DWORD g_blend_410_reject_target = 0u;
static DWORD g_blend_410_reject_bounds = 0u;
static DWORD g_blend_410_reject_size = 0u;
static DWORD g_blend_410_reject_guard = 0u;
static DWORD g_blend_6d0_invocations = 0u;
static DWORD g_blend_6d0_changed_calls = 0u;
static DWORD g_drift_unattributed[G1_LAYER_DRIFT_RECTS];
static DWORD g_drift_prev_scr[G1_LAYER_DRIFT_RECTS];
static BOOL g_drift_prev_valid = FALSE;
static BOOL g_drift_w_hit[G1_LAYER_DRIFT_RECTS];
static BOOL g_hd_negative_probe_enabled = FALSE;
static BOOL g_s3_pattern_enabled = FALSE;
static BOOL g_blend_size_reject_diag = FALSE;
static BOOL g_ret_range_diag = FALSE;
static DWORD g_ret_diag_b_kills = 0u;
static DWORD g_ret_diag_b_idle = 0u;
static DWORD g_ret_diag_textout_kills = 0u;
static DWORD g_ret_diag_textout_idle = 0u;
static char g_panel_hd_pack_dir[MAX_PATH];

static DWORD elapsed_ms(DWORD started)
{
    return GetTickCount() - started;
}

static void panel_copy_bytes(BYTE *destination, const BYTE *source, DWORD count)
{
    volatile BYTE *out = destination;
    const volatile BYTE *in = source;
    DWORD index;
    for (index = 0u; index < count; ++index) out[index] = in[index];
}

static void initialize_environment(void)
{
    char value[8];
    char stale_mask[64];
    char drift_samples[64];
    DWORD size;
    LONG state = InterlockedCompareExchange(&g_env_state, 1, 0);
    if (state == 0) {
        size = GetEnvironmentVariableA(G1_STALE_MASK_ENV, stale_mask, sizeof(stale_mask));
        g_stale_mask_spec.count = 0u;
        if (size > 0u && size < sizeof(stale_mask))
            g1_stale_mask_parse(stale_mask, size, &g_stale_mask_spec);
        size = GetEnvironmentVariableA(G1_STALE_MASK_STATE_ENV, value, sizeof(value));
        if (size > 0u && size < sizeof(value))
            g_stale_mask_state = (DWORD)g1_stale_mask_state_parse(value, size);
        size = GetEnvironmentVariableA(G1_LAYER_DRIFT_ENV, value, sizeof(value));
        g_layer_drift_enabled = size == 1u && value[0] == '1';
        size = GetEnvironmentVariableA(G1_DRIFT_SAMPLES_ENV, drift_samples, sizeof(drift_samples));
        if (size > 0u && size < sizeof(drift_samples))
            g1_layer_drift_samples_parse(drift_samples, size);
        size = GetEnvironmentVariableA(G1_MIRROR_ENV, value, sizeof(value));
        g_mirror_enabled = size == 1u && value[0] == '1';
        size = GetEnvironmentVariableA(G1_HD_NEGATIVE_ENV, value, sizeof(value));
        g_hd_negative_probe_enabled = size == 1u && value[0] == '1';
        size = GetEnvironmentVariableA(G1_S3_PATTERN_ENV, value, sizeof(value));
        g_s3_pattern_enabled = size == 1u && value[0] == '1';
        size = GetEnvironmentVariableA(G1_BLEND_SIZE_REJECT_DIAG_ENV, value, sizeof(value));
        g_blend_size_reject_diag = size == 1u && value[0] == '1';
        size = GetEnvironmentVariableA(G1_RET_RANGE_DIAG_ENV, value, sizeof(value));
        g_ret_range_diag = size == 1u && value[0] == '1';
        size = GetEnvironmentVariableA(G1_PAUSE_SNAPSHOT_ENV, value, sizeof(value));
        g_pause_snapshot_enabled = !(size == 1u && value[0] == '0');
        size = GetEnvironmentVariableA(G1_PRIMARY_READBACK_ENV, value, sizeof(value));
        g_primary_readback_enabled = !(size == 1u && value[0] == '0');
        size = GetEnvironmentVariableA(G1_BAR_COPY_ENV, value, sizeof(value));
        g_bar_copy_enabled = !(size == 1u && value[0] == '0');
        size = GetEnvironmentVariableA(G1_RECT_SOLID_WIDE_ENV, value, sizeof(value));
        g_rect_solid_wide_enabled = !(size == 1u && value[0] == '0');
        size = GetEnvironmentVariableA(G1_TEXTOUT_SCREEN_DC_ENV, value, sizeof(value));
        g_textout_screen_dc_enabled = !(size == 1u && value[0] == '0');
        size = GetEnvironmentVariableA(G1_BRIEFING_COMPOSE_ENV, value, sizeof(value));
        g_briefing_compose_enabled = !(size == 1u && value[0] == '0');
        size = GetEnvironmentVariableA(G1_SCRATCH_BLTFAST_ENV, value, sizeof(value));
        g_scratch_bltfast_enabled = !(size == 1u && value[0] == '0');
        size = GetEnvironmentVariableA(G1_KEYED_COPY_ENV, value, sizeof(value));
        g_keyed_copy_enabled = !(size == 1u && value[0] == '0');
        size = GetEnvironmentVariableA(G1_PANEL_HD_PACK_ENV,
                                       g_panel_hd_pack_dir,
                                       sizeof(g_panel_hd_pack_dir));
        if (size == 0u || size >= sizeof(g_panel_hd_pack_dir))
            g_panel_hd_pack_dir[0] = '\0';
        InterlockedExchange(&g_env_state, 2);
    } else {
        while (InterlockedCompareExchange(&g_env_state, 2, 2) != 2) Sleep(0);
    }
}

static BOOL env_enabled(void)
{
    initialize_environment();
    return g_mirror_enabled;
}

static BOOL hd_negative_probe_enabled(void)
{
    initialize_environment();
    return g_hd_negative_probe_enabled;
}

BOOL g1_mirror2x_s3_pattern_enabled(void)
{
    initialize_environment();
    return g_s3_pattern_enabled;
}

/* H-ULc U-0 (diagnostic only, default off): reproduces the lap1083 pre-H-W330 size reject of
 * 0x467580 (width > 320 or height > 160) and 0x467B00 (width > 320) so a control run can show
 * whether the H-W330 tiled mirror causes a residual. Never enabled outside the saved-scene probe. */
static BOOL blend_size_reject_diag(int width, int height, BOOL check_height)
{
    initialize_environment();
    if (!g_blend_size_reject_diag) return FALSE;
    return (DWORD)width > G1_OVERLAY_MAX_WIDTH ||
           (check_height && (DWORD)height > G1_OVERLAY_MAX_HEIGHT);
}

static void ret_range_diag_count(DWORD return_address, DWORD *kills, DWORD *idle)
{
    if (return_address >= G1_RET_RANGE_KILLS_BASE &&
        return_address - G1_RET_RANGE_KILLS_BASE < G1_RET_RANGE_SIZE) {
        ++*kills;
    } else if (return_address >= G1_RET_RANGE_IDLE_BASE &&
               return_address - G1_RET_RANGE_IDLE_BASE < G1_RET_RANGE_SIZE) {
        ++*idle;
    }
}

static __attribute__((noinline, optimize("no-tree-loop-distribute-patterns")))
void fill_pattern_bytes(void *memory, BYTE value, DWORD size)
{
    volatile BYTE *bytes = (volatile BYTE *)memory;
    DWORD i = 0u;
    DWORD word_count;
    DWORD pattern = (DWORD)value * 0x01010101u;
    BYTE *destination;
    for (; i < size && (((DWORD)(ULONG_PTR)(bytes + i) & 3u) != 0u); ++i)
        bytes[i] = value;
    word_count = (size - i) / 4u;
    destination = (BYTE *)(bytes + i);
    if (word_count != 0u) {
        __asm__ __volatile__("cld; rep stosl"
                             : "+D"(destination), "+c"(word_count)
                             : "a"(pattern)
                             : "memory", "cc");
    }
    i += ((size - i) / 4u) * 4u;
    for (; i < size; ++i) bytes[i] = value;
}

static __attribute__((noinline, optimize("no-tree-loop-distribute-patterns")))
void zero_bytes(void *memory, DWORD size)
{
    fill_pattern_bytes(memory, 0u, size);
}

static __attribute__((noinline, optimize("no-tree-loop-distribute-patterns")))
void fill_bytes(void *memory, BYTE value, DWORD size)
{
    fill_pattern_bytes(memory, value, size);
}

static void mirror_move_bytes(BYTE *destination, const BYTE *source, DWORD size)
{
    volatile BYTE *dst = destination;
    const volatile BYTE *src = source;
    DWORD index;
    if (dst < src || dst >= src + size) {
        for (index = 0u; index < size; ++index) dst[index] = src[index];
    } else {
        for (index = size; index > 0u; --index) dst[index - 1u] = src[index - 1u];
    }
}

static __attribute__((noinline, optimize("no-tree-loop-distribute-patterns")))
void clear_layer_coverage(DWORD start, DWORD end)
{
    volatile BYTE *covered = g_layer_covered;
    DWORD index;
    for (index = start; index < end; ++index) covered[index] = 0u;
}

static BOOL range_valid(DWORD stride, DWORD width, DWORD height)
{
    return stride >= width && width != 0u && height != 0u &&
           stride <= G1_MAX_STRIDE && height <= G1_MAX_HEIGHT;
}

static DWORD hash_visible_rows(const BYTE *base, DWORD stride, DWORD width,
                               DWORD height)
{
    DWORD hash = 2166136261u;
    DWORD y, x;
    if (!base || !range_valid(stride, width, height)) return 0u;
    for (y = 0; y < height; ++y) {
        const BYTE *row = base + y * stride;
        for (x = 0; x < width; ++x) {
            hash ^= row[x];
            hash *= 16777619u;
        }
    }
    return hash;
}

static void dump_first_row(const BYTE *base, DWORD stride, DWORD width,
                           char output[65])
{
    static const char hex[] = "0123456789abcdef";
    DWORD count = width < 32u ? width : 32u;
    DWORD i;
    if (!output) return;
    for (i = 0; i < count; ++i) {
        BYTE value = base[i];
        output[i * 2u] = hex[value >> 4];
        output[i * 2u + 1u] = hex[value & 0x0Fu];
    }
    (void)stride;
    output[count * 2u] = '\0';
}

BOOL g1_mirror2x_enabled(void)
{
    return env_enabled();
}

BOOL g1_mirror2x_present_rect(DWORD destination_width, DWORD destination_height,
                              DWORD source_width, DWORD source_height,
                              DWORD x, DWORD y, const RECT *source_rect,
                              RECT *destination_rect, RECT *effective_source)
{
    RECT src;
    DWORD src_width, src_height;
    if (!destination_rect || !effective_source || destination_width != 1600u ||
        destination_height != 1200u || source_width < 800u ||
        source_height != 600u) return FALSE;
    src = source_rect ? *source_rect : (RECT){0, 0, 800, 600};
    src_width = (DWORD)(src.right - src.left);
    src_height = (DWORD)(src.bottom - src.top);
    if (src.left < 0 || src.top < 0 || src.right <= src.left ||
        src.bottom <= src.top || src_width != 800u || src_height != 600u ||
        x > 800u || y > 600u || x + src_width > 800u || y + src_height > 600u)
        return FALSE;
    destination_rect->left = (LONG)(x * 2u);
    destination_rect->top = (LONG)(y * 2u);
    destination_rect->right = destination_rect->left + (LONG)(src_width * 2u);
    destination_rect->bottom = destination_rect->top + (LONG)(src_height * 2u);
    *effective_source = src;
    return destination_rect->right <= 1600 && destination_rect->bottom <= 1200;
}

BOOL g1_mirror2x_input_point(LONG physical_x, LONG physical_y,
                             LONG *logical_x, LONG *logical_y)
{
    if (!logical_x || !logical_y || physical_x < 0 || physical_y < 0) return FALSE;
    *logical_x = physical_x / 2;
    *logical_y = physical_y / 2;
    return TRUE;
}

BOOL g1_mirror2x_input_rect(const RECT *physical, RECT *logical)
{
    if (!physical || !logical || physical->left < 0 || physical->top < 0 ||
        physical->right < physical->left || physical->bottom < physical->top)
        return FALSE;
    logical->left = physical->left / 2;
    logical->top = physical->top / 2;
    logical->right = physical->right / 2;
    logical->bottom = physical->bottom / 2;
    return TRUE;
}

static BOOL patch_user32_iat(const char *name, void *replacement, void **original)
{
    BYTE *base = (BYTE *)(ULONG_PTR)G1_EXE_BASE;
    IMAGE_DOS_HEADER *dos = (IMAGE_DOS_HEADER *)base;
    IMAGE_NT_HEADERS *nt;
    IMAGE_IMPORT_DESCRIPTOR *imports;
    if (!dos || dos->e_magic != IMAGE_DOS_SIGNATURE) return FALSE;
    nt = (IMAGE_NT_HEADERS *)(base + dos->e_lfanew);
    if (nt->Signature != IMAGE_NT_SIGNATURE) return FALSE;
    imports = (IMAGE_IMPORT_DESCRIPTOR *)(base +
        nt->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_IMPORT].VirtualAddress);
    for (; imports && imports->Name; ++imports) {
        const char *dll_name = (const char *)(base + imports->Name);
        IMAGE_THUNK_DATA *names;
        IMAGE_THUNK_DATA *functions;
        if (lstrcmpiA(dll_name, G1_USER32_NAME) != 0) continue;
        names = (IMAGE_THUNK_DATA *)(base + imports->OriginalFirstThunk);
        functions = (IMAGE_THUNK_DATA *)(base + imports->FirstThunk);
        for (; names->u1.AddressOfData; ++names, ++functions) {
            IMAGE_IMPORT_BY_NAME *import_name;
            DWORD old_protect, restored;
            if (names->u1.Ordinal & IMAGE_ORDINAL_FLAG) continue;
            import_name = (IMAGE_IMPORT_BY_NAME *)(base + names->u1.AddressOfData);
            if (lstrcmpA((const char *)import_name->Name, name) != 0) continue;
            if (!VirtualProtect(&functions->u1.Function, sizeof(void *), PAGE_READWRITE,
                                &old_protect)) return FALSE;
            if (original) *original = (void *)(ULONG_PTR)functions->u1.Function;
            functions->u1.Function = (DWORD)(ULONG_PTR)replacement;
            VirtualProtect(&functions->u1.Function, sizeof(void *), old_protect, &restored);
            FlushInstructionCache(GetCurrentProcess(), &functions->u1.Function, sizeof(void *));
            return TRUE;
        }
    }
    return FALSE;
}

static BOOL WINAPI mirror_get_cursor_pos(LPPOINT point)
{
    LONG physical_x, physical_y, x, y;
    if (!g_get_cursor_pos || !g_get_cursor_pos(point)) return FALSE;
    if (!point) return TRUE;
    physical_x = point->x;
    physical_y = point->y;
    if (g1_mirror2x_input_point(physical_x, physical_y, &x, &y)) {
        point->x = x; point->y = y;
        g1_mirror2x_input_trace("GetCursorPos", NULL, 0u, physical_x, physical_y,
                                x, y, 0u, TRUE);
    }
    return TRUE;
}

static BOOL WINAPI mirror_set_cursor_pos(int x, int y)
{
    if (!g_set_cursor_pos) return FALSE;
    return g_set_cursor_pos(x * 2, y * 2);
}

static BOOL WINAPI mirror_clip_cursor(const RECT *rect)
{
    RECT physical;
    if (!g_clip_cursor) return FALSE;
    if (!rect) return g_clip_cursor(NULL);
    physical.left = rect->left * 2; physical.top = rect->top * 2;
    physical.right = rect->right * 2; physical.bottom = rect->bottom * 2;
    return g_clip_cursor(&physical);
}

static LRESULT CALLBACK mirror_wndproc(HWND hwnd, UINT message,
                                       WPARAM wparam, LPARAM lparam)
{
    if (message >= WM_MOUSEFIRST && message <= WM_MOUSELAST &&
        message != WM_MOUSEWHEEL && message != WM_MOUSEHWHEEL) {
        LONG physical_x = (LONG)(SHORT)LOWORD(lparam);
        LONG physical_y = (LONG)(SHORT)HIWORD(lparam);
        LONG logical_x, logical_y;
        if (g1_mirror2x_input_point(physical_x, physical_y, &logical_x, &logical_y)) {
            lparam = MAKELPARAM((SHORT)logical_x, (SHORT)logical_y);
            if (message == WM_LBUTTONDOWN || message == WM_LBUTTONUP ||
                message == WM_RBUTTONDOWN || message == WM_RBUTTONUP ||
                message == WM_MBUTTONDOWN || message == WM_MBUTTONUP) {
                g1_mirror2x_input_trace("WndProc", hwnd, message, physical_x,
                                        physical_y, logical_x, logical_y,
                                        wparam, TRUE);
            }
        }
    }
    return CallWindowProcA(g_input_original_wndproc, hwnd, message, wparam, lparam);
}

static BOOL CALLBACK find_input_window(HWND hwnd, LPARAM unused)
{
    RECT rect;
    DWORD pid = 0;
    (void)unused;
    if (!IsWindowVisible(hwnd)) return TRUE;
    GetWindowThreadProcessId(hwnd, &pid);
    if (pid != GetCurrentProcessId() || !GetWindowRect(hwnd, &rect)) return TRUE;
    if (!g_input_window ||
        (rect.right - rect.left) * (rect.bottom - rect.top) > g_input_window_area) {
        g_input_window = hwnd;
        g_input_window_area = (rect.right - rect.left) * (rect.bottom - rect.top);
    }
    return TRUE;
}

static DWORD WINAPI input_window_thread(LPVOID unused)
{
    DWORD attempt;
    (void)unused;
    for (attempt = 0; attempt < 6000u && !g_input_window; ++attempt) {
        EnumWindows(find_input_window, 0);
        if (!g_input_window) Sleep(1u);
    }
    if (g_input_window) {
        LONG old = SetWindowLongA(g_input_window, GWL_WNDPROC,
                                  (LONG)(ULONG_PTR)mirror_wndproc);
        if (old != 0) g_input_original_wndproc = (WNDPROC)(ULONG_PTR)old;
        else g_input_window = NULL;
    }
    return 0u;
}

BOOL g1_mirror2x_input_install(void)
{
    if (!env_enabled()) return TRUE;
    if (InterlockedCompareExchange(&g_input_installed, 1, 0) != 0) return TRUE;
    if (!patch_user32_iat("GetCursorPos", (void *)mirror_get_cursor_pos,
                          (void **)&g_get_cursor_pos)) {
        InterlockedExchange(&g_input_installed, 0);
        return FALSE;
    }
    /* The pinned EXE does not import SetCursorPos or ClipCursor.  They remain
     * optional hooks for a future build that does; their absence is not an
     * input-install failure because this build's mouse path is WndProc plus
     * GetCursorPos. */
    patch_user32_iat("SetCursorPos", (void *)mirror_set_cursor_pos,
                     (void **)&g_set_cursor_pos);
    patch_user32_iat("ClipCursor", (void *)mirror_clip_cursor,
                     (void **)&g_clip_cursor);
    if (!CreateThread(NULL, 0, input_window_thread, NULL, 0, NULL)) {
        InterlockedExchange(&g_input_installed, 0);
        return FALSE;
    }
    return TRUE;
}

BOOL g1_mirror2x_nearest2x(const BYTE *src, DWORD src_stride,
                           BYTE *dst, DWORD dst_stride,
                           DWORD width, DWORD height)
{
    DWORD y, x;
    if (!src || !dst || !range_valid(src_stride, width, height) ||
        !range_valid(dst_stride, width * 2u, height * 2u) ||
        (dst >= src && dst < src + src_stride * height) ||
        (src >= dst && src < dst + dst_stride * height * 2u)) return FALSE;
    for (y = 0; y < height; ++y) {
        const BYTE *row = src + y * src_stride;
        BYTE *top = dst + (y * 2u) * dst_stride;
        BYTE *bottom = top + dst_stride;
        for (x = 0; x < width; ++x) {
            BYTE pixel = row[x];
            top[x * 2u] = pixel; top[x * 2u + 1u] = pixel;
            bottom[x * 2u] = pixel; bottom[x * 2u + 1u] = pixel;
        }
    }
    return TRUE;
}

DWORD g1_mirror2x_compose_sentinel(const BYTE *expected800,
                                   const BYTE *scratch_a,
                                   const BYTE *scratch_b,
                                   DWORD src_stride, BYTE *mirror1600,
                                   DWORD mirror_stride, DWORD width,
                                   DWORD height, LONG primitive_x,
                                   LONG primitive_y, DWORD primitive_width,
                                   DWORD primitive_height)
{
    DWORD y, x, covered = 0;
    BOOL hd_enabled;
    G1ScratchBounds bounds;
    if (!expected800 || !scratch_a || !scratch_b || !mirror1600 ||
        !range_valid(src_stride, width, height) ||
        !range_valid(mirror_stride, width * 2u, height * 2u)) return 0;
    hd_enabled = g1_hd_asset_enabled();
    if (!g1_scratch_intersection(primitive_x, primitive_y, primitive_width,
                                 primitive_height, width, height, &bounds)) {
        bounds.x = 0u;
        bounds.y = 0u;
        bounds.width = width;
        bounds.height = height;
    }
    for (y = bounds.y; y < bounds.y + bounds.height; ++y) {
        for (x = bounds.x; x < bounds.x + bounds.width; ++x) {
            DWORD expected_index = y * src_stride + x;
            DWORD logical = y * width + x;
            BYTE a = scratch_a[expected_index], b = scratch_b[expected_index];
            if (a == b && (a != 0x00u || b != 0xFFu)) {
                BYTE top_left, top_right, bottom_left, bottom_right;
                BYTE *row = mirror1600 + (y * 2u) * mirror_stride + x * 2u;
                if (hd_enabled) {
                    if (!g1_hd_asset_lookup_identity_block(
                            logical, &top_left, &top_right, &bottom_left,
                            &bottom_right)) continue;
                } else {
                    top_left = (a != 0x00u) ? a : b;
                    top_right = top_left;
                    bottom_left = top_left;
                    bottom_right = top_left;
                }
                row[0] = top_left; row[1] = top_right;
                row[mirror_stride] = bottom_left;
                row[mirror_stride + 1u] = bottom_right;
                if (g_covered && logical < 800u * 600u) {
                    if (!g_covered[logical]) ++covered;
                    g_covered[logical] = 1u;
                    g1_hd_asset_mark(logical);
                    if (g_expected_snapshot)
                        g_expected_snapshot[logical] = expected800[expected_index];
                }
            } else if (expected800[expected_index] == expected800[expected_index]) {
                /* Keep the stale decision explicit: the present compositor
                 * will nearest-expand the same-frame source for this pixel. */
            }
        }
    }
    return covered;
}

static BOOL readable_bytes(const BYTE *source, DWORD bytes);

static BOOL layer_drift_on(void)
{
    initialize_environment();
    return g_layer_drift_enabled;
}

/* The current writer call (cache target only) and its region; set once per
 * call so the per-pixel notes of compose_cache_layer can name their writer. */
static void layer_drift_call(DWORD writer, DWORD reason, LONG origin_x,
                             LONG origin_y, DWORD width, DWORD height)
{
    DWORD i;
    unsigned px, py;
    g_drift_cur_writer = writer;
    g_drift_cur_x = origin_x;
    g_drift_cur_y = origin_y;
    g_drift_cur_w = width;
    g_drift_cur_h = height;
    for (i = 0u; i < G1_LAYER_DRIFT_RECTS; ++i) {
        G1DriftEvent *event = &g_drift_event[i];
        if (g1_layer_drift_overlap(i, origin_x, origin_y, width, height) != 0u)
            ++g_drift_calls[i][reason];
        g1_layer_drift_sample(i, &px, &py);
        if ((LONG)px >= origin_x && (LONG)px < origin_x + (LONG)width &&
            (LONG)py >= origin_y && (LONG)py < origin_y + (LONG)height) {
            event->valid = TRUE;
            event->writer = writer;
            event->present = g_drift_present;
            event->result = reason;
            event->origin_x = origin_x;
            event->origin_y = origin_y;
            event->width = width;
            event->height = height;
        }
    }
}

/* Early return of mirror_reinvoke: only a cache-target writer is a drift candidate. */
static void layer_drift_return(void *renderer, DWORD writer, DWORD reason,
                               LONG origin_x, LONG origin_y, DWORD width, DWORD height)
{
    const BYTE *field;
    if (!layer_drift_on() || !renderer) return;
    field = (const BYTE *)renderer + G1_RENDERER_BUFFER;
    if (!readable_bytes(field, sizeof(DWORD)) ||
        *(const DWORD *)field != G1_CACHE_BASE) return;
    layer_drift_call(writer, reason, origin_x, origin_y, width, height);
}

static void layer_drift_guard_bypass(void *renderer)
{
    const BYTE *field;
    if (!layer_drift_on() || !renderer) return;
    field = (const BYTE *)renderer + G1_RENDERER_BUFFER;
    if (readable_bytes(field, sizeof(DWORD)) && *(const DWORD *)field == G1_CACHE_BASE)
        ++g_drift_guard_bypass;
}

static void layer_drift_emit(const char *line, int length);
static DWORD read_game_dword(DWORD address);

/* H-B2: sample values (screen buffer) around one writer call.  Values are 0..255,
 * G1_DRIFT_UNREAD when the call is not on the screen buffer. */
#define G1_DRIFT_UNREAD 256u
typedef struct {
    BOOL on;
    BYTE *buffer;
    DWORD stride;
    DWORD before[G1_LAYER_DRIFT_RECTS];
} G1DriftWrite;

static void layer_drift_write_samples(const G1DriftWrite *write, DWORD *values)
{
    DWORD i;
    unsigned px, py;
    for (i = 0u; i < G1_LAYER_DRIFT_RECTS; ++i) {
        g1_layer_drift_sample(i, &px, &py);
        values[i] = write->on ? (DWORD)write->buffer[py * write->stride + px]
                              : G1_DRIFT_UNREAD;
    }
}

/* Only a call on the screen renderer/buffer in PS3 can touch the sample points. */
static void layer_drift_write_begin(G1DriftWrite *write, void *renderer)
{
    write->on = FALSE;
    write->buffer = NULL;
    write->stride = 0u;
    if (!layer_drift_on() || read_game_dword(G1_PROGRAM_STATE_VA) != 3u ||
        (DWORD)(ULONG_PTR)renderer != G1_RENDERER_VA) return;
    write->stride = *(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_STRIDE);
    write->buffer = *(BYTE **)((BYTE *)renderer + G1_RENDERER_BUFFER);
    if (!write->buffer || (DWORD)(ULONG_PTR)write->buffer == G1_CACHE_BASE ||
        write->buffer == g_panel_bound_buffer ||
        write->stride < G1_OVERLAY_SCREEN_WIDTH || write->stride > G1_MAX_STRIDE ||
        *(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_HEIGHT) !=
            G1_OVERLAY_SCREEN_HEIGHT) return;
    write->on = TRUE;
    layer_drift_write_samples(write, write->before);
}

/* One "w" record per call whose sample values changed or whose original
 * rectangle contains a sample point; p = ordinal of the next PS3 present. */
static void layer_drift_write_end(const G1DriftWrite *write, DWORD writer,
                                  const char *why, int x, int y, int width, int height)
{
    DWORD after[G1_LAYER_DRIFT_RECTS], i;
    unsigned px, py;
    BOOL changed = FALSE, contains = FALSE;
    char line[320];
    if (!write->on) return;
    layer_drift_write_samples(write, after);
    for (i = 0u; i < G1_LAYER_DRIFT_RECTS; ++i) {
        g1_layer_drift_sample(i, &px, &py);
        if ((int)px >= x && (int)px < x + width && (int)py >= y && (int)py < y + height)
            contains = TRUE;
        if (after[i] != write->before[i]) {
            changed = TRUE;
            g_drift_w_hit[i] = TRUE;
        }
    }
    if (changed) {
        if (writer == G1_BLEND_410) ++g_blend_410_changed_calls;
        if (writer == G1_BLEND_6D0) ++g_blend_6d0_changed_calls;
    }
    if (!changed && !contains) return;
    ++g_drift_w_records;
    layer_drift_emit(line, wsprintfA(line,
        "{\"t\":\"w\",\"f\":\"%X\",\"p\":%u,\"x\":%d,\"y\":%d,\"w\":%d,\"h\":%d,"
        "\"why\":\"%s\",\"sb\":[%u,%u,%u],\"sa\":[%u,%u,%u]}\n",
        writer, g_drift_present, x, y, width, height, why,
        write->before[0], write->before[1], write->before[2],
        after[0], after[1], after[2]));
}

static void layer_drift_pixel(DWORD x, DWORD y, DWORD result)
{
    DWORD i;
    unsigned px, py;
    for (i = 0u; i < G1_LAYER_DRIFT_RECTS; ++i) {
        if (!g1_layer_drift_contains(i, (long)x, (long)y)) continue;
        ++g_drift_px[i][result];
        g1_layer_drift_sample(i, &px, &py);
        if (px == x && py == y) {
            G1DriftEvent *event = &g_drift_event[i];
            event->valid = TRUE;
            event->writer = g_drift_cur_writer;
            event->present = g_drift_present;
            event->result = G1_DRIFT_EVENT_PIXEL_BASE + result;
            event->origin_x = g_drift_cur_x;
            event->origin_y = g_drift_cur_y;
            event->width = g_drift_cur_w;
            event->height = g_drift_cur_h;
        }
    }
}

static DWORD compose_cache_layer(const BYTE *expected, const BYTE *scratch_a,
                                 const BYTE *scratch_b, LONG origin_x,
                                 LONG origin_y, DWORD width, DWORD height)
{
    G1ScratchBounds bounds;
    DWORD x, y, added = 0u;
    const BOOL drift = layer_drift_on();
    if (!expected || !scratch_a || !scratch_b || !g_layer_mirror ||
        !g_layer_covered || !g_layer_expected || width > G1_CACHE_WIDTH ||
        height > G1_CACHE_HEIGHT ||
        !g1_mirror_scratch_bounds(origin_x, origin_y, width, height,
                                  1, G1_CACHE_HEIGHT, &bounds)) {
        if (drift)
            layer_drift_call(g_drift_cur_writer, G1_DRIFT_COMPOSE_BOUNDS, origin_x,
                             origin_y, width, height);
        return 0u;
    }
    ++g_layer_compose_calls;
    for (y = bounds.y; y < bounds.y + bounds.height; ++y) {
        for (x = bounds.x; x < bounds.x + bounds.width; ++x) {
            DWORD logical = y * G1_CACHE_WIDTH + x;
            BYTE a = scratch_a[logical], b = scratch_b[logical];
            BYTE tl, tr, bl, br;
            BYTE *row;
            /* An unwritten pixel (a=0x00, b=0xFF) is also a != b; the
             * diagnostic tells the two skips apart, the skip itself is the
             * original "a != b" test. */
            if (a != b) {
                if (drift)
                    layer_drift_pixel(x, y, a == 0u && b == 0xFFu
                                                 ? G1_DRIFT_PX_UNWRITTEN
                                                 : G1_DRIFT_PX_A_NE_B);
                continue;
            }
            if (!g1_hd_asset_lookup_identity_block_at(x, y, &tl, &tr, &bl, &br)) {
                if (drift) layer_drift_pixel(x, y, G1_DRIFT_PX_LOOKUP_MISS);
                continue;
            }
            row = g_layer_mirror + (y * 2u) * (G1_CACHE_WIDTH * 2u) + x * 2u;
            row[0] = tl; row[1] = tr;
            row[G1_CACHE_WIDTH * 2u] = bl;
            row[G1_CACHE_WIDTH * 2u + 1u] = br;
            if (!g_layer_covered[logical]) ++added;
            g_layer_covered[logical] = 1u;
            g_layer_expected[logical] = expected[logical];
            if (drift) layer_drift_pixel(x, y, G1_DRIFT_PX_COMPOSED);
        }
    }
    g_layer_covered_pixels += added;
    return added;
}

static void cache_layer_move_range(DWORD dst_offset, DWORD src_offset, DWORD bytes)
{
    DWORD dst_end = dst_offset + bytes;
    DWORD src_end = src_offset + bytes;
    DWORD pixel_start, pixel_end, step, y;
    BOOL reverse = dst_offset > src_offset && dst_offset < src_end;
    DWORD chunks;
    if ((dst_offset % G1_CACHE_WIDTH) == 0u &&
        (src_offset % G1_CACHE_WIDTH) == 0u &&
        (bytes % G1_CACHE_WIDTH) == 0u) {
        chunks = bytes / G1_CACHE_WIDTH;
        pixel_start = 0u; pixel_end = G1_CACHE_WIDTH;
    } else if (src_offset / G1_CACHE_WIDTH == (src_end - 1u) / G1_CACHE_WIDTH &&
               dst_offset / G1_CACHE_WIDTH == (dst_end - 1u) / G1_CACHE_WIDTH) {
        chunks = 1u;
        pixel_start = src_offset % G1_CACHE_WIDTH;
        pixel_end = pixel_start + bytes;
    } else {
        ++g_layer_move_unsupported;
        if (dst_offset < G1_CACHE_BYTES && bytes <= G1_CACHE_BYTES - dst_offset)
            clear_layer_coverage(dst_offset, dst_end);
        return;
    }
    for (step = 0u; step < chunks; ++step) {
        DWORD chunk = reverse ? chunks - step - 1u : step;
        DWORD src_row = src_offset / G1_CACHE_WIDTH + chunk;
        DWORD dst_row = dst_offset / G1_CACHE_WIDTH + chunk;
        DWORD src_x = chunks == 1u ? pixel_start : 0u;
        DWORD dst_x = chunks == 1u ? dst_offset % G1_CACHE_WIDTH : 0u;
        DWORD count = chunks == 1u ? pixel_end - pixel_start : G1_CACHE_WIDTH;
        DWORD src_index = src_row * G1_CACHE_WIDTH + src_x;
        DWORD dst_index = dst_row * G1_CACHE_WIDTH + dst_x;
        BYTE *src_hd = g_layer_mirror + src_row * 2u * (G1_CACHE_WIDTH * 2u) + src_x * 2u;
        BYTE *dst_hd = g_layer_mirror + dst_row * 2u * (G1_CACHE_WIDTH * 2u) + dst_x * 2u;
        DWORD hd_bytes = count * 2u;
        for (y = 0u; y < 2u; ++y)
            mirror_move_bytes(dst_hd + y * (G1_CACHE_WIDTH * 2u),
                              src_hd + y * (G1_CACHE_WIDTH * 2u), hd_bytes);
        mirror_move_bytes(g_layer_covered + dst_index,
                          g_layer_covered + src_index, count);
        mirror_move_bytes(g_layer_expected + dst_index,
                          g_layer_expected + src_index, count);
    }
}

static void *__cdecl mirror_cache_move(void *destination, const void *source,
                                        DWORD bytes)
{
    DWORD dst = (DWORD)(ULONG_PTR)destination;
    DWORD src = (DWORD)(ULONG_PTR)source;
    void *result = g_original_cache_move(destination, source, bytes);
    ++g_layer_move_calls;
    g_layer_move_bytes += bytes;
    if (dst >= G1_CACHE_BASE && src >= G1_CACHE_BASE &&
        dst < G1_CACHE_BASE + G1_CACHE_BYTES &&
        src < G1_CACHE_BASE + G1_CACHE_BYTES &&
        bytes != 0u && bytes <= G1_CACHE_BYTES - (dst - G1_CACHE_BASE) &&
        bytes <= G1_CACHE_BYTES - (src - G1_CACHE_BASE))
        cache_layer_move_range(dst - G1_CACHE_BASE, src - G1_CACHE_BASE, bytes);
    return result;
}

/* Layer model of a solid cache fill: every pixel becomes the fill colour with
 * a flat 2x2 HD block (a solid colour has no asset identity to look up). */
static void cache_layer_fill(const G1RectFill *rect, BYTE color)
{
    DWORD row, col, added = 0u;
    if (!g_layer_mirror || !g_layer_covered || !g_layer_expected) return;
    for (row = 0u; row < rect->height; ++row) {
        for (col = 0u; col < rect->width; ++col) {
            DWORD x = (DWORD)rect->x + col, y = (DWORD)rect->y + row;
            DWORD logical = y * G1_CACHE_WIDTH + x;
            BYTE *hd = g_layer_mirror + (y * 2u) * (G1_CACHE_WIDTH * 2u) + x * 2u;
            hd[0] = color; hd[1] = color;
            hd[G1_CACHE_WIDTH * 2u] = color; hd[G1_CACHE_WIDTH * 2u + 1u] = color;
            if (!g_layer_covered[logical]) ++added;
            g_layer_covered[logical] = 1u;
            g_layer_expected[logical] = color;
        }
    }
    g_layer_covered_pixels += added;
}

/* Original returns: 0x465FC0 ret 0x14.  The game clears the strip it exposes
 * next to the map edge in the terrain cache with this fill (lap863 map); the
 * layer model must follow or later cache shifts carry the old terrain. */
static DWORD __attribute__((thiscall)) mirror_cache_fill(void *renderer, DWORD x1,
                                                          DWORD y1, DWORD x2,
                                                          DWORD y2, DWORD color)
{
    G1RectFill rect;
    DWORD result;
    int status;
    if (!g_original_cache_fill) return 0u;
    ++g_cache_fill_invocations;
    result = g_original_cache_fill(renderer, x1, y1, x2, y2, color);
    if (!renderer) return result;
    if (*(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_BUFFER) != G1_CACHE_BASE ||
        *(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_STRIDE) != G1_CACHE_WIDTH) {
        ++g_cache_fill_reject_target;
        return result;
    }
    status = g1_cache_fill_region((int32_t)x1, (int32_t)y1, (int32_t)x2, (int32_t)y2,
                                  (int32_t)*(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_BPP),
                                  (int32_t)G1_CACHE_WIDTH, (int32_t)G1_CACHE_HEIGHT, &rect);
    if (status < 0) {
        ++g_cache_fill_unsupported;
    } else if (status > 0) {
        cache_layer_fill(&rect, (BYTE)color);
        ++g_cache_fill_mirrored_calls;
        g_cache_fill_mirrored_pixels += rect.width * rect.height;
    }
    return result;
}

static void transfer_cache_to_screen(DWORD x, DWORD y, DWORD width, DWORD height)
{
    DWORD left = x, top = y, right = x + width, bottom = y + height;
    DWORD row, col;
    if (right > G1_CACHE_WIDTH) right = G1_CACHE_WIDTH;
    if (bottom > G1_CACHE_HEIGHT) bottom = G1_CACHE_HEIGHT;
    if (right > 800u) right = 800u;
    if (bottom > 600u) bottom = 600u;
    if (left >= right || top >= bottom) return;
    for (row = top; row < bottom; ++row) {
        for (col = left; col < right; ++col) {
            DWORD layer_index = row * G1_CACHE_WIDTH + col;
            DWORD screen_index = row * 800u + col;
            if (!g_layer_covered[layer_index]) {
                g_covered[screen_index] = 0u;
                continue;
            }
            g_covered[screen_index] = 1u;
            g_expected_snapshot[screen_index] = g_layer_expected[layer_index];
            mirror_move_bytes(g_mirror + (row * 2u) * 1600u + col * 2u,
                              g_layer_mirror + (row * 2u) * (G1_CACHE_WIDTH * 2u) + col * 2u,
                              2u);
            mirror_move_bytes(g_mirror + (row * 2u + 1u) * 1600u + col * 2u,
                              g_layer_mirror + (row * 2u + 1u) * (G1_CACHE_WIDTH * 2u) + col * 2u,
                              2u);
        }
    }
}

static BOOL readable_bytes(const BYTE *source, DWORD bytes);

/* Menu/panel block copy (0x466280 with a packed, non-cache source): the
 * source is a packed width x height block, so Scale2x it directly instead of
 * leaving the rectangle on the nearest fallback.  The PS9 menu is the
 * full-screen (0,0,800,600) case; H-P35 adds the load-slot panel's partial
 * rectangles.  Pixels later overwritten by another writer fail the
 * expected-snapshot check at present (stale). */
static void transfer_block_copy_to_screen(void *renderer, DWORD x, DWORD y,
                                          DWORD width, DWORD height, DWORD source)
{
    const BYTE *src = (const BYTE *)(ULONG_PTR)source;
    BYTE *target = *(BYTE **)((BYTE *)renderer + G1_RENDERER_BUFFER);
    DWORD stride = *(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_STRIDE);
    DWORD surface_height = *(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_HEIGHT);
    DWORD logical, hash = 2166136261u;
    BYTE *mask = NULL, *hd = NULL;
    BOOL scale2x;
    if (!g1_frame_copy_accepts(x, y, width, height) ||
        !g_mirror || !g_covered || !g_expected_snapshot || !src ||
        (DWORD)(ULONG_PTR)target == G1_CACHE_BASE ||
        (target && target == g_panel_bound_buffer) ||
        stride < 800u || surface_height < 600u ||
        !readable_bytes(src, width * height)) return;
    scale2x = lstrcmpA(g1_hd_asset_source_name(), "scale2x") == 0;
    if (scale2x) {
        mask = (BYTE *)HeapAlloc(GetProcessHeap(), 0, width * height);
        hd = (BYTE *)HeapAlloc(GetProcessHeap(), 0, width * 2u * height * 2u);
        if (!mask || !hd) {
            if (mask) HeapFree(GetProcessHeap(), 0, mask);
            if (hd) HeapFree(GetProcessHeap(), 0, hd);
            return;
        }
        fill_bytes(mask, 1u, width * height);
    }
    if (!g1_frame_copy_apply(src, x, y, width, height, scale2x, mask, hd,
                             g_expected_snapshot, g_covered, g_mirror, 1600u)) {
        if (mask) HeapFree(GetProcessHeap(), 0, mask);
        if (hd) HeapFree(GetProcessHeap(), 0, hd);
        return;
    }
    if (width == 800u && height == 600u) {
        for (logical = 0u; logical < width * height; ++logical) {
            hash ^= src[logical];
            hash *= 16777619u;
        }
        if (scale2x) {
            /* H-HDF0: a whole-screen raw picture (the PS9 title is yfnt/title.spr, FNV-1a 1777000796) takes its
             * pack frame; the Scale2x copy above stays under it for the coverage maps and for the next frame. */
            const BYTE *pack = g1_hd_asset_fullscreen_frame(hash, width, height);
            if (pack) {
                DWORD row;
                for (row = 0u; row < height * 2u; ++row)
                    mirror_move_bytes(g_mirror + row * 1600u, pack + row * width * 2u, width * 2u);
            }
        }
        ++g_menu_copy_calls;
        if (g_menu_copy_calls == 1u) g_menu_copy_hash_first = hash;
        else if (hash != g_menu_copy_hash_last) ++g_menu_copy_hash_changes;
        g_menu_copy_hash_last = hash;
        g_menu_copy_pixels += width * height;
    } else {
        ++g_partial_copy_calls;
        g_partial_copy_pixels += width * height;
    }
    if (mask) HeapFree(GetProcessHeap(), 0, mask);
    if (hd) HeapFree(GetProcessHeap(), 0, hd);
}

/* H-P35: the load-slot screen's per-frame offscreen BltFast (0x00493CCB) copies
 * a whole 800x600 frame into the present source after the original call.  Its
 * source surface is locked read-only (pitch must be the packed 800) and mirrored
 * as a full-frame copy, so the black backdrop that the call rewrites unchanged
 * is still covered.  Rejects (lock failure, pitch, bounds) are counted. */
BOOL g1_mirror2x_frame_blt_copy(LPDIRECTDRAWSURFACE7 destination,
                                LPDIRECTDRAWSURFACE7 source)
{
    DDSURFACEDESC2 desc;
    BYTE *mask = NULL, *hd = NULL;
    BOOL scale2x, applied = FALSE;
    (void)destination;
    if (!source || !g_mirror || !g_covered || !g_expected_snapshot ||
        !g1_frame_copy_accepts(0u, 0u, 800u, 600u)) {
        ++g_frame_copy_rejects;
        return FALSE;
    }
    zero_bytes(&desc, sizeof(desc));
    desc.dwSize = sizeof(desc);
    if (FAILED(source->lpVtbl->Lock(source, NULL, &desc,
                                    DDLOCK_WAIT | DDLOCK_READONLY, NULL))) {
        ++g_frame_copy_rejects;
        return FALSE;
    }
    scale2x = lstrcmpA(g1_hd_asset_source_name(), "scale2x") == 0;
    if (desc.lpSurface && desc.lPitch == 800 && desc.dwWidth == 800u &&
        desc.dwHeight == 600u) {
        if (scale2x) {
            mask = (BYTE *)HeapAlloc(GetProcessHeap(), 0, 800u * 600u);
            hd = (BYTE *)HeapAlloc(GetProcessHeap(), 0, 1600u * 1200u);
            if (mask) fill_bytes(mask, 1u, 800u * 600u);
        }
        if (!scale2x || (mask && hd))
            applied = g1_frame_copy_apply((const BYTE *)desc.lpSurface, 0u, 0u, 800u, 600u,
                                          scale2x, mask, hd, g_expected_snapshot,
                                          g_covered, g_mirror, 1600u) != 0;
        if (mask) HeapFree(GetProcessHeap(), 0, mask);
        if (hd) HeapFree(GetProcessHeap(), 0, hd);
    }
    source->lpVtbl->Unlock(source, desc.lpSurface);
    if (applied) {
        ++g_frame_copy_calls;
        g_frame_copy_pixels += 800u * 600u;
    } else {
        ++g_frame_copy_rejects;
    }
    return applied;
}

/* H-RS2: a game readback of the primary surface (BltFast/Blt, primary source,
 * offscreen destination).  The primary holds the HD frame, so hand the game the
 * last presented logical frame instead.  Returns TRUE when the readback was
 * performed here and the original call must be skipped.  Calls are counted even
 * with the repair off (SYW2_G1_PRIMARY_READBACK=0) so the defect run is visible. */
BOOL g1_mirror2x_primary_readback(LPDIRECTDRAWSURFACE7 destination, DWORD return_address,
                                  DWORD x, DWORD y, const RECT *src, BOOL color_keyed)
{
    DDSURFACEDESC2 desc;
    size_t sx, sy, w, h;
    BOOL converted = FALSE;
    ++g_primary_readback_calls;
    g_primary_readback_return = return_address;
    if (!g_primary_readback_enabled) return FALSE;
    if (!destination || !g_last_frame || !g_last_frame_valid || color_keyed) {
        ++g_primary_readback_rejects;
        return FALSE;
    }
    zero_bytes(&desc, sizeof(desc));
    desc.dwSize = sizeof(desc);
    if (FAILED(destination->lpVtbl->Lock(destination, NULL, &desc, DDLOCK_WAIT, NULL))) {
        ++g_primary_readback_rejects;
        return FALSE;
    }
    if (desc.lpSurface && desc.lPitch > 0 && desc.ddpfPixelFormat.dwRGBBitCount == 8u &&
        g1_primary_readback_rect((const int32_t *)src, x, y, desc.dwWidth, desc.dwHeight,
                                 &sx, &sy, &w, &h) &&
        g1_primary_readback_copy(g_last_frame, (const int32_t *)src, x, y,
                                 (uint8_t *)desc.lpSurface, (size_t)desc.lPitch,
                                 desc.dwWidth, desc.dwHeight) != 0u) {
        g_primary_readback_dest_hash = hash_visible_rows(
            (const BYTE *)desc.lpSurface + y * (DWORD)desc.lPitch + x,
            (DWORD)desc.lPitch, (DWORD)w, (DWORD)h);
        g_primary_readback_source_hash = g_last_frame_source_hash;
        converted = TRUE;
    }
    destination->lpVtbl->Unlock(destination, desc.lpSurface);
    if (converted) ++g_primary_readback_converted;
    else ++g_primary_readback_rejects;
    return converted;
}

typedef DWORD (__attribute__((thiscall)) *G1RendererBlitFn)(
    void *renderer, DWORD selector, DWORD x, DWORD y, DWORD source, DWORD rect,
    DWORD flags);

/* Call-site wrapper for `call 0x469300` at 0x4C7EE6 (same thiscall, six stack
 * arguments).  Everything except a selector-1 blit whose source is the primary
 * surface goes straight to the original function. */
static DWORD __attribute__((thiscall)) mirror_primary_readback_site(
    void *renderer, DWORD selector, DWORD x, DWORD y, DWORD source, DWORD rect,
    DWORD flags)
{
    G1RendererBlitFn blit = (G1RendererBlitFn)(ULONG_PTR)G1_RENDERER_BLIT;
    const BYTE *field = (const BYTE *)renderer + G1_RENDERER_BACK_BUFFER;
    LPDIRECTDRAWSURFACE7 back = NULL;
    if (selector == 1u && source != 0u && source == read_game_dword(G1_PRIMARY_SURFACE_VA) &&
        readable_bytes(field, sizeof(DWORD)))
        back = *(LPDIRECTDRAWSURFACE7 const *)field;
    if (back && g1_mirror2x_primary_readback(back, G1_PRIMARY_READBACK_SITE + 5u, x, y,
                                             (const RECT *)(ULONG_PTR)rect,
                                             (flags & 1u) != 0u))
        return 0u;
    return blit(renderer, selector, x, y, source, rect, flags);
}

typedef DWORD (__attribute__((thiscall)) *G1RendererBarCopyFn)(
    void *renderer, DWORD dst, DWORD dst_pitch, DWORD src, DWORD src_pitch,
    DWORD sx0, DWORD sy0, DWORD sx1, DWORD sy1, DWORD dx, DWORD dy);

/* Call-site wrapper for `call 0x468BB0` at 0x4B5493 (same thiscall, ten stack
 * arguments).  The original runs first; the same rectangle is then mirrored when
 * it landed in the renderer's screen buffer.  Rejects (other destination, bad
 * rectangle, unreadable source, no memory) leave the original result alone. */
static DWORD __attribute__((thiscall)) mirror_bar_copy_site(
    void *renderer, DWORD dst, DWORD dst_pitch, DWORD src, DWORD src_pitch,
    DWORD sx0, DWORD sy0, DWORD sx1, DWORD sy1, DWORD dx, DWORD dy)
{
    G1RendererBarCopyFn original = (G1RendererBarCopyFn)(ULONG_PTR)G1_BAR_COPY_FUNC;
    DWORD result = original(renderer, dst, dst_pitch, src, src_pitch, sx0, sy0, sx1, sy1,
                            dx, dy);
    size_t width, height, offset, span;
    BYTE *packed;
    ++g_bar_copy_calls;
    if (!g_bar_copy_enabled) return result;
    if ((DWORD)(ULONG_PTR)renderer != G1_RENDERER_VA ||
        dst != *(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_BUFFER) ||
        dst_pitch != *(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_STRIDE) ||
        !g1_bar_copy_rect((int32_t)sx0, (int32_t)sy0, (int32_t)sx1, (int32_t)sy1,
                          (int32_t)dx, (int32_t)dy, &width, &height) ||
        !g1_bar_copy_source_span(sx0, sy0, src_pitch, width, height, &offset, &span) ||
        !src || !readable_bytes((const BYTE *)(ULONG_PTR)src + offset, (DWORD)span)) {
        ++g_bar_copy_rejects;
        return result;
    }
    packed = (BYTE *)HeapAlloc(GetProcessHeap(), 0, width * height);
    if (!packed) {
        ++g_bar_copy_rejects;
        return result;
    }
    g1_bar_copy_pack((const BYTE *)(ULONG_PTR)src, src_pitch, sx0, sy0, width, height, packed);
    transfer_block_copy_to_screen(renderer, dx, dy, (DWORD)width, (DWORD)height,
                                  (DWORD)(ULONG_PTR)packed);
    HeapFree(GetProcessHeap(), 0, packed);
    ++g_bar_copy_mirrored;
    g_bar_copy_pixels += (DWORD)(width * height);
    return result;
}

typedef DWORD (__attribute__((thiscall)) *G1BriefingComposeFn)(void *self, DWORD dest);

/* Call-site wrapper for `call 0x4D4620` at 0x4B23B5 (same thiscall, one stack argument).
 * The back buffer is copied before the original runs and diffed after it, so only the
 * pixels the composition changed reach the HD mirror.  A rejected surface (state, size,
 * format, lock failure) leaves the original result alone. */
static DWORD __attribute__((thiscall)) mirror_briefing_compose_site(void *self, DWORD dest)
{
    G1BriefingComposeFn original = (G1BriefingComposeFn)(ULONG_PTR)G1_BRIEFING_COMPOSE_FUNC;
    LPDIRECTDRAWSURFACE7 surface = (LPDIRECTDRAWSURFACE7)(ULONG_PTR)dest;
    DDSURFACEDESC2 desc;
    G1OverlayStats stats;
    size_t tiles = 0u;
    BOOL active = FALSE;
    DWORD result;
    ++g_briefing_compose_calls;
    g_briefing_compose_last_dest = dest;
    if (g_briefing_compose_enabled && !g_primitive_guard && g_mirror && g_covered &&
        g_expected_snapshot && dest != 0u &&
        dest == read_game_dword(G1_BACK_BUFFER_VA) &&
        read_game_dword(G1_PROGRAM_STATE_VA) == G1_BRIEFING_PROGRAM_STATE) {
        zero_bytes(&desc, sizeof(desc));
        desc.dwSize = sizeof(desc);
        if (SUCCEEDED(surface->lpVtbl->Lock(surface, NULL, &desc, DDLOCK_WAIT, NULL))) {
            g_briefing_compose_last_geometry[0] = desc.dwWidth;
            g_briefing_compose_last_geometry[1] = desc.dwHeight;
            g_briefing_compose_last_geometry[2] = (DWORD)desc.lPitch;
            g_briefing_compose_last_geometry[3] = desc.ddpfPixelFormat.dwRGBBitCount;
            if (desc.lpSurface && desc.lPitch > 0 &&
                g1_briefing_compose_accepts(G1_BRIEFING_PROGRAM_STATE, dest, dest,
                                            desc.dwWidth, desc.dwHeight,
                                            (DWORD)desc.lPitch,
                                            desc.ddpfPixelFormat.dwRGBBitCount)) {
                g1_bar_copy_pack((const BYTE *)desc.lpSurface, (size_t)desc.lPitch, 0u, 0u,
                                 G1_BRIEFING_MIN_WIDTH, G1_BRIEFING_HEIGHT,
                                 g_briefing_compose_before);
                active = TRUE;
            } else {
                ++g_briefing_compose_reject_surface;
            }
            surface->lpVtbl->Unlock(surface, desc.lpSurface);
        } else {
            ++g_briefing_compose_reject_lock;
        }
        if (!active) ++g_briefing_compose_rejects;
    } else {
        ++g_briefing_compose_reject_gate;
        ++g_briefing_compose_rejects;
    }
    result = original(self, dest);
    if (active) {
        BOOL applied = FALSE;
        zero_bytes(&desc, sizeof(desc));
        desc.dwSize = sizeof(desc);
        if (SUCCEEDED(surface->lpVtbl->Lock(surface, NULL, &desc, DDLOCK_WAIT, NULL))) {
            if (desc.lpSurface && desc.lPitch > 0 &&
                g1_briefing_compose_accepts(G1_BRIEFING_PROGRAM_STATE, dest, dest,
                                            desc.dwWidth, desc.dwHeight,
                                            (DWORD)desc.lPitch,
                                            desc.ddpfPixelFormat.dwRGBBitCount))
                applied = g1_overlay_blt_apply_tiled(
                    g_briefing_compose_before, (const BYTE *)desc.lpSurface,
                    (size_t)desc.lPitch, 0u, 0u, G1_BRIEFING_MIN_WIDTH, G1_BRIEFING_HEIGHT,
                    lstrcmpA(g1_hd_asset_source_name(), "scale2x") == 0,
                    g_overlay_scratch, g_briefing_compose_tile, g_expected_snapshot,
                    g_covered, g_mirror, 1600u, &stats, &tiles) != 0;
            surface->lpVtbl->Unlock(surface, desc.lpSurface);
        }
        if (applied) {
            ++g_briefing_compose_mirrored;
            g_briefing_compose_changed_pixels += (DWORD)stats.changed;
        } else {
            ++g_briefing_compose_rejects;
        }
    }
    return result;
}

static DWORD __attribute__((thiscall)) mirror_cache_copy(
    void *renderer, DWORD x, DWORD y, DWORD width, DWORD height, DWORD source)
{
    DWORD result = g_original_cache_copy(renderer, x, y, width, height, source);
    if (source == G1_CACHE_BASE) {
        ++g_layer_transfer_calls;
        transfer_cache_to_screen(x, y, width, height);
    } else {
        transfer_block_copy_to_screen(renderer, x, y, width, height, source);
    }
    return result;
}

static DWORD read_game_dword(DWORD address)
{
    return readable_bytes((const BYTE *)(ULONG_PTR)address, sizeof(DWORD))
        ? *(volatile DWORD *)(ULONG_PTR)address : 0xFFFFFFFFu;
}

/* Opt-in diagnostic (SYW2_G1_STALE_MASK): append one header + 800x600 map. */
static void stale_mask_write(const DWORD header[8], const BYTE *map)
{
    HANDLE file = CreateFileA(G1_STALE_MASK_PATH, GENERIC_WRITE, FILE_SHARE_READ,
                              NULL, OPEN_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    DWORD written;
    if (file == INVALID_HANDLE_VALUE) return;
    SetFilePointer(file, 0, NULL, FILE_END);
    if (WriteFile(file, header, 8u * sizeof(DWORD), &written, NULL) &&
        written == 8u * sizeof(DWORD))
        WriteFile(file, map, G1_STALE_MASK_PIXELS, &written, NULL);
    CloseHandle(file);
}

static void layer_drift_emit(const char *line, int length)
{
    DWORD written;
    if (length <= 0) return;
    if (g_drift_file == INVALID_HANDLE_VALUE) {
        g_drift_file = CreateFileA(G1_LAYER_DRIFT_PATH, GENERIC_WRITE, FILE_SHARE_READ,
                                   NULL, OPEN_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
        if (g_drift_file == INVALID_HANDLE_VALUE) return;
        SetFilePointer(g_drift_file, 0, NULL, FILE_END);
    }
    WriteFile(g_drift_file, line, (DWORD)length, &written, NULL);
}

/* Opt-in diagnostic (SYW2_G1_LAYER_DRIFT): one JSONL record per PS3 present
 * only when a sample point or rect counter changed.  Called before the stale
 * loop of g1_mirror2x_copy_present mutates g_covered. */
static void layer_drift_present(const BYTE *source, DWORD source_pitch)
{
    const BYTE *cache = (const BYTE *)(ULONG_PTR)G1_CACHE_BASE;
    char body[320], line[448];
    DWORD i, ordinal, tick;
    unsigned px, py;
    if (!layer_drift_on() || read_game_dword(G1_PROGRAM_STATE_VA) != 3u) return;
    if (!g_layer_covered || !g_layer_expected || !g_covered || !g_expected_snapshot ||
        !readable_bytes(cache, G1_CACHE_BYTES)) return;
    ordinal = g_drift_present++;
    tick = read_game_dword(G1_GAME_TICK_VA);
    if (ordinal == 0u) {
        layer_drift_emit(line, wsprintfA(line,
            "{\"t\":\"h\",\"schema\":\"syw2plus.g1-layer-drift.v1\",\"cache_base\":%u,\"pitch\":%u}\n",
            G1_CACHE_BASE, G1_LAYER_DRIFT_CACHE_PITCH));
    }
    for (i = 0u; i < G1_LAYER_DRIFT_RECTS; ++i) {
        const G1DriftEvent *event = &g_drift_event[i];
        G1LayerDriftCounts counts;
        g1_layer_drift_sample(i, &px, &py);
        {
            DWORD cache_index = py * G1_LAYER_DRIFT_CACHE_PITCH + px;
            DWORD screen_index = py * G1_LAYER_DRIFT_SCREEN_WIDTH + px;
            wsprintfA(body,
                "\"cache\":%u,\"lexp\":%u,\"lcov\":%u,\"scr\":%u,\"snap\":%u,\"cov\":%u,"
                "\"ev\":[%u,%u,%d,%d,%u,%u,%u,%u]",
                (DWORD)cache[cache_index], (DWORD)g_layer_expected[cache_index],
                (DWORD)g_layer_covered[cache_index],
                (DWORD)source[py * source_pitch + px],
                (DWORD)g_expected_snapshot[screen_index], (DWORD)g_covered[screen_index],
                (DWORD)event->valid, event->writer, event->origin_x, event->origin_y,
                event->width, event->height, event->present, event->result);
        }
        if (ordinal == 0u || lstrcmpA(body, g_drift_last_sample[i]) != 0) {
            lstrcpynA(g_drift_last_sample[i], body, sizeof(g_drift_last_sample[i]));
            layer_drift_emit(line, wsprintfA(line,
                "{\"t\":\"s\",\"i\":%u,\"p\":%u,\"tick\":%u,%s}\n", i, ordinal, tick, body));
        }
        g1_layer_drift_count(i, cache, g_layer_expected, g_layer_covered, source,
                             source_pitch, g_expected_snapshot, g_covered, &counts);
        wsprintfA(body,
            "\"stale\":%u,\"unc\":%u,\"sne\":%u,\"snl\":%u,\"guard\":%u,"
            "\"calls\":[%u,%u,%u,%u,%u,%u,%u],\"px\":[%u,%u,%u,%u]",
            counts.stale, counts.uncovered, counts.screen_ne_cache, counts.snap_ne_layer,
            g_drift_guard_bypass,
            g_drift_calls[i][0], g_drift_calls[i][1], g_drift_calls[i][2],
            g_drift_calls[i][3], g_drift_calls[i][4], g_drift_calls[i][5],
            g_drift_calls[i][6],
            g_drift_px[i][0], g_drift_px[i][1], g_drift_px[i][2], g_drift_px[i][3]);
        if (ordinal == 0u || lstrcmpA(body, g_drift_last_rect[i]) != 0) {
            lstrcpynA(g_drift_last_rect[i], body, sizeof(g_drift_last_rect[i]));
            layer_drift_emit(line, wsprintfA(line,
                "{\"t\":\"r\",\"i\":%u,\"p\":%u,\"tick\":%u,%s}\n", i, ordinal, tick, body));
        }
        /* H-B2: the sample changed since the previous present but no observed
         * writer hook (0x467580/0x467410/0x4676D0) changed it this present. */
        {
            DWORD scr = (DWORD)source[py * source_pitch + px];
            if (g_drift_prev_valid && scr != g_drift_prev_scr[i] && !g_drift_w_hit[i]) {
                ++g_drift_unattributed[i];
                layer_drift_emit(line, wsprintfA(line,
                    "{\"t\":\"u\",\"i\":%u,\"p\":%u,\"tick\":%u,\"prev\":%u,\"scr\":%u}\n",
                    i, ordinal, tick, g_drift_prev_scr[i], scr));
            }
            g_drift_prev_scr[i] = scr;
            g_drift_w_hit[i] = FALSE;
        }
    }
    g_drift_prev_valid = TRUE;
    if (ordinal % G1_LAYER_DRIFT_HEARTBEAT == 0u)
        layer_drift_emit(line, wsprintfA(line,
            "{\"t\":\"e\",\"p\":%u,\"tick\":%u}\n", ordinal, tick));
}

/* H-Z: the same popup keeps a companion strip outside the Blt rectangle that
 * wined3d rewrites every present.  While the first heal is active, find the
 * covered pixels whose screen value differs from the expected snapshot outside
 * the heal rectangle and re-diff their bounding box the same way (expected =
 * before, screen = after).  Before is the screen value for every pixel that is
 * not stale, so only stale pixels are mirrored.  Boxes beyond the overlay
 * limit are counted, never cut. */
static void rect_blt_heal2_at_present(const BYTE *screen, DWORD pitch, DWORD inside)
{
    G1OverlayStats stats;
    DWORD row, col, count = 0u, x0 = 0u, y0 = 0u, x1 = 0u, y1 = 0u, bw, bh;
    BOOL applied = FALSE;
    for (row = 0u; row < G1_OVERLAY_SCREEN_HEIGHT; ++row)
        for (col = 0u; col < G1_OVERLAY_SCREEN_WIDTH; ++col) {
            DWORD p = row * G1_OVERLAY_SCREEN_WIDTH + col;
            if (row >= g_rect_blt_heal_y && row < g_rect_blt_heal_y + g_rect_blt_heal_h &&
                col >= g_rect_blt_heal_x && col < g_rect_blt_heal_x + g_rect_blt_heal_w)
                continue;
            if (!g_covered[p] || g_expected_snapshot[p] == screen[row * pitch + col])
                continue;
            if (!count) { x0 = x1 = col; y0 = y1 = row; }
            else {
                if (col < x0) x0 = col;
                if (col > x1) x1 = col;
                if (row < y0) y0 = row;
                if (row > y1) y1 = row;
            }
            ++count;
        }
    if (count) {
        bw = x1 - x0 + 1u;
        bh = y1 - y0 + 1u;
        if (bw <= G1_OVERLAY_MAX_WIDTH && bh <= G1_OVERLAY_MAX_HEIGHT) {
            for (row = 0u; row < bh; ++row)
                for (col = 0u; col < bw; ++col) {
                    DWORD p = (y0 + row) * G1_OVERLAY_SCREEN_WIDTH + x0 + col;
                    BYTE value = screen[(y0 + row) * pitch + x0 + col];
                    g_rect_blt_before[row * bw + col] =
                        g_covered[p] && g_expected_snapshot[p] != value ?
                        g_expected_snapshot[p] : value;
                }
            if (g1_overlay_blt_apply(g_rect_blt_before, screen, pitch, x0, y0, bw, bh,
                                     lstrcmpA(g1_hd_asset_source_name(), "scale2x") == 0,
                                     g_overlay_scratch, g_expected_snapshot, g_covered,
                                     g_mirror, 1600u, &stats)) {
                ++g_rect_blt_heal2_presents;
                g_rect_blt_heal2_pixels += (DWORD)stats.changed;
                applied = TRUE;
            } else {
                ++g_rect_blt_heal2_skipped;
            }
        } else {
            ++g_rect_blt_heal2_skipped;
        }
    }
    if (count && layer_drift_on()) {
        char line[240];
        layer_drift_emit(line, wsprintfA(line,
            "{\"t\":\"z\",\"p\":%u,\"in\":%u,\"out\":%u,\"x\":%u,\"y\":%u,\"w\":%u,\"h\":%u,\"hx\":%u,\"hy\":%u,\"hw\":%u,\"hh\":%u,\"ok\":%u}\n",
            (unsigned)g_drift_present, (unsigned)inside, (unsigned)count,
            (unsigned)x0, (unsigned)y0, (unsigned)(x1 - x0 + 1u),
            (unsigned)(y1 - y0 + 1u), (unsigned)g_rect_blt_heal_x,
            (unsigned)g_rect_blt_heal_y, (unsigned)g_rect_blt_heal_w,
            (unsigned)g_rect_blt_heal_h, (unsigned)applied));
    }
}

/* H-PS5W1: BltFast wrapper for the flip-chain back buffer's own (uncloned) vtable.  It does
 * not touch the surface: the destination rectangle is queued and diffed against the expected
 * frame at the next present, when the source is already locked and wined3d has finished the
 * blits.  The original always runs exactly once. */
static HRESULT WINAPI mirror_scratch_blt_fast(LPDIRECTDRAWSURFACE7 self, DWORD x, DWORD y,
                                              LPDIRECTDRAWSURFACE7 source, LPRECT src,
                                              DWORD flags)
{
    DWORD return_address = (DWORD)(ULONG_PTR)__builtin_return_address(0);
    G1ScratchRect rect;
    ++g_scratch_calls;
    ++g_scratch_site_calls[g1_scratch_bltfast_site_index(return_address)];
    if (g_scratch_bltfast_enabled && !g_primitive_guard && g_mirror && g_covered &&
        g_expected_snapshot &&
        g1_scratch_bltfast_state_accepts(read_game_dword(G1_PROGRAM_STATE_VA)) &&
        g1_scratch_bltfast_rect(x, y, src != NULL, src ? src->left : 0, src ? src->top : 0,
                                src ? src->right : 0, src ? src->bottom : 0, &rect) &&
        g1_scratch_queue_push(&g_scratch_queue, &rect))
        ++g_scratch_recorded;
    else
        ++g_scratch_rejects;
    return g_scratch_original_blt_fast(self, x, y, source, src, flags);
}

/* Called from the primary present with its source.  A back buffer the DirectDraw trace
 * already cloned (has_record) keeps the trace hook; any other back buffer gets its own
 * vtable clone whose BltFast is the wrapper above.  Re-adopts when the object (or its
 * vtable) changed. */
void g1_mirror2x_scratch_bltfast_adopt(LPDIRECTDRAWSURFACE7 back, BOOL has_record)
{
    IDirectDrawSurface7Vtbl *original;
    if (!g_scratch_bltfast_enabled || !back || back != (LPDIRECTDRAWSURFACE7)(ULONG_PTR)
            read_game_dword(G1_BACK_BUFFER_VA))
        return;
    if (has_record) {
        ++g_scratch_adopt_skipped_record;
        return;
    }
    if (back == g_scratch_surface && back->lpVtbl == g_scratch_clone) return;
    original = back->lpVtbl;
    g_scratch_clone = (IDirectDrawSurface7Vtbl *)HeapAlloc(
        GetProcessHeap(), HEAP_ZERO_MEMORY, sizeof(IDirectDrawSurface7Vtbl));
    if (!g_scratch_clone) return;
    *g_scratch_clone = *original;
    g_scratch_original_blt_fast = (G1ScratchBltFastFn)original->BltFast;
    g_scratch_clone->BltFast = mirror_scratch_blt_fast;
    g_scratch_surface = back;
    back->lpVtbl = g_scratch_clone;
    g1_scratch_queue_reset(&g_scratch_queue);
    ++g_scratch_adopts;
}

/* Present-time half of the wrapper: the queued rectangles are the "after" regions, the
 * expected snapshot the "before"; only pixels that differ reach the HD mirror (the same
 * contract as rect_blt_heal_at_present).  screen is the locked back buffer (stride pitch). */
static void scratch_bltfast_at_present(const BYTE *screen, DWORD pitch)
{
    DWORD index;
    BOOL state_ok = g1_scratch_bltfast_state_accepts(read_game_dword(G1_PROGRAM_STATE_VA));
    if (!g_scratch_queue.count) return;
    if (!state_ok || !g_mirror || !g_covered || !g_expected_snapshot || !screen ||
        pitch < G1_OVERLAY_SCREEN_WIDTH) {
        g1_scratch_queue_reset(&g_scratch_queue);
        return;
    }
    for (index = 0u; index < g_scratch_queue.count; ++index) {
        const G1ScratchRect *rect = &g_scratch_queue.rects[index];
        G1OverlayStats stats;
        size_t tiles = 0u;
        DWORD row, col;
        for (row = 0u; row < (DWORD)rect->h; ++row)
            for (col = 0u; col < (DWORD)rect->w; ++col)
                g_scratch_before[row * (DWORD)rect->w + col] = g_expected_snapshot[
                    ((DWORD)rect->y + row) * G1_OVERLAY_SCREEN_WIDTH + (DWORD)rect->x + col];
        if (g1_overlay_blt_apply_tiled(
                g_scratch_before, screen, pitch, (size_t)rect->x, (size_t)rect->y,
                (size_t)rect->w, (size_t)rect->h,
                lstrcmpA(g1_hd_asset_source_name(), "scale2x") == 0, g_overlay_scratch,
                g_scratch_tile, g_expected_snapshot, g_covered, g_mirror, 1600u, &stats,
                &tiles)) {
            ++g_scratch_flush_applied;
            g_scratch_flush_pixels += (DWORD)stats.changed;
        } else {
            ++g_scratch_rejects;
        }
    }
    g1_scratch_queue_reset(&g_scratch_queue);
}

/* H-A2: wined3d re-syncs the Blt'd region of the back buffer from its texture
 * on every present while the popup is shown (EIP in wined3d.dll, once per
 * present), after the game's own cache copy.  The cache-copy hook has already
 * put the layer value back into the expected snapshot, so re-diff the last
 * mirrored Blt rectangle against the screen at present time.  Expected is
 * the "before", the screen the "after"; only changed pixels are mirrored.
 * Stops after three presents without a difference. */
static void rect_blt_heal_at_present(const BYTE *screen, DWORD pitch)
{
    G1OverlayStats stats;
    DWORD row, col;
    if (!g_rect_blt_heal_active) return;
    if (!g_mirror || !g_covered || !g_expected_snapshot || !screen ||
        pitch < G1_OVERLAY_SCREEN_WIDTH ||
        read_game_dword(G1_PROGRAM_STATE_VA) != 3u) {
        g_rect_blt_heal_active = FALSE;
        return;
    }
    for (row = 0u; row < g_rect_blt_heal_h; ++row)
        for (col = 0u; col < g_rect_blt_heal_w; ++col)
            g_rect_blt_before[row * g_rect_blt_heal_w + col] = g_expected_snapshot[
                (g_rect_blt_heal_y + row) * G1_OVERLAY_SCREEN_WIDTH +
                g_rect_blt_heal_x + col];
    if (!g1_overlay_blt_apply(g_rect_blt_before, screen, pitch, g_rect_blt_heal_x,
                              g_rect_blt_heal_y, g_rect_blt_heal_w, g_rect_blt_heal_h,
                              lstrcmpA(g1_hd_asset_source_name(), "scale2x") == 0,
                              g_overlay_scratch, g_expected_snapshot, g_covered,
                              g_mirror, 1600u, &stats)) {
        g_rect_blt_heal_active = FALSE;
        return;
    }
    ++g_rect_blt_heal_presents;
    g_rect_blt_heal_pixels += (DWORD)stats.changed;
    if (stats.changed) g_rect_blt_heal_quiet = 0u;
    else if (++g_rect_blt_heal_quiet >= 3u) g_rect_blt_heal_active = FALSE;
    rect_blt_heal2_at_present(screen, pitch, (DWORD)stats.changed);
}

HRESULT g1_mirror2x_copy_present(LPDIRECTDRAWSURFACE7 primary,
                                  LPDIRECTDRAWSURFACE7 source,
                                  const RECT *source_rect,
                                  const RECT *destination_rect)
{
    DDSURFACEDESC2 source_desc;
    DDSURFACEDESC2 destination_desc;
    RECT source_lock, destination_lock;
    HRESULT source_hr, destination_hr, unlock_hr;
    DWORD width, height, y, x, covered_now = 0u, stale_now = 0u;
    DWORD nearest_matches = 0u, nearest_total = 0u;
    DWORD inside_diff_now = 0u, outside_diff_now = 0u;
    DWORD started;
    HRESULT final_hr;
    DWORD program_state = 0u, mask_ordinal = 0u;
    DWORD pause_state = 0u, pause_restore_now = 0u;
    int pause_action = G1_PAUSE_ACTION_NONE;
    BOOL pause_restore_on = FALSE;
    BYTE *mask_dump = NULL;
    started = GetTickCount();
    if (g_stale_mask_spec.count != 0u) {
        program_state = read_game_dword(G1_PROGRAM_STATE_VA);
        if (program_state == g_stale_mask_state) {
            mask_ordinal = g_stale_mask_ordinal++;
            if (g1_stale_mask_selected(&g_stale_mask_spec, mask_ordinal) &&
                g_stale_mask_dumps < G1_STALE_MASK_DUMP_LIMIT) {
                if (!g_stale_mask_buffer)
                    g_stale_mask_buffer = (BYTE *)HeapAlloc(GetProcessHeap(), 0,
                                                            G1_STALE_MASK_PIXELS);
                mask_dump = g_stale_mask_buffer;
            }
        }
    }
    ZeroMemory(&g_last_present, sizeof(g_last_present));
    g_last_present.attempted = TRUE;
    if (!primary || !source || !source_rect || !destination_rect || !g_mirror || !g_covered)
        return DDERR_INVALIDPARAMS;
    width = (DWORD)(source_rect->right - source_rect->left);
    height = (DWORD)(source_rect->bottom - source_rect->top);
    g_last_present.source_width = width;
    g_last_present.source_height = height;
    g_last_present.destination_width = (DWORD)(destination_rect->right - destination_rect->left);
    g_last_present.destination_height = (DWORD)(destination_rect->bottom - destination_rect->top);
    if (width != 800u || height != 600u) return DDERR_INVALIDPARAMS;
    source_lock = *source_rect;
    destination_lock = *destination_rect;
    zero_bytes(&source_desc, sizeof(source_desc));
    zero_bytes(&destination_desc, sizeof(destination_desc));
    source_desc.dwSize = sizeof(source_desc);
    destination_desc.dwSize = sizeof(destination_desc);
    source_hr = source->lpVtbl->Lock(source, &source_lock, &source_desc,
                                     DDLOCK_WAIT | DDLOCK_READONLY, NULL);
    if (FAILED(source_hr)) return source_hr;
    destination_hr = primary->lpVtbl->Lock(primary, &destination_lock,
                                           &destination_desc, DDLOCK_WAIT, NULL);
    if (FAILED(destination_hr)) {
        source->lpVtbl->Unlock(source, source_desc.lpSurface);
        return destination_hr;
    }
    if (source_desc.lPitch <= 0 || destination_desc.lPitch <= 0 ||
        (DWORD)source_desc.lPitch < width ||
        (DWORD)destination_desc.lPitch < width * 2u) {
        primary->lpVtbl->Unlock(primary, destination_desc.lpSurface);
        source->lpVtbl->Unlock(source, source_desc.lpSurface);
        return DDERR_INVALIDPARAMS;
    }
    g_last_present_screen = (DWORD)(ULONG_PTR)source_desc.lpSurface;
    rect_blt_heal_at_present((const BYTE *)source_desc.lpSurface,
                             (DWORD)source_desc.lPitch);
    scratch_bltfast_at_present((const BYTE *)source_desc.lpSurface,
                               (DWORD)source_desc.lPitch);
    layer_drift_present((const BYTE *)source_desc.lpSurface,
                        (DWORD)source_desc.lPitch);
    g1_screen_watch_on_present((const BYTE *)source_desc.lpSurface,
                               (DWORD)source_desc.lPitch, g_drift_present);
    s3_overlay_at_present((const BYTE *)source_desc.lpSurface,
                          (DWORD)source_desc.lPitch);
    g_last_present.source_stride = (DWORD)source_desc.lPitch;
    g_last_present.destination_stride = (DWORD)destination_desc.lPitch;
    if (g_pause_snapshot_enabled) {
        pause_state = read_game_dword(G1_PROGRAM_STATE_VA);
        pause_action = g1_pause_snapshot_action(g_pause_state_prev, pause_state);
        g_pause_state_prev = pause_state;
        if (pause_action != G1_PAUSE_ACTION_NONE) {
            zero_bytes(g_pause_valid, 800u * 600u);
            g_pause_snapshot_pixels = 0u;
        }
        pause_restore_on = g1_pause_restore_active(pause_state,
                                                   g_pause_snapshot_pixels != 0u);
    }
    g_last_frame_valid = FALSE;
    for (y = 0; y < height; ++y) {
        const BYTE *source_row = (const BYTE *)source_desc.lpSurface +
                                 y * source_desc.lPitch;
        BYTE *destination_row = (BYTE *)destination_desc.lpSurface +
                                y * 2u * destination_desc.lPitch;
        if (g_primary_readback_enabled && g_last_frame)
            panel_copy_bytes(g_last_frame + y * 800u, source_row, 800u);
        for (x = 0; x < width; ++x) {
            DWORD p = y * 800u + x;
            BYTE pixel = source_row[x];
            BYTE top_left = pixel, top_right = pixel;
            BYTE bottom_left = pixel, bottom_right = pixel;
            BOOL hd_asset = g_covered[p] && g_expected_snapshot[p] == pixel;
            if (mask_dump)
                mask_dump[p] = g1_stale_mask_value(g_covered[p] != 0u,
                                                   g_expected_snapshot[p] == pixel);
            if (pause_restore_on && !hd_asset &&
                g1_pause_restore_pick(g_covered[p] != 0u, g_expected_snapshot[p], pixel,
                                      g_pause_valid[p] != 0u, g_pause_expected[p]) ==
                    G1_PAUSE_PICK_RESTORE) {
                BYTE *mirror_pixel = g_mirror + y * 2u * 1600u + x * 2u;
                const BYTE *snapshot_pixel = g_pause_hd + y * 2u * 1600u + x * 2u;
                g_covered[p] = 1u;
                g_expected_snapshot[p] = pixel;
                mirror_pixel[0] = snapshot_pixel[0];
                mirror_pixel[1] = snapshot_pixel[1];
                mirror_pixel[1600u] = snapshot_pixel[1600u];
                mirror_pixel[1601u] = snapshot_pixel[1601u];
                hd_asset = TRUE;
                ++pause_restore_now;
            }
            if (g_covered[p]) {
                ++covered_now;
                if (g_expected_snapshot[p] == pixel) {
                    BYTE *mirror_pixel = g_mirror + y * 2u * 1600u + x * 2u;
                    top_left = mirror_pixel[0];
                    top_right = mirror_pixel[1];
                    bottom_left = mirror_pixel[1600u];
                    bottom_right = mirror_pixel[1601u];
                    if (pause_action == G1_PAUSE_ACTION_CAPTURE) {
                        g_pause_valid[p] = 1u;
                        g_pause_expected[p] = pixel;
                        g_pause_hd[y * 2u * 1600u + x * 2u] = top_left;
                        g_pause_hd[y * 2u * 1600u + x * 2u + 1u] = top_right;
                        g_pause_hd[(y * 2u + 1u) * 1600u + x * 2u] = bottom_left;
                        g_pause_hd[(y * 2u + 1u) * 1600u + x * 2u + 1u] = bottom_right;
                        ++g_pause_snapshot_pixels;
                    }
                } else {
                    ++stale_now;
                    ++g_stale_pixels;
                    /* A camera/scroll mutation invalidates only this cached
                     * logical pixel; leave unrelated asset keys live. */
                    g_covered[p] = 0u;
                }
            }
            destination_row[x * 2u] = top_left;
            destination_row[x * 2u + 1u] = top_right;
            destination_row[destination_desc.lPitch + x * 2u] = bottom_left;
            destination_row[destination_desc.lPitch + x * 2u + 1u] = bottom_right;
            if (hd_asset) {
                if (top_left != pixel) ++inside_diff_now;
                if (top_right != pixel) ++inside_diff_now;
                if (bottom_left != pixel) ++inside_diff_now;
                if (bottom_right != pixel) ++inside_diff_now;
            } else {
                if (top_left != pixel) ++outside_diff_now;
                if (top_right != pixel) ++outside_diff_now;
                if (bottom_left != pixel) ++outside_diff_now;
                if (bottom_right != pixel) ++outside_diff_now;
            }
        }
    }
    s3_overlay_destination((const BYTE *)source_desc.lpSurface,
                           (DWORD)source_desc.lPitch,
                           (BYTE *)destination_desc.lpSurface,
                           (DWORD)destination_desc.lPitch);
    g_last_present.source_hash = hash_visible_rows(source_desc.lpSurface,
                                                   (DWORD)source_desc.lPitch,
                                                   width, height);
    g_last_present.destination_hash = hash_visible_rows(destination_desc.lpSurface,
                                                        (DWORD)destination_desc.lPitch,
                                                        width * 2u, height * 2u);
    g_last_frame_source_hash = g_last_present.source_hash;
    g_last_frame_valid = g_primary_readback_enabled && g_last_frame != NULL;
    dump_first_row(source_desc.lpSurface, (DWORD)source_desc.lPitch, width,
                   g_last_present.source_dump);
    dump_first_row(destination_desc.lpSurface, (DWORD)destination_desc.lPitch,
                   width * 2u, g_last_present.destination_dump);
    for (y = 0; y < height; ++y) {
        const BYTE *source_row = (const BYTE *)source_desc.lpSurface +
                                 y * source_desc.lPitch;
        const BYTE *destination_row = (const BYTE *)destination_desc.lpSurface +
                                      y * 2u * destination_desc.lPitch;
        for (x = 0; x < width; ++x) {
            BYTE expected = source_row[x];
            if (destination_row[x * 2u] == expected &&
                destination_row[x * 2u + 1u] == expected &&
                destination_row[destination_desc.lPitch + x * 2u] == expected &&
                destination_row[destination_desc.lPitch + x * 2u + 1u] == expected)
                nearest_matches += 4u;
            nearest_total += 4u;
        }
    }
    unlock_hr = primary->lpVtbl->Unlock(primary, destination_desc.lpSurface);
    source->lpVtbl->Unlock(source, source_desc.lpSurface);
    final_hr = unlock_hr;
    g_last_present.covered_pixels = covered_now;
    g_last_present.stale_pixels = stale_now;
    g_last_present.pause_snapshot_pixels = g_pause_snapshot_pixels;
    g_last_present.pause_restore_pixels = pause_restore_now;
    g_pause_restore_total += pause_restore_now;
    if (mask_dump) {
        DWORD mask_header[8];
        g1_stale_mask_header(mask_header, mask_ordinal, program_state,
                             read_game_dword(G1_GAME_TICK_VA), g_present_count,
                             covered_now, stale_now);
        stale_mask_write(mask_header, mask_dump);
        ++g_stale_mask_dumps;
    }
    g_last_present.nearest_matches = nearest_matches;
    g_last_present.nearest_total = nearest_total;
    g_last_present.hd_mask_inside_diff_subpixels = inside_diff_now;
    g_last_present.hd_mask_outside_diff_subpixels = outside_diff_now;
    g_last_present.elapsed_ms = elapsed_ms(started);
    g_last_present.primitive_reinvoke_elapsed_ms_total =
        g_primitive_reinvoke_elapsed_ms_total;
    g_last_present.primitive_reinvoke_elapsed_ms_max =
        g_primitive_reinvoke_elapsed_ms_max;
    g_last_present.primitive_reinvoke_count = g_primitive_reinvoke_count;
    g_last_present.identity_pixels = g1_hd_asset_identity_pixels();
    g_last_present.identity_keys = g1_hd_asset_identity_keys();
    g_last_present.identity_invalid_sources = g1_hd_asset_identity_invalid_sources();
    g_last_present.identity_events = g1_hd_asset_identity_events();
    g_last_present.identity_lookup_hits = g1_hd_asset_identity_lookup_hits();
    g_last_present.identity_lookup_misses = g1_hd_asset_identity_lookup_misses();
    g_last_present.identity_cache_inserts = g1_hd_asset_identity_cache_inserts();
    g_last_present.identity_cache_hits = g1_hd_asset_identity_cache_hits();
    g_last_present.identity_cache_misses = g1_hd_asset_identity_cache_misses();
    g_last_present.identity_cache_refreshes = g1_hd_asset_identity_cache_refreshes();
    g_last_present.identity_negative_lookup_attempts =
        g1_hd_asset_identity_negative_lookup_attempts();
    g_last_present.identity_negative_lookup_misses =
        g1_hd_asset_identity_negative_lookup_misses();
    g_last_present.identity_key_mismatches = g1_hd_asset_identity_key_mismatches();
    g_last_present.scale2x_blocks = g1_hd_asset_scale2x_blocks();
    g_last_present.scale2x_subpixel_differences =
        g1_hd_asset_scale2x_subpixel_differences();
    g_last_present.scale2x_palette_violations =
        g1_hd_asset_scale2x_palette_violations();
    g_last_present.success = SUCCEEDED(final_hr);
    if (g_last_present.success) ++g_present_count;
    return FAILED(final_hr) ? final_hr : DD_OK;
}

void g1_mirror2x_panel_transfer(LPDIRECTDRAWSURFACE7 destination,
                               LPDIRECTDRAWSURFACE7 source, DWORD x, DWORD y,
                               const RECT *source_rect, HRESULT result,
                               BOOL destination_is_primary)
{
    LPDIRECTDRAWSURFACE7 panel_surface;
    DDSURFACEDESC2 desc;
    RECT rect;
    HRESULT lock_result;
    G1PanelTransferStats stats;
    DWORD width, height;
    if (!source || !destination || FAILED(result) || destination_is_primary) return;
    panel_surface = *(LPDIRECTDRAWSURFACE7 *)(ULONG_PTR)G1_PANEL_SURFACE_GLOBAL;
    if (!panel_surface || source != panel_surface) return;
    if (!g_panel_bound_buffer || !g_panel_frame_height) {
        ++g_panel_unbound_transfer_count;
        return;
    }
    ZeroMemory(&desc, sizeof(desc));
    desc.dwSize = sizeof(desc);
    lock_result = source->lpVtbl->Lock(source, NULL, &desc,
                                       DDLOCK_WAIT | DDLOCK_READONLY, NULL);
    if (FAILED(lock_result)) {
        ++g_panel_lock_failures;
        ++g_panel_unbound_transfer_count;
        return;
    }
    if (!desc.lpSurface || desc.lPitch <= 0 ||
        !g1_panel_binding_matches((uintptr_t)g_panel_bound_buffer,
                                  g_panel_bound_pitch,
                                  (uintptr_t)desc.lpSurface,
                                  (size_t)desc.lPitch)) {
        if (!desc.lpSurface || (BYTE *)desc.lpSurface != g_panel_bound_buffer)
            ++g_panel_pointer_mismatches;
        if (desc.lPitch <= 0 || (DWORD)desc.lPitch != g_panel_bound_pitch)
            ++g_panel_pitch_mismatches;
        ++g_panel_unbound_transfer_count;
        source->lpVtbl->Unlock(source, desc.lpSurface);
        return;
    }
    ++g_panel_bound_transfer_count;
    rect = source_rect ? *source_rect : (RECT){0, 0, (LONG)desc.dwWidth,
                                                (LONG)desc.dwHeight};
    if (rect.left < 0 || rect.top < 0 || rect.right <= rect.left ||
        rect.bottom <= rect.top) {
        source->lpVtbl->Unlock(source, desc.lpSurface);
        return;
    }
    width = (DWORD)(rect.right - rect.left);
    height = (DWORD)(rect.bottom - rect.top);
    if (width > G1_PANEL_WIDTH || height > G1_PANEL_MAX_HEIGHT ||
        x > 800u || y > 600u || width > 800u - x || height > 600u - y) {
        source->lpVtbl->Unlock(source, desc.lpSurface);
        return;
    }
    if (g1_panel_apply_transfer(g_panel_expected, g_panel_covered, g_panel_mirror,
                                G1_PANEL_WIDTH, G1_PANEL_HD_STRIDE,
                                (const BYTE *)desc.lpSurface, (DWORD)desc.lPitch,
                                (DWORD)rect.left, (DWORD)rect.top, x, y,
                                width, height, g_expected_snapshot, g_covered,
                                g_mirror, 800u, 1600u, 800u, 600u, &stats)) {
        g_panel_transfer_copied += stats.copied;
        g_panel_transfer_key_preserved += stats.key_preserved;
        g_panel_transfer_mismatch_cleared += stats.mismatch_cleared;
    }
    source->lpVtbl->Unlock(source, desc.lpSurface);
}

BOOL g1_mirror2x_overlay_blt_begin(G1OverlayBlt *overlay,
                                   LPDIRECTDRAWSURFACE7 destination,
                                   LPDIRECTDRAWSURFACE7 source, DWORD x, DWORD y,
                                   const RECT *source_rect, DWORD flags,
                                   BOOL destination_is_primary)
{
    LPDIRECTDRAWSURFACE7 panel_surface;
    DDSURFACEDESC2 desc;
    DWORD width, height, row;
    if (!overlay) return FALSE;
    overlay->active = FALSE;
    if (!source || !destination || !g_mirror || !g_covered || !g_expected_snapshot ||
        !source_rect || source_rect->right <= source_rect->left ||
        source_rect->bottom <= source_rect->top) return FALSE;
    panel_surface = *(LPDIRECTDRAWSURFACE7 *)(ULONG_PTR)G1_PANEL_SURFACE_GLOBAL;
    width = (DWORD)(source_rect->right - source_rect->left);
    height = (DWORD)(source_rect->bottom - source_rect->top);
    ZeroMemory(&desc, sizeof(desc));
    desc.dwSize = sizeof(desc);
    if (FAILED(destination->lpVtbl->Lock(destination, NULL, &desc,
                                         DDLOCK_WAIT | DDLOCK_READONLY, NULL)))
        return FALSE;
    if (!desc.lpSurface || desc.lPitch <= 0 ||
        !g1_overlay_blt_accepts(destination_is_primary, source == panel_surface,
                                (flags & DDBLTFAST_SRCCOLORKEY) != 0u, 1,
                                desc.dwWidth, desc.dwHeight, x, y, width, height) ||
        (DWORD)desc.lPitch < 800u) {
        ++g_overlay_blt_rejects;
        destination->lpVtbl->Unlock(destination, desc.lpSurface);
        return FALSE;
    }
    for (row = 0u; row < height; ++row) {
        const BYTE *line = (const BYTE *)desc.lpSurface + (y + row) * desc.lPitch + x;
        DWORD col;
        for (col = 0u; col < width; ++col) g_overlay_before[row * width + col] = line[col];
    }
    destination->lpVtbl->Unlock(destination, desc.lpSurface);
    overlay->x = x; overlay->y = y; overlay->width = width; overlay->height = height;
    overlay->active = TRUE;
    return TRUE;
}

void g1_mirror2x_overlay_blt_end(G1OverlayBlt *overlay,
                                 LPDIRECTDRAWSURFACE7 destination, HRESULT result)
{
    DDSURFACEDESC2 desc;
    G1OverlayStats stats;
    if (!overlay || !overlay->active) return;
    overlay->active = FALSE;
    if (FAILED(result)) return;
    ZeroMemory(&desc, sizeof(desc));
    desc.dwSize = sizeof(desc);
    if (FAILED(destination->lpVtbl->Lock(destination, NULL, &desc,
                                         DDLOCK_WAIT | DDLOCK_READONLY, NULL))) {
        ++g_overlay_blt_rejects;
        return;
    }
    if (desc.lpSurface && desc.lPitch >= 800 &&
        g1_overlay_blt_apply(g_overlay_before, (const BYTE *)desc.lpSurface,
                             (DWORD)desc.lPitch, overlay->x, overlay->y,
                             overlay->width, overlay->height,
                             lstrcmpA(g1_hd_asset_source_name(), "scale2x") == 0,
                             g_overlay_scratch, g_expected_snapshot, g_covered,
                             g_mirror, 1600u, &stats)) {
        ++g_overlay_blt_mirrored_calls;
        g_overlay_blt_mirrored_pixels += (DWORD)stats.changed;
    } else {
        ++g_overlay_blt_rejects;
    }
    destination->lpVtbl->Unlock(destination, desc.lpSurface);
}

/* H-A: back buffer IDirectDrawSurface7::Blt (DDBLT_KEYSRC stretch included).
 * Same before/after diff as the BltFast overlay but keyed on the destination
 * rectangle; every pixel the original Blt changes is mirrored, so flags and
 * stretch need no emulation.  NULL dst (whole surface), a rectangle past the
 * overlay limit, a non-screen or cache/panel target are counted and skipped. */
BOOL g1_mirror2x_overlay_rect_blt_begin(G1OverlayBlt *overlay,
                                        LPDIRECTDRAWSURFACE7 destination,
                                        const RECT *destination_rect, DWORD flags,
                                        DWORD surface_width, DWORD surface_height)
{
    DDSURFACEDESC2 desc;
    LONG x0, y0, x1, y1;
    DWORD width, height, row, col;
    if (!overlay) return FALSE;
    overlay->active = FALSE;
    if (!destination || !g_mirror || !g_covered || !g_expected_snapshot) return FALSE;
    ++g_rect_blt_invocations;
    if (flags & DDBLT_KEYSRC) ++g_rect_blt_keysrc_calls;
    if (flags & DDBLT_COLORFILL) ++g_rect_blt_colorfill_calls;
    if (surface_width < G1_OVERLAY_SCREEN_WIDTH ||
        surface_height != G1_OVERLAY_SCREEN_HEIGHT) {
        ++g_rect_blt_reject_target;
        return FALSE;
    }
    if (!destination_rect) {
        ++g_rect_blt_reject_size;
        return FALSE;
    }
    x0 = destination_rect->left < 0 ? 0 : destination_rect->left;
    y0 = destination_rect->top < 0 ? 0 : destination_rect->top;
    x1 = destination_rect->right > (LONG)G1_OVERLAY_SCREEN_WIDTH
             ? (LONG)G1_OVERLAY_SCREEN_WIDTH : destination_rect->right;
    y1 = destination_rect->bottom > (LONG)G1_OVERLAY_SCREEN_HEIGHT
             ? (LONG)G1_OVERLAY_SCREEN_HEIGHT : destination_rect->bottom;
    if (x0 >= x1 || y0 >= y1) {
        ++g_rect_blt_reject_bounds;
        return FALSE;
    }
    width = (DWORD)(x1 - x0);
    height = (DWORD)(y1 - y0);
    if (width > G1_OVERLAY_MAX_WIDTH || height > G1_OVERLAY_MAX_HEIGHT) {
        ++g_rect_blt_reject_size;
        return FALSE;
    }
    ZeroMemory(&desc, sizeof(desc));
    desc.dwSize = sizeof(desc);
    if (FAILED(destination->lpVtbl->Lock(destination, NULL, &desc,
                                         DDLOCK_WAIT | DDLOCK_READONLY, NULL))) {
        ++g_rect_blt_reject_lock;
        return FALSE;
    }
    if (!desc.lpSurface || desc.lPitch < (LONG)G1_OVERLAY_SCREEN_WIDTH ||
        desc.dwWidth < G1_OVERLAY_SCREEN_WIDTH ||
        desc.dwHeight != G1_OVERLAY_SCREEN_HEIGHT ||
        (DWORD)(ULONG_PTR)desc.lpSurface == G1_CACHE_BASE ||
        (BYTE *)desc.lpSurface == g_panel_bound_buffer) {
        ++g_rect_blt_reject_target;
        destination->lpVtbl->Unlock(destination, desc.lpSurface);
        return FALSE;
    }
    if (x0 != destination_rect->left || y0 != destination_rect->top ||
        x1 != destination_rect->right || y1 != destination_rect->bottom)
        ++g_rect_blt_clipped_calls;
    for (row = 0u; row < height; ++row) {
        const BYTE *line = (const BYTE *)desc.lpSurface + (DWORD)(y0 + (LONG)row) * desc.lPitch + x0;
        for (col = 0u; col < width; ++col) g_rect_blt_before[row * width + col] = line[col];
    }
    destination->lpVtbl->Unlock(destination, desc.lpSurface);
    overlay->x = (DWORD)x0; overlay->y = (DWORD)y0;
    overlay->width = width; overlay->height = height;
    overlay->active = TRUE;
    return TRUE;
}

void g1_mirror2x_overlay_rect_blt_end(G1OverlayBlt *overlay,
                                      LPDIRECTDRAWSURFACE7 destination, HRESULT result)
{
    DDSURFACEDESC2 desc;
    G1OverlayStats stats;
    if (!overlay || !overlay->active) return;
    overlay->active = FALSE;
    if (FAILED(result)) {
        ++g_rect_blt_reject_result;
        return;
    }
    ZeroMemory(&desc, sizeof(desc));
    desc.dwSize = sizeof(desc);
    if (FAILED(destination->lpVtbl->Lock(destination, NULL, &desc,
                                         DDLOCK_WAIT | DDLOCK_READONLY, NULL))) {
        ++g_rect_blt_reject_lock;
        return;
    }
    if (desc.lpSurface && desc.lPitch >= (LONG)G1_OVERLAY_SCREEN_WIDTH &&
        g1_overlay_blt_apply(g_rect_blt_before, (const BYTE *)desc.lpSurface,
                             (DWORD)desc.lPitch, overlay->x, overlay->y,
                             overlay->width, overlay->height,
                             lstrcmpA(g1_hd_asset_source_name(), "scale2x") == 0,
                             g_overlay_scratch, g_expected_snapshot, g_covered,
                             g_mirror, 1600u, &stats)) {
        ++g_rect_blt_mirrored_calls;
        g_rect_blt_mirrored_pixels += (DWORD)stats.changed;
        if (stats.changed) {
            ++g_rect_blt_changed_calls;
            g_rect_blt_heal_x = overlay->x; g_rect_blt_heal_y = overlay->y;
            g_rect_blt_heal_w = overlay->width; g_rect_blt_heal_h = overlay->height;
            g_rect_blt_heal_quiet = 0u;
            g_rect_blt_heal_active = TRUE;
        }
        if (layer_drift_on()) {
            char line[200];
            unsigned px, py;
            DWORD bf = G1_DRIFT_UNREAD, af = G1_DRIFT_UNREAD, ex = G1_DRIFT_UNREAD;
            g1_layer_drift_sample(0u, &px, &py);
            if (px >= overlay->x && px < overlay->x + overlay->width &&
                py >= overlay->y && py < overlay->y + overlay->height) {
                bf = g_rect_blt_before[(py - overlay->y) * overlay->width + (px - overlay->x)];
                af = ((const BYTE *)desc.lpSurface)[py * (DWORD)desc.lPitch + px];
                ex = g_expected_snapshot[py * G1_OVERLAY_SCREEN_WIDTH + px];
            }
            layer_drift_emit(line, wsprintfA(line,
                "{\"t\":\"b\",\"p\":%u,\"x\":%u,\"y\":%u,\"w\":%u,\"h\":%u,\"ch\":%u,\"bf\":%u,\"af\":%u,\"ex\":%u}\n",
                g_drift_present, (unsigned)overlay->x, (unsigned)overlay->y,
                (unsigned)overlay->width, (unsigned)overlay->height, (unsigned)stats.changed,
                (unsigned)bf, (unsigned)af, (unsigned)ex));
        }
    } else {
        ++g_rect_blt_reject_size;
    }
    destination->lpVtbl->Unlock(destination, desc.lpSurface);
}

DWORD g1_mirror2x_overlay_blt_mirrored_calls(void) { return g_overlay_blt_mirrored_calls; }
DWORD g1_mirror2x_overlay_blt_mirrored_pixels(void) { return g_overlay_blt_mirrored_pixels; }
DWORD g1_mirror2x_overlay_blt_rejects(void) { return g_overlay_blt_rejects; }
DWORD g1_mirror2x_overlay_rect_blt_invocations(void) { return g_rect_blt_invocations; }
DWORD g1_mirror2x_overlay_rect_blt_mirrored_calls(void) { return g_rect_blt_mirrored_calls; }
DWORD g1_mirror2x_overlay_rect_blt_mirrored_pixels(void) { return g_rect_blt_mirrored_pixels; }
DWORD g1_mirror2x_overlay_rect_blt_changed_calls(void) { return g_rect_blt_changed_calls; }
DWORD g1_mirror2x_overlay_rect_blt_clipped_calls(void) { return g_rect_blt_clipped_calls; }
DWORD g1_mirror2x_overlay_rect_blt_keysrc_calls(void) { return g_rect_blt_keysrc_calls; }
DWORD g1_mirror2x_overlay_rect_blt_colorfill_calls(void) { return g_rect_blt_colorfill_calls; }
DWORD g1_mirror2x_overlay_rect_blt_reject_bounds(void) { return g_rect_blt_reject_bounds; }
DWORD g1_mirror2x_overlay_rect_blt_reject_size(void) { return g_rect_blt_reject_size; }
DWORD g1_mirror2x_overlay_rect_blt_reject_lock(void) { return g_rect_blt_reject_lock; }
DWORD g1_mirror2x_overlay_rect_blt_reject_target(void) { return g_rect_blt_reject_target; }
DWORD g1_mirror2x_overlay_rect_blt_reject_result(void) { return g_rect_blt_reject_result; }
DWORD g1_mirror2x_overlay_rect_blt_heal_presents(void) { return g_rect_blt_heal_presents; }
DWORD g1_mirror2x_overlay_rect_blt_heal_pixels(void) { return g_rect_blt_heal_pixels; }
DWORD g1_mirror2x_overlay_rect_blt_heal2_presents(void) { return g_rect_blt_heal2_presents; }
DWORD g1_mirror2x_overlay_rect_blt_heal2_pixels(void) { return g_rect_blt_heal2_pixels; }
DWORD g1_mirror2x_overlay_rect_blt_heal2_skipped(void) { return g_rect_blt_heal2_skipped; }
DWORD g1_mirror2x_rect_fill_invocations(void) { return g_rect_fill_invocations; }
DWORD g1_mirror2x_rect_fill_mirrored_calls(void) { return g_rect_fill_mirrored_calls; }
DWORD g1_mirror2x_rect_fill_mirrored_pixels(void) { return g_rect_fill_mirrored_pixels; }
DWORD g1_mirror2x_rect_fill_reject_target(void) { return g_rect_fill_reject_target; }
DWORD g1_mirror2x_rect_fill_reject_size(void) { return g_rect_fill_reject_size; }
DWORD g1_mirror2x_rect_fill_reject_guard(void) { return g_rect_fill_reject_guard; }
DWORD g1_mirror2x_cache_fill_invocations(void) { return g_cache_fill_invocations; }
DWORD g1_mirror2x_cache_fill_mirrored_calls(void) { return g_cache_fill_mirrored_calls; }
DWORD g1_mirror2x_cache_fill_mirrored_pixels(void) { return g_cache_fill_mirrored_pixels; }
DWORD g1_mirror2x_cache_fill_reject_target(void) { return g_cache_fill_reject_target; }
DWORD g1_mirror2x_cache_fill_unsupported(void) { return g_cache_fill_unsupported; }
DWORD g1_mirror2x_rect_border_invocations(void) { return g_rect_border_invocations; }
DWORD g1_mirror2x_rect_border_mirrored_calls(void) { return g_rect_border_mirrored_calls; }
DWORD g1_mirror2x_rect_border_mirrored_pixels(void) { return g_rect_border_mirrored_pixels; }
DWORD g1_mirror2x_rect_border_reject_target(void) { return g_rect_border_reject_target; }
DWORD g1_mirror2x_rect_border_reject_size(void) { return g_rect_border_reject_size; }
DWORD g1_mirror2x_rect_border_reject_guard(void) { return g_rect_border_reject_guard; }
DWORD g1_mirror2x_rect_border7_invocations(void) { return g_rect_border7_invocations; }
DWORD g1_mirror2x_rect_border7_mirrored_calls(void) { return g_rect_border7_mirrored_calls; }
DWORD g1_mirror2x_rect_border7_mirrored_pixels(void) { return g_rect_border7_mirrored_pixels; }
DWORD g1_mirror2x_rect_border7_reject_target(void) { return g_rect_border7_reject_target; }
DWORD g1_mirror2x_rect_border7_reject_size(void) { return g_rect_border7_reject_size; }
DWORD g1_mirror2x_rect_border7_reject_guard(void) { return g_rect_border7_reject_guard; }
DWORD g1_mirror2x_line_invocations(void) { return g_line_invocations; }
DWORD g1_mirror2x_line_mirrored_calls(void) { return g_line_mirrored_calls; }
DWORD g1_mirror2x_line_mirrored_pixels(void) { return g_line_mirrored_pixels; }
DWORD g1_mirror2x_line_reject_target(void) { return g_line_reject_target; }
DWORD g1_mirror2x_line_reject_size(void) { return g_line_reject_size; }
DWORD g1_mirror2x_line_reject_guard(void) { return g_line_reject_guard; }
DWORD g1_mirror2x_rect_solid_invocations(void) { return g_rect_solid_invocations; }
DWORD g1_mirror2x_rect_solid_mirrored_calls(void) { return g_rect_solid_mirrored_calls; }
DWORD g1_mirror2x_rect_solid_mirrored_pixels(void) { return g_rect_solid_mirrored_pixels; }
DWORD g1_mirror2x_rect_solid_reject_target(void) { return g_rect_solid_reject_target; }
DWORD g1_mirror2x_rect_solid_wide_calls(void) { return g_rect_solid_wide_calls; }
DWORD g1_mirror2x_rect_solid_reject_bounds(void) { return g_rect_solid_reject_bounds; }
DWORD g1_mirror2x_rect_solid_reject_size(void) { return g_rect_solid_reject_size; }
DWORD g1_mirror2x_rect_solid_reject_guard(void) { return g_rect_solid_reject_guard; }
DWORD g1_mirror2x_rect_solid_ybound(void) { return g_rect_solid_ybound; }
DWORD g1_mirror2x_flip_rle_invocations(void) { return g_flip_rle_invocations; }
DWORD g1_mirror2x_flip_rle_mirrored_calls(void) { return g_flip_rle_mirrored_calls; }
DWORD g1_mirror2x_flip_rle_mirrored_pixels(void) { return g_flip_rle_mirrored_pixels; }
DWORD g1_mirror2x_flip_rle_reject_target(void) { return g_flip_rle_reject_target; }
DWORD g1_mirror2x_flip_rle_reject_size(void) { return g_flip_rle_reject_size; }
DWORD g1_mirror2x_flip_rle_reject_guard(void) { return g_flip_rle_reject_guard; }
DWORD g1_mirror2x_flip_rle_reject_bounds(void) { return g_flip_rle_reject_bounds; }
DWORD g1_mirror2x_flip_rle_clipped_calls(void) { return g_flip_rle_clipped_calls; }
DWORD g1_mirror2x_flip_rle_wrap_calls(void) { return g_flip_rle_wrap_calls; }
DWORD g1_mirror2x_flip_rle_keyed_calls(void) { return g_flip_rle_keyed_calls; }
DWORD g1_mirror2x_flip_rle_key_fallbacks(void) { return g_flip_rle_key_fallbacks; }
DWORD g1_mirror2x_keyed_copy_invocations(void) { return g_keyed_copy_invocations; }
DWORD g1_mirror2x_keyed_copy_mirrored_calls(void) { return g_keyed_copy_mirrored_calls; }
DWORD g1_mirror2x_keyed_copy_mirrored_pixels(void) { return g_keyed_copy_mirrored_pixels; }
DWORD g1_mirror2x_keyed_copy_changed_calls(void) { return g_keyed_copy_changed_calls; }
DWORD g1_mirror2x_keyed_copy_clipped_calls(void) { return g_keyed_copy_clipped_calls; }
DWORD g1_mirror2x_keyed_copy_reject_target(void) { return g_keyed_copy_reject_target; }
DWORD g1_mirror2x_keyed_copy_reject_bounds(void) { return g_keyed_copy_reject_bounds; }
DWORD g1_mirror2x_keyed_copy_reject_size(void) { return g_keyed_copy_reject_size; }
DWORD g1_mirror2x_keyed_copy_reject_guard(void) { return g_keyed_copy_reject_guard; }
DWORD g1_mirror2x_flip_clip_invocations(void) { return g_flip_clip_invocations; }
DWORD g1_mirror2x_flip_clip_mirrored_calls(void) { return g_flip_clip_mirrored_calls; }
DWORD g1_mirror2x_flip_clip_mirrored_pixels(void) { return g_flip_clip_mirrored_pixels; }
DWORD g1_mirror2x_flip_clip_reject_target(void) { return g_flip_clip_reject_target; }
DWORD g1_mirror2x_flip_clip_reject_size(void) { return g_flip_clip_reject_size; }
DWORD g1_mirror2x_flip_clip_reject_guard(void) { return g_flip_clip_reject_guard; }
DWORD g1_mirror2x_flip_clip_reject_bounds(void) { return g_flip_clip_reject_bounds; }
DWORD g1_mirror2x_flip_clip_changed_calls(void) { return g_flip_clip_changed_calls; }
DWORD g1_mirror2x_flip_clip_clipped_calls(void) { return g_flip_clip_clipped_calls; }
DWORD g1_mirror2x_flip_clip_wrap_calls(void) { return g_flip_clip_wrap_calls; }
DWORD g1_mirror2x_flip_clip_keyed_calls(void) { return g_flip_clip_keyed_calls; }
DWORD g1_mirror2x_flip_clip_key_fallbacks(void) { return g_flip_clip_key_fallbacks; }
DWORD g1_mirror2x_shade_rle_invocations(void) { return g_shade_rle_invocations; }
DWORD g1_mirror2x_shade_rle_mirrored_calls(void) { return g_shade_rle_mirrored_calls; }
DWORD g1_mirror2x_shade_rle_mirrored_pixels(void) { return g_shade_rle_mirrored_pixels; }
DWORD g1_mirror2x_shade_rle_reject_target(void) { return g_shade_rle_reject_target; }
DWORD g1_mirror2x_shade_rle_reject_size(void) { return g_shade_rle_reject_size; }
DWORD g1_mirror2x_shade_rle_reject_guard(void) { return g_shade_rle_reject_guard; }
DWORD g1_mirror2x_shade_rle_reject_bounds(void) { return g_shade_rle_reject_bounds; }
DWORD g1_mirror2x_shade_rle_changed_calls(void) { return g_shade_rle_changed_calls; }
DWORD g1_mirror2x_shade_rle_clipped_calls(void) { return g_shade_rle_clipped_calls; }
DWORD g1_mirror2x_shade_rle_wrap_calls(void) { return g_shade_rle_wrap_calls; }
DWORD g1_mirror2x_shade_flip_invocations(void) { return g_shade_flip_invocations; }
DWORD g1_mirror2x_shade_flip_mirrored_calls(void) { return g_shade_flip_mirrored_calls; }
DWORD g1_mirror2x_shade_flip_mirrored_pixels(void) { return g_shade_flip_mirrored_pixels; }
DWORD g1_mirror2x_shade_flip_reject_target(void) { return g_shade_flip_reject_target; }
DWORD g1_mirror2x_shade_flip_reject_size(void) { return g_shade_flip_reject_size; }
DWORD g1_mirror2x_shade_flip_reject_guard(void) { return g_shade_flip_reject_guard; }
DWORD g1_mirror2x_shade_flip_reject_bounds(void) { return g_shade_flip_reject_bounds; }
DWORD g1_mirror2x_shade_flip_changed_calls(void) { return g_shade_flip_changed_calls; }
DWORD g1_mirror2x_shade_flip_clipped_calls(void) { return g_shade_flip_clipped_calls; }
DWORD g1_mirror2x_shade_flip_wrap_calls(void) { return g_shade_flip_wrap_calls; }
DWORD g1_mirror2x_shade_clip_invocations(void) { return g_shade_clip_invocations; }
DWORD g1_mirror2x_shade_clip_mirrored_calls(void) { return g_shade_clip_mirrored_calls; }
DWORD g1_mirror2x_shade_clip_mirrored_pixels(void) { return g_shade_clip_mirrored_pixels; }
DWORD g1_mirror2x_shade_clip_reject_target(void) { return g_shade_clip_reject_target; }
DWORD g1_mirror2x_shade_clip_reject_size(void) { return g_shade_clip_reject_size; }
DWORD g1_mirror2x_shade_clip_reject_guard(void) { return g_shade_clip_reject_guard; }
DWORD g1_mirror2x_shade_clip_reject_bounds(void) { return g_shade_clip_reject_bounds; }
DWORD g1_mirror2x_shade_clip_changed_calls(void) { return g_shade_clip_changed_calls; }
DWORD g1_mirror2x_shade_clip_clipped_calls(void) { return g_shade_clip_clipped_calls; }
DWORD g1_mirror2x_shade_clip_wrap_calls(void) { return g_shade_clip_wrap_calls; }
DWORD g1_mirror2x_blend_rle_invocations(void) { return g_blend_rle_invocations; }
DWORD g1_mirror2x_blend_rle_mirrored_calls(void) { return g_blend_rle_mirrored_calls; }
DWORD g1_mirror2x_blend_rle_mirrored_pixels(void) { return g_blend_rle_mirrored_pixels; }
DWORD g1_mirror2x_blend_rle_changed_calls(void) { return g_blend_rle_changed_calls; }
DWORD g1_mirror2x_blend_rle_reject_target(void) { return g_blend_rle_reject_target; }
DWORD g1_mirror2x_blend_rle_reject_bounds(void) { return g_blend_rle_reject_bounds; }
DWORD g1_mirror2x_blend_rle_reject_size(void) { return g_blend_rle_reject_size; }
DWORD g1_mirror2x_blend_rle_reject_guard(void) { return g_blend_rle_reject_guard; }
DWORD g1_mirror2x_blend_rle_keyed_calls(void) { return g_blend_rle_key.keyed_calls; }
DWORD g1_mirror2x_blend_rle_keyed_pixels(void) { return g_blend_rle_key.keyed_pixels; }
DWORD g1_mirror2x_blend_rle_key_fallbacks(void) { return g_blend_rle_key.key_fallbacks; }
DWORD g1_mirror2x_blend_rle_selfcheck_mismatches(void) { return g_blend_rle_key.selfcheck_mismatches; }
DWORD g1_mirror2x_blend_rle_selfcheck_pixels(void) { return g_blend_rle_key.selfcheck_pixels; }
DWORD g1_mirror2x_blend_wrle_keyed_calls(void) { return g_blend_wrle_key.keyed_calls; }
DWORD g1_mirror2x_blend_wrle_keyed_pixels(void) { return g_blend_wrle_key.keyed_pixels; }
DWORD g1_mirror2x_blend_wrle_key_fallbacks(void) { return g_blend_wrle_key.key_fallbacks; }
DWORD g1_mirror2x_blend_wrle_selfcheck_mismatches(void) { return g_blend_wrle_key.selfcheck_mismatches; }
DWORD g1_mirror2x_blend_wrle_selfcheck_pixels(void) { return g_blend_wrle_key.selfcheck_pixels; }
DWORD g1_mirror2x_blend_clip_keyed_calls(void) { return g_blend_clip_key.keyed_calls; }
DWORD g1_mirror2x_blend_clip_keyed_pixels(void) { return g_blend_clip_key.keyed_pixels; }
DWORD g1_mirror2x_blend_clip_key_fallbacks(void) { return g_blend_clip_key.key_fallbacks; }
DWORD g1_mirror2x_blend_clip_selfcheck_mismatches(void) { return g_blend_clip_key.selfcheck_mismatches; }
DWORD g1_mirror2x_blend_clip_selfcheck_pixels(void) { return g_blend_clip_key.selfcheck_pixels; }
DWORD g1_mirror2x_blend_clip_key_clip_cut(void) { return g_blend_clip_key.key_clip_cut; }
DWORD g1_mirror2x_blend_clip_key_clip_empty(void) { return g_blend_clip_key.key_clip_empty; }
DWORD g1_mirror2x_flip_blend_keyed_calls(void) { return g_flip_blend_key.keyed_calls; }
DWORD g1_mirror2x_flip_blend_keyed_pixels(void) { return g_flip_blend_key.keyed_pixels; }
DWORD g1_mirror2x_flip_blend_key_fallbacks(void) { return g_flip_blend_key.key_fallbacks; }
DWORD g1_mirror2x_flip_blend_selfcheck_mismatches(void) { return g_flip_blend_key.selfcheck_mismatches; }
DWORD g1_mirror2x_flip_blend_selfcheck_pixels(void) { return g_flip_blend_key.selfcheck_pixels; }
DWORD g1_mirror2x_flip_blend_key_wrap_mismatches(void) { return g_flip_blend_key.key_wrap_mismatches; }
DWORD g1_mirror2x_blend_skip_keyed_calls(void) { return g_blend_skip_key.keyed_calls; }
DWORD g1_mirror2x_blend_skip_keyed_pixels(void) { return g_blend_skip_key.keyed_pixels; }
DWORD g1_mirror2x_blend_skip_key_fallbacks(void) { return g_blend_skip_key.key_fallbacks; }
DWORD g1_mirror2x_blend_skip_selfcheck_mismatches(void) { return g_blend_skip_key.selfcheck_mismatches; }
DWORD g1_mirror2x_blend_skip_selfcheck_pixels(void) { return g_blend_skip_key.selfcheck_pixels; }
DWORD g1_mirror2x_blend_skip_key_clip_cut(void) { return g_blend_skip_key.key_clip_cut; }
DWORD g1_mirror2x_blend_skip_key_clip_empty(void) { return g_blend_skip_key.key_clip_empty; }
DWORD g1_mirror2x_blend_clip7_keyed_calls(void) { return g_blend_clip7_key.keyed_calls; }
DWORD g1_mirror2x_blend_clip7_keyed_pixels(void) { return g_blend_clip7_key.keyed_pixels; }
DWORD g1_mirror2x_blend_clip7_key_fallbacks(void) { return g_blend_clip7_key.key_fallbacks; }
DWORD g1_mirror2x_blend_clip7_selfcheck_mismatches(void) { return g_blend_clip7_key.selfcheck_mismatches; }
DWORD g1_mirror2x_blend_clip7_selfcheck_pixels(void) { return g_blend_clip7_key.selfcheck_pixels; }
DWORD g1_mirror2x_blend_clip7_key_clip_cut(void) { return g_blend_clip7_key.key_clip_cut; }
DWORD g1_mirror2x_blend_clip7_key_clip_empty(void) { return g_blend_clip7_key.key_clip_empty; }
DWORD g1_mirror2x_blend_clip7_key_level_rejects(void) { return g_blend_clip7_key.key_level_rejects; }
DWORD g1_mirror2x_blend_flip7_keyed_calls(void) { return g_blend_flip7_key.keyed_calls; }
DWORD g1_mirror2x_blend_flip7_keyed_pixels(void) { return g_blend_flip7_key.keyed_pixels; }
DWORD g1_mirror2x_blend_flip7_key_fallbacks(void) { return g_blend_flip7_key.key_fallbacks; }
DWORD g1_mirror2x_blend_flip7_selfcheck_mismatches(void) { return g_blend_flip7_key.selfcheck_mismatches; }
DWORD g1_mirror2x_blend_flip7_selfcheck_pixels(void) { return g_blend_flip7_key.selfcheck_pixels; }
DWORD g1_mirror2x_blend_flip7_key_clip_cut(void) { return g_blend_flip7_key.key_clip_cut; }
DWORD g1_mirror2x_blend_flip7_key_clip_empty(void) { return g_blend_flip7_key.key_clip_empty; }
DWORD g1_mirror2x_blend_flip7_key_level_rejects(void) { return g_blend_flip7_key.key_level_rejects; }
DWORD g1_mirror2x_blend_wrle_invocations(void) { return g_blend_wrle_invocations; }
DWORD g1_mirror2x_blend_wrle_mirrored_calls(void) { return g_blend_wrle_mirrored_calls; }
DWORD g1_mirror2x_blend_wrle_mirrored_pixels(void) { return g_blend_wrle_mirrored_pixels; }
DWORD g1_mirror2x_blend_wrle_changed_calls(void) { return g_blend_wrle_changed_calls; }
DWORD g1_mirror2x_blend_wrle_clipped_calls(void) { return g_blend_wrle_clipped_calls; }
DWORD g1_mirror2x_blend_wrle_reject_target(void) { return g_blend_wrle_reject_target; }
DWORD g1_mirror2x_blend_wrle_reject_bounds(void) { return g_blend_wrle_reject_bounds; }
DWORD g1_mirror2x_blend_wrle_reject_size(void) { return g_blend_wrle_reject_size; }
DWORD g1_mirror2x_blend_wrle_reject_guard(void) { return g_blend_wrle_reject_guard; }
DWORD g1_mirror2x_blend_clip_invocations(void) { return g_blend_clip_invocations; }
DWORD g1_mirror2x_blend_clip_mirrored_calls(void) { return g_blend_clip_mirrored_calls; }
DWORD g1_mirror2x_blend_clip_mirrored_pixels(void) { return g_blend_clip_mirrored_pixels; }
DWORD g1_mirror2x_blend_clip_changed_calls(void) { return g_blend_clip_changed_calls; }
DWORD g1_mirror2x_blend_clip_clipped_calls(void) { return g_blend_clip_clipped_calls; }
DWORD g1_mirror2x_blend_clip_reject_target(void) { return g_blend_clip_reject_target; }
DWORD g1_mirror2x_blend_clip_reject_bounds(void) { return g_blend_clip_reject_bounds; }
DWORD g1_mirror2x_blend_clip_reject_size(void) { return g_blend_clip_reject_size; }
DWORD g1_mirror2x_blend_clip_reject_guard(void) { return g_blend_clip_reject_guard; }
DWORD g1_mirror2x_blend_clip_band_calls(void) { return g_blend_clip_band_calls; }
DWORD g1_mirror2x_blend_skip_invocations(void) { return g_blend_skip_invocations; }
DWORD g1_mirror2x_blend_skip_mirrored_calls(void) { return g_blend_skip_mirrored_calls; }
DWORD g1_mirror2x_blend_skip_mirrored_pixels(void) { return g_blend_skip_mirrored_pixels; }
DWORD g1_mirror2x_blend_skip_changed_calls(void) { return g_blend_skip_changed_calls; }
DWORD g1_mirror2x_blend_skip_clipped_calls(void) { return g_blend_skip_clipped_calls; }
DWORD g1_mirror2x_blend_skip_reject_target(void) { return g_blend_skip_reject_target; }
DWORD g1_mirror2x_blend_skip_reject_bounds(void) { return g_blend_skip_reject_bounds; }
DWORD g1_mirror2x_blend_skip_reject_size(void) { return g_blend_skip_reject_size; }
DWORD g1_mirror2x_blend_skip_reject_guard(void) { return g_blend_skip_reject_guard; }
DWORD g1_mirror2x_blend_skip_band_calls(void) { return g_blend_skip_band_calls; }
DWORD g1_mirror2x_blend_clip7_invocations(void) { return g_blend_clip7_invocations; }
DWORD g1_mirror2x_blend_clip7_mirrored_calls(void) { return g_blend_clip7_mirrored_calls; }
DWORD g1_mirror2x_blend_clip7_mirrored_pixels(void) { return g_blend_clip7_mirrored_pixels; }
DWORD g1_mirror2x_blend_clip7_changed_calls(void) { return g_blend_clip7_changed_calls; }
DWORD g1_mirror2x_blend_clip7_clipped_calls(void) { return g_blend_clip7_clipped_calls; }
DWORD g1_mirror2x_blend_clip7_reject_target(void) { return g_blend_clip7_reject_target; }
DWORD g1_mirror2x_blend_clip7_reject_bounds(void) { return g_blend_clip7_reject_bounds; }
DWORD g1_mirror2x_blend_clip7_reject_size(void) { return g_blend_clip7_reject_size; }
DWORD g1_mirror2x_blend_clip7_reject_guard(void) { return g_blend_clip7_reject_guard; }
DWORD g1_mirror2x_flip_blend_invocations(void) { return g_flip_blend_invocations; }
DWORD g1_mirror2x_flip_blend_mirrored_calls(void) { return g_flip_blend_mirrored_calls; }
DWORD g1_mirror2x_flip_blend_mirrored_pixels(void) { return g_flip_blend_mirrored_pixels; }
DWORD g1_mirror2x_flip_blend_changed_calls(void) { return g_flip_blend_changed_calls; }
DWORD g1_mirror2x_flip_blend_clipped_calls(void) { return g_flip_blend_clipped_calls; }
DWORD g1_mirror2x_flip_blend_reject_target(void) { return g_flip_blend_reject_target; }
DWORD g1_mirror2x_flip_blend_reject_bounds(void) { return g_flip_blend_reject_bounds; }
DWORD g1_mirror2x_flip_blend_reject_size(void) { return g_flip_blend_reject_size; }
DWORD g1_mirror2x_flip_blend_reject_guard(void) { return g_flip_blend_reject_guard; }
DWORD g1_mirror2x_flip_blend_wrap_calls(void) { return g_flip_blend_wrap_calls; }
DWORD g1_mirror2x_blend_flip7_invocations(void) { return g_blend_flip7_invocations; }
DWORD g1_mirror2x_blend_flip7_mirrored_calls(void) { return g_blend_flip7_mirrored_calls; }
DWORD g1_mirror2x_blend_flip7_mirrored_pixels(void) { return g_blend_flip7_mirrored_pixels; }
DWORD g1_mirror2x_blend_flip7_changed_calls(void) { return g_blend_flip7_changed_calls; }
DWORD g1_mirror2x_blend_flip7_clipped_calls(void) { return g_blend_flip7_clipped_calls; }
DWORD g1_mirror2x_blend_flip7_reject_target(void) { return g_blend_flip7_reject_target; }
DWORD g1_mirror2x_blend_flip7_reject_bounds(void) { return g_blend_flip7_reject_bounds; }
DWORD g1_mirror2x_blend_flip7_reject_size(void) { return g_blend_flip7_reject_size; }
DWORD g1_mirror2x_blend_flip7_reject_guard(void) { return g_blend_flip7_reject_guard; }
DWORD g1_mirror2x_flip_blend7_invocations(void) { return g_flip_blend7_invocations; }
DWORD g1_mirror2x_flip_blend7_mirrored_calls(void) { return g_flip_blend7_mirrored_calls; }
DWORD g1_mirror2x_flip_blend7_mirrored_pixels(void) { return g_flip_blend7_mirrored_pixels; }
DWORD g1_mirror2x_flip_blend7_changed_calls(void) { return g_flip_blend7_changed_calls; }
DWORD g1_mirror2x_flip_blend7_reject_target(void) { return g_flip_blend7_reject_target; }
DWORD g1_mirror2x_flip_blend7_reject_bounds(void) { return g_flip_blend7_reject_bounds; }
DWORD g1_mirror2x_flip_blend7_reject_size(void) { return g_flip_blend7_reject_size; }
DWORD g1_mirror2x_flip_blend7_reject_guard(void) { return g_flip_blend7_reject_guard; }
DWORD g1_mirror2x_blend_410_invocations(void) { return g_blend_410_invocations; }
DWORD g1_mirror2x_blend_410_changed_calls(void) { return g_blend_410_changed_calls; }
DWORD g1_mirror2x_blend_410_mirrored_calls(void) { return g_blend_410_mirrored_calls; }
DWORD g1_mirror2x_blend_410_mirrored_pixels(void) { return g_blend_410_mirrored_pixels; }
DWORD g1_mirror2x_blend_410_reject_target(void) { return g_blend_410_reject_target; }
DWORD g1_mirror2x_blend_410_reject_bounds(void) { return g_blend_410_reject_bounds; }
DWORD g1_mirror2x_blend_410_reject_size(void) { return g_blend_410_reject_size; }
DWORD g1_mirror2x_blend_410_reject_guard(void) { return g_blend_410_reject_guard; }
DWORD g1_mirror2x_blend_6d0_invocations(void) { return g_blend_6d0_invocations; }
DWORD g1_mirror2x_blend_6d0_changed_calls(void) { return g_blend_6d0_changed_calls; }
DWORD g1_mirror2x_drift_w_records(void) { return g_drift_w_records; }
DWORD g1_mirror2x_primitive_guard(void) { return (DWORD)g_primitive_guard; }
BOOL g1_mirror2x_drift_410_installed(void) { return g_hook_blend_410.installed; }
BOOL g1_mirror2x_drift_6d0_installed(void) { return g_hook_blend_6d0.installed; }
DWORD g1_mirror2x_drift_unattributed(DWORD index)
{
    return index < G1_LAYER_DRIFT_RECTS ? g_drift_unattributed[index] : 0u;
}
DWORD g1_mirror2x_textout_invocations(void) { return g_textout_invocations; }
BOOL g1_mirror2x_ret_range_diag_enabled(void) { return g_ret_range_diag; }
DWORD g1_mirror2x_ret_diag_b_kills(void) { return g_ret_diag_b_kills; }
DWORD g1_mirror2x_ret_diag_b_idle(void) { return g_ret_diag_b_idle; }
DWORD g1_mirror2x_ret_diag_textout_kills(void) { return g_ret_diag_textout_kills; }
DWORD g1_mirror2x_ret_diag_textout_idle(void) { return g_ret_diag_textout_idle; }
DWORD g1_mirror2x_textout_mirrored_calls(void) { return g_textout_mirrored_calls; }
DWORD g1_mirror2x_textout_mirrored_pixels(void) { return g_textout_mirrored_pixels; }
DWORD g1_mirror2x_textout_changed_calls(void) { return g_textout_changed_calls; }
DWORD g1_mirror2x_textout_reject_target(void) { return g_textout_reject_target; }
DWORD g1_mirror2x_textout_reject_size(void) { return g_textout_reject_size; }
DWORD g1_mirror2x_textout_screen_dc_calls(void) { return g_textout_screen_dc_calls; }
DWORD g1_mirror2x_textout_reject_target_ps5(void) { return g_textout_reject_target_ps5; }
DWORD g1_mirror2x_textout_reject_target_ps7(void) { return g_textout_reject_target_ps7; }
DWORD g1_mirror2x_textout_reject_target_other(void) { return g_textout_reject_target_other; }
DWORD g1_mirror2x_textout_reject_target_dc_screen(void) { return g_textout_reject_target_dc_screen; }
DWORD g1_mirror2x_textout_reject_target_dc_buffer(void) { return g_textout_reject_target_dc_buffer; }
DWORD g1_mirror2x_textout_reject_target_dc_other(void) { return g_textout_reject_target_dc_other; }
DWORD g1_mirror2x_textout_reject_guard(void) { return g_textout_reject_guard; }
DWORD g1_mirror2x_textout_reject_align(void) { return g_textout_reject_align; }
DWORD g1_mirror2x_textout_install_mismatch(void) { return g_textout_install_mismatch; }
DWORD g1_mirror2x_textout_slot_installed(void) { return g_textout_slot_active ? 1u : 0u; }
DWORD g1_mirror2x_textout_slot_restored(void) { return g_textout_slot_restored; }

DWORD g1_mirror2x_panel_bound_transfers(void) { return g_panel_bound_transfer_count; }
DWORD g1_mirror2x_panel_unbound_transfers(void) { return g_panel_unbound_transfer_count; }
DWORD g1_mirror2x_panel_lock_failures(void) { return g_panel_lock_failures; }
DWORD g1_mirror2x_panel_pointer_mismatches(void) { return g_panel_pointer_mismatches; }
DWORD g1_mirror2x_panel_pitch_mismatches(void) { return g_panel_pitch_mismatches; }
DWORD g1_mirror2x_panel_foreign_writer_calls(void) { return g_panel_foreign_writer_count; }
DWORD g1_mirror2x_panel_frame_width(void) { return g_panel_frame_width; }
DWORD g1_mirror2x_panel_frame_height(void) { return g_panel_frame_height; }
const char *g1_mirror2x_panel_frame_sha256(void) { return g_panel_frame_sha256; }
const char *g1_mirror2x_panel_asset_key(void) { return g_panel_asset_key_name; }
BOOL g1_mirror2x_panel_hd_pack_loaded(void) { return g_panel_hd_pack_loaded; }
DWORD g1_mirror2x_panel_key_subpixels_emitted(void) { return g_panel_key_subpixels; }
DWORD g1_mirror2x_panel_transfer_copied(void) { return g_panel_transfer_copied; }
DWORD g1_mirror2x_panel_transfer_key_preserved(void) { return g_panel_transfer_key_preserved; }
DWORD g1_mirror2x_panel_transfer_mismatch_cleared(void)
{ return g_panel_transfer_mismatch_cleared; }

void g1_mirror2x_last_present_metrics(G1MirrorPresentMetrics *metrics)
{
    if (metrics) *metrics = g_last_present;
}

static BOOL bytes_equal(const BYTE *address, const BYTE *expected, DWORD length)
{
    DWORD i;
    for (i = 0; i < length; ++i) if (address[i] != expected[i]) return FALSE;
    return TRUE;
}

static BOOL install_one(DWORD address, const BYTE *expected, DWORD length,
                        void *wrapper, G1HookState *hook, G1PrimitiveFn *original)
{
    BYTE *target = (BYTE *)(ULONG_PTR)address;
    BYTE *copy;
    DWORD old_protect, restored, relative;
    if (!hook || length > sizeof(hook->original) ||
        !bytes_equal(target, expected, length)) return FALSE;
    ZeroMemory(hook, sizeof(*hook));
    hook->target = target;
    hook->length = length;
    for (DWORD i = 0; i < length; ++i) hook->original[i] = expected[i];
    copy = (BYTE *)VirtualAlloc(NULL, length + 5u, MEM_COMMIT | MEM_RESERVE,
                                PAGE_EXECUTE_READWRITE);
    if (!copy) return FALSE;
    for (DWORD i = 0; i < length; ++i) copy[i] = target[i];
    copy[length] = 0xE9;
    *(DWORD *)(copy + length + 1u) = (address + length) -
        ((DWORD)(ULONG_PTR)copy + length + 5u);
    if (!VirtualProtect(target, length, PAGE_EXECUTE_READWRITE, &old_protect)) {
        VirtualFree(copy, 0, MEM_RELEASE); return FALSE;
    }
    target[0] = 0xE9;
    relative = (DWORD)(ULONG_PTR)wrapper - (address + 5u);
    *(DWORD *)(target + 1) = relative;
    for (DWORD i = 5u; i < length; ++i) target[i] = 0x90;
    for (DWORD i = 0; i < length; ++i) hook->patched[i] = target[i];
    VirtualProtect(target, length, old_protect, &restored);
    FlushInstructionCache(GetCurrentProcess(), target, length);
    hook->trampoline = copy;
    hook->installed = TRUE;
    *original = (G1PrimitiveFn)(ULONG_PTR)copy;
    return TRUE;
}

static BOOL install_callsite(DWORD address, const BYTE expected[5], void *wrapper,
                             G1HookState *hook)
{
    BYTE *target = (BYTE *)(ULONG_PTR)address;
    DWORD old_protect, restored, relative;
    if (!hook || !bytes_equal(target, expected, 5u)) return FALSE;
    ZeroMemory(hook, sizeof(*hook));
    hook->target = target;
    hook->length = 5u;
    for (DWORD index = 0u; index < 5u; ++index) hook->original[index] = expected[index];
    if (!VirtualProtect(target, 5u, PAGE_EXECUTE_READWRITE, &old_protect)) return FALSE;
    target[0] = 0xE8;
    relative = (DWORD)(ULONG_PTR)wrapper - (address + 5u);
    *(DWORD *)(target + 1u) = relative;
    for (DWORD index = 0u; index < 5u; ++index) hook->patched[index] = target[index];
    VirtualProtect(target, 5u, old_protect, &restored);
    FlushInstructionCache(GetCurrentProcess(), target, 5u);
    hook->installed = TRUE;
    return TRUE;
}

static BOOL restore_hook(G1HookState *hook)
{
    DWORD old_protect, restored, i;
    if (!hook || !hook->installed) return TRUE;
    if (bytes_equal(hook->target, hook->original, hook->length)) {
        hook->installed = FALSE;
        return TRUE;
    }
    if (!bytes_equal(hook->target, hook->patched, hook->length)) return FALSE;
    if (!VirtualProtect(hook->target, hook->length, PAGE_EXECUTE_READWRITE,
                        &old_protect)) return FALSE;
    for (i = 0; i < hook->length; ++i) hook->target[i] = hook->original[i];
    VirtualProtect(hook->target, hook->length, old_protect, &restored);
    FlushInstructionCache(GetCurrentProcess(), hook->target, hook->length);
    hook->installed = FALSE;
    return bytes_equal(hook->target, hook->original, hook->length);
}

static BOOL readable_bytes(const BYTE *source, DWORD bytes)
{
    MEMORY_BASIC_INFORMATION info;
    DWORD checked = 0u;
    while (checked < bytes) {
        const BYTE *cursor = source + checked;
        DWORD available;
        if (!source || !VirtualQuery(cursor, &info, sizeof(info)) ||
            info.State != MEM_COMMIT ||
            (info.Protect & (PAGE_NOACCESS | PAGE_GUARD)) != 0u) return FALSE;
        available = (DWORD)((BYTE *)info.BaseAddress + info.RegionSize - cursor);
        if (available == 0u) return FALSE;
        checked += available < bytes - checked ? available : bytes - checked;
    }
    return TRUE;
}

static DWORD auxiliary_digest(const BYTE *source, DWORD bytes, BOOL *valid)
{
    DWORD hash = 2166136261u, index;
    *valid = source == NULL || (bytes != 0u && readable_bytes(source, bytes));
    if (!source || !*valid) return 0u;
    for (index = 0u; index < bytes; ++index) {
        hash ^= source[index];
        hash *= 16777619u;
    }
    return hash;
}

static void invoke_original(DWORD writer, void *renderer,
                            const DWORD args[6], BOOL unclipped)
{
    DWORD x = unclipped ? 0u : args[0];
    DWORD y = unclipped ? 0u : args[1];
    switch (writer) {
    case G1_TARGET_A:
        if (g_original_a) g_original_a(renderer, x, y, args[2], args[3], args[4]);
        break;
    case G1_TARGET_B:
        if (g_original_b) g_original_b(renderer, x, y, args[2], args[3], args[4]);
        break;
    case G1_TERRAIN_RLE:
        if (g_original_terrain_rle)
            g_original_terrain_rle(renderer, x, y, args[2], args[3]);
        break;
    case G1_TERRAIN_SHADE:
        if (g_original_terrain_shade)
            g_original_terrain_shade(renderer, x, y, args[2], args[3], args[4], args[5]);
        break;
    case G1_TERRAIN_CHECKER:
        if (g_original_terrain_checker)
            g_original_terrain_checker(renderer, x, y, args[2], args[3], args[4]);
        break;
    case G1_TERRAIN_CLIP:
        if (g_original_terrain_clip)
            g_original_terrain_clip(renderer, x, y, args[2], args[3], args[4]);
        break;
    case G1_TERRAIN_CLIP_SHADE:
        if (g_original_terrain_clip_shade)
            g_original_terrain_clip_shade(renderer, x, y, args[2], args[3], args[4], args[5]);
        break;
    case G1_TINTED_RLE:
        if (g_original_tinted_rle)
            g_original_tinted_rle(renderer, x, y, args[2], args[3], args[4], args[5]);
        break;
    case G1_TINTED_CLIP_RLE:
        if (g_original_tinted_clip_rle)
            g_original_tinted_clip_rle(renderer, x, y, args[2], args[3], args[4], args[5]);
        break;
    case G1_FLIP_RLE:
        if (g_original_flip_rle)
            g_original_flip_rle(renderer, x, y, args[2], args[3], args[4], args[5]);
        break;
    case G1_FLIP_CLIP:
        if (g_original_flip_clip)
            g_original_flip_clip(renderer, x, y, args[2], args[3], args[4], args[5]);
        break;
    default:
        break;
    }
}

static BYTE *clip_prepare_alloc(SIZE_T bytes)
{
    ULONGLONG started = g1_perf_sections_start();
    BYTE *result = (BYTE *)HeapAlloc(GetProcessHeap(), 0, bytes);
    ULONGLONG elapsed = g1_perf_sections_elapsed(started);
    g1_perf_sections_accumulate(G1_PERF_CLIP_TEMP_ALLOC_FREE, elapsed,
                                (ULONGLONG)bytes);
    return result;
}

static void clip_prepare_free(void *memory)
{
    ULONGLONG started;
    ULONGLONG elapsed;
    if (!memory) return;
    started = g1_perf_sections_start();
    HeapFree(GetProcessHeap(), 0, memory);
    elapsed = g1_perf_sections_elapsed(started);
    g1_perf_sections_accumulate(G1_PERF_CLIP_TEMP_ALLOC_FREE, elapsed, 0u);
}

static void clip_prepare_fill(BYTE *destination, BYTE value, DWORD bytes)
{
    ULONGLONG started = g1_perf_sections_start();
    fill_bytes(destination, value, bytes);
    {
        ULONGLONG elapsed = g1_perf_sections_elapsed(started);
        g1_perf_sections_accumulate(G1_PERF_CLIP_BUFFER_FILL, elapsed,
                                    (ULONGLONG)bytes);
    }
}

static void clip_prepare_mask(const BYTE *zero_frame, const BYTE *ff_frame,
                              DWORD stride, DWORD width, DWORD height,
                              BYTE *written)
{
    DWORD y, x;
    ULONGLONG started = g1_perf_sections_start();
    for (y = 0u; y < height; ++y) {
        const BYTE *zero_row = zero_frame + y * stride;
        const BYTE *ff_row = ff_frame + y * stride;
        BYTE *mask_row = written + y * width;
        for (x = 0u; x < width; ++x)
            mask_row[x] = zero_row[x] == ff_row[x];
    }
    {
        ULONGLONG bytes = (ULONGLONG)width * height;
        ULONGLONG elapsed = g1_perf_sections_elapsed(started);
        g1_perf_sections_accumulate(G1_PERF_CLIP_MASK_PREPARE, elapsed, bytes);
    }
}

static void mirror_reinvoke(void *renderer, const DWORD args[6],
                            DWORD argument_count, DWORD width, DWORD height,
                            const BYTE *source, const BYTE *auxiliary,
                            DWORD auxiliary_bytes, DWORD writer,
                            BOOL clipped)
{
    DWORD stride, surface_height, bytes, covered, i, y, x, elapsed;
    DWORD clip_mismatches_before;
    DWORD started;
    ULONGLONG perf_started;
    ULONGLONG whole_started;
    ULONGLONG clip_prepare_started = 0u;
    ULONGLONG clip_prepare_ticks = 0u;
    ULONGLONG clip_prepare_bytes = 0u;
    BOOL clip_prepare_active = FALSE;
    BYTE *expected;
    volatile BYTE *scratch_a;
    volatile BYTE *scratch_b;
    BOOL auxiliary_valid;
    BOOL asset_started = FALSE;
    DWORD aux_digest;
    DWORD frame_width;
    G1ScratchBounds bounds;
    BOOL cache_target;
    BOOL scratch_bounds_valid;
    LONG origin_x = (LONG)(SHORT)args[0];
    LONG origin_y = (LONG)(SHORT)args[1];
    g_reinvoke_composed = FALSE;
    if (!renderer || !g_scratch_a || !g_scratch_b || !g_mirror ||
        argument_count == 0u || argument_count > 6u || width == 0u ||
        height == 0u || width > G1_CACHE_WIDTH || height > 600u || !source) {
        layer_drift_return(renderer, writer, G1_DRIFT_RET_ARGS, origin_x, origin_y,
                           width, height);
        return;
    }
    started = GetTickCount();
    whole_started = g1_perf_sections_start();
    stride = *(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_STRIDE);
    surface_height = *(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_HEIGHT);
    expected = *(BYTE **)((BYTE *)renderer + G1_RENDERER_BUFFER);
    bytes = stride * surface_height;
    if (!expected || bytes > G1_MAX_BUFFER) {
        layer_drift_return(renderer, writer, G1_DRIFT_RET_BUFFER, origin_x, origin_y,
                           width, height);
        return;
    }
    if (expected == g_panel_bound_buffer && stride == g_panel_bound_pitch &&
        surface_height == g_panel_bound_height) {
        ++g_panel_foreign_writer_count;
        layer_drift_return(renderer, writer, G1_DRIFT_RET_PANEL_FOREIGN, origin_x,
                           origin_y, width, height);
        return;
    }
    cache_target = (DWORD)(ULONG_PTR)expected == G1_CACHE_BASE;
    frame_width = g1_mirror_frame_width(cache_target);
    if (!range_valid(stride, frame_width, surface_height)) {
        layer_drift_return(renderer, writer, G1_DRIFT_RET_RANGE, origin_x, origin_y,
                           width, height);
        return;
    }
    scratch_a = g_scratch_a;
    scratch_b = g_scratch_b;
    perf_started = g1_perf_sections_start();
    scratch_bounds_valid = g1_mirror_scratch_bounds(origin_x, origin_y, width, height,
                                                    cache_target, surface_height, &bounds);
    if (scratch_bounds_valid) {
        for (y = bounds.y; y < bounds.y + bounds.height; ++y) {
            DWORD row = y * stride + bounds.x;
            for (x = 0u; x < bounds.width; ++x) {
                scratch_a[row + x] = 0x00u;
                scratch_b[row + x] = 0xFFu;
            }
        }
    } else {
        for (i = 0; i < bytes; ++i) {
            scratch_a[i] = 0x00u;
            scratch_b[i] = 0xFFu;
        }
    }
    g1_perf_sections_end(G1_PERF_SCRATCH_CLEAR, perf_started,
                          scratch_bounds_valid
                              ? (ULONGLONG)bounds.width * bounds.height * 2u
                              : (ULONGLONG)bytes * 2u);
    *(BYTE **)((BYTE *)renderer + G1_RENDERER_BUFFER) = g_scratch_a;
    perf_started = g1_perf_sections_start();
    invoke_original(writer, renderer, args, FALSE);
    g1_perf_sections_end(writer == G1_TARGET_A ? G1_PERF_ORIGINAL_A : G1_PERF_ORIGINAL_B,
                          perf_started, 0u);
    *(BYTE **)((BYTE *)renderer + G1_RENDERER_BUFFER) = g_scratch_b;
    perf_started = g1_perf_sections_start();
    invoke_original(writer, renderer, args, FALSE);
    g1_perf_sections_end(writer == G1_TARGET_A ? G1_PERF_ORIGINAL_A : G1_PERF_ORIGINAL_B,
                          perf_started, 0u);
    *(BYTE **)((BYTE *)renderer + G1_RENDERER_BUFFER) = expected;
    aux_digest = auxiliary_digest(auxiliary, auxiliary_bytes, &auxiliary_valid);
    clip_mismatches_before = g1_hd_asset_clip_replay_mismatches();
    if (auxiliary_valid)
        asset_started = g1_hd_asset_begin_with_aux(source, writer, auxiliary,
                                                   aux_digest, width, height,
                                                   origin_x, origin_y);
    if (asset_started && g1_hd_asset_needs_identity_frame()) {
        clip_prepare_started = g1_perf_sections_start();
        clip_prepare_active = TRUE;
    }
    if (asset_started && !g1_hd_asset_needs_identity_frame()) {
        const LONG *hit_viewport = (const LONG *)((BYTE *)renderer +
                                                  G1_RENDERER_VIEWPORT);
        (void)g1_hd_asset_compare_visible_frame_in_viewport(
            (const BYTE *)scratch_a, stride, width, height, hit_viewport[0],
            hit_viewport[1], hit_viewport[2], hit_viewport[3]);
    }
    if (asset_started && g1_hd_asset_needs_identity_frame() && clipped) {
        BYTE *unclipped = clip_prepare_alloc(bytes);
        BYTE *unclipped_ff = clip_prepare_alloc(bytes);
        if (unclipped) clip_prepare_bytes += bytes;
        if (unclipped_ff) clip_prepare_bytes += bytes;
        clip_prepare_ticks += g1_perf_sections_elapsed(clip_prepare_started);
        clip_prepare_started = 0u;
        if (unclipped && unclipped_ff) {
            BYTE *saved_buffer = *(BYTE **)((BYTE *)renderer + G1_RENDERER_BUFFER);
            LONG *viewport = (LONG *)((BYTE *)renderer + G1_RENDERER_VIEWPORT);
            LONG saved_viewport[4];
            LONG full_viewport[4];
            DWORD viewport_index;
            g1_mirror_replay_viewport(cache_target, surface_height, full_viewport);
            for (viewport_index = 0u; viewport_index < 4u; ++viewport_index)
                saved_viewport[viewport_index] = viewport[viewport_index];
            if (cache_target) {
                ++g_cache_clip_attempts;
                if (!g_cache_clip_viewport_seen) {
                    g_cache_clip_viewport_seen = TRUE;
                    for (viewport_index = 0u; viewport_index < 4u; ++viewport_index)
                        g_cache_clip_first_viewport[viewport_index] =
                            saved_viewport[viewport_index];
                }
            }
            clip_prepare_started = g1_perf_sections_start();
            clip_prepare_fill(unclipped, 0x00u, bytes);
            *(BYTE **)((BYTE *)renderer + G1_RENDERER_BUFFER) = unclipped;
            for (viewport_index = 0u; viewport_index < 4u; ++viewport_index)
                viewport[viewport_index] = full_viewport[viewport_index];
            ++g_viewport_replay_count;
            clip_prepare_bytes += bytes;
            clip_prepare_ticks += g1_perf_sections_elapsed(clip_prepare_started);
            clip_prepare_started = 0u;
            perf_started = g1_perf_sections_start();
            invoke_original(writer, renderer, args, TRUE);
            g1_perf_sections_end(writer == G1_TARGET_A ? G1_PERF_ORIGINAL_A : G1_PERF_ORIGINAL_B,
                                  perf_started, 0u);
            clip_prepare_started = g1_perf_sections_start();
            for (viewport_index = 0u; viewport_index < 4u; ++viewport_index) {
                LONG returned_value = viewport[viewport_index];
                if (returned_value != full_viewport[viewport_index])
                    ++g_viewport_field_mutations;
                viewport[viewport_index] = saved_viewport[viewport_index];
                if (viewport[viewport_index] != saved_viewport[viewport_index])
                    ++g_viewport_restore_failures;
            }
            *(BYTE **)((BYTE *)renderer + G1_RENDERER_BUFFER) = saved_buffer;
            clip_prepare_ticks += g1_perf_sections_elapsed(clip_prepare_started);
            clip_prepare_started = 0u;
            if (!g1_hd_asset_verify_unclipped_frame_in_viewport(
                    (const BYTE *)scratch_a, unclipped, stride, stride,
                    width, height, saved_viewport[0], saved_viewport[1],
                    saved_viewport[2], saved_viewport[3])) {
                if (cache_target) ++g_cache_clip_verify_failures;
            } else {
                clip_prepare_started = g1_perf_sections_start();
                BYTE *written = clip_prepare_alloc((SIZE_T)width * height);
                if (written) clip_prepare_bytes += (ULONGLONG)width * height;
                clip_prepare_ticks += g1_perf_sections_elapsed(clip_prepare_started);
                clip_prepare_started = 0u;
                if (written) {
                    clip_prepare_started = g1_perf_sections_start();
                    *(BYTE **)((BYTE *)renderer + G1_RENDERER_BUFFER) = unclipped_ff;
                    for (viewport_index = 0u; viewport_index < 4u; ++viewport_index)
                        viewport[viewport_index] = full_viewport[viewport_index];
                    clip_prepare_fill(unclipped_ff, 0xFFu, bytes);
                    clip_prepare_bytes += bytes;
                    ++g_viewport_replay_count;
                    clip_prepare_ticks += g1_perf_sections_elapsed(clip_prepare_started);
                    clip_prepare_started = 0u;
                    perf_started = g1_perf_sections_start();
                    invoke_original(writer, renderer, args, TRUE);
                    g1_perf_sections_end(writer == G1_TARGET_A ? G1_PERF_ORIGINAL_A : G1_PERF_ORIGINAL_B,
                                        perf_started, 0u);
                    clip_prepare_started = g1_perf_sections_start();
                    for (viewport_index = 0u; viewport_index < 4u; ++viewport_index) {
                        LONG returned_value = viewport[viewport_index];
                        if (returned_value != full_viewport[viewport_index])
                            ++g_viewport_field_mutations;
                        viewport[viewport_index] = saved_viewport[viewport_index];
                        if (viewport[viewport_index] != saved_viewport[viewport_index])
                            ++g_viewport_restore_failures;
                    }
                    *(BYTE **)((BYTE *)renderer + G1_RENDERER_BUFFER) = saved_buffer;
                    clip_prepare_ticks += g1_perf_sections_elapsed(clip_prepare_started);
                    clip_prepare_started = g1_perf_sections_start();
                    clip_prepare_mask(unclipped, unclipped_ff, stride, width,
                                      height, written);
                    clip_prepare_bytes += (ULONGLONG)width * height;
                    clip_prepare_ticks += g1_perf_sections_elapsed(clip_prepare_started);
                    clip_prepare_started = 0u;
                    if (!g1_hd_asset_verify_unclipped_frame_in_viewport(
                            (const BYTE *)scratch_b, unclipped_ff, stride, stride,
                            width, height, saved_viewport[0], saved_viewport[1],
                            saved_viewport[2], saved_viewport[3])) {
                        if (cache_target) ++g_cache_clip_verify_failures;
                    } else {
                        (void)g1_hd_asset_bind_identity_frame(unclipped, stride,
                                                              written, width,
                                                              width, height);
                    }
                    clip_prepare_started = g1_perf_sections_start();
                    clip_prepare_free(written);
                    clip_prepare_ticks += g1_perf_sections_elapsed(clip_prepare_started);
                    clip_prepare_started = 0u;
                }
            }
        }
        clip_prepare_started = g1_perf_sections_start();
        clip_prepare_free(unclipped);
        clip_prepare_free(unclipped_ff);
        clip_prepare_ticks += g1_perf_sections_elapsed(clip_prepare_started);
        clip_prepare_started = 0u;
    } else if (asset_started && g1_hd_asset_needs_identity_frame() &&
               g1_mirror_unclipped_bind_fits(origin_x, origin_y, width, height,
                                             cache_target, surface_height)) {
        const BYTE *origin_frame = (const BYTE *)scratch_a +
                                   (DWORD)origin_y * stride + (DWORD)origin_x;
        const BYTE *origin_b = (const BYTE *)scratch_b +
                               (DWORD)origin_y * stride + (DWORD)origin_x;
        BYTE *written = clip_prepare_alloc((SIZE_T)width * height);
        if (cache_target && (DWORD)origin_x + width > G1_MIRROR_SCREEN_WIDTH)
            ++g_cache_edge_unclipped_binds;
        if (written) clip_prepare_bytes += (ULONGLONG)width * height;
        if (written) {
            clip_prepare_mask(origin_frame, origin_b, stride, width, height,
                              written);
            clip_prepare_bytes += (ULONGLONG)width * height;
            clip_prepare_ticks += g1_perf_sections_elapsed(clip_prepare_started);
            clip_prepare_started = g1_perf_sections_start();
            (void)g1_hd_asset_bind_identity_frame(origin_frame, stride,
                                                  written, width, width, height);
            clip_prepare_started = g1_perf_sections_start();
            clip_prepare_free(written);
            clip_prepare_ticks += g1_perf_sections_elapsed(clip_prepare_started);
            clip_prepare_started = 0u;
        }
    }
    if (clip_prepare_active) {
        clip_prepare_ticks += g1_perf_sections_elapsed(clip_prepare_started);
        g1_perf_sections_accumulate(G1_PERF_CLIP_PREPARE,
                                    clip_prepare_ticks, clip_prepare_bytes);
    }
    if (g1_hd_asset_clip_replay_mismatches() != clip_mismatches_before) {
        DWORD writer_index = writer == G1_TARGET_A ? 0u :
                             writer == G1_TARGET_B ? 1u :
                             writer == G1_TERRAIN_RLE ? 2u :
                             writer == G1_TERRAIN_SHADE ? 3u :
                             writer == G1_TERRAIN_CHECKER ? 4u :
                             writer == G1_TERRAIN_CLIP ? 5u :
                             writer == G1_TERRAIN_CLIP_SHADE ? 6u : 7u;
        if (writer_index < 7u) ++g_writer_clip_mismatch_counts[writer_index];
        g_last_clip_mismatch_writer = writer;
        g_last_clip_mismatch_origin_x = (DWORD)origin_x;
        g_last_clip_mismatch_origin_y = (DWORD)origin_y;
        g_last_clip_mismatch_width = width;
        g_last_clip_mismatch_height = height;
        g1_hd_asset_last_clip_mismatch(&g_last_clip_mismatch_x,
                                       &g_last_clip_mismatch_y,
                                       &g_last_clip_screen_value,
                                       &g_last_clip_replay_value);
    }
    if (cache_target && layer_drift_on())
        layer_drift_call(writer, g1_hd_asset_current_ready() ? G1_DRIFT_COMPOSE_RAN
                                                              : G1_DRIFT_NOT_READY,
                         origin_x, origin_y, width, height);
    g_reinvoke_composed = g1_hd_asset_current_ready();
    if (g1_hd_asset_current_ready() && cache_target) {
        perf_started = g1_perf_sections_start();
        covered = compose_cache_layer(expected, g_scratch_a, g_scratch_b,
                                      origin_x, origin_y, width, height);
        g1_perf_sections_end(G1_PERF_COMPOSE, perf_started,
                             (ULONGLONG)width * height);
    } else if (g1_hd_asset_current_ready()) {
        perf_started = g1_perf_sections_start();
        covered = g1_mirror2x_compose_sentinel(expected, g_scratch_a, g_scratch_b,
                                                stride, g_mirror, 1600u, 800u,
                                                surface_height, origin_x, origin_y,
                                                width, height);
        g1_perf_sections_end(G1_PERF_COMPOSE, perf_started,
                              (ULONGLONG)width * height);
    } else {
        covered = 0u;
    }
    if (hd_negative_probe_enabled()) {
        perf_started = g1_perf_sections_start();
        (void)g1_hd_asset_probe_negative_key_mismatch();
        g1_perf_sections_end(G1_PERF_NEGATIVE_PROBE, perf_started, 0u);
    }
    g1_hd_asset_end();
    g_covered_pixels += covered;
    elapsed = elapsed_ms(started);
    g_primitive_reinvoke_elapsed_ms_total += elapsed;
    if (elapsed > g_primitive_reinvoke_elapsed_ms_max)
        g_primitive_reinvoke_elapsed_ms_max = elapsed;
    ++g_primitive_reinvoke_count;
    g1_perf_sections_end(writer == G1_TINTED_RLE ? G1_PERF_WHOLE_TINTED :
                         writer == G1_TINTED_CLIP_RLE ? G1_PERF_WHOLE_TINTED_CLIP :
                         G1_PERF_WHOLE_OTHER, whole_started, 0u);
}

static DWORD s3_apply_resource_pattern(void)
{
    DWORD logical, pixels = 0u;
    if (!g1_mirror2x_s3_pattern_enabled() || g_s3_pattern_applied || !g_mirror || !g_covered)
        return 0u;
    for (logical = 0u; logical < 800u * 600u; ++logical) {
        DWORD x, y, mirror_index;
        BYTE base, *pixel;
        if (!g_covered[logical]) continue;
        x = logical % 800u;
        y = logical / 800u;
        mirror_index = y * 2u * 1600u + x * 2u;
        pixel = g_mirror + mirror_index;
        base = pixel[0];
        /* The 20x24 resource frame is already rasterized by the original
         * primitive.  This diagnostic changes only its covered 2x2 blocks;
         * each block becomes a four-value checker, so it cannot be mistaken
         * for a nearest-neighbour expansion. */
        pixel[0] = base;
        pixel[1] = (BYTE)(base ^ 0x01u);
        pixel[1600u] = (BYTE)(base ^ 0x02u);
        pixel[1601u] = (BYTE)(base ^ 0x03u);
        if (g_s3_mask) g_s3_mask[logical] = 1u;
        ++pixels;
    }
    if (pixels != 0u) {
        g_s3_pattern_applied = TRUE;
        g_s3_pattern_pixels = pixels;
    }
    return pixels;
}

static void s3_overlay_at_present(const BYTE *source, DWORD source_stride)
{
    DWORD logical;
    if (!g_s3_pattern_applied || !g_s3_mask || !source || !g_mirror)
        return;
    for (logical = 0u; logical < 800u * 600u; ++logical) {
        DWORD x, y, mirror_index;
        BYTE base, *pixel;
        if (!g_s3_mask[logical]) continue;
        x = logical % 800u;
        y = logical / 800u;
        g_covered[logical] = 1u;
        base = source[y * source_stride + x];
        g_expected_snapshot[logical] = base;
        mirror_index = y * 2u * 1600u + x * 2u;
        pixel = g_mirror + mirror_index;
        pixel[0] = base;
        pixel[1] = (BYTE)(base ^ 0x01u);
        pixel[1600u] = (BYTE)(base ^ 0x02u);
        pixel[1601u] = (BYTE)(base ^ 0x03u);
    }
    /* Keep the marked frame visible across the capture window.  The pattern
     * is diagnostic-only and the private process is torn down after capture. */
    g_s3_overlay_done = TRUE;
}

static void s3_overlay_destination(const BYTE *source, DWORD source_stride,
                                   BYTE *destination, DWORD destination_stride)
{
    DWORD logical;
    if (!g_s3_pattern_applied || !g_s3_mask || !source || !destination) return;
    for (logical = 0u; logical < 800u * 600u; ++logical) {
        DWORD x, y;
        BYTE base, *pixel;
        if (!g_s3_mask[logical]) continue;
        x = logical % 800u;
        y = logical / 800u;
        base = source[y * source_stride + x];
        pixel = destination + (y * 2u) * destination_stride + x * 2u;
        pixel[0] = base;
        pixel[1] = (BYTE)(base ^ 0x01u);
        pixel[destination_stride] = (BYTE)(base ^ 0x02u);
        pixel[destination_stride + 1u] = (BYTE)(base ^ 0x03u);
    }
}

static BOOL s3_resource_frame0_target(DWORD x, DWORD y, DWORD width, DWORD height)
{
    return g1_mirror2x_s3_pattern_enabled() && !g_s3_pattern_applied &&
           x == 10u && y == 3u && width == 20u && height == 24u;
}

static BOOL panel_load_hd_pack(const BYTE *source, DWORD height,
                               const BYTE *panel_frame)
{
    char key[64], path[MAX_PATH], pal8[9];
    DWORD directory_length, digest, expected_bytes, file_high = 0u;
    HANDLE file;
    DWORD file_bytes, bytes_read = 0u;
    BOOL valid = FALSE;
    directory_length = lstrlenA(g_panel_hd_pack_dir);
    if (!readable_bytes(source, 128u)) return FALSE;
    digest = g1_panel_source_digest(source, 128u);
    if (!g1_panel_asset_key(key, sizeof(key), G1_PANEL_RLE,
                            831u, height, digest)) return FALSE;
    /* H-HDPAL: <pack>\<pal8>\<key>, pal8 = the screen palette the panel picture was quantised to */
    if (!g1_hd_pack_format_pal(pal8, sizeof(pal8), g1_hd_asset_palette_digest())) return FALSE;
    expected_bytes = G1_PANEL_WIDTH * height * 4u;
    if (g1_hd_asset_load_named_frame(key, g1_hd_asset_palette_digest(), g_panel_pack, expected_bytes) &&
        g1_panel_hd_pack_valid(panel_frame, G1_PANEL_WIDTH, G1_PANEL_WIDTH, height,
                               g_panel_pack, expected_bytes)) {
        panel_copy_bytes(g_panel_mirror, g_panel_pack, expected_bytes);
        return TRUE;
    }
    /* Legacy pack override remains useful for diagnostics; normal use auto-discovers _hd files. */
    if (!directory_length) return FALSE;
    if (directory_length + 1u + 8u + 1u + lstrlenA(key) >= sizeof(path)) return FALSE;
    panel_copy_bytes((BYTE *)path, (const BYTE *)g_panel_hd_pack_dir,
                     directory_length);
    if (g_panel_hd_pack_dir[directory_length - 1u] != '\\' &&
        g_panel_hd_pack_dir[directory_length - 1u] != '/')
        path[directory_length++] = '\\';
    panel_copy_bytes((BYTE *)path + directory_length, (const BYTE *)pal8, 8u);
    directory_length += 8u;
    path[directory_length++] = '\\';
    panel_copy_bytes((BYTE *)path + directory_length, (const BYTE *)key,
                     lstrlenA(key) + 1u);
    file = CreateFileA(path, GENERIC_READ, FILE_SHARE_READ, NULL,
                       OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
    if (file == INVALID_HANDLE_VALUE) return FALSE;
    file_bytes = GetFileSize(file, &file_high);
    if (file_high == 0u && file_bytes == expected_bytes &&
        ReadFile(file, g_panel_pack, expected_bytes, &bytes_read, NULL) &&
        bytes_read == expected_bytes &&
        g1_panel_hd_pack_valid(panel_frame, G1_PANEL_WIDTH,
                               G1_PANEL_WIDTH, height,
                               g_panel_pack, expected_bytes)) {
        panel_copy_bytes(g_panel_mirror, g_panel_pack, expected_bytes);
        valid = TRUE;
    }
    CloseHandle(file);
    return valid;
}

static BOOL panel_capture_frame(void *renderer, DWORD width, DWORD height,
                                const BYTE *source)
{
    BYTE *buffer;
    DWORD stride, surface_height, y, x;
    BOOL pack_loaded;
    g_panel_bound_buffer = NULL;
    g_panel_bound_pitch = 0u;
    g_panel_bound_height = 0u;
    g_panel_frame_width = 0u;
    g_panel_frame_height = 0u;
    g_panel_frame_sha256[0] = '\0';
    g_panel_asset_key_name[0] = '\0';
    g_panel_hd_pack_loaded = FALSE;
    if (!renderer || !g_panel_expected || !g_panel_covered || !g_panel_mirror ||
        width != 831u || height == 0u || height > G1_PANEL_MAX_HEIGHT)
        return FALSE;
    if (readable_bytes(source, 128u)) {
        DWORD digest = g1_panel_source_digest(source, 128u);
        char key[64];
        if (g1_panel_asset_key(key, sizeof(key), G1_PANEL_RLE, 831u, height,
                               digest))
            panel_copy_bytes((BYTE *)g_panel_asset_key_name, (const BYTE *)key,
                             lstrlenA(key) + 1u);
    }
    buffer = *(BYTE **)((BYTE *)renderer + G1_RENDERER_BUFFER);
    stride = *(DWORD *)((BYTE *)renderer + G1_RENDERER_STRIDE);
    surface_height = *(DWORD *)((BYTE *)renderer + G1_RENDERER_HEIGHT);
    if (!buffer || stride != G1_PANEL_WIDTH || surface_height < height ||
        !readable_bytes(buffer, stride * height)) return FALSE;
    for (y = 0u; y < height; ++y) {
        BYTE *expected = g_panel_expected + y * G1_PANEL_WIDTH;
        BYTE *covered = g_panel_covered + y * G1_PANEL_WIDTH;
        const BYTE *row = buffer + y * stride;
        for (x = 0u; x < G1_PANEL_WIDTH; ++x) {
            expected[x] = row[x];
            covered[x] = 1u;
        }
    }
    pack_loaded = panel_load_hd_pack(source, height, g_panel_expected);
    if (!pack_loaded &&
        !g1_panel_build_scale2x(g_panel_expected, G1_PANEL_WIDTH,
                                G1_PANEL_WIDTH, height, g_panel_mirror,
                                G1_PANEL_HD_STRIDE)) return FALSE;
    g_panel_hd_pack_loaded = pack_loaded;
    g_panel_bound_buffer = buffer;
    g_panel_bound_pitch = stride;
    g_panel_bound_height = surface_height;
    g_panel_frame_width = G1_PANEL_WIDTH;
    g_panel_frame_height = height;
    if (!g1_panel_sha256_rows(g_panel_expected, G1_PANEL_WIDTH,
                              G1_PANEL_WIDTH, height, g_panel_frame_sha256))
        return FALSE;
    g_panel_key_subpixels = (DWORD)g1_panel_key_subpixels(
        g_panel_expected, G1_PANEL_WIDTH, G1_PANEL_WIDTH, height,
        g_panel_mirror, G1_PANEL_HD_STRIDE);
    return TRUE;
}

static DWORD __attribute__((thiscall)) mirror_panel_rle(void *renderer,
                                                         DWORD x, DWORD y,
                                                         DWORD width, DWORD height,
                                                         DWORD source)
{
    DWORD result;
    DWORD return_address = (DWORD)(ULONG_PTR)__builtin_return_address(0);
    if (!g_original_panel_rle) return 0u;
    if (InterlockedExchange(&g_primitive_guard, 1) != 0) {
        layer_drift_guard_bypass(renderer);
        result = g_original_panel_rle(renderer, x, y, width, height, source);
        InterlockedExchange(&g_primitive_guard, 0);
        return result;
    }
    result = g_original_panel_rle(renderer, x, y, width, height, source);
    if (g1_panel_writer_return(return_address))
        (void)panel_capture_frame(renderer, width, height,
                                  (const BYTE *)(ULONG_PTR)source);
    InterlockedExchange(&g_primitive_guard, 0);
    return result;
}

static DWORD __attribute__((thiscall)) mirror_primitive_a(void *renderer,
                                                            DWORD a, DWORD b,
                                                            DWORD c, DWORD d,
                                                            DWORD e)
{
    DWORD result;
    const DWORD args[6] = {a, b, c, d, e, 0u};
    if (!g_original_a) return 0u;
    if (InterlockedExchange(&g_primitive_guard, 1) != 0) {
        layer_drift_guard_bypass(renderer);
        result = g_original_a(renderer, a, b, c, d, e);
        InterlockedExchange(&g_primitive_guard, 0);
        return result;
    }
    result = g_original_a(renderer, a, b, c, d, e);
    mirror_reinvoke(renderer, args, 5u, (DWORD)(SHORT)c, (DWORD)(SHORT)d,
                    (const BYTE *)(ULONG_PTR)e, NULL, 0u, G1_TARGET_A, TRUE);
    ++g_primitive_calls;
    ++g_writer_call_counts[0];
    InterlockedExchange(&g_primitive_guard, 0);
    return result;
}

static DWORD __attribute__((thiscall)) mirror_primitive_b(void *renderer,
                                                            DWORD a, DWORD b,
                                                            DWORD c, DWORD d,
                                                            DWORD e)
{
    DWORD result;
    const DWORD args[6] = {a, b, c, d, e, 0u};
    DWORD return_address = (DWORD)(ULONG_PTR)__builtin_return_address(0);
    BOOL s3_target = s3_resource_frame0_target(a, b, c, d);
    if (!g_original_b) return 0u;
    if (g_ret_range_diag) ret_range_diag_count(return_address, &g_ret_diag_b_kills, &g_ret_diag_b_idle);
    if (InterlockedExchange(&g_primitive_guard, 1) != 0) {
        layer_drift_guard_bypass(renderer);
        result = g_original_b(renderer, a, b, c, d, e);
        InterlockedExchange(&g_primitive_guard, 0);
        return result;
    }
    if (s3_target) {
        /* Do not let earlier calls make the diagnostic mask ambiguous. */
        zero_bytes(g_covered, 800u * 600u);
        zero_bytes(g_expected_snapshot, 800u * 600u);
    }
    result = g_original_b(renderer, a, b, c, d, e);
    mirror_reinvoke(renderer, args, 5u, (DWORD)(SHORT)c, (DWORD)(SHORT)d,
                    (const BYTE *)(ULONG_PTR)e, NULL, 0u, G1_TARGET_B, TRUE);
    if (s3_target) (void)s3_apply_resource_pattern();
    ++g_primitive_calls;
    ++g_writer_call_counts[1];
    InterlockedExchange(&g_primitive_guard, 0);
    return result;
}

static BOOL rle_dimensions(const BYTE *source, DWORD rows, DWORD *width)
{
    const BYTE *cursor = source;
    DWORD row, widest = 0u;
    if (!source || !width || rows == 0u || rows > 600u) return FALSE;
    for (row = 0u; row < rows; ++row) {
        DWORD skip, length, end;
        if (!readable_bytes(cursor, 2u)) return FALSE;
        skip = cursor[0];
        length = cursor[1];
        end = skip + length;
        if (end > 800u) return FALSE;
        cursor += 2u;
        if (!readable_bytes(cursor, length)) return FALSE;
        if (end > widest) widest = end;
        cursor += length;
    }
    *width = widest;
    return widest != 0u;
}

/* Original returns: 0x468C30 ret 0x10. */
static DWORD __attribute__((thiscall)) mirror_terrain_rle(void *renderer,
                                                            DWORD x, DWORD y,
                                                            DWORD rows, DWORD source_word)
{
    DWORD result, width;
    const BYTE *source = (const BYTE *)(ULONG_PTR)source_word;
    const DWORD args[6] = {x, y, rows, source_word, 0u, 0u};
    if (!g_original_terrain_rle) return 0u;
    if (InterlockedExchange(&g_primitive_guard, 1) != 0) {
        layer_drift_guard_bypass(renderer);
        result = g_original_terrain_rle(renderer, x, y, rows, source_word);
        InterlockedExchange(&g_primitive_guard, 0);
        return result;
    }
    result = g_original_terrain_rle(renderer, x, y, rows, source_word);
    if (rle_dimensions(source, (DWORD)(SHORT)rows, &width))
        mirror_reinvoke(renderer, args, 4u, width, (DWORD)(SHORT)rows,
                        source, NULL, 0u, G1_TERRAIN_RLE, FALSE);
    ++g_primitive_calls;
    ++g_writer_call_counts[2];
    InterlockedExchange(&g_primitive_guard, 0);
    return result;
}

/* Original returns: 0x468CC0 ret 0x18. */
static DWORD __attribute__((thiscall)) mirror_terrain_shade(void *renderer,
                                                             DWORD x, DWORD y,
                                                             DWORD width_word,
                                                             DWORD height_word,
                                                             DWORD source_word,
                                                             DWORD shade_word)
{
    DWORD result, width = (DWORD)(SHORT)width_word, height = (DWORD)(SHORT)height_word;
    const BYTE *source = (const BYTE *)(ULONG_PTR)source_word;
    const BYTE *shade = (const BYTE *)(ULONG_PTR)shade_word;
    const DWORD args[6] = {x, y, width_word, height_word, source_word, shade_word};
    if (!g_original_terrain_shade) return 0u;
    if (InterlockedExchange(&g_primitive_guard, 1) != 0) {
        layer_drift_guard_bypass(renderer);
        result = g_original_terrain_shade(renderer, x, y, width_word, height_word,
                                          source_word, shade_word);
        InterlockedExchange(&g_primitive_guard, 0);
        return result;
    }
    result = g_original_terrain_shade(renderer, x, y, width_word, height_word,
                                      source_word, shade_word);
    mirror_reinvoke(renderer, args, 6u, width, height, source, shade,
                    width * height, G1_TERRAIN_SHADE, FALSE);
    ++g_primitive_calls;
    ++g_writer_call_counts[3];
    InterlockedExchange(&g_primitive_guard, 0);
    return result;
}

/* Original returns: 0x468E10 ret 0x14. */
static DWORD __attribute__((thiscall)) mirror_terrain_checker(void *renderer,
                                                               DWORD x, DWORD y,
                                                               DWORD rows,
                                                               DWORD source_word,
                                                               DWORD lut_word)
{
    DWORD result, width;
    const BYTE *source = (const BYTE *)(ULONG_PTR)source_word;
    const BYTE *lut = (const BYTE *)(ULONG_PTR)lut_word;
    const DWORD args[6] = {x, y, rows, source_word, lut_word, 0u};
    if (!g_original_terrain_checker) return 0u;
    if (InterlockedExchange(&g_primitive_guard, 1) != 0) {
        layer_drift_guard_bypass(renderer);
        result = g_original_terrain_checker(renderer, x, y, rows, source_word, lut_word);
        InterlockedExchange(&g_primitive_guard, 0);
        return result;
    }
    result = g_original_terrain_checker(renderer, x, y, rows, source_word, lut_word);
    if (rle_dimensions(source, (DWORD)(SHORT)rows, &width))
        mirror_reinvoke(renderer, args, 5u, width, (DWORD)(SHORT)rows,
                        source, lut, 256u, G1_TERRAIN_CHECKER, FALSE);
    ++g_primitive_calls;
    ++g_writer_call_counts[4];
    InterlockedExchange(&g_primitive_guard, 0);
    return result;
}

/* Original returns: 0x468F00 ret 0x14. */
static DWORD __attribute__((thiscall)) mirror_terrain_clip(void *renderer,
                                                            DWORD x, DWORD y,
                                                            DWORD width_word,
                                                            DWORD height_word,
                                                            DWORD source_word)
{
    DWORD result, width = (DWORD)(SHORT)width_word, height = (DWORD)(SHORT)height_word;
    const BYTE *source = (const BYTE *)(ULONG_PTR)source_word;
    const DWORD args[6] = {x, y, width_word, height_word, source_word, 0u};
    if (!g_original_terrain_clip) return 0u;
    if (InterlockedExchange(&g_primitive_guard, 1) != 0) {
        layer_drift_guard_bypass(renderer);
        result = g_original_terrain_clip(renderer, x, y, width_word, height_word,
                                         source_word);
        InterlockedExchange(&g_primitive_guard, 0);
        return result;
    }
    result = g_original_terrain_clip(renderer, x, y, width_word, height_word,
                                     source_word);
    mirror_reinvoke(renderer, args, 5u, width, height, source, NULL, 0u,
                    G1_TERRAIN_CLIP, TRUE);
    ++g_primitive_calls;
    ++g_writer_call_counts[5];
    InterlockedExchange(&g_primitive_guard, 0);
    return result;
}

/* Original returns: 0x4690A0 ret 0x18. */
static DWORD __attribute__((thiscall)) mirror_terrain_clip_shade(void *renderer,
                                                                 DWORD x, DWORD y,
                                                                 DWORD width_word,
                                                                 DWORD height_word,
                                                                 DWORD source_word,
                                                                 DWORD shade_word)
{
    DWORD result, width = (DWORD)(SHORT)width_word, height = (DWORD)(SHORT)height_word;
    const BYTE *source = (const BYTE *)(ULONG_PTR)source_word;
    const BYTE *shade = (const BYTE *)(ULONG_PTR)shade_word;
    const DWORD args[6] = {x, y, width_word, height_word, source_word, shade_word};
    if (!g_original_terrain_clip_shade) return 0u;
    if (InterlockedExchange(&g_primitive_guard, 1) != 0) {
        layer_drift_guard_bypass(renderer);
        result = g_original_terrain_clip_shade(renderer, x, y, width_word, height_word,
                                              source_word, shade_word);
        InterlockedExchange(&g_primitive_guard, 0);
        return result;
    }
    result = g_original_terrain_clip_shade(renderer, x, y, width_word, height_word,
                                          source_word, shade_word);
    mirror_reinvoke(renderer, args, 6u, width, height, source, shade,
                    width * height, G1_TERRAIN_CLIP_SHADE, TRUE);
    ++g_primitive_calls;
    ++g_writer_call_counts[6];
    InterlockedExchange(&g_primitive_guard, 0);
    return result;
}

/* The non-clipping bind path needs the whole sprite inside the screen.  A
 * sprite that straddles the edge is replayed through the viewport path instead
 * (the original writer clips itself to the renderer viewport). */
static BOOL tinted_origin_outside_screen(void *renderer, DWORD x, DWORD y,
                                         DWORD width, DWORD height)
{
    LONG origin_x = (LONG)(SHORT)x;
    LONG origin_y = (LONG)(SHORT)y;
    DWORD surface_height = *(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_HEIGHT);
    if (width > 800u || height > surface_height) return TRUE;
    return origin_x < 0 || origin_y < 0 ||
           (DWORD)origin_x > 800u - width ||
           (DWORD)origin_y > surface_height - height;
}

/* The two tinted sprite writers have six stack arguments and both return with
 * ret 0x18.  Keep the LUT pointer and its bytes in the asset identity. */
static DWORD __attribute__((thiscall)) mirror_tinted_rle(void *renderer,
                                                           DWORD x, DWORD y,
                                                           DWORD width_word,
                                                           DWORD height_word,
                                                           DWORD source_word,
                                                           DWORD lut_word)
{
    DWORD result, covered_before;
    DWORD width = (DWORD)(SHORT)width_word;
    DWORD height = (DWORD)(SHORT)height_word;
    const BYTE *source = (const BYTE *)(ULONG_PTR)source_word;
    const BYTE *lut = (const BYTE *)(ULONG_PTR)lut_word;
    const DWORD args[6] = {x, y, width_word, height_word, source_word, lut_word};
    if (!g_original_tinted_rle) return 0u;
    if (InterlockedExchange(&g_primitive_guard, 1) != 0) {
        layer_drift_guard_bypass(renderer);
        result = g_original_tinted_rle(renderer, x, y, width_word, height_word,
                                       source_word, lut_word);
        InterlockedExchange(&g_primitive_guard, 0);
        return result;
    }
    result = g_original_tinted_rle(renderer, x, y, width_word, height_word,
                                   source_word, lut_word);
    covered_before = g_covered_pixels;
    mirror_reinvoke(renderer, args, 6u, width, height, source, lut,
                    256u, G1_TINTED_RLE,
                    tinted_origin_outside_screen(renderer, x, y, width, height));
    ++g_primitive_calls;
    ++g_tinted_writer_calls[0];
    g_tinted_writer_covered[0] += g_covered_pixels - covered_before;
    InterlockedExchange(&g_primitive_guard, 0);
    return result;
}

static DWORD __attribute__((thiscall)) mirror_tinted_clip_rle(void *renderer,
                                                                DWORD x, DWORD y,
                                                                DWORD width_word,
                                                                DWORD height_word,
                                                                DWORD source_word,
                                                                DWORD lut_word)
{
    DWORD result, covered_before;
    DWORD width = (DWORD)(SHORT)width_word;
    DWORD height = (DWORD)(SHORT)height_word;
    const BYTE *source = (const BYTE *)(ULONG_PTR)source_word;
    const BYTE *lut = (const BYTE *)(ULONG_PTR)lut_word;
    const DWORD args[6] = {x, y, width_word, height_word, source_word, lut_word};
    if (!g_original_tinted_clip_rle) return 0u;
    if (InterlockedExchange(&g_primitive_guard, 1) != 0) {
        layer_drift_guard_bypass(renderer);
        result = g_original_tinted_clip_rle(renderer, x, y, width_word, height_word,
                                            source_word, lut_word);
        InterlockedExchange(&g_primitive_guard, 0);
        return result;
    }
    result = g_original_tinted_clip_rle(renderer, x, y, width_word, height_word,
                                        source_word, lut_word);
    covered_before = g_covered_pixels;
    mirror_reinvoke(renderer, args, 6u, width, height, source, lut,
                    256u, G1_TINTED_CLIP_RLE, TRUE);
    ++g_primitive_calls;
    ++g_tinted_writer_calls[1];
    g_tinted_writer_covered[1] += g_covered_pixels - covered_before;
    InterlockedExchange(&g_primitive_guard, 0);
    return result;
}

static void rect_fill_clip(void *renderer, int32_t clip[4])
{
    const volatile LONG *viewport =
        (const volatile LONG *)((BYTE *)renderer + G1_RENDERER_VIEWPORT);
    DWORD index;
    for (index = 0u; index < 4u; ++index) clip[index] = (int32_t)viewport[index];
}

/* Original returns: 0x466070 ret 0x14.  Solid clipped fill that lands on the
 * screen frame after the cache copy; only the pixels it changes are mirrored. */
static DWORD __attribute__((thiscall)) mirror_rect_fill(void *renderer, DWORD x1,
                                                         DWORD y1, DWORD x2,
                                                         DWORD y2, DWORD color)
{
    G1RectFill rect = {0, 0, 0u, 0u};
    int32_t clip[4];
    G1OverlayStats stats;
    BYTE *buffer = NULL;
    DWORD stride = 0u, row, col, result;
    BOOL active = FALSE;
    if (!g_original_rect_fill) return 0u;
    ++g_rect_fill_invocations;
    if (g_primitive_guard) {
        ++g_rect_fill_reject_guard;
    } else if (renderer && g_mirror && g_covered && g_expected_snapshot) {
        stride = *(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_STRIDE);
        buffer = *(BYTE **)((BYTE *)renderer + G1_RENDERER_BUFFER);
        if (!buffer || (DWORD)(ULONG_PTR)buffer == G1_CACHE_BASE ||
            buffer == g_panel_bound_buffer || stride < G1_OVERLAY_SCREEN_WIDTH ||
            stride > G1_MAX_STRIDE ||
            *(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_HEIGHT) !=
                G1_OVERLAY_SCREEN_HEIGHT) {
            ++g_rect_fill_reject_target;
        } else if (rect_fill_clip(renderer, clip),
                   g1_rect_fill_region((int32_t)x1, (int32_t)y1, (int32_t)x2,
                                       (int32_t)y2, clip, &rect)) {
            if (rect.x < 0 || rect.y < 0 ||
                !g1_overlay_blt_accepts(0, 0, 1, 1, G1_OVERLAY_SCREEN_WIDTH,
                                        G1_OVERLAY_SCREEN_HEIGHT, (size_t)rect.x,
                                        (size_t)rect.y, rect.width, rect.height)) {
                ++g_rect_fill_reject_size;
            } else {
                for (row = 0u; row < rect.height; ++row)
                    for (col = 0u; col < rect.width; ++col)
                        g_rect_fill_before[row * rect.width + col] =
                            buffer[(rect.y + row) * stride + rect.x + col];
                active = TRUE;
            }
        }
    }
    result = g_original_rect_fill(renderer, x1, y1, x2, y2, color);
    if (active) {
        if (g1_overlay_blt_apply(g_rect_fill_before, buffer, stride,
                                 (size_t)rect.x, (size_t)rect.y, rect.width,
                                 rect.height,
                                 lstrcmpA(g1_hd_asset_source_name(), "scale2x") == 0,
                                 g_overlay_scratch, g_expected_snapshot, g_covered,
                                 g_mirror, 1600u, &stats)) {
            ++g_rect_fill_mirrored_calls;
            g_rect_fill_mirrored_pixels += (DWORD)stats.changed;
        } else {
            ++g_rect_fill_reject_size;
        }
    }
    return result;
}

/* H-LB B-0: env-gated record of a 0x465B30 rectangle the mirror rejected (reason, raw
 * arguments, colour, renderer clip, stride, resulting region when there is one), capped
 * at 64 lines per run. */
static void rect_border_reject_log(const char *why, DWORD x1, DWORD y1, DWORD x2,
                                   DWORD y2, DWORD color, const int32_t clip[4],
                                   DWORD stride, const G1RectFill *rect)
{
    char line[320];
    if (!layer_drift_on() || g_rect_border_reject_logged >= 64u) return;
    ++g_rect_border_reject_logged;
    layer_drift_emit(line, wsprintfA(line,
        "{\"t\":\"g\",\"why\":\"%s\",\"p\":%u,\"x1\":%d,\"y1\":%d,\"x2\":%d,\"y2\":%d,\"c\":%u,\"clip\":[%d,%d,%d,%d],\"stride\":%u,\"rx\":%d,\"ry\":%d,\"rw\":%u,\"rh\":%u}\n",
        why, (unsigned)g_drift_present, (int)x1, (int)y1, (int)x2, (int)y2,
        (unsigned)color, (int)clip[0], (int)clip[1], (int)clip[2], (int)clip[3],
        (unsigned)stride, (int)rect->x, (int)rect->y, (unsigned)rect->width,
        (unsigned)rect->height));
}

/* Original returns: 0x465B30 ret 0x14 (leaf).  One-pixel rectangle outline;
 * every pixel it writes lies inside the same sorted+clipped rectangle as the
 * 0x466070 fill.  H-LB: the renderer clip can open into the stride padding, so the box is
 * limited to the visible screen (g1_rect_screen_region) and diffed in <=320x160 tiles. */
static DWORD __attribute__((thiscall)) mirror_rect_border(void *renderer, DWORD x1,
                                                         DWORD y1, DWORD x2,
                                                         DWORD y2, DWORD color)
{
    G1RectFill rect = {0, 0, 0u, 0u};
    int32_t clip[4];
    G1OverlayStats stats;
    BYTE *buffer = NULL;
    DWORD stride = 0u, row, col, result;
    size_t tiles = 0u;
    BOOL active = FALSE;
    if (!g_original_rect_border) return 0u;
    ++g_rect_border_invocations;
    if (g_primitive_guard) {
        ++g_rect_border_reject_guard;
    } else if (renderer && g_mirror && g_covered && g_expected_snapshot) {
        stride = *(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_STRIDE);
        buffer = *(BYTE **)((BYTE *)renderer + G1_RENDERER_BUFFER);
        if (!buffer || (DWORD)(ULONG_PTR)buffer == G1_CACHE_BASE ||
            buffer == g_panel_bound_buffer || stride < G1_OVERLAY_SCREEN_WIDTH ||
            stride > G1_MAX_STRIDE ||
            *(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_HEIGHT) !=
                G1_OVERLAY_SCREEN_HEIGHT) {
            ++g_rect_border_reject_target;
        } else if (rect_fill_clip(renderer, clip),
                   g1_rect_screen_region((int32_t)x1, (int32_t)y1, (int32_t)x2,
                                         (int32_t)y2, clip,
                                         (int32_t)G1_OVERLAY_SCREEN_WIDTH,
                                         (int32_t)G1_OVERLAY_SCREEN_HEIGHT, &rect)) {
            if (rect.x < 0 || rect.y < 0 ||
                (size_t)rect.x + rect.width > G1_OVERLAY_SCREEN_WIDTH ||
                (size_t)rect.y + rect.height > G1_OVERLAY_SCREEN_HEIGHT) {
                ++g_rect_border_reject_size;
                rect_border_reject_log("size", x1, y1, x2, y2, color, clip, stride, &rect);
            } else {
                for (row = 0u; row < rect.height; ++row)
                    for (col = 0u; col < rect.width; ++col)
                        g_rect_border_before[row * rect.width + col] =
                            buffer[(rect.y + row) * stride + rect.x + col];
                active = TRUE;
            }
        }
    }
    result = g_original_rect_border(renderer, x1, y1, x2, y2, color);
    if (active) {
        if (g1_overlay_blt_apply_tiled(g_rect_border_before, buffer, stride,
                                       (size_t)rect.x, (size_t)rect.y, rect.width,
                                       rect.height,
                                       lstrcmpA(g1_hd_asset_source_name(), "scale2x") == 0,
                                       g_overlay_scratch, g_rect_border_tile,
                                       g_expected_snapshot, g_covered, g_mirror, 1600u,
                                       &stats, &tiles)) {
            ++g_rect_border_mirrored_calls;
            g_rect_border_mirrored_pixels += (DWORD)stats.changed;
        } else {
            ++g_rect_border_reject_size;
        }
    }
    return result;
}

/* H-D2t: 0x465CA0 ret 0x1c (7 stack args: x0 y0 x1 y1 + 3 palette-LUT indices),
 * thiscall.  Sibling of 0x465B30: a one-pixel rectangle outline (selection drag
 * box) whose colour is looked up in the renderer table; the original sorts the
 * corners, rejects a rectangle outside [renderer+0x4D0..0x4DC] and draws only
 * the edges that lie inside it, so every written pixel is inside the sorted
 * rectangle clipped to the viewport.  That box (up to the whole screen) is
 * diffed in <=320x160 tiles from its own before copy. */
static DWORD __attribute__((thiscall)) mirror_rect_border7(void *renderer, DWORD x1,
                                                          DWORD y1, DWORD x2,
                                                          DWORD y2, DWORD c1,
                                                          DWORD c2, DWORD c3)
{
    G1RectFill rect = {0, 0, 0u, 0u};
    int32_t clip[4];
    G1OverlayStats stats;
    BYTE *buffer = NULL;
    DWORD stride = 0u, row, col, result;
    size_t tiles = 0u;
    BOOL active = FALSE;
    if (!g_original_rect_border7) return 0u;
    ++g_rect_border7_invocations;
    if (g_primitive_guard) {
        ++g_rect_border7_reject_guard;
    } else if (renderer && g_mirror && g_covered && g_expected_snapshot) {
        stride = *(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_STRIDE);
        buffer = *(BYTE **)((BYTE *)renderer + G1_RENDERER_BUFFER);
        if (!buffer || (DWORD)(ULONG_PTR)buffer == G1_CACHE_BASE ||
            buffer == g_panel_bound_buffer || stride < G1_OVERLAY_SCREEN_WIDTH ||
            stride > G1_MAX_STRIDE ||
            *(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_HEIGHT) !=
                G1_OVERLAY_SCREEN_HEIGHT) {
            ++g_rect_border7_reject_target;
        } else if (rect_fill_clip(renderer, clip),
                   g1_rect_fill_region((int32_t)x1, (int32_t)y1, (int32_t)x2,
                                       (int32_t)y2, clip, &rect)) {
            if (rect.x < 0 || rect.y < 0 || rect.width > G1_OVERLAY_SCREEN_WIDTH ||
                rect.height > G1_OVERLAY_SCREEN_HEIGHT ||
                (size_t)rect.x + rect.width > G1_OVERLAY_SCREEN_WIDTH ||
                (size_t)rect.y + rect.height > G1_OVERLAY_SCREEN_HEIGHT) {
                ++g_rect_border7_reject_size;
            } else {
                for (row = 0u; row < rect.height; ++row)
                    for (col = 0u; col < rect.width; ++col)
                        g_rect_border7_before[row * rect.width + col] =
                            buffer[(rect.y + row) * stride + rect.x + col];
                active = TRUE;
            }
        }
    }
    result = g_original_rect_border7(renderer, x1, y1, x2, y2, c1, c2, c3);
    if (active) {
        if (g1_overlay_blt_apply_tiled(g_rect_border7_before, buffer, stride,
                                       (size_t)rect.x, (size_t)rect.y, rect.width,
                                       rect.height,
                                       lstrcmpA(g1_hd_asset_source_name(), "scale2x") == 0,
                                       g_overlay_scratch, g_rect_border7_tile,
                                       g_expected_snapshot, g_covered, g_mirror, 1600u,
                                       &stats, &tiles)) {
            ++g_rect_border7_mirrored_calls;
            g_rect_border7_mirrored_pixels += (DWORD)stats.changed;
        } else {
            ++g_rect_border7_reject_size;
        }
    }
    return result;
}

/* H-LN: 0x4659B0 ret 0x14 (5 stack args: x0 y0 x1 y1 colour), thiscall.  Clipped
 * Bresenham-style line (selection/drag overlay): max(|dx|,|dy|)+2 plots through the
 * 0x465900 clip [renderer+0x4D0..0x4DC].  Every written pixel lies inside the end-point
 * box grown by 1 px and clipped (g1_line_region); that box is diffed in <=320x160 tiles
 * from its own before copy.  0x465900 is only called from here and is not hooked. */
static DWORD __attribute__((thiscall)) mirror_line(void *renderer, DWORD x0, DWORD y0,
                                                  DWORD x1, DWORD y1, DWORD color)
{
    G1RectFill rect = {0, 0, 0u, 0u};
    int32_t clip[4];
    G1OverlayStats stats;
    BYTE *buffer = NULL;
    DWORD stride = 0u, row, col, result;
    size_t tiles = 0u;
    BOOL active = FALSE;
    if (!g_original_line) return 0u;
    ++g_line_invocations;
    if (g_primitive_guard) {
        ++g_line_reject_guard;
    } else if (renderer && g_mirror && g_covered && g_expected_snapshot) {
        stride = *(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_STRIDE);
        buffer = *(BYTE **)((BYTE *)renderer + G1_RENDERER_BUFFER);
        if (!buffer || (DWORD)(ULONG_PTR)buffer == G1_CACHE_BASE ||
            buffer == g_panel_bound_buffer || stride < G1_OVERLAY_SCREEN_WIDTH ||
            stride > G1_MAX_STRIDE ||
            *(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_HEIGHT) !=
                G1_OVERLAY_SCREEN_HEIGHT) {
            ++g_line_reject_target;
        } else if (rect_fill_clip(renderer, clip),
                   g1_line_region((int32_t)x0, (int32_t)y0, (int32_t)x1, (int32_t)y1,
                                  clip, &rect)) {
            if (rect.x < 0 || rect.y < 0 || rect.width > G1_OVERLAY_SCREEN_WIDTH ||
                rect.height > G1_OVERLAY_SCREEN_HEIGHT ||
                (size_t)rect.x + rect.width > G1_OVERLAY_SCREEN_WIDTH ||
                (size_t)rect.y + rect.height > G1_OVERLAY_SCREEN_HEIGHT) {
                ++g_line_reject_size;
            } else {
                for (row = 0u; row < rect.height; ++row)
                    for (col = 0u; col < rect.width; ++col)
                        g_line_before[row * rect.width + col] =
                            buffer[(rect.y + row) * stride + rect.x + col];
                active = TRUE;
            }
        }
    }
    result = g_original_line(renderer, x0, y0, x1, y1, color);
    if (active) {
        if (g1_overlay_blt_apply_tiled(g_line_before, buffer, stride, (size_t)rect.x,
                                       (size_t)rect.y, rect.width, rect.height,
                                       lstrcmpA(g1_hd_asset_source_name(), "scale2x") == 0,
                                       g_overlay_scratch, g_line_tile, g_expected_snapshot,
                                       g_covered, g_mirror, 1600u, &stats, &tiles)) {
            ++g_line_mirrored_calls;
            g_line_mirrored_pixels += (DWORD)stats.changed;
        } else {
            ++g_line_reject_size;
        }
    }
    return result;
}

/* H-Z Z-1(a): env-gated record of a 0x465E80 rectangle the mirror rejected
 * (reason, raw arguments, target stride/buffer, whether the buffer is the
 * panel-bound or cache buffer), capped at 64 lines per run. */
static void rect_solid_reject_log(const char *why, DWORD x0, DWORD y0, DWORD x1,
                                  DWORD y1, DWORD color, DWORD stride,
                                  const BYTE *buffer)
{
    char line[256];
    if (!layer_drift_on() || g_rect_solid_reject_logged >= 64u) return;
    ++g_rect_solid_reject_logged;
    layer_drift_emit(line, wsprintfA(line,
        "{\"t\":\"q\",\"why\":\"%s\",\"p\":%u,\"x0\":%d,\"y0\":%d,\"x1\":%d,\"y1\":%d,\"c\":%u,\"stride\":%u,\"buf\":%u,\"panel\":%u,\"cache\":%u}\n",
        why, (unsigned)g_drift_present, (int)x0, (int)y0, (int)x1, (int)y1,
        (unsigned)color, (unsigned)stride, (unsigned)(ULONG_PTR)buffer,
        (unsigned)(buffer == g_panel_bound_buffer),
        (unsigned)((DWORD)(ULONG_PTR)buffer == G1_CACHE_BASE)));
}

/* Original returns: 0x465E80 ret 0x14 (leaf, 5 stack args: x0 y0 x1 y1 color).
 * Unclipped solid rectangle: nothing is written unless every corner lies in
 * [0, stride) x [0, [renderer+0x14]), so the wrapper replicates that check
 * (reject_bounds, never cut) and mirrors the sorted inclusive rectangle
 * intersected with the logical screen.  No viewport intersection. */
static DWORD __attribute__((thiscall)) mirror_rect_solid(void *renderer, DWORD x0,
                                                        DWORD y0, DWORD x1,
                                                        DWORD y1, DWORD color)
{
    G1RectFill rect = {0, 0, 0u, 0u};
    G1OverlayStats stats;
    BYTE *buffer = NULL;
    DWORD stride = 0u, row, col, result;
    BOOL active = FALSE;
    if (!g_original_rect_solid) return 0u;
    ++g_rect_solid_invocations;
    if (g_primitive_guard) {
        ++g_rect_solid_reject_guard;
    } else if (renderer && g_mirror && g_covered && g_expected_snapshot) {
        stride = *(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_STRIDE);
        buffer = *(BYTE **)((BYTE *)renderer + G1_RENDERER_BUFFER);
        if (!buffer || (DWORD)(ULONG_PTR)buffer == G1_CACHE_BASE ||
            buffer == g_panel_bound_buffer || stride < G1_OVERLAY_SCREEN_WIDTH ||
            stride > G1_MAX_STRIDE ||
            *(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_HEIGHT) !=
                G1_OVERLAY_SCREEN_HEIGHT) {
            ++g_rect_solid_reject_target;
            rect_solid_reject_log("target", x0, y0, x1, y1, color, stride, buffer);
        } else {
            DWORD ybound = *(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_YBOUND);
            if (!g_rect_solid_ybound) g_rect_solid_ybound = ybound;
            if (!g1_rect_solid_region((int32_t)x0, (int32_t)y0, (int32_t)x1,
                                      (int32_t)y1, (int32_t)stride,
                                      (int32_t)ybound,
                                      (int32_t)G1_OVERLAY_SCREEN_WIDTH,
                                      (int32_t)G1_OVERLAY_SCREEN_HEIGHT, &rect)) {
                ++g_rect_solid_reject_bounds;
            } else if (!g1_overlay_blt_accepts(0, 0, 1, 1, G1_OVERLAY_SCREEN_WIDTH,
                                               G1_OVERLAY_SCREEN_HEIGHT,
                                               (size_t)rect.x, (size_t)rect.y,
                                               g_rect_solid_wide_enabled &&
                                                   rect.width > G1_OVERLAY_MAX_WIDTH
                                                   ? G1_OVERLAY_MAX_WIDTH : rect.width,
                                               g_rect_solid_wide_enabled &&
                                                   rect.height > G1_OVERLAY_MAX_HEIGHT
                                                   ? G1_OVERLAY_MAX_HEIGHT : rect.height)) {
                ++g_rect_solid_reject_size;
                rect_solid_reject_log("size", x0, y0, x1, y1, color, stride, buffer);
            } else {
                for (row = 0u; row < rect.height; ++row)
                    for (col = 0u; col < rect.width; ++col)
                        g_rect_solid_before[row * rect.width + col] =
                            buffer[(rect.y + row) * stride + rect.x + col];
                active = TRUE;
            }
        }
    }
    result = g_original_rect_solid(renderer, x0, y0, x1, y1, color);
    if (active) {
        size_t tiles = 0u;
        BOOL wide = rect.width > G1_OVERLAY_MAX_WIDTH || rect.height > G1_OVERLAY_MAX_HEIGHT;
        if (wide ? g1_overlay_blt_apply_tiled(g_rect_solid_before, buffer, stride,
                                              (size_t)rect.x, (size_t)rect.y, rect.width,
                                              rect.height,
                                              lstrcmpA(g1_hd_asset_source_name(), "scale2x") == 0,
                                              g_overlay_scratch, g_rect_solid_tile,
                                              g_expected_snapshot, g_covered, g_mirror,
                                              1600u, &stats, &tiles)
                 : g1_overlay_blt_apply(g_rect_solid_before, buffer, stride,
                                        (size_t)rect.x, (size_t)rect.y, rect.width,
                                        rect.height,
                                        lstrcmpA(g1_hd_asset_source_name(), "scale2x") == 0,
                                        g_overlay_scratch, g_expected_snapshot, g_covered,
                                        g_mirror, 1600u, &stats)) {
            if (wide) ++g_rect_solid_wide_calls;
            ++g_rect_solid_mirrored_calls;
            g_rect_solid_mirrored_pixels += (DWORD)stats.changed;
        } else {
            ++g_rect_solid_reject_size;
        }
    }
    return result;
}

/* Original returns: 0x466B50 ret 0x18 (6 stack args: x y width height rle lut).
 * Unclipped left/right-flipped remap RLE.  The original uses all four
 * rectangle arguments as full 32-bit signed values and never clips, so a
 * rectangle past the screen edge writes into the stride padding or wraps into
 * the next row.  H-R: the wrapper mirrors only the screen intersection
 * [0,800) x [0,600) (rows are diffed in a dedicated before buffer), counts
 * calls that leave [0, stride) x [0, 600) in wrap_calls and forwards the six
 * original arguments unchanged exactly once. */
static DWORD __attribute__((thiscall)) mirror_flip_rle(void *renderer, DWORD a_x,
                                                      DWORD a_y, DWORD a_w,
                                                      DWORD a_h, DWORD rle,
                                                      DWORD lut)
{
    G1OverlayStats stats;
    G1FlipRleRegion region;
    BYTE *buffer = NULL;
    int32_t x = (int32_t)a_x, y = (int32_t)a_y, width = (int32_t)a_w,
            height = (int32_t)a_h;
    DWORD stride = 0u, result, row, col;
    BOOL active = FALSE;
    G1DriftWrite drift;
    const char *why = "not_ready";
    if (!g_original_flip_rle) return 0u;
    ++g_flip_rle_invocations;
    layer_drift_write_begin(&drift, renderer);
    if (g_primitive_guard) {
        why = "guard";
        ++g_flip_rle_reject_guard;
    } else if (renderer && g_mirror && g_covered && g_expected_snapshot) {
        stride = *(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_STRIDE);
        buffer = *(BYTE **)((BYTE *)renderer + G1_RENDERER_BUFFER);
        if (!buffer || (DWORD)(ULONG_PTR)buffer == G1_CACHE_BASE ||
            buffer == g_panel_bound_buffer || stride < G1_OVERLAY_SCREEN_WIDTH ||
            stride > G1_MAX_STRIDE ||
            *(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_HEIGHT) !=
                G1_OVERLAY_SCREEN_HEIGHT) {
            why = "reject_target";
            ++g_flip_rle_reject_target;
        } else {
            BOOL inside = g1_flip_rle_region(x, y, width, height, (int32_t)stride,
                                             (int32_t)G1_OVERLAY_SCREEN_WIDTH,
                                             (int32_t)G1_OVERLAY_SCREEN_HEIGHT,
                                             &region);
            if (region.wrap) ++g_flip_rle_wrap_calls;
            if (!inside) {
                why = "reject_bounds";
                ++g_flip_rle_reject_bounds;
            } else if (region.width > G1_OVERLAY_MAX_WIDTH ||
                       region.height > G1_OVERLAY_MAX_HEIGHT) {
                why = "reject_size";
                ++g_flip_rle_reject_size;
            } else {
                why = "mirrored";
                if (region.clipped) {
                    why = "clipped";
                    ++g_flip_rle_clipped_calls;
                }
                for (row = 0u; row < region.height; ++row)
                    for (col = 0u; col < region.width; ++col)
                        g_flip_rle_before[row * region.width + col] =
                            buffer[(DWORD)(region.y + row) * stride +
                                   (DWORD)region.x + col];
                active = TRUE;
            }
        }
    }
    result = g_original_flip_rle(renderer, a_x, a_y, a_w, a_h, rle, lut);
    if (active && !region.clipped && !region.wrap && g1_hd_asset_flip_key_path()) {
        /* H-HDU0: a rectangle fully on screen takes the tinted key path (source, remap table and
         * size are the identity; the pack frame is flipped by the loader).  When the key does not
         * become ready the diff mirror below still covers the call. */
        const DWORD key_args[6] = {a_x, a_y, a_w, a_h, rle, lut};
        InterlockedExchange(&g_primitive_guard, 1);
        mirror_reinvoke(renderer, key_args, 6u, region.width, region.height,
                        (const BYTE *)(ULONG_PTR)rle, (const BYTE *)(ULONG_PTR)lut,
                        256u, G1_FLIP_RLE, FALSE);
        InterlockedExchange(&g_primitive_guard, 0);
        if (g_reinvoke_composed) {
            ++g_flip_rle_keyed_calls;
            active = FALSE;
            why = "keyed";
        } else {
            ++g_flip_rle_key_fallbacks;
        }
    }
    if (active) {
        if (g1_overlay_blt_apply(g_flip_rle_before, buffer, stride,
                                 (size_t)region.x, (size_t)region.y, region.width,
                                 region.height,
                                 lstrcmpA(g1_hd_asset_source_name(), "scale2x") == 0,
                                 g_overlay_scratch, g_expected_snapshot, g_covered,
                                 g_mirror, 1600u, &stats)) {
            ++g_flip_rle_mirrored_calls;
            g_flip_rle_mirrored_pixels += (DWORD)stats.changed;
        } else {
            why = "reject_size";
            ++g_flip_rle_reject_size;
        }
    }
    layer_drift_write_end(&drift, G1_FLIP_RLE, why, x, y, width, height);
    return result;
}

/* Original returns: 0x466480 ret 0x14 (thiscall, 5 stack args: x y width height src).
 * Unclipped colorkey copy: dest = [renderer+0x1514] + y*[renderer+0x10] + x, `height` rows
 * of `width` bytes read contiguously from `src`, bytes equal to 0xFE are skipped, all four
 * rectangle arguments are signed 32-bit and nothing is clipped.  H-TM1: the wrapper diffs the
 * screen intersection of the rectangle in tiles (screen-sized before copy) and forwards the
 * five original arguments unchanged exactly once.  The prologue (8B 51 10 / 53 / 8B C2) is
 * six relocatable bytes. */
static DWORD __attribute__((thiscall)) mirror_keyed_copy(void *renderer, DWORD a_x,
                                                        DWORD a_y, DWORD a_w,
                                                        DWORD a_h, DWORD src)
{
    G1OverlayStats stats;
    G1FlipRleRegion region;
    BYTE *buffer = NULL;
    int32_t x = (int32_t)a_x, y = (int32_t)a_y, width = (int32_t)a_w,
            height = (int32_t)a_h;
    DWORD stride = 0u, result, row, col;
    size_t tiles = 0u;
    BOOL active = FALSE;
    G1DriftWrite drift;
    const char *why = "not_ready";
    if (!g_original_keyed_copy) return 0u;
    ++g_keyed_copy_invocations;
    layer_drift_write_begin(&drift, renderer);
    if (!g_keyed_copy_enabled) {
        why = "off";
    } else if (g_primitive_guard) {
        why = "guard";
        ++g_keyed_copy_reject_guard;
    } else if (renderer && g_mirror && g_covered && g_expected_snapshot) {
        stride = *(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_STRIDE);
        buffer = *(BYTE **)((BYTE *)renderer + G1_RENDERER_BUFFER);
        if (!buffer || (DWORD)(ULONG_PTR)buffer == G1_CACHE_BASE ||
            buffer == g_panel_bound_buffer || stride < G1_OVERLAY_SCREEN_WIDTH ||
            stride > G1_MAX_STRIDE ||
            *(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_HEIGHT) !=
                G1_OVERLAY_SCREEN_HEIGHT) {
            why = "reject_target";
            ++g_keyed_copy_reject_target;
        } else if (!g1_flip_rle_region(x, y, width, height, (int32_t)stride,
                                       (int32_t)G1_OVERLAY_SCREEN_WIDTH,
                                       (int32_t)G1_OVERLAY_SCREEN_HEIGHT, &region)) {
            why = "reject_bounds";
            ++g_keyed_copy_reject_bounds;
        } else {
            why = "mirrored";
            if (region.clipped) {
                why = "clipped";
                ++g_keyed_copy_clipped_calls;
            }
            for (row = 0u; row < region.height; ++row)
                for (col = 0u; col < region.width; ++col)
                    g_keyed_copy_before[row * region.width + col] =
                        buffer[((DWORD)region.y + row) * stride + (DWORD)region.x + col];
            active = TRUE;
        }
    }
    result = g_original_keyed_copy(renderer, a_x, a_y, a_w, a_h, src);
    if (active) {
        if (g1_overlay_blt_apply_tiled(g_keyed_copy_before, buffer, stride,
                                       (size_t)region.x, (size_t)region.y, region.width,
                                       region.height,
                                       lstrcmpA(g1_hd_asset_source_name(), "scale2x") == 0,
                                       g_overlay_scratch, g_keyed_copy_tile,
                                       g_expected_snapshot, g_covered, g_mirror, 1600u,
                                       &stats, &tiles)) {
            ++g_keyed_copy_mirrored_calls;
            g_keyed_copy_mirrored_pixels += (DWORD)stats.changed;
            if (stats.changed) ++g_keyed_copy_changed_calls;
        } else {
            why = "reject_size";
            ++g_keyed_copy_reject_size;
        }
    }
    layer_drift_write_end(&drift, G1_KEYED_COPY, why, x, y, width, height);
    return result;
}

/* Original returns: 0x466BE0 ret 0x18 (6 stack args: x y width height rle lut).
 * Clipped left/right-flipped remap RLE, the clip-box sibling of 0x466B50.  The
 * original uses the four rectangle arguments as full 32-bit signed values and
 * clips the write to the renderer clip box ([+0x4D0..+0x4D8] x [+0x4D4..+0x4DC]),
 * so every pixel it writes lies inside rect ∩ clip.  H-V: the wrapper mirrors the
 * screen intersection of the rectangle like mirror_flip_rle (rows are diffed in a
 * dedicated before buffer), counts calls that leave [0, stride) x [0, 600) in
 * wrap_calls and forwards the six original arguments unchanged exactly once. */
static DWORD __attribute__((thiscall)) mirror_flip_clip(void *renderer, DWORD a_x,
                                                      DWORD a_y, DWORD a_w,
                                                      DWORD a_h, DWORD rle,
                                                      DWORD lut)
{
    G1OverlayStats stats;
    G1FlipRleRegion region;
    BYTE *buffer = NULL;
    int32_t x = (int32_t)a_x, y = (int32_t)a_y, width = (int32_t)a_w,
            height = (int32_t)a_h;
    DWORD stride = 0u, result, row, col;
    BOOL active = FALSE;
    G1DriftWrite drift;
    const char *why = "not_ready";
    if (!g_original_flip_clip) return 0u;
    ++g_flip_clip_invocations;
    layer_drift_write_begin(&drift, renderer);
    if (g_primitive_guard) {
        why = "guard";
        ++g_flip_clip_reject_guard;
    } else if (renderer && g_mirror && g_covered && g_expected_snapshot) {
        stride = *(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_STRIDE);
        buffer = *(BYTE **)((BYTE *)renderer + G1_RENDERER_BUFFER);
        if (!buffer || (DWORD)(ULONG_PTR)buffer == G1_CACHE_BASE ||
            buffer == g_panel_bound_buffer || stride < G1_OVERLAY_SCREEN_WIDTH ||
            stride > G1_MAX_STRIDE ||
            *(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_HEIGHT) !=
                G1_OVERLAY_SCREEN_HEIGHT) {
            why = "reject_target";
            ++g_flip_clip_reject_target;
        } else {
            BOOL inside = g1_flip_rle_region(x, y, width, height, (int32_t)stride,
                                             (int32_t)G1_OVERLAY_SCREEN_WIDTH,
                                             (int32_t)G1_OVERLAY_SCREEN_HEIGHT,
                                             &region);
            if (region.wrap) ++g_flip_clip_wrap_calls;
            if (!inside) {
                why = "reject_bounds";
                ++g_flip_clip_reject_bounds;
            } else if (region.width > G1_OVERLAY_MAX_WIDTH ||
                       region.height > G1_OVERLAY_MAX_HEIGHT) {
                why = "reject_size";
                ++g_flip_clip_reject_size;
            } else {
                why = "mirrored";
                if (region.clipped) {
                    why = "clipped";
                    ++g_flip_clip_clipped_calls;
                }
                for (row = 0u; row < region.height; ++row)
                    for (col = 0u; col < region.width; ++col)
                        g_flip_clip_before[row * region.width + col] =
                            buffer[(DWORD)(region.y + row) * stride +
                                   (DWORD)region.x + col];
                active = TRUE;
            }
        }
    }
    result = g_original_flip_clip(renderer, a_x, a_y, a_w, a_h, rle, lut);
    if (active && g1_hd_asset_flip_key_path() &&
        x >= -32768 && x <= 32767 && y >= -32768 && y <= 32767 &&
        width > 0 && width <= 800 && height > 0 && height <= 600) {
        /* H-HDU1: the clip-box flip draw takes the same key path as 0x466540 (whole sprite rectangle,
         * viewport replay for the written mask).  `region.wrap` does not apply: this writer clips to the
         * viewport instead of wrapping, so an edge sprite is exactly the case the replay is for.  A key
         * that does not become ready leaves the call to the diff mirror below. */
        const DWORD key_args[6] = {a_x, a_y, a_w, a_h, rle, lut};
        InterlockedExchange(&g_primitive_guard, 1);
        mirror_reinvoke(renderer, key_args, 6u, (DWORD)width, (DWORD)height,
                        (const BYTE *)(ULONG_PTR)rle, (const BYTE *)(ULONG_PTR)lut,
                        256u, G1_FLIP_CLIP, TRUE);
        InterlockedExchange(&g_primitive_guard, 0);
        if (g_reinvoke_composed) {
            ++g_flip_clip_keyed_calls;
            active = FALSE;
            why = "keyed";
        } else {
            ++g_flip_clip_key_fallbacks;
        }
    }
    if (active) {
        if (g1_overlay_blt_apply(g_flip_clip_before, buffer, stride,
                                 (size_t)region.x, (size_t)region.y, region.width,
                                 region.height,
                                 lstrcmpA(g1_hd_asset_source_name(), "scale2x") == 0,
                                 g_overlay_scratch, g_expected_snapshot, g_covered,
                                 g_mirror, 1600u, &stats)) {
            ++g_flip_clip_mirrored_calls;
            if (stats.changed) ++g_flip_clip_changed_calls;
            g_flip_clip_mirrored_pixels += (DWORD)stats.changed;
        } else {
            why = "reject_size";
            ++g_flip_clip_reject_size;
        }
    }
    layer_drift_write_end(&drift, G1_FLIP_CLIP, why, x, y, width, height);
    return result;
}

/* Original returns: 0x4687F0 ret 0x18 (6 stack args: x y width height rle lut), thiscall.
 * The original uses the four rectangle arguments as full 32-bit signed values, has no clip
 * and rewrites each destination pixel it covers through `lut` (destination-dependent remap,
 * no left-right flip, RLE pointer continues across rows).  H-W: the wrapper mirrors the
 * screen intersection of the rectangle like mirror_flip_rle (rows are diffed in a dedicated
 * before buffer), counts calls that leave [0, stride) x [0, 600) in wrap_calls and forwards
 * the six original arguments unchanged exactly once.  The prologue's second instruction is
 * esp-relative, so the call must keep the original stack frame (install_one trampoline). */
static DWORD __attribute__((thiscall)) mirror_shade_rle(void *renderer, DWORD a_x,
                                                      DWORD a_y, DWORD a_w,
                                                      DWORD a_h, DWORD rle,
                                                      DWORD lut)
{
    G1OverlayStats stats;
    G1FlipRleRegion region;
    BYTE *buffer = NULL;
    int32_t x = (int32_t)a_x, y = (int32_t)a_y, width = (int32_t)a_w,
            height = (int32_t)a_h;
    DWORD stride = 0u, result, row, col;
    BOOL active = FALSE;
    G1DriftWrite drift;
    const char *why = "not_ready";
    if (!g_original_shade_rle) return 0u;
    ++g_shade_rle_invocations;
    layer_drift_write_begin(&drift, renderer);
    if (g_primitive_guard) {
        why = "guard";
        ++g_shade_rle_reject_guard;
    } else if (renderer && g_mirror && g_covered && g_expected_snapshot) {
        stride = *(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_STRIDE);
        buffer = *(BYTE **)((BYTE *)renderer + G1_RENDERER_BUFFER);
        if (!buffer || (DWORD)(ULONG_PTR)buffer == G1_CACHE_BASE ||
            buffer == g_panel_bound_buffer || stride < G1_OVERLAY_SCREEN_WIDTH ||
            stride > G1_MAX_STRIDE ||
            *(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_HEIGHT) !=
                G1_OVERLAY_SCREEN_HEIGHT) {
            why = "reject_target";
            ++g_shade_rle_reject_target;
        } else {
            BOOL inside = g1_flip_rle_region(x, y, width, height, (int32_t)stride,
                                             (int32_t)G1_OVERLAY_SCREEN_WIDTH,
                                             (int32_t)G1_OVERLAY_SCREEN_HEIGHT,
                                             &region);
            if (region.wrap) ++g_shade_rle_wrap_calls;
            if (!inside) {
                why = "reject_bounds";
                ++g_shade_rle_reject_bounds;
            } else if (region.width > G1_OVERLAY_MAX_WIDTH ||
                       region.height > G1_OVERLAY_MAX_HEIGHT) {
                why = "reject_size";
                ++g_shade_rle_reject_size;
            } else {
                why = "mirrored";
                if (region.clipped) {
                    why = "clipped";
                    ++g_shade_rle_clipped_calls;
                }
                for (row = 0u; row < region.height; ++row)
                    for (col = 0u; col < region.width; ++col)
                        g_shade_rle_before[row * region.width + col] =
                            buffer[(DWORD)(region.y + row) * stride +
                                   (DWORD)region.x + col];
                active = TRUE;
            }
        }
    }
    result = g_original_shade_rle(renderer, a_x, a_y, a_w, a_h, rle, lut);
    if (active) {
        if (g1_overlay_blt_apply(g_shade_rle_before, buffer, stride,
                                 (size_t)region.x, (size_t)region.y, region.width,
                                 region.height,
                                 lstrcmpA(g1_hd_asset_source_name(), "scale2x") == 0,
                                 g_overlay_scratch, g_expected_snapshot, g_covered,
                                 g_mirror, 1600u, &stats)) {
            ++g_shade_rle_mirrored_calls;
            if (stats.changed) ++g_shade_rle_changed_calls;
            g_shade_rle_mirrored_pixels += (DWORD)stats.changed;
        } else {
            why = "reject_size";
            ++g_shade_rle_reject_size;
        }
    }
    layer_drift_write_end(&drift, G1_SHADE_RLE, why, x, y, width, height);
    return result;
}

/* Original returns: 0x4689C0 ret 0x18 (6 stack args: x y width height rle lut), thiscall.
 * Same as 0x4687F0 but mirrored left to right: the column of RLE position k is w-1-k
 * (16-bit sign-extended) and the destination pixel is read, remapped through `lut` and
 * written back in place.  The write set is still the rectangle [x, x+w) x [y, y+h), no clip,
 * 32-bit rectangle arguments.  H-X: the wrapper mirrors the screen intersection of the
 * rectangle like mirror_shade_rle (dedicated before buffer, wrap_calls for calls that leave
 * [0, stride) x [0, 600)) and forwards the six original arguments unchanged exactly once.
 * The prologue is five 1-byte pushes, so the install_one trampoline is safe. */
static DWORD __attribute__((thiscall)) mirror_shade_flip(void *renderer, DWORD a_x,
                                                      DWORD a_y, DWORD a_w,
                                                      DWORD a_h, DWORD rle,
                                                      DWORD lut)
{
    G1OverlayStats stats;
    G1FlipRleRegion region;
    BYTE *buffer = NULL;
    int32_t x = (int32_t)a_x, y = (int32_t)a_y, width = (int32_t)a_w,
            height = (int32_t)a_h;
    DWORD stride = 0u, result, row, col;
    BOOL active = FALSE;
    G1DriftWrite drift;
    const char *why = "not_ready";
    if (!g_original_shade_flip) return 0u;
    ++g_shade_flip_invocations;
    layer_drift_write_begin(&drift, renderer);
    if (g_primitive_guard) {
        why = "guard";
        ++g_shade_flip_reject_guard;
    } else if (renderer && g_mirror && g_covered && g_expected_snapshot) {
        stride = *(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_STRIDE);
        buffer = *(BYTE **)((BYTE *)renderer + G1_RENDERER_BUFFER);
        if (!buffer || (DWORD)(ULONG_PTR)buffer == G1_CACHE_BASE ||
            buffer == g_panel_bound_buffer || stride < G1_OVERLAY_SCREEN_WIDTH ||
            stride > G1_MAX_STRIDE ||
            *(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_HEIGHT) !=
                G1_OVERLAY_SCREEN_HEIGHT) {
            why = "reject_target";
            ++g_shade_flip_reject_target;
        } else {
            BOOL inside = g1_flip_rle_region(x, y, width, height, (int32_t)stride,
                                             (int32_t)G1_OVERLAY_SCREEN_WIDTH,
                                             (int32_t)G1_OVERLAY_SCREEN_HEIGHT,
                                             &region);
            if (region.wrap) ++g_shade_flip_wrap_calls;
            if (!inside) {
                why = "reject_bounds";
                ++g_shade_flip_reject_bounds;
            } else if (region.width > G1_OVERLAY_MAX_WIDTH ||
                       region.height > G1_OVERLAY_MAX_HEIGHT) {
                why = "reject_size";
                ++g_shade_flip_reject_size;
            } else {
                why = "mirrored";
                if (region.clipped) {
                    why = "clipped";
                    ++g_shade_flip_clipped_calls;
                }
                for (row = 0u; row < region.height; ++row)
                    for (col = 0u; col < region.width; ++col)
                        g_shade_flip_before[row * region.width + col] =
                            buffer[(DWORD)(region.y + row) * stride +
                                   (DWORD)region.x + col];
                active = TRUE;
            }
        }
    }
    result = g_original_shade_flip(renderer, a_x, a_y, a_w, a_h, rle, lut);
    if (active) {
        if (g1_overlay_blt_apply(g_shade_flip_before, buffer, stride,
                                 (size_t)region.x, (size_t)region.y, region.width,
                                 region.height,
                                 lstrcmpA(g1_hd_asset_source_name(), "scale2x") == 0,
                                 g_overlay_scratch, g_expected_snapshot, g_covered,
                                 g_mirror, 1600u, &stats)) {
            ++g_shade_flip_mirrored_calls;
            if (stats.changed) ++g_shade_flip_changed_calls;
            g_shade_flip_mirrored_pixels += (DWORD)stats.changed;
        } else {
            why = "reject_size";
            ++g_shade_flip_reject_size;
        }
    }
    layer_drift_write_end(&drift, G1_SHADE_FLIP, why, x, y, width, height);
    return result;
}

/* Original returns: 0x468870 ret 0x18 (6 stack args: x y width height rle lut), thiscall.
 * H-S3t: clipped sibling of 0x4687F0 (single caller 0x41A1F0, ecx = the screen renderer): the
 * destination pixel is read, remapped through `lut` and written back in place, but only inside
 * the intersection of [x, x+w) x [y, y+h) with the renderer clip rectangle (+0x4D0..+0x4DC);
 * the 0xFE n bytes skip n columns.  32-bit rectangle arguments.  The wrapper mirrors the
 * screen intersection of the passed rectangle like mirror_shade_rle (a superset of what the
 * original can touch; dedicated before buffer, wrap_calls for calls that leave
 * [0, stride) x [0, 600)) and forwards the six original arguments unchanged exactly once.
 * The prologue is `sub esp,0x14; mov edx,[esp+0x1c]` (3 + 4 B, the second is esp-relative),
 * so the call must keep the original stack frame (install_one trampoline). */
static DWORD __attribute__((thiscall)) mirror_shade_clip(void *renderer, DWORD a_x,
                                                      DWORD a_y, DWORD a_w,
                                                      DWORD a_h, DWORD rle,
                                                      DWORD lut)
{
    G1OverlayStats stats;
    G1FlipRleRegion region;
    BYTE *buffer = NULL;
    int32_t x = (int32_t)a_x, y = (int32_t)a_y, width = (int32_t)a_w,
            height = (int32_t)a_h;
    DWORD stride = 0u, result, row, col;
    BOOL active = FALSE;
    G1DriftWrite drift;
    const char *why = "not_ready";
    if (!g_original_shade_clip) return 0u;
    ++g_shade_clip_invocations;
    layer_drift_write_begin(&drift, renderer);
    if (g_primitive_guard) {
        why = "guard";
        ++g_shade_clip_reject_guard;
    } else if (renderer && g_mirror && g_covered && g_expected_snapshot) {
        stride = *(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_STRIDE);
        buffer = *(BYTE **)((BYTE *)renderer + G1_RENDERER_BUFFER);
        if (!buffer || (DWORD)(ULONG_PTR)buffer == G1_CACHE_BASE ||
            buffer == g_panel_bound_buffer || stride < G1_OVERLAY_SCREEN_WIDTH ||
            stride > G1_MAX_STRIDE ||
            *(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_HEIGHT) !=
                G1_OVERLAY_SCREEN_HEIGHT) {
            why = "reject_target";
            ++g_shade_clip_reject_target;
        } else {
            BOOL inside = g1_flip_rle_region(x, y, width, height, (int32_t)stride,
                                             (int32_t)G1_OVERLAY_SCREEN_WIDTH,
                                             (int32_t)G1_OVERLAY_SCREEN_HEIGHT,
                                             &region);
            if (region.wrap) ++g_shade_clip_wrap_calls;
            if (!inside) {
                why = "reject_bounds";
                ++g_shade_clip_reject_bounds;
            } else if (region.width > G1_OVERLAY_MAX_WIDTH ||
                       region.height > G1_OVERLAY_MAX_HEIGHT) {
                why = "reject_size";
                ++g_shade_clip_reject_size;
            } else {
                why = "mirrored";
                if (region.clipped) {
                    why = "clipped";
                    ++g_shade_clip_clipped_calls;
                }
                for (row = 0u; row < region.height; ++row)
                    for (col = 0u; col < region.width; ++col)
                        g_shade_clip_before[row * region.width + col] =
                            buffer[(DWORD)(region.y + row) * stride +
                                   (DWORD)region.x + col];
                active = TRUE;
            }
        }
    }
    result = g_original_shade_clip(renderer, a_x, a_y, a_w, a_h, rle, lut);
    if (active) {
        if (g1_overlay_blt_apply(g_shade_clip_before, buffer, stride,
                                 (size_t)region.x, (size_t)region.y, region.width,
                                 region.height,
                                 lstrcmpA(g1_hd_asset_source_name(), "scale2x") == 0,
                                 g_overlay_scratch, g_expected_snapshot, g_covered,
                                 g_mirror, 1600u, &stats)) {
            ++g_shade_clip_mirrored_calls;
            if (stats.changed) ++g_shade_clip_changed_calls;
            g_shade_clip_mirrored_pixels += (DWORD)stats.changed;
        } else {
            why = "reject_size";
            ++g_shade_clip_reject_size;
        }
    }
    layer_drift_write_end(&drift, G1_SHADE_CLIP, why, x, y, width, height);
    return result;
}

/* H-HDB0/H-HDB1: copy the covered flags and the HD destination of the screen window (visible_width x visible_height
 * at x0, y0) ahead of the original draw; the key overlay needs the destination the original blended with. */
static void blend_key_snapshot(int x0, int y0, int visible_width, int visible_height)
{
    int row, col;
    for (row = 0; row < visible_height; ++row) {
        for (col = 0; col < visible_width; ++col)
            g_blend_key_covered[row * visible_width + col] =
                g_covered[(DWORD)(y0 + row) * G1_OVERLAY_SCREEN_WIDTH + (DWORD)(x0 + col)];
        for (col = 0; col < 2; ++col)
            mirror_move_bytes(g_blend_key_hd_before + (size_t)(row * 2 + col) * (size_t)visible_width * 2u,
                              g_mirror + ((size_t)(y0 + row) * 2u + (size_t)col) * 1600u + (size_t)x0 * 2u,
                              (DWORD)visible_width * 2u);
    }
}

/* After the diff mirror, blend the HD pack frame of this translucent stream with the HD destination the way the
 * original blends the 1x pixels: 0x4672E0 averages through the renderer palette and inverse LUT, 0x467580
 * (`weighted`) goes through the weight table at renderer + 0x41CA0.  The stream is decoded here (its rows end by
 * width, not by a marker), the original's 1x output over the screen window is checked against the same formula, and
 * only a call that passes and hits a pack file overwrites the diff mirror's Scale2x blocks; any other outcome keeps
 * them.  The identity key covers the whole stream rectangle (x, y, width, height); the window (x0, y0,
 * visible_width, visible_height) is the part on the screen and the only part checked and drawn.  `before` is the
 * window's 1x pre-draw copy; `covered`/`hd_before` were copied by blend_key_snapshot before the diff mirror ran. */
static BOOL blend_key_apply(const void *renderer, DWORD writer, BOOL weighted, DWORD rle, int x, int y, int width,
                            int height, int x0, int y0, int visible_width, int visible_height,
                            const BYTE *buffer, DWORD stride, const BYTE *before, G1BlendKeyStats *stats)
{
    /* H-HDB3: 0x467FD0 and 0x4685C0 draw the stream right to left; the planes below are turned into screen direction
     * right after the decode, so the crop offsets, the self check and the identity bind need no flip of their own. */
    const BOOL remapped = writer == G1_BLEND_CLIP7 || writer == G1_BLEND_FLIP7;
    const BOOL flip = writer == G1_FLIP_BLEND || writer == G1_BLEND_SKIP || writer == G1_BLEND_FLIP7;
    const BYTE *palette = (const BYTE *)renderer + 0x419A0u;
    const BYTE *inverse = (const BYTE *)renderer + 0x19A0u;
    const int16_t *weights = weighted ? (const int16_t *)((const BYTE *)renderer + 0x41CA0u) : NULL;
    const BYTE *source_plane = g_blend_key_vidx;
    size_t checked = 0u, pixels = (size_t)width * (size_t)height, written;
    size_t offset_x = (size_t)(x0 - x), offset_y = (size_t)(y0 - y);
    const BYTE *frame;
    DWORD hd_width = 0u, hd_height = 0u;
    BOOL keyed = FALSE;
    /* H-HDB4: 0x4678C0 / 0x468360 index the DWORD table renderer + 0x43CA0 by level; the slice becomes the int16
     * weights above, and the source colour of a token is remap[token].  Anything the table or the remap cannot
     * express is refused before the stream is decoded. */
    if (remapped) {
        if (!g_blend_key_remap ||
            !g1_blend_level_weights((const uint32_t *)((const BYTE *)renderer + 0x43CA0u), g_blend_key_level,
                                    g_blend_key_level_weights)) {
            ++stats->key_level_rejects;
            return FALSE;
        }
        weights = g_blend_key_level_weights;
    }
    fill_bytes(g_blend_key_idx, 0u, (DWORD)pixels);
    fill_bytes(g_blend_key_mask, 0u, (DWORD)pixels);
    if (!g1_blend_decode_rle((const BYTE *)(ULONG_PTR)rle, pixels * 2u + (size_t)height * 2u, (size_t)width,
                             (size_t)height, g_blend_key_idx, g_blend_key_mask))
        return FALSE;
    if (flip) {
        g1_blend_flip_rows(g_blend_key_idx, (size_t)width, (size_t)height);
        g1_blend_flip_rows(g_blend_key_mask, (size_t)width, (size_t)height);
    }
    g1_blend_crop(g_blend_key_idx, (size_t)width, offset_x, offset_y, (size_t)visible_width,
                  (size_t)visible_height, g_blend_key_vidx);
    g1_blend_crop(g_blend_key_mask, (size_t)width, offset_x, offset_y, (size_t)visible_width,
                  (size_t)visible_height, g_blend_key_vmask);
    if (remapped) {
        g1_blend_remap_plane(g_blend_key_remap, g_blend_key_vidx, g_blend_key_vmask,
                             (size_t)visible_width * (size_t)visible_height, g_blend_key_vsrc);
        source_plane = g_blend_key_vsrc;
    }
    if (!g1_blend_selfcheck(palette, inverse, weights, before, source_plane, g_blend_key_vmask,
                            (size_t)visible_width, (size_t)visible_height,
                            buffer + (DWORD)y0 * stride + (DWORD)x0, stride, &checked)) {
        ++stats->selfcheck_mismatches;
        return FALSE;
    }
    stats->selfcheck_pixels += (DWORD)checked;
    if (remapped ? !g1_hd_asset_begin_with_aux((const BYTE *)(ULONG_PTR)rle, writer, g_blend_key_remap,
                                               g_blend_key_remap_digest, (DWORD)width, (DWORD)height, x, y)
                 : !g1_hd_asset_begin((const BYTE *)(ULONG_PTR)rle, writer, (DWORD)width, (DWORD)height, x, y))
        return FALSE;
    if (g1_hd_asset_needs_identity_frame())
        (void)g1_hd_asset_bind_identity_frame(g_blend_key_idx, (DWORD)width, g_blend_key_mask,
                                              (DWORD)width, (DWORD)width, (DWORD)height);
    frame = g1_hd_asset_current_ready() ? g1_hd_asset_current_pack_frame(&hd_width, &hd_height) : NULL;
    if (frame && hd_width == (DWORD)width * 2u && hd_height == (DWORD)height * 2u) {
        written = g1_blend_apply_hd(palette, inverse, weights, g_blend_key_vmask, g_blend_key_covered,
                                    (size_t)visible_width, (size_t)visible_height, g_blend_key_hd_before,
                                    frame + offset_y * 2u * hd_width + offset_x * 2u, hd_width, g_mirror, 1600u,
                                    (size_t)x0, (size_t)y0, G1_HD_PACK_KEY);
        stats->keyed_pixels += (DWORD)written;
        keyed = TRUE;
    }
    g1_hd_asset_end();
    return keyed;
}

/* Original returns: 0x4672E0 ret 0x14 (5 stack args: x y width height rle).
 * Translucent logo RLE.  The original sign-extends only the low 16 bits of each
 * argument (callers leave garbage in the upper words) and never clips, so the
 * wrapper does the same and rejects (never cuts) rectangles outside the screen. */
static DWORD __attribute__((thiscall)) mirror_blend_rle(void *renderer, DWORD a_x,
                                                       DWORD a_y, DWORD a_w,
                                                       DWORD a_h, DWORD rle)
{
    G1OverlayStats stats;
    BYTE *buffer = NULL;
    int x = (int16_t)a_x, y = (int16_t)a_y, width = (int16_t)a_w,
        height = (int16_t)a_h;
    DWORD stride = 0u, result;
    int row, col;
    BOOL active = FALSE, key_try = FALSE;
    if (!g_original_blend_rle) return 0u;
    ++g_blend_rle_invocations;
    if (g_primitive_guard) {
        ++g_blend_rle_reject_guard;
    } else if ((DWORD)(ULONG_PTR)renderer == G1_RENDERER_VA && g_mirror &&
               g_covered && g_expected_snapshot) {
        stride = *(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_STRIDE);
        buffer = *(BYTE **)((BYTE *)renderer + G1_RENDERER_BUFFER);
        if (!buffer ||
            (DWORD)(ULONG_PTR)buffer == G1_CACHE_BASE ||
            buffer == g_panel_bound_buffer || stride < G1_OVERLAY_SCREEN_WIDTH ||
            stride > G1_MAX_STRIDE ||
            *(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_HEIGHT) !=
                G1_OVERLAY_SCREEN_HEIGHT) {
            ++g_blend_rle_reject_target;
        } else if (width <= 0 || height <= 0 || x < 0 || y < 0 ||
                   x + width > (int)G1_OVERLAY_SCREEN_WIDTH ||
                   y + height > (int)G1_OVERLAY_SCREEN_HEIGHT) {
            ++g_blend_rle_reject_bounds;
        } else if ((DWORD)width > G1_OVERLAY_MAX_WIDTH ||
                   (DWORD)height > G1_OVERLAY_MAX_HEIGHT) {
            ++g_blend_rle_reject_size;
        } else {
            for (row = 0; row < height; ++row)
                for (col = 0; col < width; ++col)
                    g_blend_rle_before[row * width + col] =
                        buffer[(DWORD)(y + row) * stride + (DWORD)(x + col)];
            active = TRUE;
            key_try = g1_hd_asset_blend_key_path();
            if (key_try) blend_key_snapshot(x, y, width, height);
        }
    }
    result = g_original_blend_rle(renderer, a_x, a_y, a_w, a_h, rle);
    if (active) {
        if (g1_overlay_blt_apply(g_blend_rle_before, buffer, stride, (size_t)x,
                                 (size_t)y, (size_t)width, (size_t)height,
                                 lstrcmpA(g1_hd_asset_source_name(), "scale2x") == 0,
                                 g_overlay_scratch, g_expected_snapshot, g_covered,
                                 g_mirror, 1600u, &stats)) {
            ++g_blend_rle_mirrored_calls;
            g_blend_rle_mirrored_pixels += (DWORD)stats.changed;
            if (stats.changed) ++g_blend_rle_changed_calls;
            if (key_try) {
                if (blend_key_apply(renderer, G1_BLEND_RLE, FALSE, rle, x, y, width, height, x, y, width, height,
                                    buffer, stride, g_blend_rle_before, &g_blend_rle_key))
                    ++g_blend_rle_key.keyed_calls;
                else
                    ++g_blend_rle_key.key_fallbacks;
            }
        } else {
            ++g_blend_rle_reject_size;
        }
    }
    return result;
}

/* Original returns: 0x467580 ret 0x14 (5 stack args: x y width height rle).
 * Weighted translucent RLE (clouds/shadows; callers 0x41A00D/0x41ABF5, ecx
 * always the screen renderer).  Same contract as 0x4672E0: the original
 * sign-extends only the low 16 bits of each argument (callers leave garbage in
 * the upper words) and never clips, so the wrapper does the same.  Clouds drift
 * over the screen edge (save000: ~26% of calls), so unlike 0x4672E0 a partially
 * off-screen rectangle is mirrored over its screen intersection only; the
 * original still runs with the full rectangle and the wrapper reads nothing
 * outside the intersection (wrapped writes beyond it stay untracked).
 * H-HDB1: with a Scale2x pack run the same HD key path as 0x4672E0 follows the diff mirror, over the intersection. */
static DWORD __attribute__((thiscall)) mirror_blend_wrle(void *renderer, DWORD a_x,
                                                       DWORD a_y, DWORD a_w,
                                                       DWORD a_h, DWORD rle)
{
    G1OverlayStats stats;
    BYTE *buffer = NULL;
    int x = (int16_t)a_x, y = (int16_t)a_y, width = (int16_t)a_w,
        height = (int16_t)a_h;
    int x0 = 0, y0 = 0, x1 = 0, y1 = 0;
    DWORD stride = 0u, result;
    size_t tiles = 0u;
    int row, col;
    BOOL active = FALSE, key_try = FALSE;
    G1DriftWrite drift;
    const char *why = "not_ready";
    if (!g_original_blend_wrle) return 0u;
    ++g_blend_wrle_invocations;
    layer_drift_write_begin(&drift, renderer);
    if (g_primitive_guard) {
        why = "guard";
        ++g_blend_wrle_reject_guard;
    } else if ((DWORD)(ULONG_PTR)renderer == G1_RENDERER_VA && g_mirror &&
               g_covered && g_expected_snapshot) {
        stride = *(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_STRIDE);
        buffer = *(BYTE **)((BYTE *)renderer + G1_RENDERER_BUFFER);
        if (!buffer ||
            (DWORD)(ULONG_PTR)buffer == G1_CACHE_BASE ||
            buffer == g_panel_bound_buffer || stride < G1_OVERLAY_SCREEN_WIDTH ||
            stride > G1_MAX_STRIDE ||
            *(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_HEIGHT) !=
                G1_OVERLAY_SCREEN_HEIGHT) {
            why = "reject_target";
            ++g_blend_wrle_reject_target;
        } else if (width <= 0 || height <= 0 ||
                   (x0 = x < 0 ? 0 : x,
                    y0 = y < 0 ? 0 : y,
                    x1 = x + width > (int)G1_OVERLAY_SCREEN_WIDTH
                             ? (int)G1_OVERLAY_SCREEN_WIDTH : x + width,
                    y1 = y + height > (int)G1_OVERLAY_SCREEN_HEIGHT
                             ? (int)G1_OVERLAY_SCREEN_HEIGHT : y + height,
                    x0 >= x1 || y0 >= y1)) {
            why = "reject_bounds";
            ++g_blend_wrle_reject_bounds;
        } else if (blend_size_reject_diag(x1 - x0, y1 - y0, TRUE)) {
            why = "reject_size";
            g_blend_wrle_reject_size += 1u;
        } else {
            why = "mirrored";
            if (x0 != x || y0 != y || x1 != x + width || y1 != y + height) {
                why = "clipped";
                ++g_blend_wrle_clipped_calls;
            }
            for (row = 0; row < y1 - y0; ++row)
                for (col = 0; col < x1 - x0; ++col)
                    g_blend_wrle_before[row * (x1 - x0) + col] =
                        buffer[(DWORD)(y0 + row) * stride + (DWORD)(x0 + col)];
            active = TRUE;
            key_try = g1_hd_asset_blend_key_path();
            if (key_try && (size_t)width * (size_t)height > G1_BLEND_KEY_MAX_PIXELS) {
                ++g_blend_wrle_key.key_fallbacks;
                key_try = FALSE;
            }
            if (key_try) blend_key_snapshot(x0, y0, x1 - x0, y1 - y0);
        }
    }
    result = g_original_blend_wrle(renderer, a_x, a_y, a_w, a_h, rle);
    if (active) {
        if (g1_overlay_blt_apply_tiled(g_blend_wrle_before, buffer, stride, (size_t)x0,
                                       (size_t)y0, (size_t)(x1 - x0), (size_t)(y1 - y0),
                                       lstrcmpA(g1_hd_asset_source_name(), "scale2x") == 0,
                                       g_overlay_scratch, g_blend_wrle_tile,
                                       g_expected_snapshot, g_covered, g_mirror, 1600u,
                                       &stats, &tiles)) {
            ++g_blend_wrle_mirrored_calls;
            g_blend_wrle_mirrored_pixels += (DWORD)stats.changed;
            if (stats.changed) ++g_blend_wrle_changed_calls;
            if (key_try) {
                if (blend_key_apply(renderer, G1_BLEND_WRLE, TRUE, rle, x, y, width, height, x0, y0, x1 - x0,
                                    y1 - y0, buffer, stride, g_blend_wrle_before, &g_blend_wrle_key))
                    ++g_blend_wrle_key.keyed_calls;
                else
                    ++g_blend_wrle_key.key_fallbacks;
            }
        } else {
            why = "reject_size";
            ++g_blend_wrle_reject_size;
        }
    }
    layer_drift_write_end(&drift, G1_BLEND_WRLE, why, x, y, width, height);
    return result;
}

/* H-D2r: taller blends (lap1061: 330x200 at x-167) are no longer reject_size.
 * H-W330: the rect is diffed in <=320x160 tiles, so widths > 320 (lap1083 330x200)
 * are mirrored too; blend_467B00_band_calls now counts calls that needed more than one tile.
 *
 * H-B4: 0x467B00 ret 0x14 (5 stack args: x y width height rle), thiscall.
 * Clipped, destination-dependent translucent RLE (callers 0x41A06D/0x41AC45,
 * ecx = the screen renderer): reads dst, blends two palette colors and writes
 * the nearest palette index back.  The original sign-extends only the low 16
 * bits of each argument and clips itself to the renderer clip rectangle
 * (+0x4D0..+0x4DC); the wrapper mirrors the screen intersection of the passed
 * rectangle only, which is a superset of what the original can touch.
 * H-HDB2: with a Scale2x pack run the HD key path of 0x467580 follows the diff mirror over the screen intersection
 * cut by the renderer clip rectangle (the original does not write outside it). */
static DWORD __attribute__((thiscall)) mirror_blend_clip(void *renderer, DWORD a_x,
                                                       DWORD a_y, DWORD a_w,
                                                       DWORD a_h, DWORD rle)
{
    G1OverlayStats stats;
    BYTE *buffer = NULL;
    size_t tiles = 0u;
    int x = (int16_t)a_x, y = (int16_t)a_y, width = (int16_t)a_w,
        height = (int16_t)a_h;
    int x0 = 0, y0 = 0, x1 = 0, y1 = 0;
    int kx0 = 0, ky0 = 0, kx1 = 0, ky1 = 0;
    DWORD stride = 0u, result;
    int row, col;
    BOOL active = FALSE, key_try = FALSE, key_cut = FALSE;
    G1DriftWrite drift;
    const char *why = "not_ready";
    if (!g_original_blend_clip) return 0u;
    ++g_blend_clip_invocations;
    layer_drift_write_begin(&drift, renderer);
    if (g_primitive_guard) {
        why = "guard";
        ++g_blend_clip_reject_guard;
    } else if ((DWORD)(ULONG_PTR)renderer == G1_RENDERER_VA && g_mirror &&
               g_covered && g_expected_snapshot) {
        stride = *(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_STRIDE);
        buffer = *(BYTE **)((BYTE *)renderer + G1_RENDERER_BUFFER);
        if (!buffer ||
            (DWORD)(ULONG_PTR)buffer == G1_CACHE_BASE ||
            buffer == g_panel_bound_buffer || stride < G1_OVERLAY_SCREEN_WIDTH ||
            stride > G1_MAX_STRIDE ||
            *(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_HEIGHT) !=
                G1_OVERLAY_SCREEN_HEIGHT) {
            why = "reject_target";
            ++g_blend_clip_reject_target;
        } else if (width <= 0 || height <= 0 ||
                   (x0 = x < 0 ? 0 : x,
                    y0 = y < 0 ? 0 : y,
                    x1 = x + width > (int)G1_OVERLAY_SCREEN_WIDTH
                             ? (int)G1_OVERLAY_SCREEN_WIDTH : x + width,
                    y1 = y + height > (int)G1_OVERLAY_SCREEN_HEIGHT
                             ? (int)G1_OVERLAY_SCREEN_HEIGHT : y + height,
                    x0 >= x1 || y0 >= y1)) {
            why = "reject_bounds";
            ++g_blend_clip_reject_bounds;
        } else if (blend_size_reject_diag(x1 - x0, y1 - y0, FALSE)) {
            why = "reject_size";
            g_blend_clip_reject_size += 1u;
        } else {
            why = "mirrored";
            if (x0 != x || y0 != y || x1 != x + width || y1 != y + height) {
                why = "clipped";
                ++g_blend_clip_clipped_calls;
            }
            for (row = 0; row < y1 - y0; ++row)
                for (col = 0; col < x1 - x0; ++col)
                    g_blend_clip_before[row * (x1 - x0) + col] =
                        buffer[(DWORD)(y0 + row) * stride + (DWORD)(x0 + col)];
            active = TRUE;
            /* H-HDB2: the key checks and draws the screen intersection cut by the renderer clip, which is read
             * before the original runs (inclusive right and bottom); a clip with nothing left skips the key. */
            key_try = g1_hd_asset_blend_key_path();
            if (key_try && (size_t)width * (size_t)height > G1_BLEND_KEY_MAX_PIXELS) {
                ++g_blend_clip_key.key_fallbacks;
                key_try = FALSE;
            }
            if (key_try &&
                !g1_blend_clip_window(x0, y0, x1, y1,
                                      *(const volatile int32_t *)((BYTE *)renderer + G1_RENDERER_VIEWPORT),
                                      *(const volatile int32_t *)((BYTE *)renderer + G1_RENDERER_VIEWPORT + 4u),
                                      *(const volatile int32_t *)((BYTE *)renderer + G1_RENDERER_VIEWPORT + 8u),
                                      *(const volatile int32_t *)((BYTE *)renderer + G1_RENDERER_VIEWPORT + 12u),
                                      &kx0, &ky0, &kx1, &ky1)) {
                ++g_blend_clip_key.key_clip_empty;
                key_try = FALSE;
            }
            if (key_try) {
                key_cut = kx0 != x0 || ky0 != y0 || kx1 != x1 || ky1 != y1;
                blend_key_snapshot(kx0, ky0, kx1 - kx0, ky1 - ky0);
                g1_blend_crop(g_blend_clip_before, (size_t)(x1 - x0), (size_t)(kx0 - x0), (size_t)(ky0 - y0),
                              (size_t)(kx1 - kx0), (size_t)(ky1 - ky0), g_blend_clip_key_before);
            }
        }
    }
    result = g_original_blend_clip(renderer, a_x, a_y, a_w, a_h, rle);
    if (active) {
        if (g1_overlay_blt_apply_tiled(g_blend_clip_before, buffer, stride,
                                       (size_t)x0, (size_t)y0, (size_t)(x1 - x0),
                                       (size_t)(y1 - y0),
                                       lstrcmpA(g1_hd_asset_source_name(), "scale2x") == 0,
                                       g_overlay_scratch, g_blend_clip_tile,
                                       g_expected_snapshot, g_covered, g_mirror, 1600u,
                                       &stats, &tiles)) {
            if (tiles > 1u) ++g_blend_clip_band_calls;
            ++g_blend_clip_mirrored_calls;
            g_blend_clip_mirrored_pixels += (DWORD)stats.changed;
            if (stats.changed) ++g_blend_clip_changed_calls;
            if (key_try) {
                if (blend_key_apply(renderer, G1_BLEND_CLIP, TRUE, rle, x, y, width, height, kx0, ky0, kx1 - kx0,
                                    ky1 - ky0, buffer, stride, g_blend_clip_key_before, &g_blend_clip_key)) {
                    ++g_blend_clip_key.keyed_calls;
                    if (key_cut) ++g_blend_clip_key.key_clip_cut;
                } else {
                    ++g_blend_clip_key.key_fallbacks;
                }
            }
        } else {
            why = "reject_size";
            ++g_blend_clip_reject_size;
        }
    }
    layer_drift_write_end(&drift, G1_BLEND_CLIP, why, x, y, width, height);
    return result;
}

/* H-D2r: 0x4685C0 ret 0x14 (5 stack args: x y width height rle), thiscall.
 * Sibling of 0x467B00 (callers 0x41A12D/0x41ACE5, ecx = the screen renderer):
 * clipped (+0x4D0..+0x4DC) RLE whose 0xFE n codes skip n pixels and whose other
 * codes blend with the destination through a lookup (objdump, write at
 * 0x4687A1).  Mirrors the screen intersection of the passed rectangle only (a
 * superset of what the original can touch) and forwards all 5 original
 * arguments unchanged. */
static DWORD __attribute__((thiscall)) mirror_blend_skip(void *renderer, DWORD a_x,
                                                       DWORD a_y, DWORD a_w,
                                                       DWORD a_h, DWORD rle)
{
    G1OverlayStats stats;
    BYTE *buffer = NULL;
    size_t bands = 0u;
    int x = (int16_t)a_x, y = (int16_t)a_y, width = (int16_t)a_w,
        height = (int16_t)a_h;
    int x0 = 0, y0 = 0, x1 = 0, y1 = 0;
    int kx0 = 0, ky0 = 0, kx1 = 0, ky1 = 0;
    DWORD stride = 0u, result;
    int row, col;
    BOOL active = FALSE, key_try = FALSE, key_cut = FALSE;
    G1DriftWrite drift;
    const char *why = "not_ready";
    if (!g_original_blend_skip) return 0u;
    ++g_blend_skip_invocations;
    layer_drift_write_begin(&drift, renderer);
    if (g_primitive_guard) {
        why = "guard";
        ++g_blend_skip_reject_guard;
    } else if ((DWORD)(ULONG_PTR)renderer == G1_RENDERER_VA && g_mirror &&
               g_covered && g_expected_snapshot) {
        stride = *(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_STRIDE);
        buffer = *(BYTE **)((BYTE *)renderer + G1_RENDERER_BUFFER);
        if (!buffer ||
            (DWORD)(ULONG_PTR)buffer == G1_CACHE_BASE ||
            buffer == g_panel_bound_buffer || stride < G1_OVERLAY_SCREEN_WIDTH ||
            stride > G1_MAX_STRIDE ||
            *(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_HEIGHT) !=
                G1_OVERLAY_SCREEN_HEIGHT) {
            why = "reject_target";
            ++g_blend_skip_reject_target;
        } else if (width <= 0 || height <= 0 ||
                   (x0 = x < 0 ? 0 : x,
                    y0 = y < 0 ? 0 : y,
                    x1 = x + width > (int)G1_OVERLAY_SCREEN_WIDTH
                             ? (int)G1_OVERLAY_SCREEN_WIDTH : x + width,
                    y1 = y + height > (int)G1_OVERLAY_SCREEN_HEIGHT
                             ? (int)G1_OVERLAY_SCREEN_HEIGHT : y + height,
                    x0 >= x1 || y0 >= y1)) {
            why = "reject_bounds";
            ++g_blend_skip_reject_bounds;
        } else if ((DWORD)(x1 - x0) > G1_OVERLAY_MAX_WIDTH) {
            why = "reject_size";
            ++g_blend_skip_reject_size;
        } else {
            why = "mirrored";
            if (x0 != x || y0 != y || x1 != x + width || y1 != y + height) {
                why = "clipped";
                ++g_blend_skip_clipped_calls;
            }
            for (row = 0; row < y1 - y0; ++row)
                for (col = 0; col < x1 - x0; ++col)
                    g_blend_skip_before[row * (x1 - x0) + col] =
                        buffer[(DWORD)(y0 + row) * stride + (DWORD)(x0 + col)];
            active = TRUE;
            /* H-HDB3: the key checks and draws the screen intersection cut by the renderer clip (read before the
             * original runs, inclusive right and bottom), exactly like 0x467B00; the stream is mirrored left to right. */
            key_try = g1_hd_asset_blend_flip_key_path();
            if (key_try && (size_t)width * (size_t)height > G1_BLEND_KEY_MAX_PIXELS) {
                ++g_blend_skip_key.key_fallbacks;
                key_try = FALSE;
            }
            if (key_try &&
                !g1_blend_clip_window(x0, y0, x1, y1,
                                      *(const volatile int32_t *)((BYTE *)renderer + G1_RENDERER_VIEWPORT),
                                      *(const volatile int32_t *)((BYTE *)renderer + G1_RENDERER_VIEWPORT + 4u),
                                      *(const volatile int32_t *)((BYTE *)renderer + G1_RENDERER_VIEWPORT + 8u),
                                      *(const volatile int32_t *)((BYTE *)renderer + G1_RENDERER_VIEWPORT + 12u),
                                      &kx0, &ky0, &kx1, &ky1)) {
                ++g_blend_skip_key.key_clip_empty;
                key_try = FALSE;
            }
            if (key_try) {
                key_cut = kx0 != x0 || ky0 != y0 || kx1 != x1 || ky1 != y1;
                blend_key_snapshot(kx0, ky0, kx1 - kx0, ky1 - ky0);
                g1_blend_crop(g_blend_skip_before, (size_t)(x1 - x0), (size_t)(kx0 - x0), (size_t)(ky0 - y0),
                              (size_t)(kx1 - kx0), (size_t)(ky1 - ky0), g_blend_clip_key_before);
            }
        }
    }
    result = g_original_blend_skip(renderer, a_x, a_y, a_w, a_h, rle);
    if (active) {
        if (g1_overlay_blt_apply_banded(g_blend_skip_before, buffer, stride,
                                        (size_t)x0, (size_t)y0, (size_t)(x1 - x0),
                                        (size_t)(y1 - y0),
                                        lstrcmpA(g1_hd_asset_source_name(), "scale2x") == 0,
                                        g_overlay_scratch, g_expected_snapshot,
                                        g_covered, g_mirror, 1600u, &stats, &bands)) {
            if (bands > 1u) ++g_blend_skip_band_calls;
            ++g_blend_skip_mirrored_calls;
            g_blend_skip_mirrored_pixels += (DWORD)stats.changed;
            if (stats.changed) ++g_blend_skip_changed_calls;
            if (key_try) {
                if (blend_key_apply(renderer, G1_BLEND_SKIP, TRUE, rle, x, y, width, height, kx0, ky0, kx1 - kx0,
                                    ky1 - ky0, buffer, stride, g_blend_clip_key_before, &g_blend_skip_key)) {
                    ++g_blend_skip_key.keyed_calls;
                    if (key_cut) ++g_blend_skip_key.key_clip_cut;
                } else {
                    ++g_blend_skip_key.key_fallbacks;
                }
            }
        } else {
            why = "reject_size";
            ++g_blend_skip_reject_size;
        }
    }
    layer_drift_write_end(&drift, G1_BLEND_SKIP, why, x, y, width, height);
    return result;
}

/* H-HDB4: the 7-arg writers' remap table (256 B) and 16-bit level for the next blend_key_apply.  An unreadable table
 * leaves the remap NULL, which blend_key_apply refuses. */
static void blend_key_set_remap(DWORD remap, DWORD level)
{
    BOOL valid = FALSE;
    g_blend_key_remap_digest = auxiliary_digest((const BYTE *)(ULONG_PTR)remap, 256u, &valid);
    g_blend_key_remap = valid && remap != 0u ? (const BYTE *)(ULONG_PTR)remap : NULL;
    g_blend_key_level = (int16_t)level;
}

/* H-P: 0x4678C0 ret 0x1c (7 stack args: x y width height rle remap level),
 * thiscall.  Sibling of 0x467B00: clipped (+0x4D0..+0x4DC), destination-
 * dependent translucent RLE with a remap table and a 16-bit level (callers
 * 0x41A827/0x41A99F, ecx = the screen renderer).  Mirrors the screen
 * intersection of the passed rectangle only (a superset of what the original
 * can touch) and forwards all 7 original arguments unchanged. */
static DWORD __attribute__((thiscall)) mirror_blend_clip7(void *renderer, DWORD a_x,
                                                        DWORD a_y, DWORD a_w,
                                                        DWORD a_h, DWORD rle,
                                                        DWORD remap, DWORD level)
{
    G1OverlayStats stats;
    BYTE *buffer = NULL;
    int x = (int16_t)a_x, y = (int16_t)a_y, width = (int16_t)a_w,
        height = (int16_t)a_h;
    int x0 = 0, y0 = 0, x1 = 0, y1 = 0;
    int kx0 = 0, ky0 = 0, kx1 = 0, ky1 = 0;
    DWORD stride = 0u, result;
    int row, col;
    BOOL active = FALSE, key_try = FALSE, key_cut = FALSE;
    G1DriftWrite drift;
    const char *why = "not_ready";
    if (!g_original_blend_clip7) return 0u;
    ++g_blend_clip7_invocations;
    layer_drift_write_begin(&drift, renderer);
    if (g_primitive_guard) {
        why = "guard";
        ++g_blend_clip7_reject_guard;
    } else if ((DWORD)(ULONG_PTR)renderer == G1_RENDERER_VA && g_mirror &&
               g_covered && g_expected_snapshot) {
        stride = *(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_STRIDE);
        buffer = *(BYTE **)((BYTE *)renderer + G1_RENDERER_BUFFER);
        if (!buffer ||
            (DWORD)(ULONG_PTR)buffer == G1_CACHE_BASE ||
            buffer == g_panel_bound_buffer || stride < G1_OVERLAY_SCREEN_WIDTH ||
            stride > G1_MAX_STRIDE ||
            *(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_HEIGHT) !=
                G1_OVERLAY_SCREEN_HEIGHT) {
            why = "reject_target";
            ++g_blend_clip7_reject_target;
        } else if (width <= 0 || height <= 0 ||
                   (x0 = x < 0 ? 0 : x,
                    y0 = y < 0 ? 0 : y,
                    x1 = x + width > (int)G1_OVERLAY_SCREEN_WIDTH
                             ? (int)G1_OVERLAY_SCREEN_WIDTH : x + width,
                    y1 = y + height > (int)G1_OVERLAY_SCREEN_HEIGHT
                             ? (int)G1_OVERLAY_SCREEN_HEIGHT : y + height,
                    x0 >= x1 || y0 >= y1)) {
            why = "reject_bounds";
            ++g_blend_clip7_reject_bounds;
        } else if ((DWORD)(x1 - x0) > G1_OVERLAY_MAX_WIDTH ||
                   (DWORD)(y1 - y0) > G1_OVERLAY_MAX_HEIGHT) {
            why = "reject_size";
            ++g_blend_clip7_reject_size;
        } else {
            why = "mirrored";
            if (x0 != x || y0 != y || x1 != x + width || y1 != y + height) {
                why = "clipped";
                ++g_blend_clip7_clipped_calls;
            }
            for (row = 0; row < y1 - y0; ++row)
                for (col = 0; col < x1 - x0; ++col)
                    g_blend_clip7_before[row * (x1 - x0) + col] =
                        buffer[(DWORD)(y0 + row) * stride + (DWORD)(x0 + col)];
            active = TRUE;
            /* H-HDB4: like 0x467B00, the key checks and draws the screen intersection cut by the renderer clip (read before the
             * original runs, inclusive right and bottom); the remap table and level are the extra inputs of the blend. */
            key_try = g1_hd_asset_blend_key_path();
            if (key_try && (size_t)width * (size_t)height > G1_BLEND_KEY_MAX_PIXELS) {
                ++g_blend_clip7_key.key_fallbacks;
                key_try = FALSE;
            }
            if (key_try &&
                !g1_blend_clip_window(x0, y0, x1, y1,
                                      *(const volatile int32_t *)((BYTE *)renderer + G1_RENDERER_VIEWPORT),
                                      *(const volatile int32_t *)((BYTE *)renderer + G1_RENDERER_VIEWPORT + 4u),
                                      *(const volatile int32_t *)((BYTE *)renderer + G1_RENDERER_VIEWPORT + 8u),
                                      *(const volatile int32_t *)((BYTE *)renderer + G1_RENDERER_VIEWPORT + 12u),
                                      &kx0, &ky0, &kx1, &ky1)) {
                ++g_blend_clip7_key.key_clip_empty;
                key_try = FALSE;
            }
            if (key_try) {
                key_cut = kx0 != x0 || ky0 != y0 || kx1 != x1 || ky1 != y1;
                blend_key_snapshot(kx0, ky0, kx1 - kx0, ky1 - ky0);
                g1_blend_crop(g_blend_clip7_before, (size_t)(x1 - x0), (size_t)(kx0 - x0), (size_t)(ky0 - y0),
                              (size_t)(kx1 - kx0), (size_t)(ky1 - ky0), g_blend_clip_key_before);
            }
        }
    }
    result = g_original_blend_clip7(renderer, a_x, a_y, a_w, a_h, rle, remap, level);
    if (active) {
        if (g1_overlay_blt_apply(g_blend_clip7_before, buffer, stride, (size_t)x0,
                                 (size_t)y0, (size_t)(x1 - x0), (size_t)(y1 - y0),
                                 lstrcmpA(g1_hd_asset_source_name(), "scale2x") == 0,
                                 g_overlay_scratch, g_expected_snapshot, g_covered,
                                 g_mirror, 1600u, &stats)) {
            ++g_blend_clip7_mirrored_calls;
            g_blend_clip7_mirrored_pixels += (DWORD)stats.changed;
            if (stats.changed) ++g_blend_clip7_changed_calls;
            if (key_try) {
                blend_key_set_remap(remap, level);
                if (blend_key_apply(renderer, G1_BLEND_CLIP7, TRUE, rle, x, y, width, height, kx0, ky0, kx1 - kx0,
                                    ky1 - ky0, buffer, stride, g_blend_clip_key_before, &g_blend_clip7_key)) {
                    ++g_blend_clip7_key.keyed_calls;
                    if (key_cut) ++g_blend_clip7_key.key_clip_cut;
                } else {
                    ++g_blend_clip7_key.key_fallbacks;
                }
                g_blend_key_remap = NULL;
            }
        } else {
            why = "reject_size";
            ++g_blend_clip7_reject_size;
        }
    }
    layer_drift_write_end(&drift, G1_BLEND_CLIP7, why, x, y, width, height);
    return result;
}

/* H-U: 0x468360 ret 0x1c (7 stack args: x y width height rle remap level),
 * thiscall.  Left-right flipped sibling of 0x4678C0: clipped (+0x4D0..+0x4DC),
 * destination-dependent translucent RLE with a remap table and a 16-bit level.
 * The flip does not change the destination range (rect intersect clip), so the
 * screen intersection of the passed rectangle is a superset of what the
 * original can touch.  All 7 original arguments are forwarded unchanged. */
static DWORD __attribute__((thiscall)) mirror_blend_flip7(void *renderer, DWORD a_x,
                                                        DWORD a_y, DWORD a_w,
                                                        DWORD a_h, DWORD rle,
                                                        DWORD remap, DWORD level)
{
    G1OverlayStats stats;
    BYTE *buffer = NULL;
    int x = (int16_t)a_x, y = (int16_t)a_y, width = (int16_t)a_w,
        height = (int16_t)a_h;
    int x0 = 0, y0 = 0, x1 = 0, y1 = 0;
    int kx0 = 0, ky0 = 0, kx1 = 0, ky1 = 0;
    DWORD stride = 0u, result;
    int row, col;
    BOOL active = FALSE, key_try = FALSE, key_cut = FALSE;
    G1DriftWrite drift;
    const char *why = "not_ready";
    if (!g_original_blend_flip7) return 0u;
    ++g_blend_flip7_invocations;
    layer_drift_write_begin(&drift, renderer);
    if (g_primitive_guard) {
        why = "guard";
        ++g_blend_flip7_reject_guard;
    } else if ((DWORD)(ULONG_PTR)renderer == G1_RENDERER_VA && g_mirror &&
               g_covered && g_expected_snapshot) {
        stride = *(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_STRIDE);
        buffer = *(BYTE **)((BYTE *)renderer + G1_RENDERER_BUFFER);
        if (!buffer ||
            (DWORD)(ULONG_PTR)buffer == G1_CACHE_BASE ||
            buffer == g_panel_bound_buffer || stride < G1_OVERLAY_SCREEN_WIDTH ||
            stride > G1_MAX_STRIDE ||
            *(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_HEIGHT) !=
                G1_OVERLAY_SCREEN_HEIGHT) {
            why = "reject_target";
            ++g_blend_flip7_reject_target;
        } else if (width <= 0 || height <= 0 ||
                   (x0 = x < 0 ? 0 : x,
                    y0 = y < 0 ? 0 : y,
                    x1 = x + width > (int)G1_OVERLAY_SCREEN_WIDTH
                             ? (int)G1_OVERLAY_SCREEN_WIDTH : x + width,
                    y1 = y + height > (int)G1_OVERLAY_SCREEN_HEIGHT
                             ? (int)G1_OVERLAY_SCREEN_HEIGHT : y + height,
                    x0 >= x1 || y0 >= y1)) {
            why = "reject_bounds";
            ++g_blend_flip7_reject_bounds;
        } else if ((DWORD)(x1 - x0) > G1_OVERLAY_MAX_WIDTH ||
                   (DWORD)(y1 - y0) > G1_OVERLAY_MAX_HEIGHT) {
            why = "reject_size";
            ++g_blend_flip7_reject_size;
        } else {
            why = "mirrored";
            if (x0 != x || y0 != y || x1 != x + width || y1 != y + height) {
                why = "clipped";
                ++g_blend_flip7_clipped_calls;
            }
            for (row = 0; row < y1 - y0; ++row)
                for (col = 0; col < x1 - x0; ++col)
                    g_blend_flip7_before[row * (x1 - x0) + col] =
                        buffer[(DWORD)(y0 + row) * stride + (DWORD)(x0 + col)];
            active = TRUE;
            /* H-HDB4: like 0x4685C0, the key checks and draws the screen intersection cut by the renderer clip (read before the
             * original runs, inclusive right and bottom); the remap table and level are the extra inputs of the blend. */
            key_try = g1_hd_asset_blend_flip_key_path();
            if (key_try && (size_t)width * (size_t)height > G1_BLEND_KEY_MAX_PIXELS) {
                ++g_blend_flip7_key.key_fallbacks;
                key_try = FALSE;
            }
            if (key_try &&
                !g1_blend_clip_window(x0, y0, x1, y1,
                                      *(const volatile int32_t *)((BYTE *)renderer + G1_RENDERER_VIEWPORT),
                                      *(const volatile int32_t *)((BYTE *)renderer + G1_RENDERER_VIEWPORT + 4u),
                                      *(const volatile int32_t *)((BYTE *)renderer + G1_RENDERER_VIEWPORT + 8u),
                                      *(const volatile int32_t *)((BYTE *)renderer + G1_RENDERER_VIEWPORT + 12u),
                                      &kx0, &ky0, &kx1, &ky1)) {
                ++g_blend_flip7_key.key_clip_empty;
                key_try = FALSE;
            }
            if (key_try) {
                key_cut = kx0 != x0 || ky0 != y0 || kx1 != x1 || ky1 != y1;
                blend_key_snapshot(kx0, ky0, kx1 - kx0, ky1 - ky0);
                g1_blend_crop(g_blend_flip7_before, (size_t)(x1 - x0), (size_t)(kx0 - x0), (size_t)(ky0 - y0),
                              (size_t)(kx1 - kx0), (size_t)(ky1 - ky0), g_blend_clip_key_before);
            }
        }
    }
    result = g_original_blend_flip7(renderer, a_x, a_y, a_w, a_h, rle, remap, level);
    if (active) {
        if (g1_overlay_blt_apply(g_blend_flip7_before, buffer, stride, (size_t)x0,
                                 (size_t)y0, (size_t)(x1 - x0), (size_t)(y1 - y0),
                                 lstrcmpA(g1_hd_asset_source_name(), "scale2x") == 0,
                                 g_overlay_scratch, g_expected_snapshot, g_covered,
                                 g_mirror, 1600u, &stats)) {
            ++g_blend_flip7_mirrored_calls;
            g_blend_flip7_mirrored_pixels += (DWORD)stats.changed;
            if (stats.changed) ++g_blend_flip7_changed_calls;
            if (key_try) {
                blend_key_set_remap(remap, level);
                if (blend_key_apply(renderer, G1_BLEND_FLIP7, TRUE, rle, x, y, width, height, kx0, ky0, kx1 - kx0,
                                    ky1 - ky0, buffer, stride, g_blend_clip_key_before, &g_blend_flip7_key)) {
                    ++g_blend_flip7_key.keyed_calls;
                    if (key_cut) ++g_blend_flip7_key.key_clip_cut;
                } else {
                    ++g_blend_flip7_key.key_fallbacks;
                }
                g_blend_key_remap = NULL;
            }
        } else {
            why = "reject_size";
            ++g_blend_flip7_reject_size;
        }
    }
    layer_drift_write_end(&drift, G1_BLEND_FLIP7, why, x, y, width, height);
    return result;
}

/* H-Q: 0x467FD0 ret 0x14 (5 stack args: x y width height rle), thiscall.
 * Left-right flipped, destination-dependent translucent RLE (callers
 * 0x41A0CD/0x41AC95, ecx = the screen renderer).  Unlike 0x467B00 the original
 * has NO clip: it writes exactly [x, x+w) x [y, y+h) of the 16-bit-extended
 * arguments, so a rectangle past the stride wraps into the next row.  The
 * wrapper mirrors the screen intersection only and counts calls that leave
 * [0, stride) x [0, 600) in wrap_calls; the original arguments are forwarded
 * unchanged. */
static DWORD __attribute__((thiscall)) mirror_flip_blend(void *renderer, DWORD a_x,
                                                       DWORD a_y, DWORD a_w,
                                                       DWORD a_h, DWORD rle)
{
    G1OverlayStats stats;
    BYTE *buffer = NULL;
    int x = (int16_t)a_x, y = (int16_t)a_y, width = (int16_t)a_w,
        height = (int16_t)a_h;
    int x0 = 0, y0 = 0, x1 = 0, y1 = 0;
    DWORD stride = 0u, result;
    int row, col;
    BOOL active = FALSE, key_try = FALSE, wrapped = FALSE;
    G1DriftWrite drift;
    const char *why = "not_ready";
    if (!g_original_flip_blend) return 0u;
    ++g_flip_blend_invocations;
    layer_drift_write_begin(&drift, renderer);
    if (g_primitive_guard) {
        why = "guard";
        ++g_flip_blend_reject_guard;
    } else if ((DWORD)(ULONG_PTR)renderer == G1_RENDERER_VA && g_mirror &&
               g_covered && g_expected_snapshot) {
        stride = *(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_STRIDE);
        buffer = *(BYTE **)((BYTE *)renderer + G1_RENDERER_BUFFER);
        if (!buffer ||
            (DWORD)(ULONG_PTR)buffer == G1_CACHE_BASE ||
            buffer == g_panel_bound_buffer || stride < G1_OVERLAY_SCREEN_WIDTH ||
            stride > G1_MAX_STRIDE ||
            *(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_HEIGHT) !=
                G1_OVERLAY_SCREEN_HEIGHT) {
            why = "reject_target";
            ++g_flip_blend_reject_target;
        } else if (width <= 0 || height <= 0 ||
                   (x0 = x < 0 ? 0 : x,
                    y0 = y < 0 ? 0 : y,
                    x1 = x + width > (int)G1_OVERLAY_SCREEN_WIDTH
                             ? (int)G1_OVERLAY_SCREEN_WIDTH : x + width,
                    y1 = y + height > (int)G1_OVERLAY_SCREEN_HEIGHT
                             ? (int)G1_OVERLAY_SCREEN_HEIGHT : y + height,
                    x0 >= x1 || y0 >= y1)) {
            why = "reject_bounds";
            ++g_flip_blend_reject_bounds;
        } else if ((DWORD)(x1 - x0) > G1_OVERLAY_MAX_WIDTH ||
                   (DWORD)(y1 - y0) > G1_OVERLAY_MAX_HEIGHT) {
            why = "reject_size";
            ++g_flip_blend_reject_size;
        } else {
            why = "mirrored";
            if (x0 != x || y0 != y || x1 != x + width || y1 != y + height) {
                why = "clipped";
                ++g_flip_blend_clipped_calls;
            }
            wrapped = x < 0 || x + width > (int)stride || y < 0 || y + height > (int)G1_OVERLAY_SCREEN_HEIGHT;
            if (wrapped) ++g_flip_blend_wrap_calls;
            for (row = 0; row < y1 - y0; ++row)
                for (col = 0; col < x1 - x0; ++col)
                    g_flip_blend_before[row * (x1 - x0) + col] =
                        buffer[(DWORD)(y0 + row) * stride + (DWORD)(x0 + col)];
            active = TRUE;
            /* H-HDB3: the key checks and draws the screen intersection (the original has no clip); a wrapped write
             * that lands in the window fails the self check and keeps the diff mirror. */
            key_try = g1_hd_asset_blend_flip_key_path();
            if (key_try && (size_t)width * (size_t)height > G1_BLEND_KEY_MAX_PIXELS) {
                ++g_flip_blend_key.key_fallbacks;
                key_try = FALSE;
            }
            if (key_try) blend_key_snapshot(x0, y0, x1 - x0, y1 - y0);
        }
    }
    result = g_original_flip_blend(renderer, a_x, a_y, a_w, a_h, rle);
    if (active) {
        if (g1_overlay_blt_apply(g_flip_blend_before, buffer, stride, (size_t)x0,
                                 (size_t)y0, (size_t)(x1 - x0), (size_t)(y1 - y0),
                                 lstrcmpA(g1_hd_asset_source_name(), "scale2x") == 0,
                                 g_overlay_scratch, g_expected_snapshot, g_covered,
                                 g_mirror, 1600u, &stats)) {
            ++g_flip_blend_mirrored_calls;
            g_flip_blend_mirrored_pixels += (DWORD)stats.changed;
            if (stats.changed) ++g_flip_blend_changed_calls;
            if (key_try) {
                DWORD mismatches = g_flip_blend_key.selfcheck_mismatches;
                if (blend_key_apply(renderer, G1_FLIP_BLEND, TRUE, rle, x, y, width, height, x0, y0, x1 - x0,
                                    y1 - y0, buffer, stride, g_flip_blend_before, &g_flip_blend_key)) {
                    ++g_flip_blend_key.keyed_calls;
                } else {
                    ++g_flip_blend_key.key_fallbacks;
                    if (wrapped && g_flip_blend_key.selfcheck_mismatches != mismatches)
                        ++g_flip_blend_key.key_wrap_mismatches;
                }
            }
        } else {
            why = "reject_size";
            ++g_flip_blend_reject_size;
        }
    }
    layer_drift_write_end(&drift, G1_FLIP_BLEND, why, x, y, width, height);
    return result;
}

/* H-L2: 0x467E60 ret 0x1c (7 stack args: x y width height rle remap level),
 * thiscall.  Left-right flipped sibling of 0x4678C0 and 7-arg sibling of 0x467FD0:
 * destination-dependent translucent RLE with NO clip.  It writes column x+w-1-k from
 * the destination read at column x+k, so one call reads back pixels it already wrote and
 * the original runs exactly once; the screen intersection of the 16-bit rectangle is
 * diffed in <=320x160 tiles (a unit is small, a stray rectangle can span the screen).
 * Rows that wrap past the stride are not mirrored.  All 7 arguments are forwarded. */
static DWORD __attribute__((thiscall)) mirror_flip_blend7(void *renderer, DWORD a_x,
                                                        DWORD a_y, DWORD a_w,
                                                        DWORD a_h, DWORD rle,
                                                        DWORD remap, DWORD level)
{
    G1OverlayStats stats;
    G1FlipRleRegion region;
    BYTE *buffer = NULL;
    DWORD stride = 0u, result;
    size_t tiles = 0u;
    DWORD row, col;
    BOOL active = FALSE;
    G1DriftWrite drift;
    const char *why = "not_ready";
    int x = (int16_t)a_x, y = (int16_t)a_y, width = (int16_t)a_w,
        height = (int16_t)a_h;
    if (!g_original_flip_blend7) return 0u;
    ++g_flip_blend7_invocations;
    layer_drift_write_begin(&drift, renderer);
    if (g_primitive_guard) {
        why = "guard";
        ++g_flip_blend7_reject_guard;
    } else if ((DWORD)(ULONG_PTR)renderer == G1_RENDERER_VA && g_mirror &&
               g_covered && g_expected_snapshot) {
        stride = *(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_STRIDE);
        buffer = *(BYTE **)((BYTE *)renderer + G1_RENDERER_BUFFER);
        if (!buffer ||
            (DWORD)(ULONG_PTR)buffer == G1_CACHE_BASE ||
            buffer == g_panel_bound_buffer || stride < G1_OVERLAY_SCREEN_WIDTH ||
            stride > G1_MAX_STRIDE ||
            *(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_HEIGHT) !=
                G1_OVERLAY_SCREEN_HEIGHT) {
            why = "reject_target";
            ++g_flip_blend7_reject_target;
        } else if (!g1_flip_rle_region(x, y, width, height, (int32_t)stride,
                                       (int32_t)G1_OVERLAY_SCREEN_WIDTH,
                                       (int32_t)G1_OVERLAY_SCREEN_HEIGHT, &region)) {
            why = "reject_bounds";
            ++g_flip_blend7_reject_bounds;
        } else {
            why = region.clipped ? "clipped" : "mirrored";
            for (row = 0u; row < region.height; ++row)
                for (col = 0u; col < region.width; ++col)
                    g_flip_blend7_before[row * region.width + col] =
                        buffer[((DWORD)region.y + row) * stride + (DWORD)region.x + col];
            active = TRUE;
        }
    }
    result = g_original_flip_blend7(renderer, a_x, a_y, a_w, a_h, rle, remap, level);
    if (active) {
        if (g1_overlay_blt_apply_tiled(g_flip_blend7_before, buffer, stride,
                                       (size_t)region.x, (size_t)region.y, region.width,
                                       region.height,
                                       lstrcmpA(g1_hd_asset_source_name(), "scale2x") == 0,
                                       g_overlay_scratch, g_flip_blend7_tile,
                                       g_expected_snapshot, g_covered, g_mirror, 1600u,
                                       &stats, &tiles)) {
            ++g_flip_blend7_mirrored_calls;
            g_flip_blend7_mirrored_pixels += (DWORD)stats.changed;
            if (stats.changed) ++g_flip_blend7_changed_calls;
        } else {
            why = "reject_size";
            ++g_flip_blend7_reject_size;
        }
    }
    layer_drift_write_end(&drift, G1_FLIP_BLEND7, why, x, y, width, height);
    return result;
}

/* H-D2k-s1: 0x467410 is the unclipped weighted translucent RLE writer (ret 0x1C,
 * 7 stack args: x y w h rle remap weight; objdump: dest = buffer + y*stride + x,
 * h rows of w pixels, 0xFE RLE skip codes, dest-dependent blend).  It writes the
 * passed rectangle only, so the diff mirror snapshots the screen-clipped
 * intersection of that rectangle (a superset of what the original touches) and
 * forwards all 7 original arguments unchanged.  Arguments are low-16-bit
 * sign-extended like the original.  0x4676D0 (5 args) stays observe-only below. */
static DWORD __attribute__((thiscall)) mirror_blend_410(void *renderer, DWORD a_x,
                                                       DWORD a_y, DWORD a_w,
                                                       DWORD a_h, DWORD rle,
                                                       DWORD remap, DWORD weight)
{
    G1OverlayStats stats;
    BYTE *buffer = NULL;
    int x = (int16_t)a_x, y = (int16_t)a_y, width = (int16_t)a_w,
        height = (int16_t)a_h;
    int x0 = 0, y0 = 0, x1 = 0, y1 = 0;
    DWORD stride = 0u, result;
    int row, col;
    BOOL active = FALSE;
    G1DriftWrite drift;
    const char *why = "not_ready";
    if (!g_original_blend_410) return 0u;
    ++g_blend_410_invocations;
    layer_drift_write_begin(&drift, renderer);
    if (g_primitive_guard) {
        why = "guard";
        ++g_blend_410_reject_guard;
    } else if ((DWORD)(ULONG_PTR)renderer == G1_RENDERER_VA && g_mirror &&
               g_covered && g_expected_snapshot) {
        stride = *(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_STRIDE);
        buffer = *(BYTE **)((BYTE *)renderer + G1_RENDERER_BUFFER);
        if (!buffer ||
            (DWORD)(ULONG_PTR)buffer == G1_CACHE_BASE ||
            buffer == g_panel_bound_buffer || stride < G1_OVERLAY_SCREEN_WIDTH ||
            stride > G1_MAX_STRIDE ||
            *(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_HEIGHT) !=
                G1_OVERLAY_SCREEN_HEIGHT) {
            why = "reject_target";
            ++g_blend_410_reject_target;
        } else if (width <= 0 || height <= 0 ||
                   (x0 = x < 0 ? 0 : x,
                    y0 = y < 0 ? 0 : y,
                    x1 = x + width > (int)G1_OVERLAY_SCREEN_WIDTH
                             ? (int)G1_OVERLAY_SCREEN_WIDTH : x + width,
                    y1 = y + height > (int)G1_OVERLAY_SCREEN_HEIGHT
                             ? (int)G1_OVERLAY_SCREEN_HEIGHT : y + height,
                    x0 >= x1 || y0 >= y1)) {
            why = "reject_bounds";
            ++g_blend_410_reject_bounds;
        } else if ((DWORD)(x1 - x0) > G1_OVERLAY_MAX_WIDTH ||
                   (DWORD)(y1 - y0) > G1_OVERLAY_MAX_HEIGHT) {
            why = "reject_size";
            ++g_blend_410_reject_size;
        } else {
            why = "mirrored";
            for (row = 0; row < y1 - y0; ++row)
                for (col = 0; col < x1 - x0; ++col)
                    g_blend_410_before[row * (x1 - x0) + col] =
                        buffer[(DWORD)(y0 + row) * stride + (DWORD)(x0 + col)];
            active = TRUE;
        }
    }
    result = g_original_blend_410(renderer, a_x, a_y, a_w, a_h, rle, remap, weight);
    if (active) {
        if (g1_overlay_blt_apply(g_blend_410_before, buffer, stride, (size_t)x0,
                                 (size_t)y0, (size_t)(x1 - x0), (size_t)(y1 - y0),
                                 lstrcmpA(g1_hd_asset_source_name(), "scale2x") == 0,
                                 g_overlay_scratch, g_expected_snapshot, g_covered,
                                 g_mirror, 1600u, &stats)) {
            ++g_blend_410_mirrored_calls;
            g_blend_410_mirrored_pixels += (DWORD)stats.changed;
        } else {
            why = "reject_size";
            ++g_blend_410_reject_size;
        }
    }
    layer_drift_write_end(&drift, G1_BLEND_410, why, x, y, width, height);
    return result;
}

static DWORD __attribute__((thiscall)) observe_blend_6d0(void *renderer, DWORD a_x,
                                                        DWORD a_y, DWORD a_w,
                                                        DWORD a_h, DWORD rle)
{
    G1DriftWrite drift;
    DWORD result;
    if (!g_original_blend_6d0) return 0u;
    ++g_blend_6d0_invocations;
    layer_drift_write_begin(&drift, renderer);
    result = g_original_blend_6d0(renderer, a_x, a_y, a_w, a_h, rle);
    layer_drift_write_end(&drift, G1_BLEND_6D0, "observe", (int16_t)a_x, (int16_t)a_y,
                          (int16_t)a_w, (int16_t)a_h);
    return result;
}

/* H-OS2 OS2-0: why does a menu-screen TextOutA fail the renderer target check?
 * Counts rejects per program state and, under layer_drift only, logs up to 4096
 * calls per state (5, 7) with the renderer binding and the DC's selected bitmap (bits pointer,
 * size, stride) next to the last present's screen pointer.  Diagnostic only. */
#define G1_TEXTOUT_REJECT_LOG_LIMIT 4096u
typedef HGDIOBJ (WINAPI *G1GetCurrentObject)(HDC, UINT);
typedef int (WINAPI *G1GetObjectA)(HGDIOBJ, int, LPVOID);

/* The bitmap selected into the TextOutA DC (zeroed when it has none). */
static void textout_dc_bitmap(HDC hdc, BITMAP *bitmap)
{
    static G1GetCurrentObject current_object = NULL;
    static G1GetObjectA get_object = NULL;
    HGDIOBJ handle;
    ZeroMemory(bitmap, sizeof(*bitmap));
    if (!current_object || !get_object) {
        HMODULE gdi = GetModuleHandleA("gdi32.dll");
        if (!gdi) return;
        current_object = (G1GetCurrentObject)(ULONG_PTR)GetProcAddress(gdi, "GetCurrentObject");
        get_object = (G1GetObjectA)(ULONG_PTR)GetProcAddress(gdi, "GetObjectA");
        if (!current_object || !get_object) return;
    }
    handle = current_object(hdc, OBJ_BITMAP);
    if (!handle || get_object(handle, (int)sizeof(*bitmap), bitmap) <= 0)
        ZeroMemory(bitmap, sizeof(*bitmap));
}

/* H-OS2 OS2-2 (i): menu text is drawn straight onto the back buffer while the
 * renderer is still bound to an off-screen panel, so the binding check rejects
 * it.  The DC's own bitmap bits being exactly the last present's screen is the
 * stronger proof, so use that buffer and stride instead. */
static BOOL textout_screen_dc_target(HDC hdc, BYTE **buffer, DWORD *stride)
{
    BITMAP bitmap;
    if (!g_textout_screen_dc_enabled || !g_last_present_screen) return FALSE;
    textout_dc_bitmap(hdc, &bitmap);
    if (!bitmap.bmBits || (DWORD)(ULONG_PTR)bitmap.bmBits != g_last_present_screen ||
        bitmap.bmWidthBytes < (LONG)G1_OVERLAY_SCREEN_WIDTH ||
        bitmap.bmWidthBytes > (LONG)G1_MAX_STRIDE ||
        bitmap.bmHeight < (LONG)G1_OVERLAY_SCREEN_HEIGHT) return FALSE;
    *buffer = (BYTE *)bitmap.bmBits;
    *stride = (DWORD)bitmap.bmWidthBytes;
    ++g_textout_screen_dc_calls;
    return TRUE;
}

static void textout_reject_target_note(HDC hdc, int x, int y, LPCSTR text, int length)
{
    void *renderer = (void *)(ULONG_PTR)G1_RENDERER_VA;
    DWORD state = read_game_dword(G1_PROGRAM_STATE_VA);
    DWORD *logged = state == 5u ? &g_textout_reject_logged_ps5 : &g_textout_reject_logged_ps7;
    BITMAP bitmap;
    SIZE extent;
    char line[384];
    if (state == 5u) ++g_textout_reject_target_ps5;
    else if (state == 7u) ++g_textout_reject_target_ps7;
    else ++g_textout_reject_target_other;
    textout_dc_bitmap(hdc, &bitmap);
    if (bitmap.bmBits && (DWORD)(ULONG_PTR)bitmap.bmBits == g_last_present_screen)
        ++g_textout_reject_target_dc_screen;
    else if (bitmap.bmBits && bitmap.bmBits ==
             *(BYTE **)((BYTE *)renderer + G1_RENDERER_BUFFER))
        ++g_textout_reject_target_dc_buffer;
    else
        ++g_textout_reject_target_dc_other;
    if (!layer_drift_on() || (state != 5u && state != 7u) ||
        *logged >= G1_TEXTOUT_REJECT_LOG_LIMIT) return;
    ++*logged;
    extent.cx = 0;
    extent.cy = 0;
    if (g_textout_extent) g_textout_extent(hdc, text, length, &extent);
    layer_drift_emit(line, wsprintfA(line,
        "{\"t\":\"tx\",\"p\":%u,\"state\":%u,\"x\":%d,\"y\":%d,\"len\":%d,\"cx\":%d,\"cy\":%d,\"rbuf\":%u,\"rstride\":%u,\"rh\":%u,\"dcbits\":%u,\"dcw\":%d,\"dch\":%d,\"dcstride\":%d,\"scr\":%u}\n",
        (unsigned)g_drift_present, (unsigned)state, x, y, length, (int)extent.cx,
        (int)extent.cy,
        (unsigned)(ULONG_PTR)*(BYTE **)((BYTE *)renderer + G1_RENDERER_BUFFER),
        (unsigned)*(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_STRIDE),
        (unsigned)*(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_HEIGHT),
        (unsigned)(ULONG_PTR)bitmap.bmBits, (int)bitmap.bmWidth, (int)bitmap.bmHeight,
        (int)bitmap.bmWidthBytes, (unsigned)g_last_present_screen));
}

/* GDI text: the game calls gdi32!TextOutA through IAT slot 0x4E502C (59 call
 * sites, many draw a +1,+1 shadow first).  Only TA_LEFT|TA_TOP calls are
 * handled; the rectangle is the measured text extent plus a 1 px margin, so the
 * shadow offset and glyph overhang stay inside it.  GdiFlush makes sure the
 * glyph bits are in the surface memory before the changed pixels are read. */
static BOOL WINAPI mirror_textout(HDC hdc, int x, int y, LPCSTR text, int length)
{
    G1OverlayStats stats;
    void *renderer = (void *)(ULONG_PTR)G1_RENDERER_VA;
    BYTE *buffer = NULL;
    DWORD stride = 0u, row, col;
    LONG x0 = 0, y0 = 0, x1 = 0, y1 = 0;
    SIZE extent;
    BOOL active = FALSE, result;
    DWORD return_address = (DWORD)(ULONG_PTR)__builtin_return_address(0);
    if (!g_real_textout) return FALSE;
    ++g_textout_invocations;
    if (g_ret_range_diag) ret_range_diag_count(return_address, &g_ret_diag_textout_kills, &g_ret_diag_textout_idle);
    extent.cx = 0;
    extent.cy = 0;
    if (g_primitive_guard) {
        ++g_textout_reject_guard;
    } else if (g_mirror && g_covered && g_expected_snapshot && text && length > 0) {
        stride = *(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_STRIDE);
        buffer = *(BYTE **)((BYTE *)renderer + G1_RENDERER_BUFFER);
        if ((!buffer || (DWORD)(ULONG_PTR)buffer == G1_CACHE_BASE ||
             buffer == g_panel_bound_buffer || stride < G1_OVERLAY_SCREEN_WIDTH ||
             stride > G1_MAX_STRIDE ||
             *(volatile DWORD *)((BYTE *)renderer + G1_RENDERER_HEIGHT) !=
                 G1_OVERLAY_SCREEN_HEIGHT) &&
            !textout_screen_dc_target(hdc, &buffer, &stride)) {
            ++g_textout_reject_target;
            textout_reject_target_note(hdc, x, y, text, length);
        } else if (g_textout_align(hdc) != 0u) {
            ++g_textout_reject_align;
        } else if (!g_textout_extent(hdc, text, length, &extent) || extent.cx <= 0 ||
                   extent.cy <= 0) {
            ++g_textout_reject_size;
        } else {
            x0 = (LONG)x - 1;
            y0 = (LONG)y - 1;
            x1 = (LONG)x + extent.cx + 1;
            y1 = (LONG)y + extent.cy + 1;
            if (x0 < 0) x0 = 0;
            if (y0 < 0) y0 = 0;
            if (x1 > (LONG)G1_OVERLAY_SCREEN_WIDTH) x1 = (LONG)G1_OVERLAY_SCREEN_WIDTH;
            if (y1 > (LONG)G1_OVERLAY_SCREEN_HEIGHT) y1 = (LONG)G1_OVERLAY_SCREEN_HEIGHT;
            if (x0 >= x1 || y0 >= y1 ||
                !g1_overlay_blt_accepts(0, 0, 1, 1, G1_OVERLAY_SCREEN_WIDTH,
                                        G1_OVERLAY_SCREEN_HEIGHT, (size_t)x0,
                                        (size_t)y0, (size_t)(x1 - x0),
                                        (size_t)(y1 - y0))) {
                ++g_textout_reject_size;
            } else {
                for (row = 0u; row < (DWORD)(y1 - y0); ++row)
                    for (col = 0u; col < (DWORD)(x1 - x0); ++col)
                        g_textout_before[row * (DWORD)(x1 - x0) + col] =
                            buffer[((DWORD)y0 + row) * stride + (DWORD)x0 + col];
                active = TRUE;
            }
        }
    }
    result = g_real_textout(hdc, x, y, text, length);
    if (active) {
        g_textout_flush();
        if (g1_overlay_blt_apply(g_textout_before, buffer, stride, (size_t)x0,
                                 (size_t)y0, (size_t)(x1 - x0), (size_t)(y1 - y0),
                                 lstrcmpA(g1_hd_asset_source_name(), "scale2x") == 0,
                                 g_overlay_scratch, g_expected_snapshot, g_covered,
                                 g_mirror, 1600u, &stats)) {
            ++g_textout_mirrored_calls;
            g_textout_mirrored_pixels += (DWORD)stats.changed;
            if (stats.changed) ++g_textout_changed_calls;
        } else {
            ++g_textout_reject_size;
        }
    }
    return result;
}

/* The EXE file is never touched: only the in-memory IAT slot, and only while it
 * still holds the real gdi32!TextOutA.  A mismatch leaves it alone. */
static BOOL textout_install(void)
{
    DWORD *slot = (DWORD *)(ULONG_PTR)G1_TEXTOUT_SLOT;
    HMODULE gdi = GetModuleHandleA("gdi32.dll");
    FARPROC real = gdi ? GetProcAddress(gdi, "TextOutA") : NULL;
    FARPROC extent = gdi ? GetProcAddress(gdi, "GetTextExtentPoint32A") : NULL;
    FARPROC align = gdi ? GetProcAddress(gdi, "GetTextAlign") : NULL;
    FARPROC flush = gdi ? GetProcAddress(gdi, "GdiFlush") : NULL;
    DWORD old_protect, restored;
    if (!real || !extent || !align || !flush || !readable_bytes((const BYTE *)slot, 4u) ||
        *slot != (DWORD)(ULONG_PTR)real ||
        !VirtualProtect(slot, sizeof(DWORD), PAGE_READWRITE, &old_protect)) {
        ++g_textout_install_mismatch;
        return FALSE;
    }
    g_real_textout = (G1TextOutA)(ULONG_PTR)real;
    g_textout_extent = (G1TextExtentA)(ULONG_PTR)extent;
    g_textout_align = (G1TextAlign)(ULONG_PTR)align;
    g_textout_flush = (G1GdiFlush)(ULONG_PTR)flush;
    *slot = (DWORD)(ULONG_PTR)mirror_textout;
    VirtualProtect(slot, sizeof(DWORD), old_protect, &restored);
    g_textout_slot_active = TRUE;
    return TRUE;
}

static BOOL textout_restore(void)
{
    DWORD *slot = (DWORD *)(ULONG_PTR)G1_TEXTOUT_SLOT;
    DWORD old_protect, restored;
    if (!g_textout_slot_active) return TRUE;
    if (*slot == (DWORD)(ULONG_PTR)mirror_textout &&
        VirtualProtect(slot, sizeof(DWORD), PAGE_READWRITE, &old_protect)) {
        *slot = (DWORD)(ULONG_PTR)g_real_textout;
        VirtualProtect(slot, sizeof(DWORD), old_protect, &restored);
        if (*slot == (DWORD)(ULONG_PTR)g_real_textout) {
            g_textout_slot_active = FALSE;
            ++g_textout_slot_restored;
            return TRUE;
        }
    }
    return FALSE;
}

BOOL g1_mirror2x_primitives_install(void)
{
    static const DWORD move_sites[8] = {
        0x00432A2Du, 0x00432AB5u, 0x00432B38u, 0x00432BD4u,
        0x00432C7Cu, 0x00432D4Eu, 0x00432E1Du, 0x00432ED2u
    };
    static const BYTE move_bytes[8][5] = {
        {0xE8,0x9E,0x87,0x0A,0x00}, {0xE8,0x16,0x87,0x0A,0x00},
        {0xE8,0x93,0x86,0x0A,0x00}, {0xE8,0xF7,0x85,0x0A,0x00},
        {0xE8,0x4F,0x85,0x0A,0x00}, {0xE8,0x7D,0x84,0x0A,0x00},
        {0xE8,0xAE,0x83,0x0A,0x00}, {0xE8,0xF9,0x82,0x0A,0x00}
    };
    static const BYTE expected_cache_move[8] =
        {0x55,0x8B,0xEC,0x57,0x56,0x8B,0x75,0x0C};
    static const BYTE expected_primary_readback_site[5] = {0xE8, 0x15, 0x14, 0xFA, 0xFF};
    static const BYTE expected_bar_copy_site[5] = {0xE8, 0x18, 0x37, 0xFB, 0xFF};
    static const BYTE expected_briefing_compose_site[5] = {0xE8, 0x66, 0x22, 0x02, 0x00};
    static const BYTE expected_cache_copy[8] =
        {0x8B,0x41,0x0C,0x53,0x99,0x83,0xE2,0x07};
    static const BYTE expected_a[G1_TARGET_A_LEN] =
        {0x83, 0xEC, 0x14, 0x8B, 0x54, 0x24, 0x1C};
    static const BYTE expected_b[G1_TARGET_B_LEN] =
        {0x55, 0x56, 0x8B, 0x74, 0x24, 0x10, 0x8B, 0xE9};
    static const BYTE expected_terrain_rle[G1_TERRAIN_RLE_LEN] =
        {0x83, 0xEC, 0x0C, 0x0F, 0xBF, 0x54, 0x24, 0x14};
    static const BYTE expected_terrain_shade[G1_TERRAIN_SHADE_LEN] =
        {0x83, 0xEC, 0x10, 0x53, 0x56};
    static const BYTE expected_terrain_checker[G1_TERRAIN_CHECKER_LEN] =
        {0x83, 0xEC, 0x10, 0x53, 0x56};
    static const BYTE expected_terrain_clip[G1_TERRAIN_CLIP_LEN] =
        {0x83, 0xEC, 0x0C, 0x0F, 0xBF, 0x44, 0x24, 0x14};
    static const BYTE expected_terrain_clip_shade[G1_TERRAIN_CLIP_SHADE_LEN] =
        {0x83, 0xEC, 0x28, 0x33, 0xC0};
    static const BYTE expected_panel_rle[G1_PANEL_RLE_LEN] =
        {0x51, 0x53, 0x8B, 0x5C, 0x24, 0x10};
    static const BYTE expected_tinted_rle[G1_TINTED_RLE_LEN] =
        {0x83, 0xEC, 0x14, 0x8B, 0x44, 0x24, 0x1C};
    static const BYTE expected_tinted_clip_rle[G1_TINTED_CLIP_RLE_LEN] =
        {0x51, 0x53, 0x56, 0x57, 0x8B, 0x7C, 0x24, 0x18};
    static const BYTE expected_rect_fill[G1_RECT_FILL_LEN] =
        {0x8B, 0x44, 0x24, 0x04, 0x53};
    static const BYTE expected_cache_fill[G1_CACHE_FILL_LEN] =
        {0x8B, 0x54, 0x24, 0x0C, 0x53};
    static const BYTE expected_rect_border[G1_RECT_BORDER_LEN] =
        {0x83, 0xEC, 0x10, 0x53, 0x8B, 0x5C, 0x24, 0x18};
    static const BYTE expected_rect_border7[G1_RECT_BORDER7_LEN] =
        {0x83, 0xEC, 0x10, 0x53, 0xB8, 0x01, 0x00, 0x00, 0x00};
    static const BYTE expected_line[G1_LINE_LEN] =
        {0x83, 0xEC, 0x0C, 0x8B, 0x44, 0x24, 0x18};
    static const BYTE expected_rect_solid[G1_RECT_SOLID_LEN] =
        {0x8B, 0x41, 0x10, 0x53, 0x55};
    static const BYTE expected_flip_rle[G1_FLIP_RLE_LEN] =
        {0x51, 0x53, 0x56, 0x57, 0x8B, 0x7C, 0x24, 0x18};
    static const BYTE expected_keyed_copy[G1_KEYED_COPY_LEN] =
        {0x8B, 0x51, 0x10, 0x53, 0x8B, 0xC2};
    static const BYTE expected_flip_clip[G1_FLIP_CLIP_LEN] =
        {0x83, 0xEC, 0x18, 0x33, 0xC0};
    static const BYTE expected_shade_rle[G1_SHADE_RLE_LEN] =
        {0x51, 0x8B, 0x54, 0x24, 0x0C};
    static const BYTE expected_shade_flip[G1_SHADE_FLIP_LEN] =
        {0x51, 0x53, 0x55, 0x56, 0x57};
    static const BYTE expected_shade_clip[G1_SHADE_CLIP_LEN] =
        {0x83, 0xEC, 0x14, 0x8B, 0x54, 0x24, 0x1C};
    static const BYTE expected_blend_rle[G1_BLEND_RLE_LEN] =
        {0x51, 0x53, 0x56, 0x8B, 0xF1, 0x57};
    static const BYTE expected_blend_wrle[G1_BLEND_WRLE_LEN] =
        {0x51, 0x0F, 0xBF, 0x54, 0x24, 0x0C};
    static const BYTE expected_blend_clip[G1_BLEND_CLIP_LEN] =
        {0x83, 0xEC, 0x14, 0x33, 0xC0};
    static const BYTE expected_blend_skip[G1_BLEND_SKIP_LEN] =
        {0x83, 0xEC, 0x18, 0x53, 0x55};
    static const BYTE expected_blend_clip7[G1_BLEND_CLIP7_LEN] =
        {0x83, 0xEC, 0x18, 0x33, 0xC0};
    static const BYTE expected_flip_blend[G1_FLIP_BLEND_LEN] =
        {0x83, 0xEC, 0x08, 0x53, 0x56};
    static const BYTE expected_blend_flip7[G1_BLEND_FLIP7_LEN] =
        {0x83, 0xEC, 0x1C, 0x53, 0x55};
    static const BYTE expected_flip_blend7[G1_FLIP_BLEND7_LEN] =
        {0x83, 0xEC, 0x08, 0x55, 0x56};
    static const BYTE expected_blend_410[G1_BLEND_410_LEN] =
        {0x83, 0xEC, 0x08, 0x53, 0x56};
    static const BYTE expected_blend_6d0[G1_BLEND_6D0_LEN] =
        {0x83, 0xEC, 0x14, 0x33, 0xC0};
    DWORD move_index;
    if (!env_enabled()) return TRUE;
    if (InterlockedCompareExchange(&g_primitives_installed, 1, 0) != 0) return TRUE;
    g_scratch_a = (BYTE *)HeapAlloc(GetProcessHeap(), 0, G1_MAX_BUFFER);
    g_scratch_b = (BYTE *)HeapAlloc(GetProcessHeap(), 0, G1_MAX_BUFFER);
    g_mirror = (BYTE *)HeapAlloc(GetProcessHeap(), 0, 1600u * 1200u);
    g_covered = (BYTE *)HeapAlloc(GetProcessHeap(), 0, 800u * 600u);
    g_expected_snapshot = (BYTE *)HeapAlloc(GetProcessHeap(), 0, 800u * 600u);
    g_s3_mask = (BYTE *)HeapAlloc(GetProcessHeap(), 0, 800u * 600u);
    g_layer_mirror = (BYTE *)HeapAlloc(GetProcessHeap(), 0,
                                       G1_CACHE_WIDTH * 2u * G1_CACHE_HEIGHT * 2u);
    g_layer_covered = (BYTE *)HeapAlloc(GetProcessHeap(), 0, G1_CACHE_BYTES);
    g_layer_expected = (BYTE *)HeapAlloc(GetProcessHeap(), 0, G1_CACHE_BYTES);
    g_panel_expected = (BYTE *)HeapAlloc(GetProcessHeap(), 0,
                                         G1_PANEL_WIDTH * G1_PANEL_MAX_HEIGHT);
    g_panel_covered = (BYTE *)HeapAlloc(GetProcessHeap(), 0,
                                        G1_PANEL_WIDTH * G1_PANEL_MAX_HEIGHT);
    g_panel_mirror = (BYTE *)HeapAlloc(GetProcessHeap(), 0,
                                       G1_PANEL_HD_STRIDE * G1_PANEL_MAX_HEIGHT * 2u);
    g_panel_pack = (BYTE *)HeapAlloc(GetProcessHeap(), 0,
                                     G1_PANEL_HD_STRIDE * G1_PANEL_MAX_HEIGHT * 2u);
    g_pause_valid = (BYTE *)HeapAlloc(GetProcessHeap(), HEAP_ZERO_MEMORY, 800u * 600u);
    g_pause_expected = (BYTE *)HeapAlloc(GetProcessHeap(), 0, 800u * 600u);
    g_pause_hd = (BYTE *)HeapAlloc(GetProcessHeap(), 0, 1600u * 1200u);
    if (!g_pause_valid || !g_pause_expected || !g_pause_hd)
        g_pause_snapshot_enabled = FALSE;
    g_last_frame = (BYTE *)HeapAlloc(GetProcessHeap(), 0, 800u * 600u);
    if (!g_last_frame) g_primary_readback_enabled = FALSE;
    if (!g_scratch_a || !g_scratch_b || !g_mirror || !g_covered ||
        !g_expected_snapshot || !g_s3_mask || !g_layer_mirror ||
        !g_layer_covered || !g_layer_expected || !g_panel_expected ||
        !g_panel_covered || !g_panel_mirror || !g_panel_pack ||
        !install_one(G1_TARGET_A, expected_a, G1_TARGET_A_LEN,
                     (void *)mirror_primitive_a, &g_hook_a, &g_original_a) ||
        !install_one(G1_TARGET_B, expected_b, G1_TARGET_B_LEN,
                     (void *)mirror_primitive_b, &g_hook_b, &g_original_b) ||
        !install_one(G1_TERRAIN_RLE, expected_terrain_rle, G1_TERRAIN_RLE_LEN,
                     (void *)mirror_terrain_rle, &g_hook_terrain_rle,
                     (G1PrimitiveFn *)&g_original_terrain_rle) ||
        !install_one(G1_TERRAIN_SHADE, expected_terrain_shade, G1_TERRAIN_SHADE_LEN,
                     (void *)mirror_terrain_shade, &g_hook_terrain_shade,
                     (G1PrimitiveFn *)&g_original_terrain_shade) ||
        !install_one(G1_TERRAIN_CHECKER, expected_terrain_checker,
                     G1_TERRAIN_CHECKER_LEN, (void *)mirror_terrain_checker,
                     &g_hook_terrain_checker, &g_original_terrain_checker) ||
        !install_one(G1_TERRAIN_CLIP, expected_terrain_clip, G1_TERRAIN_CLIP_LEN,
                     (void *)mirror_terrain_clip, &g_hook_terrain_clip,
                     &g_original_terrain_clip) ||
        !install_one(G1_TERRAIN_CLIP_SHADE, expected_terrain_clip_shade,
                     G1_TERRAIN_CLIP_SHADE_LEN, (void *)mirror_terrain_clip_shade,
                     &g_hook_terrain_clip_shade,
                     (G1PrimitiveFn *)&g_original_terrain_clip_shade) ||
        !install_one(G1_PANEL_RLE, expected_panel_rle, G1_PANEL_RLE_LEN,
                     (void *)mirror_panel_rle, &g_hook_panel_rle,
                     (G1PrimitiveFn *)&g_original_panel_rle) ||
        !install_one(G1_TINTED_RLE, expected_tinted_rle, G1_TINTED_RLE_LEN,
                     (void *)mirror_tinted_rle, &g_hook_tinted_rle,
                     (G1PrimitiveFn *)&g_original_tinted_rle) ||
        !install_one(G1_TINTED_CLIP_RLE, expected_tinted_clip_rle,
                     G1_TINTED_CLIP_RLE_LEN, (void *)mirror_tinted_clip_rle,
                     &g_hook_tinted_clip_rle,
                     (G1PrimitiveFn *)&g_original_tinted_clip_rle) ||
        !install_one(G1_RECT_FILL, expected_rect_fill, G1_RECT_FILL_LEN,
                     (void *)mirror_rect_fill, &g_hook_rect_fill,
                     &g_original_rect_fill) ||
        !install_one(G1_CACHE_FILL, expected_cache_fill, G1_CACHE_FILL_LEN,
                     (void *)mirror_cache_fill, &g_hook_cache_fill,
                     &g_original_cache_fill) ||
        !install_one(G1_RECT_BORDER, expected_rect_border, G1_RECT_BORDER_LEN,
                     (void *)mirror_rect_border, &g_hook_rect_border,
                     &g_original_rect_border) ||
        !install_one(G1_RECT_BORDER7, expected_rect_border7, G1_RECT_BORDER7_LEN,
                     (void *)mirror_rect_border7, &g_hook_rect_border7,
                     (G1PrimitiveFn *)&g_original_rect_border7) ||
        !install_one(G1_LINE, expected_line, G1_LINE_LEN,
                     (void *)mirror_line, &g_hook_line, &g_original_line) ||
        !install_one(G1_RECT_SOLID, expected_rect_solid, G1_RECT_SOLID_LEN,
                     (void *)mirror_rect_solid, &g_hook_rect_solid,
                     &g_original_rect_solid) ||
        !install_one(G1_FLIP_RLE, expected_flip_rle, G1_FLIP_RLE_LEN,
                     (void *)mirror_flip_rle, &g_hook_flip_rle,
                     (G1PrimitiveFn *)&g_original_flip_rle) ||
        !install_one(G1_KEYED_COPY, expected_keyed_copy, G1_KEYED_COPY_LEN,
                     (void *)mirror_keyed_copy, &g_hook_keyed_copy,
                     &g_original_keyed_copy) ||
        !install_one(G1_FLIP_CLIP, expected_flip_clip, G1_FLIP_CLIP_LEN,
                     (void *)mirror_flip_clip, &g_hook_flip_clip,
                     (G1PrimitiveFn *)&g_original_flip_clip) ||
        !install_one(G1_SHADE_RLE, expected_shade_rle, G1_SHADE_RLE_LEN,
                     (void *)mirror_shade_rle, &g_hook_shade_rle,
                     (G1PrimitiveFn *)&g_original_shade_rle) ||
        !install_one(G1_SHADE_FLIP, expected_shade_flip, G1_SHADE_FLIP_LEN,
                     (void *)mirror_shade_flip, &g_hook_shade_flip,
                     (G1PrimitiveFn *)&g_original_shade_flip) ||
        !install_one(G1_SHADE_CLIP, expected_shade_clip, G1_SHADE_CLIP_LEN,
                     (void *)mirror_shade_clip, &g_hook_shade_clip,
                     (G1PrimitiveFn *)&g_original_shade_clip) ||
        !install_one(G1_BLEND_RLE, expected_blend_rle, G1_BLEND_RLE_LEN,
                     (void *)mirror_blend_rle, &g_hook_blend_rle,
                     &g_original_blend_rle) ||
        !install_one(G1_BLEND_WRLE, expected_blend_wrle, G1_BLEND_WRLE_LEN,
                     (void *)mirror_blend_wrle, &g_hook_blend_wrle,
                     &g_original_blend_wrle) ||
        !install_one(G1_BLEND_CLIP, expected_blend_clip, G1_BLEND_CLIP_LEN,
                     (void *)mirror_blend_clip, &g_hook_blend_clip,
                     &g_original_blend_clip) ||
        !install_one(G1_BLEND_SKIP, expected_blend_skip, G1_BLEND_SKIP_LEN,
                     (void *)mirror_blend_skip, &g_hook_blend_skip,
                     &g_original_blend_skip) ||
        !install_one(G1_BLEND_CLIP7, expected_blend_clip7, G1_BLEND_CLIP7_LEN,
                     (void *)mirror_blend_clip7, &g_hook_blend_clip7,
                     (G1PrimitiveFn *)&g_original_blend_clip7) ||
        !install_one(G1_FLIP_BLEND, expected_flip_blend, G1_FLIP_BLEND_LEN,
                     (void *)mirror_flip_blend, &g_hook_flip_blend,
                     &g_original_flip_blend) ||
        !install_one(G1_BLEND_FLIP7, expected_blend_flip7, G1_BLEND_FLIP7_LEN,
                     (void *)mirror_blend_flip7, &g_hook_blend_flip7,
                     (G1PrimitiveFn *)&g_original_blend_flip7) ||
        !install_one(G1_FLIP_BLEND7, expected_flip_blend7, G1_FLIP_BLEND7_LEN,
                     (void *)mirror_flip_blend7, &g_hook_flip_blend7,
                     (G1PrimitiveFn *)&g_original_flip_blend7) ||
        !install_one(G1_BLEND_410, expected_blend_410,
                     G1_BLEND_410_LEN, (void *)mirror_blend_410, &g_hook_blend_410,
                     (G1PrimitiveFn *)&g_original_blend_410) ||
        (layer_drift_on() && !install_one(G1_BLEND_6D0, expected_blend_6d0,
                     G1_BLEND_6D0_LEN, (void *)observe_blend_6d0, &g_hook_blend_6d0,
                     &g_original_blend_6d0)) ||
        !bytes_equal((const BYTE *)(ULONG_PTR)G1_CACHE_MOVE,
                     expected_cache_move, sizeof(expected_cache_move)) ||
        !bytes_equal((const BYTE *)(ULONG_PTR)G1_CACHE_COPY,
                     expected_cache_copy, sizeof(expected_cache_copy)) ||
        !install_one(G1_CACHE_COPY, expected_cache_copy, sizeof(expected_cache_copy),
                     (void *)mirror_cache_copy, &g_hook_cache_copy,
                     &g_original_cache_copy)) {
        g1_mirror2x_primitives_detach();
        return FALSE;
    }
    g_original_cache_move = (G1MemmoveFn)(ULONG_PTR)G1_CACHE_MOVE;
    for (move_index = 0u; move_index < 8u; ++move_index) {
        if (!install_callsite(move_sites[move_index], move_bytes[move_index],
                              (void *)mirror_cache_move,
                              &g_hook_cache_moves[move_index])) {
            g1_mirror2x_primitives_detach();
            return FALSE;
        }
    }
    if (!install_callsite(G1_PRIMARY_READBACK_SITE, expected_primary_readback_site,
                          (void *)mirror_primary_readback_site, &g_hook_primary_readback)) {
        g1_mirror2x_primitives_detach();
        return FALSE;
    }
    if (!install_callsite(G1_BAR_COPY_SITE, expected_bar_copy_site,
                          (void *)mirror_bar_copy_site, &g_hook_bar_copy)) {
        g1_mirror2x_primitives_detach();
        return FALSE;
    }
    if (!install_callsite(G1_BRIEFING_COMPOSE_SITE, expected_briefing_compose_site,
                          (void *)mirror_briefing_compose_site, &g_hook_briefing_compose)) {
        g1_mirror2x_primitives_detach();
        return FALSE;
    }
    zero_bytes(g_covered, 800u * 600u);
    zero_bytes(g_expected_snapshot, 800u * 600u);
    zero_bytes(g_s3_mask, 800u * 600u);
    zero_bytes(g_layer_mirror, G1_CACHE_WIDTH * 2u * G1_CACHE_HEIGHT * 2u);
    zero_bytes(g_layer_covered, G1_CACHE_BYTES);
    zero_bytes(g_layer_expected, G1_CACHE_BYTES);
    zero_bytes(g_panel_expected, G1_PANEL_WIDTH * G1_PANEL_MAX_HEIGHT);
    zero_bytes(g_panel_covered, G1_PANEL_WIDTH * G1_PANEL_MAX_HEIGHT);
    zero_bytes(g_panel_mirror, G1_PANEL_HD_STRIDE * G1_PANEL_MAX_HEIGHT * 2u);
    zero_bytes(g_panel_pack, G1_PANEL_HD_STRIDE * G1_PANEL_MAX_HEIGHT * 2u);
    g_panel_bound_buffer = NULL;
    g_panel_bound_pitch = 0u;
    g_panel_bound_height = 0u;
    g_panel_frame_width = 0u;
    g_panel_frame_height = 0u;
    g_panel_frame_sha256[0] = '\0';
    g_panel_key_subpixels = 0u;
    g_panel_bound_transfer_count = 0u;
    g_panel_unbound_transfer_count = 0u;
    g_panel_lock_failures = 0u;
    g_panel_pointer_mismatches = 0u;
    g_panel_pitch_mismatches = 0u;
    g_panel_foreign_writer_count = 0u;
    g_panel_transfer_copied = 0u;
    g_panel_transfer_key_preserved = 0u;
    g_panel_transfer_mismatch_cleared = 0u;
    g_overlay_blt_mirrored_calls = 0u;
    g_overlay_blt_mirrored_pixels = 0u;
    g_overlay_blt_rejects = 0u;
    g_rect_fill_invocations = 0u;
    g_rect_fill_mirrored_calls = 0u;
    g_rect_fill_mirrored_pixels = 0u;
    g_rect_fill_reject_target = 0u;
    g_rect_fill_reject_size = 0u;
    g_rect_fill_reject_guard = 0u;
    g_cache_fill_invocations = 0u;
    g_cache_fill_mirrored_calls = 0u;
    g_cache_fill_mirrored_pixels = 0u;
    g_cache_fill_reject_target = 0u;
    g_cache_fill_unsupported = 0u;
    g_rect_border_invocations = 0u;
    g_rect_border_mirrored_calls = 0u;
    g_rect_border_mirrored_pixels = 0u;
    g_rect_border_reject_target = 0u;
    g_rect_border_reject_size = 0u;
    g_rect_border_reject_guard = 0u;
    g_rect_border7_invocations = 0u;
    g_rect_border7_mirrored_calls = 0u;
    g_rect_border7_mirrored_pixels = 0u;
    g_rect_border7_reject_target = 0u;
    g_rect_border7_reject_size = 0u;
    g_rect_border7_reject_guard = 0u;
    g_line_invocations = 0u;
    g_line_mirrored_calls = 0u;
    g_line_mirrored_pixels = 0u;
    g_line_reject_target = 0u;
    g_line_reject_size = 0u;
    g_line_reject_guard = 0u;
    g_rect_solid_invocations = 0u;
    g_rect_solid_mirrored_calls = 0u;
    g_rect_solid_mirrored_pixels = 0u;
    g_rect_solid_reject_target = 0u;
    g_rect_solid_wide_calls = 0u;
    g_rect_solid_reject_bounds = 0u;
    g_rect_solid_reject_size = 0u;
    g_rect_solid_reject_guard = 0u;
    g_rect_solid_ybound = 0u;
    g_flip_rle_invocations = 0u;
    g_flip_rle_mirrored_calls = 0u;
    g_flip_rle_mirrored_pixels = 0u;
    g_flip_rle_reject_target = 0u;
    g_flip_rle_reject_size = 0u;
    g_flip_rle_reject_guard = 0u;
    g_flip_rle_reject_bounds = 0u;
    g_flip_rle_clipped_calls = 0u;
    g_flip_rle_wrap_calls = 0u;
    g_flip_rle_keyed_calls = 0u;
    g_flip_rle_key_fallbacks = 0u;
    g_keyed_copy_invocations = 0u;
    g_keyed_copy_mirrored_calls = 0u;
    g_keyed_copy_mirrored_pixels = 0u;
    g_keyed_copy_changed_calls = 0u;
    g_keyed_copy_clipped_calls = 0u;
    g_keyed_copy_reject_target = 0u;
    g_keyed_copy_reject_bounds = 0u;
    g_keyed_copy_reject_size = 0u;
    g_keyed_copy_reject_guard = 0u;
    g_flip_clip_invocations = 0u;
    g_flip_clip_mirrored_calls = 0u;
    g_flip_clip_mirrored_pixels = 0u;
    g_flip_clip_reject_target = 0u;
    g_flip_clip_reject_size = 0u;
    g_flip_clip_reject_guard = 0u;
    g_flip_clip_reject_bounds = 0u;
    g_flip_clip_changed_calls = 0u;
    g_flip_clip_clipped_calls = 0u;
    g_flip_clip_wrap_calls = 0u;
    g_shade_rle_invocations = 0u;
    g_shade_rle_mirrored_calls = 0u;
    g_shade_rle_mirrored_pixels = 0u;
    g_shade_rle_reject_target = 0u;
    g_shade_rle_reject_size = 0u;
    g_shade_rle_reject_guard = 0u;
    g_shade_rle_reject_bounds = 0u;
    g_shade_rle_changed_calls = 0u;
    g_shade_rle_clipped_calls = 0u;
    g_shade_rle_wrap_calls = 0u;
    g_shade_flip_invocations = 0u;
    g_shade_flip_mirrored_calls = 0u;
    g_shade_flip_mirrored_pixels = 0u;
    g_shade_flip_reject_target = 0u;
    g_shade_flip_reject_size = 0u;
    g_shade_flip_reject_guard = 0u;
    g_shade_flip_reject_bounds = 0u;
    g_shade_flip_changed_calls = 0u;
    g_shade_flip_clipped_calls = 0u;
    g_shade_flip_wrap_calls = 0u;
    g_shade_clip_invocations = 0u;
    g_shade_clip_mirrored_calls = 0u;
    g_shade_clip_mirrored_pixels = 0u;
    g_shade_clip_reject_target = 0u;
    g_shade_clip_reject_size = 0u;
    g_shade_clip_reject_guard = 0u;
    g_shade_clip_reject_bounds = 0u;
    g_shade_clip_changed_calls = 0u;
    g_shade_clip_clipped_calls = 0u;
    g_shade_clip_wrap_calls = 0u;
    g_blend_rle_invocations = 0u;
    g_blend_rle_mirrored_calls = 0u;
    g_blend_rle_mirrored_pixels = 0u;
    g_blend_rle_changed_calls = 0u;
    g_blend_rle_reject_target = 0u;
    g_blend_rle_reject_bounds = 0u;
    g_blend_rle_reject_size = 0u;
    g_blend_rle_reject_guard = 0u;
    g_blend_rle_key.keyed_calls = 0u;
    g_blend_rle_key.keyed_pixels = 0u;
    g_blend_rle_key.key_fallbacks = 0u;
    g_blend_rle_key.selfcheck_mismatches = 0u;
    g_blend_rle_key.selfcheck_pixels = 0u;
    g_blend_wrle_key.keyed_calls = 0u;
    g_blend_wrle_key.keyed_pixels = 0u;
    g_blend_wrle_key.key_fallbacks = 0u;
    g_blend_wrle_key.selfcheck_mismatches = 0u;
    g_blend_wrle_key.selfcheck_pixels = 0u;
    g_blend_clip_key.keyed_calls = 0u;
    g_blend_clip_key.keyed_pixels = 0u;
    g_blend_clip_key.key_fallbacks = 0u;
    g_blend_clip_key.selfcheck_mismatches = 0u;
    g_blend_clip_key.selfcheck_pixels = 0u;
    g_blend_clip_key.key_clip_cut = 0u;
    g_blend_clip_key.key_clip_empty = 0u;
    g_flip_blend_key.keyed_calls = 0u;
    g_flip_blend_key.keyed_pixels = 0u;
    g_flip_blend_key.key_fallbacks = 0u;
    g_flip_blend_key.selfcheck_mismatches = 0u;
    g_flip_blend_key.selfcheck_pixels = 0u;
    g_flip_blend_key.key_wrap_mismatches = 0u;
    g_blend_skip_key.keyed_calls = 0u;
    g_blend_skip_key.keyed_pixels = 0u;
    g_blend_skip_key.key_fallbacks = 0u;
    g_blend_skip_key.selfcheck_mismatches = 0u;
    g_blend_skip_key.selfcheck_pixels = 0u;
    g_blend_skip_key.key_clip_cut = 0u;
    g_blend_skip_key.key_clip_empty = 0u;
    g_blend_clip7_key.keyed_calls = 0u;
    g_blend_clip7_key.keyed_pixels = 0u;
    g_blend_clip7_key.key_fallbacks = 0u;
    g_blend_clip7_key.selfcheck_mismatches = 0u;
    g_blend_clip7_key.selfcheck_pixels = 0u;
    g_blend_clip7_key.key_clip_cut = 0u;
    g_blend_clip7_key.key_clip_empty = 0u;
    g_blend_clip7_key.key_level_rejects = 0u;
    g_blend_flip7_key.keyed_calls = 0u;
    g_blend_flip7_key.keyed_pixels = 0u;
    g_blend_flip7_key.key_fallbacks = 0u;
    g_blend_flip7_key.selfcheck_mismatches = 0u;
    g_blend_flip7_key.selfcheck_pixels = 0u;
    g_blend_flip7_key.key_clip_cut = 0u;
    g_blend_flip7_key.key_clip_empty = 0u;
    g_blend_flip7_key.key_level_rejects = 0u;
    g_blend_wrle_invocations = 0u;
    g_blend_wrle_mirrored_calls = 0u;
    g_blend_wrle_mirrored_pixels = 0u;
    g_blend_wrle_changed_calls = 0u;
    g_blend_wrle_clipped_calls = 0u;
    g_blend_wrle_reject_target = 0u;
    g_blend_wrle_reject_bounds = 0u;
    g_blend_wrle_reject_size = 0u;
    g_blend_wrle_reject_guard = 0u;
    g_blend_clip_invocations = 0u;
    g_blend_clip_mirrored_calls = 0u;
    g_blend_clip_mirrored_pixels = 0u;
    g_blend_clip_changed_calls = 0u;
    g_blend_clip_clipped_calls = 0u;
    g_blend_clip_reject_target = 0u;
    g_blend_clip_reject_bounds = 0u;
    g_blend_clip_reject_size = 0u;
    g_blend_clip_reject_guard = 0u;
    g_blend_clip_band_calls = 0u;
    g_blend_skip_invocations = 0u;
    g_blend_skip_mirrored_calls = 0u;
    g_blend_skip_mirrored_pixels = 0u;
    g_blend_skip_changed_calls = 0u;
    g_blend_skip_clipped_calls = 0u;
    g_blend_skip_reject_target = 0u;
    g_blend_skip_reject_bounds = 0u;
    g_blend_skip_reject_size = 0u;
    g_blend_skip_reject_guard = 0u;
    g_blend_skip_band_calls = 0u;
    g_blend_clip7_invocations = 0u;
    g_blend_clip7_mirrored_calls = 0u;
    g_blend_clip7_mirrored_pixels = 0u;
    g_blend_clip7_changed_calls = 0u;
    g_blend_clip7_clipped_calls = 0u;
    g_blend_clip7_reject_target = 0u;
    g_blend_clip7_reject_bounds = 0u;
    g_blend_clip7_reject_size = 0u;
    g_blend_clip7_reject_guard = 0u;
    g_flip_blend_invocations = 0u;
    g_flip_blend_mirrored_calls = 0u;
    g_flip_blend_mirrored_pixels = 0u;
    g_flip_blend_changed_calls = 0u;
    g_flip_blend_clipped_calls = 0u;
    g_flip_blend_reject_target = 0u;
    g_flip_blend_reject_bounds = 0u;
    g_flip_blend_reject_size = 0u;
    g_flip_blend_reject_guard = 0u;
    g_flip_blend_wrap_calls = 0u;
    g_blend_flip7_invocations = 0u;
    g_blend_flip7_mirrored_calls = 0u;
    g_blend_flip7_mirrored_pixels = 0u;
    g_blend_flip7_changed_calls = 0u;
    g_blend_flip7_clipped_calls = 0u;
    g_blend_flip7_reject_target = 0u;
    g_blend_flip7_reject_bounds = 0u;
    g_blend_flip7_reject_size = 0u;
    g_blend_flip7_reject_guard = 0u;
    g_flip_blend7_invocations = 0u;
    g_flip_blend7_mirrored_calls = 0u;
    g_flip_blend7_mirrored_pixels = 0u;
    g_flip_blend7_changed_calls = 0u;
    g_flip_blend7_reject_target = 0u;
    g_flip_blend7_reject_bounds = 0u;
    g_flip_blend7_reject_size = 0u;
    g_flip_blend7_reject_guard = 0u;
    g_rect_blt_invocations = 0u;
    g_rect_blt_mirrored_calls = 0u;
    g_rect_blt_mirrored_pixels = 0u;
    g_rect_blt_changed_calls = 0u;
    g_rect_blt_clipped_calls = 0u;
    g_rect_blt_keysrc_calls = 0u;
    g_rect_blt_colorfill_calls = 0u;
    g_rect_blt_reject_bounds = 0u;
    g_rect_blt_reject_size = 0u;
    g_rect_blt_reject_lock = 0u;
    g_rect_blt_reject_target = 0u;
    g_rect_blt_reject_result = 0u;
    g_rect_blt_heal_active = FALSE;
    g_rect_blt_heal_quiet = 0u;
    g_rect_blt_heal_presents = 0u;
    g_rect_blt_heal_pixels = 0u;
    g_rect_blt_heal2_presents = 0u;
    g_rect_blt_heal2_pixels = 0u;
    g_rect_blt_heal2_skipped = 0u;
    g_rect_solid_reject_logged = 0u;
    g_rect_border_reject_logged = 0u;
    g_drift_w_records = 0u;
    g_blend_410_invocations = 0u;
    g_blend_410_changed_calls = 0u;
    g_blend_410_mirrored_calls = 0u;
    g_blend_410_mirrored_pixels = 0u;
    g_blend_410_reject_target = 0u;
    g_blend_410_reject_bounds = 0u;
    g_blend_410_reject_size = 0u;
    g_blend_410_reject_guard = 0u;
    g_blend_6d0_invocations = 0u;
    g_blend_6d0_changed_calls = 0u;
    ZeroMemory(g_drift_unattributed, sizeof(g_drift_unattributed));
    ZeroMemory(g_drift_w_hit, sizeof(g_drift_w_hit));
    g_drift_prev_valid = FALSE;
    g_textout_invocations = 0u;
    g_ret_diag_b_kills = 0u;
    g_ret_diag_b_idle = 0u;
    g_ret_diag_textout_kills = 0u;
    g_ret_diag_textout_idle = 0u;
    g_textout_mirrored_calls = 0u;
    g_textout_mirrored_pixels = 0u;
    g_textout_changed_calls = 0u;
    g_textout_reject_target = 0u;
    g_textout_reject_target_ps5 = 0u;
    g_textout_reject_target_ps7 = 0u;
    g_textout_reject_target_other = 0u;
    g_textout_screen_dc_calls = 0u;
    g_textout_reject_target_dc_screen = 0u;
    g_textout_reject_target_dc_buffer = 0u;
    g_textout_reject_target_dc_other = 0u;
    g_textout_reject_logged_ps5 = 0u;
    g_textout_reject_logged_ps7 = 0u;
    g_textout_reject_size = 0u;
    g_textout_reject_guard = 0u;
    g_textout_reject_align = 0u;
    g_textout_install_mismatch = 0u;
    g_textout_slot_restored = 0u;
    g1_hd_asset_reset();
    g_primitive_reinvoke_elapsed_ms_total = 0u;
    g_primitive_reinvoke_elapsed_ms_max = 0u;
    g_primitive_reinvoke_count = 0u;
    g_viewport_replay_count = 0u;
    g_viewport_field_mutations = 0u;
    g_viewport_restore_failures = 0u;
    g_cache_clip_attempts = 0u;
    g_cache_clip_verify_failures = 0u;
    g_cache_clip_viewport_seen = FALSE;
    g_cache_edge_unclipped_binds = 0u;
    ZeroMemory(g_cache_clip_first_viewport, sizeof(g_cache_clip_first_viewport));
    ZeroMemory(g_writer_call_counts, sizeof(g_writer_call_counts));
    ZeroMemory(g_tinted_writer_calls, sizeof(g_tinted_writer_calls));
    ZeroMemory(g_tinted_writer_covered, sizeof(g_tinted_writer_covered));
    ZeroMemory(g_writer_clip_mismatch_counts, sizeof(g_writer_clip_mismatch_counts));
    g_last_clip_mismatch_writer = 0u;
    g_last_clip_mismatch_origin_x = 0u;
    g_last_clip_mismatch_origin_y = 0u;
    g_last_clip_mismatch_width = 0u;
    g_last_clip_mismatch_height = 0u;
    g_last_clip_mismatch_x = 0u;
    g_last_clip_mismatch_y = 0u;
    g_last_clip_screen_value = 0u;
    g_last_clip_replay_value = 0u;
    textout_install();
    return TRUE;
}

void g1_mirror2x_primitives_detach(void)
{
    textout_restore();
    BOOL restored_a = restore_hook(&g_hook_a);
    BOOL restored_b = restore_hook(&g_hook_b);
    BOOL restored_rle = restore_hook(&g_hook_terrain_rle);
    BOOL restored_shade = restore_hook(&g_hook_terrain_shade);
    BOOL restored_checker = restore_hook(&g_hook_terrain_checker);
    BOOL restored_clip = restore_hook(&g_hook_terrain_clip);
    BOOL restored_clip_shade = restore_hook(&g_hook_terrain_clip_shade);
    BOOL restored_panel_rle = restore_hook(&g_hook_panel_rle);
    BOOL restored_tinted_rle = restore_hook(&g_hook_tinted_rle);
    BOOL restored_tinted_clip_rle = restore_hook(&g_hook_tinted_clip_rle);
    BOOL restored_rect_fill = restore_hook(&g_hook_rect_fill);
    BOOL restored_cache_fill = restore_hook(&g_hook_cache_fill);
    BOOL restored_rect_border = restore_hook(&g_hook_rect_border);
    BOOL restored_rect_border7 = restore_hook(&g_hook_rect_border7);
    BOOL restored_line = restore_hook(&g_hook_line);
    BOOL restored_rect_solid = restore_hook(&g_hook_rect_solid);
    BOOL restored_flip_rle = restore_hook(&g_hook_flip_rle);
    BOOL restored_keyed_copy = restore_hook(&g_hook_keyed_copy);
    BOOL restored_flip_clip = restore_hook(&g_hook_flip_clip);
    BOOL restored_shade_rle = restore_hook(&g_hook_shade_rle);
    BOOL restored_shade_flip = restore_hook(&g_hook_shade_flip);
    BOOL restored_shade_clip = restore_hook(&g_hook_shade_clip);
    BOOL restored_blend_rle = restore_hook(&g_hook_blend_rle);
    BOOL restored_blend_wrle = restore_hook(&g_hook_blend_wrle);
    BOOL restored_blend_clip = restore_hook(&g_hook_blend_clip);
    BOOL restored_blend_skip = restore_hook(&g_hook_blend_skip);
    BOOL restored_blend_clip7 = restore_hook(&g_hook_blend_clip7);
    BOOL restored_flip_blend = restore_hook(&g_hook_flip_blend);
    BOOL restored_blend_flip7 = restore_hook(&g_hook_blend_flip7);
    BOOL restored_flip_blend7 = restore_hook(&g_hook_flip_blend7);
    BOOL restored_blend_410 = restore_hook(&g_hook_blend_410);
    BOOL restored_blend_6d0 = restore_hook(&g_hook_blend_6d0);
    BOOL restored_cache_copy = restore_hook(&g_hook_cache_copy);
    BOOL restored_primary_readback = restore_hook(&g_hook_primary_readback);
    BOOL restored_bar_copy = restore_hook(&g_hook_bar_copy);
    BOOL restored_briefing_compose = restore_hook(&g_hook_briefing_compose);
    BOOL restored_moves = TRUE;
    DWORD move_index;
    for (move_index = 0u; move_index < 8u; ++move_index)
        if (!restore_hook(&g_hook_cache_moves[move_index])) restored_moves = FALSE;
    if (!restored_a || !restored_b || !restored_rle || !restored_shade ||
        !restored_checker || !restored_clip || !restored_clip_shade ||
        !restored_panel_rle || !restored_tinted_rle || !restored_tinted_clip_rle ||
        !restored_rect_fill || !restored_cache_fill || !restored_rect_border || !restored_rect_border7 ||
        !restored_line ||
        !restored_rect_solid ||
        !restored_flip_rle ||
        !restored_keyed_copy ||
        !restored_flip_clip ||
        !restored_shade_rle ||
        !restored_shade_flip ||
        !restored_shade_clip ||
        !restored_blend_rle || !restored_blend_wrle || !restored_blend_clip ||
        !restored_blend_skip ||
        !restored_blend_clip7 || !restored_flip_blend || !restored_blend_flip7 ||
        !restored_flip_blend7 ||
        !restored_blend_410 ||
        !restored_blend_6d0 || !restored_cache_copy || !restored_primary_readback ||
        !restored_bar_copy || !restored_briefing_compose || !restored_moves) return;
    g_original_a = NULL;
    g_original_b = NULL;
    g_original_terrain_rle = NULL;
    g_original_terrain_shade = NULL;
    g_original_terrain_checker = NULL;
    g_original_terrain_clip = NULL;
    g_original_terrain_clip_shade = NULL;
    g_original_panel_rle = NULL;
    g_original_tinted_rle = NULL;
    g_original_tinted_clip_rle = NULL;
    g_original_rect_fill = NULL;
    g_original_cache_fill = NULL;
    g_original_rect_border = NULL;
    g_original_rect_border7 = NULL;
    g_original_line = NULL;
    g_original_rect_solid = NULL;
    g_original_flip_rle = NULL;
    g_original_keyed_copy = NULL;
    g_original_flip_clip = NULL;
    g_original_shade_rle = NULL;
    g_original_shade_flip = NULL;
    g_original_shade_clip = NULL;
    g_original_blend_rle = NULL;
    g_original_blend_wrle = NULL;
    g_original_blend_clip = NULL;
    g_original_blend_skip = NULL;
    g_original_blend_clip7 = NULL;
    g_original_flip_blend = NULL;
    g_original_blend_flip7 = NULL;
    g_original_flip_blend7 = NULL;
    g_original_blend_410 = NULL;
    g_original_blend_6d0 = NULL;
    g_original_cache_copy = NULL;
    g_original_cache_move = NULL;
    InterlockedExchange(&g_primitives_installed, 0);
}

DWORD g1_mirror2x_primitive_call_count(void) { return g_primitive_calls; }
DWORD g1_mirror2x_terrain_writer_calls(DWORD writer_index)
{
    return writer_index < 5u ? g_writer_call_counts[writer_index + 2u] : 0u;
}
DWORD g1_mirror2x_tinted_writer_calls(DWORD writer_index)
{
    return writer_index < 2u ? g_tinted_writer_calls[writer_index] : 0u;
}
DWORD g1_mirror2x_tinted_writer_covered(DWORD writer_index)
{
    return writer_index < 2u ? g_tinted_writer_covered[writer_index] : 0u;
}
DWORD g1_mirror2x_writer_clip_mismatches(DWORD writer_index)
{
    return writer_index < 7u ? g_writer_clip_mismatch_counts[writer_index] : 0u;
}
void g1_mirror2x_last_clip_mismatch(DWORD *writer, DWORD *origin_x,
                                    DWORD *origin_y, DWORD *width,
                                    DWORD *height, DWORD *pixel_x,
                                    DWORD *pixel_y, BYTE *screen_value,
                                    BYTE *replay_value)
{
    if (writer) *writer = g_last_clip_mismatch_writer;
    if (origin_x) *origin_x = g_last_clip_mismatch_origin_x;
    if (origin_y) *origin_y = g_last_clip_mismatch_origin_y;
    if (width) *width = g_last_clip_mismatch_width;
    if (height) *height = g_last_clip_mismatch_height;
    if (pixel_x) *pixel_x = g_last_clip_mismatch_x;
    if (pixel_y) *pixel_y = g_last_clip_mismatch_y;
    if (screen_value) *screen_value = g_last_clip_screen_value;
    if (replay_value) *replay_value = g_last_clip_replay_value;
}
DWORD g1_mirror2x_primitive_covered_pixels(void) { return g_covered_pixels; }
DWORD g1_mirror2x_stale_pixel_count(void) { return g_stale_pixels; }
DWORD g1_mirror2x_present_count(void) { return g_present_count; }
DWORD g1_mirror2x_viewport_replay_count(void) { return g_viewport_replay_count; }
DWORD g1_mirror2x_cache_clip_attempts(void) { return g_cache_clip_attempts; }
DWORD g1_mirror2x_cache_clip_verify_failures(void) { return g_cache_clip_verify_failures; }
DWORD g1_mirror2x_cache_edge_unclipped_binds(void) { return g_cache_edge_unclipped_binds; }
void g1_mirror2x_cache_clip_first_viewport(LONG viewport[4])
{
    DWORD i;
    for (i = 0u; i < 4u; ++i) viewport[i] = g_cache_clip_first_viewport[i];
}
DWORD g1_mirror2x_viewport_field_mutations(void) { return g_viewport_field_mutations; }
DWORD g1_mirror2x_viewport_restore_failures(void) { return g_viewport_restore_failures; }
DWORD g1_mirror2x_layer_compose_calls(void) { return g_layer_compose_calls; }
DWORD g1_mirror2x_layer_move_calls(void) { return g_layer_move_calls; }
DWORD g1_mirror2x_layer_move_bytes(void) { return g_layer_move_bytes; }
DWORD g1_mirror2x_layer_move_unsupported(void) { return g_layer_move_unsupported; }
DWORD g1_mirror2x_layer_transfer_calls(void) { return g_layer_transfer_calls; }
DWORD g1_mirror2x_layer_covered_pixels(void) { return g_layer_covered_pixels; }
DWORD g1_mirror2x_menu_copy_calls(void) { return g_menu_copy_calls; }
DWORD g1_mirror2x_menu_copy_pixels(void) { return g_menu_copy_pixels; }
DWORD g1_mirror2x_menu_copy_hash_first(void) { return g_menu_copy_hash_first; }
DWORD g1_mirror2x_menu_copy_hash_last(void) { return g_menu_copy_hash_last; }
DWORD g1_mirror2x_menu_copy_hash_changes(void) { return g_menu_copy_hash_changes; }
DWORD g1_mirror2x_partial_copy_calls(void) { return g_partial_copy_calls; }
DWORD g1_mirror2x_partial_copy_pixels(void) { return g_partial_copy_pixels; }
DWORD g1_mirror2x_frame_copy_calls(void) { return g_frame_copy_calls; }
DWORD g1_mirror2x_frame_copy_pixels(void) { return g_frame_copy_pixels; }
DWORD g1_mirror2x_frame_copy_rejects(void) { return g_frame_copy_rejects; }
DWORD g1_mirror2x_pause_restore_total(void) { return g_pause_restore_total; }
DWORD g1_mirror2x_primary_readback_calls(void) { return g_primary_readback_calls; }
DWORD g1_mirror2x_primary_readback_converted(void) { return g_primary_readback_converted; }
DWORD g1_mirror2x_primary_readback_rejects(void) { return g_primary_readback_rejects; }
DWORD g1_mirror2x_primary_readback_dest_hash(void) { return g_primary_readback_dest_hash; }
DWORD g1_mirror2x_primary_readback_source_hash(void) { return g_primary_readback_source_hash; }
DWORD g1_mirror2x_primary_readback_return_address(void) { return g_primary_readback_return; }
DWORD g1_mirror2x_bar_copy_calls(void) { return g_bar_copy_calls; }
DWORD g1_mirror2x_bar_copy_mirrored(void) { return g_bar_copy_mirrored; }
DWORD g1_mirror2x_bar_copy_rejects(void) { return g_bar_copy_rejects; }
DWORD g1_mirror2x_bar_copy_pixels(void) { return g_bar_copy_pixels; }
DWORD g1_mirror2x_scratch_bltfast_calls(void) { return g_scratch_calls; }
DWORD g1_mirror2x_scratch_bltfast_recorded(void) { return g_scratch_recorded; }
DWORD g1_mirror2x_scratch_bltfast_rejects(void) { return g_scratch_rejects; }
DWORD g1_mirror2x_scratch_bltfast_flush_applied(void) { return g_scratch_flush_applied; }
DWORD g1_mirror2x_scratch_bltfast_flush_pixels(void) { return g_scratch_flush_pixels; }
DWORD g1_mirror2x_scratch_bltfast_adopts(void) { return g_scratch_adopts; }
DWORD g1_mirror2x_scratch_bltfast_adopt_skipped_record(void) { return g_scratch_adopt_skipped_record; }
DWORD g1_mirror2x_scratch_bltfast_overflow(void) { return g_scratch_queue.overflow; }
DWORD g1_mirror2x_scratch_bltfast_other_site_calls(void)
{
    return g_scratch_site_calls[G1_SCRATCH_BLTFAST_SITE_COUNT];
}
DWORD g1_mirror2x_scratch_bltfast_site_calls(DWORD index)
{
    return index < G1_SCRATCH_BLTFAST_SITE_COUNT ? g_scratch_site_calls[index] : 0u;
}
DWORD g1_mirror2x_briefing_compose_calls(void) { return g_briefing_compose_calls; }
DWORD g1_mirror2x_briefing_compose_mirrored(void) { return g_briefing_compose_mirrored; }
DWORD g1_mirror2x_briefing_compose_pixels(void) { return g_briefing_compose_changed_pixels; }
DWORD g1_mirror2x_briefing_compose_rejects(void) { return g_briefing_compose_rejects; }
DWORD g1_mirror2x_briefing_compose_reject_gate(void) { return g_briefing_compose_reject_gate; }
DWORD g1_mirror2x_briefing_compose_reject_lock(void) { return g_briefing_compose_reject_lock; }
DWORD g1_mirror2x_briefing_compose_reject_surface(void) { return g_briefing_compose_reject_surface; }
DWORD g1_mirror2x_briefing_compose_last_dest(void) { return g_briefing_compose_last_dest; }
DWORD g1_mirror2x_briefing_compose_last_geometry(DWORD index)
{
    return index < 4u ? g_briefing_compose_last_geometry[index] : 0u;
}
BOOL g1_mirror2x_s3_pattern_applied(void) { return g_s3_pattern_applied; }
DWORD g1_mirror2x_s3_pattern_pixel_count(void) { return g_s3_pattern_pixels; }
BOOL g1_mirror2x_primitives_installed(void)
{
    return g_hook_a.installed && g_hook_b.installed &&
           g_hook_terrain_rle.installed && g_hook_terrain_shade.installed &&
           g_hook_terrain_checker.installed && g_hook_terrain_clip.installed &&
           g_hook_terrain_clip_shade.installed && g_hook_cache_copy.installed &&
           g_hook_panel_rle.installed && g_hook_tinted_rle.installed &&
           g_hook_tinted_clip_rle.installed && g_hook_rect_fill.installed &&
           g_hook_cache_fill.installed &&
           g_hook_rect_border.installed && g_hook_rect_border7.installed &&
           g_hook_line.installed &&
           g_hook_rect_solid.installed &&
           g_hook_flip_rle.installed &&
           g_hook_keyed_copy.installed &&
           g_hook_flip_clip.installed &&
           g_hook_shade_rle.installed &&
           g_hook_shade_flip.installed &&
           g_hook_shade_clip.installed &&
           g_hook_blend_rle.installed && g_hook_blend_wrle.installed &&
           g_hook_blend_clip.installed && g_hook_blend_skip.installed &&
           g_hook_blend_clip7.installed &&
           g_hook_flip_blend.installed && g_hook_blend_flip7.installed &&
           g_hook_flip_blend7.installed &&
           (!layer_drift_on() ||
            (g_hook_blend_6d0.installed)) &&
           g_hook_blend_410.installed &&
           g_hook_cache_moves[0].installed && g_hook_cache_moves[1].installed &&
           g_hook_cache_moves[2].installed && g_hook_cache_moves[3].installed &&
           g_hook_cache_moves[4].installed && g_hook_cache_moves[5].installed &&
           g_hook_cache_moves[6].installed && g_hook_cache_moves[7].installed &&
           g_hook_primary_readback.installed && g_hook_bar_copy.installed &&
           g_hook_briefing_compose.installed;
}
