# G1 finalD3D9 trace — pre-run review (2026-09-16)

## First candidate: REJECT / no game run

Luna/high implementation: opt-in/defaultOFF, pixelsOFF, pinned DxWrapper export stubs,
real factory/device COM clones and trace. Build passed, static8 tests passed, Ruff passed.
Bridge SHA `826b0b6b9b1120985cd1243ddaff831fff1c4c5762a99b546727db9d02d7ac1a`.
Rejected bridge preserved externally `temp/Syw2plus_patch/g1_hud_detail/20260916_d3d9_trace_prerun_reject/`.

Root Sol/high found pre-run blockers:

- Intercepted caller GetBackBuffer reference was Released before returning to caller. Only an extra observer-owned acquisition may be balanced by observer Release.
- Original Release returning0 may destroy object; subsequent vtable restoration writes freed memory.
- Timestamp/RVA checks do not verify logged SHA/version constants. Manifest/file pin must be genuinely validated or narrowly disclosed.
- Present/Reset failure did not gate ordinary read-only device queries; lost state/HRESULT must remain explicit.
- Ex clone did not intercept typed PresentEx/ResetEx. Reject unsupported shape before cloning.
- Inactive/stale pointer lookup can collide with reused objects; clone/lifetime cleanup must not dereference destroyed objects.

No fresh game was run with this candidate. Static tests/build are not behavioral COM ownership proof.
Luna scoped repair assigned: prefer deleting intercepted GetBackBuffer hook, separate own observer query,
no object access after final Release, bounded process-lifetime clone/tombstone handling, actual file pin,
unsupportedEx SKIP and successful-device/HRESULT gates. Independent Sol review runs alongside repair.
G1 phase budget starts17:11,60–90min/two failed hypotheses. No renderer rewrite/framework expansion.

## First repair — still NO-GAME

Bridge7fcaf292e4fed816b5b138cb8ec3ad76763dbaa02d5ae97d9f041f6f025078b0, freshstatic8PASS. Caller-owned GetBackBuffer hook deleted, observer extra acquisition balanced; finalRelease0 object writes removed; inactive slots tombstoned/notreused, clone/tramp storage retained; ExSKIP; caller captured at hook. ExternalmanifestSHA requirement is disclosed instead of claiming runtimehashverified.

Still NO-GAME: processdetach retained object-vtable writes, failedReset had no persistent unusable-device gate. Narrow second repair assigned, plus regression locks for detach/Release0/Resetfail/publish/rollback. IndependentSol also identified trampoline publication/rollback forwarding hazards; publish-before-livepatch and retainedstorage repairs are inspected, not actual multithread proof. Original source/on-diskgame unchanged; no candidate pixelwrites.

## Final bounded repair / Sol single-run CONFIRM

C990fed50aec53e23f9bd5333b3b54f47d73096be580f375402a9c2ba2a98bf9c; stubfedffae652829e9168d07fe945261dd2232597ad8642ceaa64d319aedb5d31a0; DLLdd36540dcae4256c4e2b096d901e68eaa0bf59a1cceea4f866ad77955bd00f0d. Rootfresh12tests/RuffPASS,buildPASS. Finaldetach noCOMobjectwrites; Resetfailedusablefalse/successrestore; factorycallbackscomplete-beforepublish,atomicallyreservedprocesslifetimeslots; trampolinepublishedbeforelivepatch/retainedonrollback; actualcaller/modulepath/base logs andexternalSHA requirement.

IndependentSol CONFIRM **single first private pixel-OFF startup/process-lifetime observation only**. Genericconcurrenthotpatch/unload/SPRhook/pixelwritesnotapproved. Freshprepare/check and finalFast must pass beforegame. Planned existingg1-presentation-trace dxwrapper2x,1600x1200screen,90sec cap,PS3dwell3; original800composition profile installed/uninstalled. Actualfactory→device→successfulPresent +same device/generation GetDesc1600x1200,actualmodulepath/base/manifestpinbinding required; noevent/mismatch/Exunsupported meansSTOP,notDDrawtrace/dummyfallback. Atthisrecord actualgamePENDING.
