#ifndef SURFACE_REUSE_CONTRACT_H
#define SURFACE_REUSE_CONTRACT_H

/*
 * Shared, side-effect-free decision contract for DirectDraw surface reuse.
 *
 * The production trace and the native regression harness both call this
 * function.  Keep the contract independent of Win32 headers so the harness
 * can execute it on the host without loading the game or a DLL.
 */
typedef void (*G1SurfaceMethodPointer)(void);

enum {
    G1_SURFACE_REUSE_OK = 0,
    G1_SURFACE_REUSE_STALE_UNINSTALLED = 1,
    G1_SURFACE_REUSE_NOT_INSTALLED = 2,
    G1_SURFACE_REUSE_RECORD_OBJECT_MISSING = 3,
    G1_SURFACE_REUSE_RECORD_OBJECT_MISMATCH = 4,
    G1_SURFACE_REUSE_OBJECT_MISSING = 5,
    G1_SURFACE_REUSE_OBJECT_VTABLE_MISSING = 6,
    G1_SURFACE_REUSE_ORIGINAL_VTABLE_MISSING = 7,
    G1_SURFACE_REUSE_CLONE_VTABLE_MISSING = 8,
    G1_SURFACE_REUSE_CLONE_VTABLE_MISMATCH = 9,
    G1_SURFACE_REUSE_GET_DESC_WRAPPER_MISMATCH = 10,
    G1_SURFACE_REUSE_BLT_WRAPPER_MISMATCH = 11,
    G1_SURFACE_REUSE_BLT_FAST_WRAPPER_MISMATCH = 12,
    G1_SURFACE_REUSE_FLIP_WRAPPER_MISMATCH = 13,
    G1_SURFACE_REUSE_GET_DESC_ORIGINAL_MISSING = 14,
    G1_SURFACE_REUSE_BLT_ORIGINAL_MISSING = 15,
    G1_SURFACE_REUSE_BLT_FAST_ORIGINAL_MISSING = 16,
    G1_SURFACE_REUSE_FLIP_ORIGINAL_MISSING = 17,
    G1_SURFACE_REUSE_RELEASE_WRAPPER_MISSING = 18,
    G1_SURFACE_REUSE_RELEASE_HOOK_MISSING = 19,
    G1_SURFACE_REUSE_RELEASE_WRAPPER_MISMATCH = 20,
    G1_SURFACE_REUSE_RELEASE_ORIGINAL_MISSING = 21,
    G1_SURFACE_REUSE_RELEASE_KEEP = 22,
    G1_SURFACE_REUSE_RELEASE_RETIRE = 23
};

typedef struct {
    int reusable;
    unsigned method_count;
    unsigned reason;
} G1SurfaceReuseDecision;

typedef struct {
    int installed;
    const void *record_object;
    const void *object;
    const void *object_vtable;
    const void *original_vtable;
    const void *clone_vtable;
    G1SurfaceMethodPointer clone_get_surface_desc;
    G1SurfaceMethodPointer clone_blt;
    G1SurfaceMethodPointer clone_blt_fast;
    G1SurfaceMethodPointer clone_flip;
    G1SurfaceMethodPointer clone_release;
    G1SurfaceMethodPointer hook_get_surface_desc;
    G1SurfaceMethodPointer hook_blt;
    G1SurfaceMethodPointer hook_blt_fast;
    G1SurfaceMethodPointer hook_flip;
    G1SurfaceMethodPointer hook_release;
    G1SurfaceMethodPointer original_get_surface_desc;
    G1SurfaceMethodPointer original_blt;
    G1SurfaceMethodPointer original_blt_fast;
    G1SurfaceMethodPointer original_flip;
    G1SurfaceMethodPointer original_release;
} G1SurfaceReuseInput;

typedef struct {
    G1SurfaceMethodPointer clone_release;
    G1SurfaceMethodPointer hook_release;
    G1SurfaceMethodPointer original_release;
    unsigned release_result;
} G1SurfaceReleaseInput;

