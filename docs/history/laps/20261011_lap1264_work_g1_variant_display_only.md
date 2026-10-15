# 2026-10-11 | lap1264 | H-G1VARIANT2613 display-only probe

- 지정 역할: hands-on work. 당시 실행 argv 확인: Codex `gpt-6-luna`, reasoning effort high, fast mode off (`loop.sh --role=work --laps=1`).
- 목표/가설: lap1261 FEASIBLE handoff에 따라 G2+G6+G8 두 변형 EXE에서 G1 off/on 부팅, 새 게임 시작, save006 타이틀 로드가 가능한지 표시 전용으로 확인한다. 같은 variant SHA를 두 lane에 사용한다. 성공은 Wine 표시/로드 생존만 뜻한다.
- 실행 조건: stock unit/SFX/shadow/snapshot/supply/control 진단을 사용하지 않고 PS/tick/camera/screen만 관측한다. save006 상세 scene snapshot은 생략한다. 새 게임은 PS9→PS7→PS5→PS3까지 진행한다. 동일 save fixture SHA `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064`.
- 원본/후보 SHA: 보호 원본 EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; 공식2613 baseline identity `818721a5e8539f9ed97090a6d64cfdba429d46ec9caaa5671528005b22f5b724`; G2+G6+G8 `1e83466eab020818a6c0e9057508d71451af3ee1098af43ebefc20de8ab96e3d`; G2+G6+G8+G9 `b612109b8cd9e313927871a5a35f28cc09b9c95f80626c938f4d42192cb00556`. 입력 변형판은 읽기 전용이며 각 private game에만 복사.
- display DLL: `make -C tools/inmm_stub default-on`, 빌드 산출물 SHA256 `205b89b2c6ff3ae530ed3cbb705b644ea454404a0efee37de3980a85da36c28c`. `runtime_bridge` 주입 없음. 양 lane에서 unit ticks off/SFX probe off; shadow/snapshot/supply/control/pack env unset. 같은 sidecar 입력은 `../temp/Syw2plus_patch/20261011_lap1258_hdlayout/sibling_tree_v3/`.

## 구현 및 회귀

- `patches/population/runtime_driver.py`: display-only read는 program state `0x4ED818`와 tick `0x8924B8` 두 4-byte 읽기만 수행.
- `tools/g1_saved_scene_probe.py`: display-only 경로에서 startup/menu/new-game/load 관측에 위 reader 사용, G2가 재배치한 stock unit pool을 읽는 상세 scene snapshot을 건너뜀. PS3 load/화면·candidate present trace·close/cleanup은 유지.
- `tools/g1_variant_display_probe.py`: 정확한 variant 경로/SHA 고정, default-on DLL private install, 같은 EXE로 off/on 4개 lane, 원본 source validation 및 결과 요약.
- 테스트: `tests/test_runtime_driver_read.py`, `tests/test_g1_saved_scene_probe.py`, `tests/test_g1_mirror2x.py`. 수정 후 집중 검사 `248 passed`; `make lint`, `make typecheck` PASS.
- 현재 파일 SHA256: `tools/g1_variant_display_probe.py` `2b8fb39afc120bb36d924254010b05d6c2608acc16d738a4eb585dfa5e93f662`; `tools/g1_saved_scene_probe.py` `49830d63651f98477b6ca073bf72e02e9fccedb4f77de486b453f1bfb7bab50a`; `patches/population/runtime_driver.py` `212f2db7b35bcac647c55940b91fa3d439fa7961ddabde19ce63ae17117a0ced`; tests (순서 위와 같음) `4d596286fe08bb3a20941466adc26a4084f03570dc3bd14e5ca596c2e79c55aa`, `1b3b75f3338733d76749b6f556ab8bbd12015f92b7c82d2959dc60d536b7fdaa`, `13407117aebca14c81b561c81d9587db4590110afbfcba10cb31a6d031879870`.
- 첫 `make check`: 773.74s, `2194 passed, 9 skipped, 1 failed`. 새 display-only 양 lane에서 unit tick opt-out 문자열을 추가한 변화와 기존 단일 문자열 개수 assertion이 충돌했다. 회귀를 display-only 조건과 기존 candidate-only 조건을 각각 확인하도록 고친 뒤 같은 전체 게이트 재실행.
- 최종 `make check`: exit0, `2195 passed, 9 skipped` in 773.76s; Ruff/compileall/mypy 12 files/context 모두 PASS. 로그 `logs/gates/lap1264-work-make-check-rerun.log`.

