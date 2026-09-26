#ifndef ASSET_HOOK_H
#define ASSET_HOOK_H

#include <windows.h>

/* IAT hook for kernel32!CreateFileA / CreateFileW.
 * Logs file paths + current PROGRAM_STATE to C:\inmm_asset_log.jsonl.
 *
 * Call asset_hook_install() once from DllMain DLL_PROCESS_ATTACH.
 * Returns count of slots successfully patched (CreateFileA + CreateFileW = 2 max).
 */
int asset_hook_install(void);

#endif /* ASSET_HOOK_H */
