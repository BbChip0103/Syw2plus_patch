# 2026-10-07 | lap1161 | G1 work — H-DEF1: `SYW2_G1_DEFAULT_ON` 저장소 반영 · `sfx_probe_live_units` opt-in화

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5` / work(실무). 커밋 0, 원본·참고·`260921_temp` 쓰기 0.
- 입력: lap1160 middle 사전등록 §4(`docs/history/laps/20261007_lap1160_middle_g1_hdx2_review_hdef1_preregistration.md`), INBOX 2026-10-07 19:3x "함께 처리". `loop/STOP`·`loop/ESCALATE_SOL`(들어온 것)·APPROVALS 새 반려·사용자 G1 시험 결과 없음.
- 가설: (1) `default_on.patch` 블록을 그대로 반영하면 lap1151 스냅샷에서 `_G1MM.dll` `05bf7010…`이 PE 가변 필드 외 동일하게 재현된다. (2) `SYW2_G1_DEFAULT_ON` 빌드에서만 `sfx_probe_live_units()` 호출 앞에 env opt-in(`INMM_STUB_SFX_PROBE`) 게이트를 두면 플래그 없는 빌드는 바뀌지 않고, 기본 켬 빌드는 엔진 표 로더·SFX resolver 호출과 옛 유닛 주소 읽기를 하지 않는다.
- 변경 파일(전부 uncommitted):
  - `tools/inmm_stub/inmm_stub.c` `2560b4af…`: ① DllMain `DLL_PROCESS_ATTACH` 첫머리 `#ifdef SYW2_G1_DEFAULT_ON` 블록(env 4개 `SYW2_G1_NATIVE_2X_BLIT=1`·`SYW2_G1_MIRROR2X=1`·`SYW2_G1_HD_SOURCE=scale2x`·`INMM_STUB_NO_UNIT_TICKS=1`, 비어 있을 때만 — `default_on.patch`와 텍스트 byte 동일). ② 워커 스레드 `if (ps_ok && ps == 3)` 안 `sfx_probe_live_units();` 앞에 `#ifdef SYW2_G1_DEFAULT_ON … if (sfx_probe_opted_in()) … #endif`. ③ 같은 플래그 안 `static BOOL sfx_probe_opted_in(void)`(`INMM_STUB_SFX_PROBE` 정의됨·값이 "0"만이 아님).
  - `tools/inmm_stub/Makefile` `81d3598c…`: `default-on` 대상(`_G1MM.dll`, `-DSYW2_G1_DEFAULT_ON`, 별도 implib `lib_g1mm.a`). 기본 `all`/`_inmm.dll` 규칙은 그대로.
  - `tests/test_g1_mirror2x.py`: 첫 전체 `make check`(1 failed·1889 passed·5 skipped/762.60s, 로그 `logs/gates/lap1161-work-full-check.log` 첫 실행)에서 기존 `test_ua2_stub_unit_tick_dump_has_env_opt_out_before_file_open`이 `stub.count('"INMM_STUB_NO_UNIT_TICKS"') == 1`로 실패 — 저장소 반영한 default-on 블록이 같은 문자열을 한 번 더 넣기 때문(제품 결함 아님, "env 읽기는 `dump_units_at_tick` 한 곳"이라는 불변식은 그대로). `#ifdef SYW2_G1_DEFAULT_ON … #endif` 구간을 제외하고 세도록 고침(`import re` 추가), 나머지 assertion 불변.
  - `tests/test_g1_default_on.py` `cb5a7719…`(신규, 6개): 블록 텍스트·env 이름/값/"비어 있을 때만" 조건·설치 전 위치·게이트 위치·플래그 없는 빌드 영향 없음(mingw 객체에 `INMM_STUB_SFX_PROBE`·`SYW2_G1_HD_SOURCE` 문자열 부재/존재 대조)·Makefile 대상.