typedef struct {
    int retire;
    unsigned reason;
} G1SurfaceReleaseDecision;

static G1SurfaceReuseDecision g1_surface_reuse_decide(const G1SurfaceReuseInput *input)
{
    G1SurfaceReuseDecision decision;

    decision.reusable = 0;
    decision.method_count = 0;
    decision.reason = G1_SURFACE_REUSE_NOT_INSTALLED;
    if (!input) return decision;
    if (!input->installed && input->record_object) {
        decision.reason = G1_SURFACE_REUSE_STALE_UNINSTALLED;
        return decision;
    }
    if (!input->installed) return decision;
    if (!input->object) {
        decision.reason = G1_SURFACE_REUSE_OBJECT_MISSING;
        return decision;
    }
    if (!input->record_object) {
        decision.reason = G1_SURFACE_REUSE_RECORD_OBJECT_MISSING;
        return decision;
    }
    if (input->record_object != input->object) {
        decision.reason = G1_SURFACE_REUSE_RECORD_OBJECT_MISMATCH;
        return decision;
    }
    if (!input->object_vtable) {
        decision.reason = G1_SURFACE_REUSE_OBJECT_VTABLE_MISSING;
        return decision;
    }
    if (!input->original_vtable) {
        decision.reason = G1_SURFACE_REUSE_ORIGINAL_VTABLE_MISSING;
        return decision;
    }
    if (!input->clone_vtable) {
        decision.reason = G1_SURFACE_REUSE_CLONE_VTABLE_MISSING;
        return decision;
    }
    if (input->object_vtable != input->clone_vtable) {
        decision.reason = G1_SURFACE_REUSE_CLONE_VTABLE_MISMATCH;
        return decision;
    }
    if (input->clone_get_surface_desc != input->hook_get_surface_desc) {
        decision.reason = G1_SURFACE_REUSE_GET_DESC_WRAPPER_MISMATCH;
        return decision;
    }
    if (input->clone_blt != input->hook_blt) {
        decision.reason = G1_SURFACE_REUSE_BLT_WRAPPER_MISMATCH;
        return decision;
    }
    if (input->clone_blt_fast != input->hook_blt_fast) {
        decision.reason = G1_SURFACE_REUSE_BLT_FAST_WRAPPER_MISMATCH;
        return decision;
    }
    if (input->clone_flip != input->hook_flip) {
        decision.reason = G1_SURFACE_REUSE_FLIP_WRAPPER_MISMATCH;
        return decision;
    }
    if (!input->original_get_surface_desc) {
        decision.reason = G1_SURFACE_REUSE_GET_DESC_ORIGINAL_MISSING;
        return decision;
    }
    if (!input->original_blt) {
        decision.reason = G1_SURFACE_REUSE_BLT_ORIGINAL_MISSING;
        return decision;
    }
    if (!input->original_blt_fast) {
        decision.reason = G1_SURFACE_REUSE_BLT_FAST_ORIGINAL_MISSING;
        return decision;
    }
    if (!input->original_flip) {
        decision.reason = G1_SURFACE_REUSE_FLIP_ORIGINAL_MISSING;
        return decision;
    }
    if (!input->clone_release) {
        decision.reason = G1_SURFACE_REUSE_RELEASE_WRAPPER_MISSING;
        return decision;
    }
    if (!input->hook_release) {
        decision.reason = G1_SURFACE_REUSE_RELEASE_HOOK_MISSING;
        return decision;
    }
    if (input->clone_release != input->hook_release) {
        decision.reason = G1_SURFACE_REUSE_RELEASE_WRAPPER_MISMATCH;
        return decision;
    }
    if (!input->original_release) {
        decision.reason = G1_SURFACE_REUSE_RELEASE_ORIGINAL_MISSING;
        return decision;
    }
    decision.reusable = 1;
    decision.method_count = 49u;
    decision.reason = G1_SURFACE_REUSE_OK;
    return decision;
}

