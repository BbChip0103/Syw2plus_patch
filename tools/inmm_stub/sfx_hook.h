#ifndef SFX_HOOK_H
#define SFX_HOOK_H

#include <windows.h>

/* Inline trampoline hook for the original SFX dispatch/selection function
 * FUN_00445930 @ 0x00445930 (syw2plus_original.exe, image base 0x00400000).
 *
 * Signature (confirmed by disassembly + FUN_00445110 table loader):
 *   int __stdcall FUN_00445930(short unit_type, short event_type,
 *                              char *out_path, char *out2);
 * Given (unit_type, event_type) it scans the DAT_00c19358 SFX table
 * (populated from EffectSound.dat / gamejvi YAV paths), randomly selects a
 * matching variant using DAT_009b5210 (tick/PRNG), and writes the selected
 * YAV path into out_path. Returns 1 on hit, 0 on no match.
 *
 * The hook runs the original first (so out_path is filled), then logs the
 * captured SFX *event* — (unit_type, event_type, selected YAV path,
 * PROGRAM_STATE, GLOBAL_TICK) — to C:\inmm_sfx_log.jsonl.
 *
 * Call sfx_hook_install() once from DllMain DLL_PROCESS_ATTACH (the EXE image
 * is already mapped at that point, as _inmm.dll is a static import).
 * Returns 1 if the hook was installed, 0 on failure.
 */
int sfx_hook_install(void);

/* Probe the engine's own SFX resolver (FUN_00445930) once, using the REAL
 * unit_type of each live in-game unit, for the die/recover/train event types.
 * The resolver is read-only on game state (it scans the SFX table + PRNG and
 * writes only to caller buffers), so this is crash-safe. Because the resolver
 * entry is hooked, each invocation is auto-logged to C:\inmm_sfx_log.jsonl.
 *
 * This captures the engine's AUTHENTIC unit_type -> YAV dispatch mapping. The
 * trigger is synthetic (a probe, not natural combat) — reports must label it
 * as such and must NOT claim a natural gameplay event.
 *
 * Returns the number of resolver invocations made. No-op (returns 0) until the
 * hook is installed and PROGRAM_STATE indicates in-game (PS==3).
 */
int sfx_probe_live_units(void);

#endif /* SFX_HOOK_H */
