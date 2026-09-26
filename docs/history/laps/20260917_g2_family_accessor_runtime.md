# G2 family-accessor runtime boundary

This is a separate, default-off build selected through the existing
`g2_relocation_diag_build` manifest argument.  It never reuses the approved
47-fixup DLL pin; it has its own Sol-reviewed DLL pin.  The existing
`g2_six_arena_failstop_v1` mode and its 8a2da2… pin are unchanged.

The family manifest uses the exact mode
`g2_six_arena_family_accessor_v1`, capacity 1201, union patch count 120, and
the same eight-word op6 request.  The fixed 4096-byte raw mapping retains the
49-DWORD base manifest (union patch count 120), 20-DWORD first-fault record at
offset 512, and 120 five-DWORD patch records at offset 640.  The family progress POD is exactly
608 bytes at offset 3328: 24 DWORD header plus 16 eight-DWORD identities.

Completion requires marker `0x524C5032`, version 1, status 2, at least 256
unique ticks and a 256-tick start/end delta within the 20-second deadline;
base/family/union patch counts are 47/73/120.  Each owner 0..7 must have one
HQ type 49 and one worker type 7 with unique slot/full ID, full-ID low16
matching slot, active=1, positive HP, and preserved category-list bits.
The result is the bounded `BOUNDED256TICK_NEW_ARENA_WITNESS`, not proof of
allocator memory safety, persistent gameplay, LAN behavior, or product pass.

The Sol-reviewed family DLL is pinned to
`71244523c24dcfe5986929a1ccb580e377f895e5de1355ccdd91614b3cfd541f`; it is a
separate gate from the approved 8a2da2… relocation build.  Before issuing op6,
the harness freezes the exact 16 scene identities (slot, full ID, owner, type)
and requires the completed progress identities to match that set exactly.

Malformed, partial, first-fault-only, identity-mismatch, timeout, or missing
progress records remain `BLOCKED_RELOCATION_DIAGNOSTIC_BOUNDARY`; no retries
or normal G1 tail readers run after the one-shot op6.
