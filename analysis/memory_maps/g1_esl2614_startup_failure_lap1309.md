# ESL2614 G1 startup failure boundary — lap1309 middle

- Input: `[ESL]Syw2plus 2614.exe`, SHA256 `ac61a28f84f71d602c581a17c835ec4dbb99aad0341c6755e395549005cf88bf`; WINMM `f32ee6190716e705a0376213adbe8fc0722d9a3abdaed07f248bdd4766912655`. Offline `objdump -d -Mintel`, no target execution or writes.
- Reproducible calculation/disassembly: `../temp/Syw2plus_patch/20261014_lap1309_middle_g1boot_review/review.py`, `review.json`, four `.asm` files. Review JSON SHA256 `7690407d3b9d76b320c3514c99e8918435c1471ec333ece9356e69799a20b680`.

| Address | Exact bytes / observation | Interpretation and limit |
|---|---|---|
| `004644A0` | `8B 44 24 04 81 EC 90 02 00 00` | Mode setup entry, with mode selector argument and `0x290` stack allocation. |
| `0046457A` | `FF 51 54` | Calls DirectDraw vtable `+0x54` after pushing self/width/height/bpp/refresh/flags. |
| `0046457D` | `85 C0 0F 85 15 03 00 00` | Tests returned HRESULT; any nonzero return branches to `0046489A`. This is the recorded caller/return address of both mode requests. |
| `0046489A` | `5F 5E 5D 33 C0 5B 81 C4 90 02 00 00 C2 10 00` | Failure exit restores registers and returns FALSE with `ret 0x10`; it does not itself branch to the observed fault target. |
| `00464C64` | `E8 37 F8 FF FF` | Recreate-mode path calls `004644A0` after releasing old surfaces. Caller above this path at the exception remains unobserved. |
| `0046529D` | `FF 15 CC 51 4E 00` | Error-dialog routine calls EXE IAT `004E51CC`; DllMain separately patches user32 `MessageBoxA`. Not proof the failing run reaches this instruction. |
| `01FC01AD` | root `c0000005`; lap1308 noVD `c000001d`; combined `c0000096` | Runtime address with no retained instruction bytes, allocation/module map, or fault stack. It is outside the official EXE image. Matching address is insufficient for common-cause attribution. |

## Runtime facts and bounded inference

- lap1308 noVD and combined trace line5: `800x600x8` forwarded to `1600x1200x8`, HRESULT0. Subsequent primary `CreateSurface` also returns0 and descriptor reports1600x1200.
- Both trace line52: `640x480x32` forwarded unchanged, HRESULT `-2147467263` (`0x80004001`, E_NOTIMPL). G1 skips its exact 800x600x8 gate here. Both runs subsequently fail to reach PS9 and remain at runner-observed PS60/debugger wait. Trace event itself still records PS40; these are different observations.
- The virtual-desktop lane successfully handles the same alternating 640/800 requests and reaches PS3. Initial1600 failure is therefore not established by these runs; no-desktop is not an initial1600-failure fixture.
- `tools/inmm_stub/inmm_stub.c:556` writes an unconditional five-byte `JMP rel32` into user32 `MessageBoxA`. Fault-time patch bytes/target and return stack are absent; this is a diagnostic hypothesis, not a reproduced cause or approved patch.
- Root `I_hd2_loaddll.hqcdd.log` is byte-identical to input `hqcdd.log`, SHA256 `629f5626e4e1b3d0751754bd3944acacbb218c0c8245b557c1f566554cd8e441`. Its PID24272/ASI/mode messages are inherited input, not proof of root-run loading or modes. Root Wine `+loaddll` and lap1308 ASI-disabled debug message are separate evidence; exact two-ASI ranges/SHA remain uncollected for lap1308.
- Confidence: high for requests/HRESULTs, exception transcription, inherited-log identity, and static FALSE return; low/UNKNOWN for shared root cause, MessageBox/vtable corruption, or Windows equivalence. Work handoff is in lap1309 history; current queue remains only STATUS.
