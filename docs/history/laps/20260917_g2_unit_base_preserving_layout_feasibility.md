# G2 Unit-base-preserving tail-layout — bounded feasibility

## Scope / stop
2026-09-17 21:05–21:25 KST, **read-only**; Astra/medium approved only a finite structural/workload assessment. Keep Unit base `66B790` and stride `758`; insert extra body space at old Unit end/Bulk start `892410`, relocate the following BSS and resource section. This is distinct from and does not reopen STOP getter, typed-Unit inference generator, or TYPE7 fixture. No implementation or game execution is authorized by this card. Full G2 remains active/incomplete.

## Evidence
Pinned original SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`.
- `.data` initialized raw ends `4F9000`; virtual end `108BA38`. Entire Unit/tail suffix is zero-initialized BSS.
- Exact extra slots must be a multiple of512 to preserve page alignment without breaking UnitEnd==BulkStart. Calculation-only capacity9904/extra8704/deltaF9B000/newUnitEnd182D410;303 shared slots is **not an adequacy proof** and capacity is not adopted.
- Root resource geometry:9 data entries/payloads inside old `.rsrc`; shifting resource section/directory/payload RVAs conserves the5C8 gap and fits32bit; computed new SizeOfImage1C2A000. No edits made, no pointer-completeness proof.
- Sol independent native-byte review: preserving body base/stride avoids the specific old moved-body reads40FC60/4178C1. It does not fix the shifted existence guards or other globals.
- Allocator442FAC starts age[1],442FB1 uses existence-age displacement−960,442FD1 stops at old1200. Growing existence alone overlaps age: each provisional9904 WORD vector needs19808B rather than2400B.
- Save40F4B0/load40F4F0 independently traverse existence0..1199;440C20/440FF0 separately transfer bulkE397C; postload441441 has CMPBX4B0. Unit insertion size must not be blindly added to bulk serialization length.
- Native43B5AF AND ECX,00FFFFFF and439887 AND EAX,00FFFFFF are scalar masks **inside the old moving VA range**. Blind numerical rebasing would corrupt them.
- Missed oldtail VA8990C8 now aliases new Unit slot1214+5E8: silent corruption is possible rather than an access violation.

## Inference / unresolved
This trades Unit-address reference migration for global-tail reference migration; it is not a capacity-only patch. Capacity-aware sidecar ABI, bulk-relative offsets, reset/lifecycle, dense sector225, owner/headroom, versioned save/load and supportedLAN remain unclosed. Luna's bounded actual-instruction/reference workload assessment is pending. A heuristic census is not a verified relocation list; no new address inference engine is permitted. No schedule/success probability or automatic patcher GO is inferred.

## Artifacts
External `temp/Syw2plus_patch/g2_capacity/20260917_unit_base_preserving_layout_feasibility_v1/`: structural_facts.json, root_pe_resource_geometry_v1.json, root_selected_native_raw_v1.json, root_numerical_false_candidates_v1.json, middle_assessment_v1.json. Root numerical initial sample assertion failed because it expected an explicit full-width TEST immediate; this was a diagnostic expectation error, not game execution or a patch. Corrected known-entry AND-mask evidence is preserved with that disclosure.

Root source/protected hash recheck: existing offline builder/test,7-byte cap builder/test, canonical shared DLL/controlC/bridge and original match the frozen pins. Last Fast621 remains valid for unchanged project code, not proof of this layout or 8-player play. User report21:06KST; next21:16.

## Final bounded disposition — 21:16KST
Root independently reproduced the scope-corrected whole-tail heuristic counts9213 absolute-MEM/2312 indexed-MEM/6059 IMM, total17584, excluding preserved Unitbody. These are linear Capstone skipdata candidate counts, **not actual whole-program instruction boundaries or approved fixups**. The author originally reused six old regions; that04ff v1 is rejected as scope mismatch and kept unchanged. Corrected5fa7 v2 is external under `20260917_tail_reference_workload_v2/`. Its policy phrase “No fulltextlinear scan” is incorrect; Root recount/erratum and Sol disposition explicitly correct it without modifying the original artifact.

Sol final dispositione20b: **layout plausible, integration/automatic broad patcher/runtime NO-GO at present**. Keeping Unitbase avoids known body-reference failures but retains1200-entry sidecar/allocator/save/postload limits. A new nonuniform capacity-aware sidecar/bulk/lifecycle/persistence ABI remains missing. No evidenced quick safe implementation route; not proof of global impossibility or32-bit OOM. Read-only card finished before21:25 deadline; no third inventory repair/address-inference engine/PE/runtime.

Middle original assessment2287 was not prearchived before a mask-proof addition; reviewer reconstructed exact old bytes afterward, Root independently matched its SHA against prior receipt.6ee3 revised bytes are separately frozen. Old receiptv1 is historical, not current exactsource assertion. External provenance receipt discloses reconstruction.

User new cutoff: “한국시간 기준12시까지만 루프 … 진행속도나 가능성 생각해서”. At21:16 Root conservatively interprets today-night12 as2026-09-18 00:00KST, not next-noon, pending user correction. Previous STOP attempt budgets remain spent. Next finite middle assessment examines whether the **already successful original8-owner assisted high-cost fixture** can safely support an actual long-lifecycle/performance24k baseline using bounded Python observation only. This is not an expanded-pool product or reduced G2. No run/card promise unless existing execution/cleanup contract is established.