static G1SurfaceReleaseDecision g1_surface_release_decide(
    const G1SurfaceReleaseInput *input)
{
    G1SurfaceReleaseDecision decision;

    decision.retire = 0;
    decision.reason = G1_SURFACE_REUSE_RELEASE_WRAPPER_MISSING;
    if (!input || !input->clone_release) return decision;
    if (!input->hook_release) {
        decision.reason = G1_SURFACE_REUSE_RELEASE_HOOK_MISSING;
        return decision;
    }
    if (input->clone_release != input->hook_release) {
        decision.reason = G1_SURFACE_REUSE_RELEASE_WRAPPER_MISMATCH;
        return decision;
    }
    if (!input->original_release) {
        decision.reason = G1_SURFACE_REUSE_RELEASE_ORIGINAL_MISSING;
        return decision;
    }
    if (input->release_result == 0u) {
        decision.retire = 1;
        decision.reason = G1_SURFACE_REUSE_RELEASE_RETIRE;
    } else {
        decision.reason = G1_SURFACE_REUSE_RELEASE_KEEP;
    }
    return decision;
}

static const char *g1_surface_reuse_reason_name(unsigned reason)
{
    switch (reason) {
    case G1_SURFACE_REUSE_OK: return "ok";
    case G1_SURFACE_REUSE_STALE_UNINSTALLED: return "stale_uninstalled";
    case G1_SURFACE_REUSE_NOT_INSTALLED: return "not_installed";
    case G1_SURFACE_REUSE_RECORD_OBJECT_MISSING: return "record_object_missing";
    case G1_SURFACE_REUSE_RECORD_OBJECT_MISMATCH: return "record_object_mismatch";
    case G1_SURFACE_REUSE_OBJECT_MISSING: return "object_missing";
    case G1_SURFACE_REUSE_OBJECT_VTABLE_MISSING: return "object_vtable_missing";
    case G1_SURFACE_REUSE_ORIGINAL_VTABLE_MISSING: return "original_vtable_missing";
    case G1_SURFACE_REUSE_CLONE_VTABLE_MISSING: return "clone_vtable_missing";
    case G1_SURFACE_REUSE_CLONE_VTABLE_MISMATCH: return "clone_vtable_mismatch";
    case G1_SURFACE_REUSE_GET_DESC_WRAPPER_MISMATCH: return "get_desc_wrapper_mismatch";
    case G1_SURFACE_REUSE_BLT_WRAPPER_MISMATCH: return "blt_wrapper_mismatch";
    case G1_SURFACE_REUSE_BLT_FAST_WRAPPER_MISMATCH: return "blt_fast_wrapper_mismatch";
    case G1_SURFACE_REUSE_FLIP_WRAPPER_MISMATCH: return "flip_wrapper_mismatch";
    case G1_SURFACE_REUSE_GET_DESC_ORIGINAL_MISSING: return "get_desc_original_missing";
    case G1_SURFACE_REUSE_BLT_ORIGINAL_MISSING: return "blt_original_missing";
    case G1_SURFACE_REUSE_BLT_FAST_ORIGINAL_MISSING: return "blt_fast_original_missing";
    case G1_SURFACE_REUSE_FLIP_ORIGINAL_MISSING: return "flip_original_missing";
    case G1_SURFACE_REUSE_RELEASE_WRAPPER_MISSING: return "release_wrapper_missing";
    case G1_SURFACE_REUSE_RELEASE_HOOK_MISSING: return "release_hook_missing";
    case G1_SURFACE_REUSE_RELEASE_WRAPPER_MISMATCH: return "release_wrapper_mismatch";
    case G1_SURFACE_REUSE_RELEASE_ORIGINAL_MISSING: return "release_original_missing";
    case G1_SURFACE_REUSE_RELEASE_KEEP: return "release_keep";
    case G1_SURFACE_REUSE_RELEASE_RETIRE: return "release_retire";
    default: return "unknown";
    }
}

#endif /* SURFACE_REUSE_CONTRACT_H */
