# Original PE32 QHD feasibility probe (2026-09-10)

> **2026-09-10 사용자 정정:** 이 파일은 시야 확장 참고 실험이다. 원본 UI/스프라이트
> 상대 크기와 구도를 유지하는 실제 요구는 미충족. `PRODUCT_GOAL.md`가 현재 목표다.


**Research prototype, not a release-ready resolution patch.** Original 32-bit code and assets rendered a true 2560×1440 viewport under isolated Wine. Original HQ at screen x=1280 was selected through X11 mouse input; keyboard camera movement and mouse x=2400 also worked. This is not 800×600 image scaling or Plan C execution.

## Reversible file patch

Requires existing `pefile` and `capstone` Python modules. Original SHA256 is pinned. Output must be a NEW path distinct from input; `.original-backup` and `.patch.json` sidecars are written. Binary outputs must not be committed.

```sh
python patches/resolution/qhd_probe.py apply Syw2plus/syw2plus_original.exe /path/to/private/game/qhd_probe.exe
python patches/resolution/qhd_probe.py restore /path/to/private/game/qhd_probe.exe
pytest -q patches/resolution/test_qhd_probe.py
ruff check patches/resolution/*.py
```

The tested final candidate has SHA256
`c4b912d96e623de91b7cc25de35c57395d8de1e01801e948f45b5b456b80f993`.
It preserves PE32/x86, adds a private data section, changes 74 guarded code ranges, and changes section metadata. No new runtime dependency is introduced by the patch itself. The experiment's pre-existing DirectDraw/Wine/audio instrumentation dependencies remain.

## Runtime experiment

`run_qhd_probe.py` is deliberately configured for a private copied game root `/home/dev_00/syw2plus-qhd-probe-0910`, private prefix `/home/dev_00/.wine_syw2_qhd_probe_0910_r2`, and free Xvfb `:193`. It refuses an occupied display and stops only its own processes/prefix. It is not a general launcher.

The game root was copied (not hardlinked) from `Syw2plus`; prefix copied from `~/.wine_syw2`. Private `dxwrapper.ini` has `LoadCustomDllPath` blank to avoid loading `syw2x.dll`. Private `_inmm.dll` is the existing instrumentation build from `plan_c/tools/inmm_stub/_inmm.dll` (SHA256 `19c18929f61b93a2c278ba16f28a5af48f4743469d05b3506c24b07228b108d5`). Existing short intro-movie fixtures were inherited from the game copy.

The existing `_inmm` control bridge navigated title→custom game→original PS3 (`enter_custom_game`, `_custom_game_chain_inject`). It did not render terrain, change fog visibility, inject selection, or implement game simulation. Mouse and Right-arrow actions were real X11 events. Binary and memory changes are explicitly logged; the two experimental deferred-display writes belong only to the earlier failed variant.

Final run:

```sh
QHD_PROBE_RUN=qhd_clear_input \
QHD_PROBE_EXE=qhd_clear.exe \
QHD_PROBE_MANIFEST=qhd_clear.exe.patch.json \
python patches/resolution/run_qhd_probe.py
```

Evidence root: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/20260910_qhd_probe/`.

## Findings and limits

- Original renderer width/height/pitch = 2560/1440/2560, indexed 8-bit; clip = (0,0,2559,1439).
- Final presented screen: `qhd_clear_input/20260910_043003_after8.png`.
- HQ click: `20260910_043005_hq_click_wide.png`, corresponding JSON shows mouse (1280,730), selected count 0→1, slot1199.
- Right-arrow camera: (7,6)→(81,0); continued original PS3 to tick1238 (~37 seconds).
- Final raw terrain snapshot has nonzero pixels spanning x925..1975 (1051 pixels, exceeding original832). This is an asynchronous buffer read, NOT a frame-fenced full-frame coverage measurement.
- Full-redraw stale-cache artifact was reproduced, then fixed; at the same distant unexplored camera the stale strip disappears (raw nonzero116565→0; before/after screenshots retained).
- **Unfinished:** HUD anchors/hitboxes do not all match the new layout. No claim of a finished playable UI, all-effects parity, long-session stability, large-army performance, native Windows-driver coverage, or LAN/save compatibility in this lane.
- All original binary/assets remain unchanged. No production Plan C source was modified.

See `analysis/memory_maps/original_qhd_probe_0910.md` for address evidence, failure root cause and safety boundaries.

**이관 안전 보강:** 과거 `run_qhd_probe.py`의 직접 실행 진입점은 비활성화했다.
고정된 옛 Wine prefix의 로그 삭제/종료를 실수로 실행하지 않도록 기본 거부한다.