## 실제 격리 실행

명령은 각 variant별로 아래 형식, `PYTHONPATH=.`로 실행했다:
`python3 tools/g1_variant_display_probe.py --variant <g2_g6_g8|g2_g6_g8_g9> --variant-exe <pinned input> --default-on-dll tools/inmm_stub/_G1MM.dll --hd-sidecar ../temp/Syw2plus_patch/20261011_lap1258_hdlayout/sibling_tree_v3 --runtime-root local/runtime/lap1264_<variant> --artifact-root ../temp/Syw2plus_patch/20261011_lap1264_variant_display/<variant>`.

공통: 네 lane 모두 status PASS, private EXE SHA가 지정 variant와 일치, PS3 title load와 owned trace close/flush PASS, drop0, source unchanged, 자기 game copy removed 및 prefix process count0. Manifest/prefix/output/raw/captures 보존. 실제 fixture player count/units, G2/G9 gameplay parity는 읽거나 주장하지 않음.

| Variant | G1 | 새 게임 | save006 title load | candidate trace / HD sidecar |
| --- | --- | --- | --- | --- |
| G2+G6+G8 | off/on PASS, PS3 | PASS, PS3 | PASS, PS3 tick24571 | 1,149 presents, hit340, reject0, fallback0, drop0 |
| G2+G6+G8+G9 | off/on PASS, PS3 | PASS, PS3 | PASS, PS3 tick24571 | 1,180 presents, hit337, reject1, fallback0, drop0 |

- G2+G6+G8 save006 candidate: 263 presents, hit279/reject0/fallback0/drop0. G9 save006 candidate: 266 presents, hit255/reject0/fallback0/drop0. 각 Scale2x trace validator PASS.
- G9 새 게임의 reject1 key: writer `0x00466EA0`, digest `44c611f6`, 96×112, written5257/opaque5261, opaque_unwritten4, `(51,104)`~`(53,105)`. 이는 lap1259~1263에 보존된 `tree_plus.spr.hd/0000.idx8` 런타임 mask reject와 writer/digest/크기가 일치한다. 이 frame은 fail-closed로 Scale2x fallback되며 reject를 숨기지 않는다. 원인은 기존 UNKNOWN/backlog 그대로; asset 투명화/guard 변경 없음.
- 결과/raw/capture 경로: `../temp/Syw2plus_patch/20261011_lap1264_variant_display/{g2_g6_g8,g2_g6_g8_g9}/`. 상위 result SHA256: G2+G6+G8 `f30cba9309e9be93bc5ec6065eec95aa6e47fc5da9906015ce2c5b5b1ca24443`; G9 `21f9a1a6be88dbd190b6b4ffecad6a0d315b4ba5c17a5734a731895c0a229201`. PNG 24개는 `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/captures/`에 `20261011_023039_lap1264_<variant>_<lane>_<screen>.png`로 복사했다. 원래 lane artifact도 보존했고 `captures_manifest.json`에 대응 경로/바이트/SHA를 고정했다.
- 최종 안전: `python3 checks/safety.py check --require-game` SAFETY_PASS; `python3 checks/context_limits.py` CONTEXT_PASS; `git diff --check` exit0. 커밋/전달/원본 수정0.

## 판정 및 다음 한 가지

- H-G1VARIANT2613 display-only Wine probe: scoped PASS. 두 후보의 G1 display path와 save006 title load가 이 격리 환경에서 생존함을 보였다. G2 unit state/pool, eight-player stress, G9 seat order behavior, multiplayer, Windows native execution, DxWnd, 24k/144k, G1 milestone/user acceptance는 미검증이다.
- G9 Windows 실행은 별도 사용자 보고 FAIL 상태로 유지한다. 이 Wine 결과를 Windows 합격이나 배포 승인으로 바꾸지 않는다. G1 milestone 미승인.
- 다음 한 가지: fresh middle이 두 variant의 private EXE SHA, four-lane raw/close/cleanup, HD hit/reject/key log와 이 handoff의 관측 경계를 독립 확인한다. 알려진 tree_plus reject는 기존 backlog로 유지하고 재수리/re-run하지 않는다.