- 원본 SHA: `[HQ]Syw2plus 2002.exe` `b56986e0…8ac`(harness `validate_original_source`·`source_unchanged=true`). R5_G1 EXE `9fe0e9f3…`·`bfddd8d8…`, `_G1MM.dll` `05bf7010…` 실행 뒤 재확인 불변.
- TDD: 테스트 먼저 작성 → 6 FAIL(RED) → 구현 → 6 passed(GREEN). 처음 작성한 게이트 순서 assertion 1건은 내 테스트 오류(#endif는 `if` 줄 뒤·호출 앞)라 테스트를 고쳤다.

## 실행·수치 (공유 temp `20261007_lap1161_work_hdef1/`)

| 항목 | 판정 | 근거 |
|---|---|---|
| D-1 반영 충실도 | **PASS** | lap1151 스냅샷(`20261007_g1r5_combo/build_src`)에서 `default_on.patch` 블록을 떼고 **저장소 블록 텍스트로 다시 넣은 결과가 스냅샷 `inmm_stub.c`와 byte 동일**. 그대로 `-DSYW2_G1_DEFAULT_ON`+`--image-base=0x6b640000`으로 빌드 → `_G1MM.dll` `05bf7010…`과 **7바이트만 다름**: PE TimeDateStamp 2(0x88·0x89)·CheckSum 3(0xd8~0xda)·export 디렉터리 TimeDateStamp 2(0x54c04·0x54c05). 이미지 베이스를 안 고정하면 ld가 DLL마다 임의 베이스(0x6b640000 vs 0x6fd00000)를 골라 12,934 B가 달라진다(재배치) — 사용자 판은 베이스 0x6b640000. 스크립트 `pecmp.py` |
| D-2 기본 빌드 불변 | **PASS** | 변경 전(저장소 트리에서 H-DEF1 편집만 되돌린 사본) vs 변경 후 플래그 없는 `_inmm.dll`: **5바이트** = PE 타임스탬프 2·체크섬 1·export 디렉터리 타임스탬프 2(`.edata` 0x53200+4). 코드·데이터 차이 0 |
| D-3 진단 끔 실측 | **PASS** | 현재 트리 `_G1MM.dll` `2bad42a0…` + R5 일반 `…R5_G1.exe`(`9fe0e9f3…`), `tools/g1_r5_combo_probe.py::run_probe`(래퍼 `d3_run.py`가 고정 sha 상수만 재바인딩, probe 소스 무변경). **끔**: 창 1600×1200·`install_failed` 0·훅 7곳 패치·PS3+30.2초 생존·입력 PASS, `inmm_sfx_log.jsonl` **0줄**(`sfx_table_probe`·`probe` 0). **켬**(`INMM_STUB_SFX_PROBE=1`): 같은 PASS + 로그 801줄 = `sfx_table_probe`(count 94→94) 1 + `sfx_dispatch` `trigger:"probe"` 800(= 형식 0..199 × 4 이벤트; 이 장면은 `0x8990C8` 존재 표가 비어 유닛 순회 호출 0) → 게이트가 실제 그 경로를 막는다는 대조 성립 |
| D-4 비회귀 | **PASS(후보 레인)** | 현재 트리 기본 켬 DLL(`make` PATH shim으로 `-DSYW2_G1_DEFAULT_ON` 추가, 번들 `bridge/_inmm.dll`에 `INMM_STUB_SFX_PROBE` 문자열 포함 확인) + 원본 HQ2002 EXE, `tools/g1_saved_scene_probe.py --new-game-path --new-game-start --new-game-act --new-game-play --hd-source scale2x`: 후보 레인 PASS, PS3 present 2,622개(select 4·produce 32·drag_move 23·act dwell 1,200·scroll 4방향 각 40~41·play dwell 1,201) HD min **100.0**·stale_max 0·fallback 0·안전 7종 0·p95 6~7ms, 선택 0→1·생산 쌀 5000→4200·드래그/이동 효과 true, scale2x validator PASS(3,953 present). **top-level FAIL은 베이스라인(대조) 레인**: 대조 레인은 G1 env 없음 = 800×600 원본이어야 하는데 기본 켬 DLL은 env가 없을 때 G1을 켜므로 창이 1600×1200이 되어 `no original game window in allowed sizes: 800x600` — 기본 켬 설계의 필연이며 shim 조합의 한계다(제품 결함 아님). mirror_validator BLOCKED는 lap1115 e와 동일(3,985 vs 3,953 record, 이미 알려진 하네스 판정) |
| 원본 보호 | **PASS** | 원본 EXE SHA·R5 EXE 2·`_G1MM.dll` SHA 전후 불변, game 사본 전부 삭제(`local/runtime/20261007_21…` 16K·`lap1161_d4` 1.2G는 prefix·manifest·로그 보존) |

- 기본 켬 빌드가 켜는 다른 무조건 진단 census(목록 공개, 변경 없음): `sfx_hook_install()`(엔진 `0x445930` 5바이트 hook + `C:\inmm_sfx_log.jsonl` 파일 생성 — 엔진이 자연 호출하지 않으면 기록 0줄, D-3 끔 실측 0줄), `asset_hook_install`(IAT, `C:\inmm_asset_log.jsonl`), 워커의 watch 표 읽기(`read_u32_safe`, 읽기 전용)와 `INMM_STUB_NO_UNIT_TICKS=1`로 유닛 tick 덤프 끔. **엔진 함수 호출·옛 G2 주소 읽기는 `sfx_probe_live_units`뿐**이었고 그것을 끈다.
- 공개 한계: D-4 대조(baseline) 레인은 기본 켬 DLL과 구조적으로 양립하지 않아 NG5 pair 비교는 아님(후보 레인 단독). 플래그 없는 빌드의 `sfx_probe_live_units`는 의도대로 그대로(옛 진단 하네스 경로 유지). 저장소 트리 `tools/inmm_stub/_inmm.dll`(gitignore 산출물)은 `make default-on` 첫 시도의 `rm`으로 한 번 지워졌고 같은 트리에서 재빌드했다(내용은 현재 트리 기준, 옛 산출물과 다를 수 있음). 이미지 베이스 고정은 재현성용 링커 옵션이라 저장소 Makefile에는 넣지 않았다(제품 영향 없음, middle이 필요하면 판단).

## 검사
- `make lint` PASS(ruff), `make typecheck` PASS(12 파일). focused `tests/test_g1_default_on.py` 6 passed. 전체 `make check`·`checks/safety.sh check` 결과는 STATUS 검증 줄에 보강한다.

## 다음 행동
middle(Opus) 독립 검수: D-1~D-4 새 스크립트 재계산(특히 D-1 베이스 고정 재현·D-3 로그 대조) → 수용 시 ③ HUD 패널 1장 시범 사전등록. 사용자 G1 시험 결과가 오면 최우선.
