# 2026-10-07 | lap1135 | G1 work — H-TR2: 묶음 시험판 재스테이징(save006 pair + victory-poke + DLL 동일성 + 4파일)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실무) 1 lap. C·하네스·테스트 변경 0.
- 입력: lap1134 사전등록 §7(`20261007_lap1134_middle_g1_hvs0_review_htr2_preregistration.md`). INBOX 새 사용자 지시 없음, APPROVALS 새 반려 없음, `loop/STOP` 없음.
- 가설: 현재 트리(lap1133 full PASS 1786 그대로)로 만든 단일 `_inmm.dll`이 사용자 시험 경로(save006 full pair)와 수리 경로(승리 배너·결과 표)를 모두 통과하고, 두 run의 DLL이 타임스탬프 외 같다.
- 원본 SHA: `[HQ]Syw2plus 2002.exe` `b56986e018b4…` — pair 두 lane `private_exe_sha256 == source_exe_sha256`, `source_unchanged` true. 후보 SHA = 스테이징 `_inmm.dll` `6cbb12aca8be4e420ea303a9ab922bae25cd096736de6f6b2dd8db1bc00266cf`(448,133 B).

## 0. TR2-0 출처

시작 때 source SHA가 §1 값과 일치: `g1_mirror2x.c` `1213c4abb660`·`g1_bar_copy.h` `ff12d6299246`·`g1_mirror2x.h` `d3af97ed6adf`·`direct_draw_trace.c` `5ee7c6e90021`·`Makefile` `f6b0a382c75a`·`g1_saved_scene_probe.py` `8c22de763922`·`test_g1_victory_poke.py` `5d383d080cf0`. 이번 회차 C·하네스·테스트 변경 0(실행 스크립트는 공유 temp `scripts/`에만).

## 1. TR2-1 save006 full pair 1회

명령(`scripts/run_tr2_1.sh`): `PYTHONPATH=. .venv/bin/python -u tools/g1_saved_scene_probe.py --runtime-root local/runtime/lap1135_tr2_pair --artifact-root <공유 temp>/20261007_lap1135_work_htr2/pair --hd-source scale2x --candidate-no-present-trace --candidate-no-unit-ticks`. 로그 `logs/gates/lap1135_tr2_1.log` `9f9f99475102…`, exit 0. 결과 `pair/pair-result.json` `56f4ae7f3e7f…`.

| 항목 | 값 | 판정 |
|---|---|---|
| pair `status` / `scene_state_equal` | PASS / true | PASS |
| input_effect checks | 7/7 true(selection_target·empty_click·drag_exact·drag_capture_binding·minimap_gate_restore·production_effect·production_completion) | PASS |
| minimap parity | PASS(effect PASS, 4/4) | PASS |
| V2·V2s·V2q 게이트 | 5 tag 모두 PASS | PASS |
| loaded: V2s 단일 흑색 블록 / Scale2x 기준 / 설명 안 된 블록 | 1,876 / 2,179 / **96**(gate ≤2,000) | PASS |
| Scale2x gate | PASS, present 1,192/1,192, outside diff 0, palette violation 0 | PASS |
| 두 lane EXE SHA·`source_unchanged` | `b56986e0…` 둘 다·true | PASS |
| cleanup | 두 lane `ok` true·`game_removed` true·prefix 프로세스 0 | PASS |
| 후보 창 | 1600×1200, scale 2 | PASS |
| 후보 prefix `inmm_unit_ticks.jsonl` | 0개(baseline lane prefix에는 있음 — `--candidate-no-unit-ticks`는 후보만) | PASS |

공개: `candidate.mirror_validator`는 `BLOCKED`("trace has no final summary", 1,193 errors) — `--candidate-no-present-trace` 경로의 기존 종류이며 lap1103 UA2-3 pair도 같은 BLOCKED(1,246 errors)에서 pair `PASS`였다. 스크립트가 pair `status`에 반영하지 않는 진단이다.

## 2. TR2-2 같은 트리 수리 경로(present trace 켬) — 시도 2회

- 시도 1(`vs_attempt1_baseline_poke_readback0/`, 로그 `logs/gates/lap1135_tr2_2_attempt1.log` `c75ada27acc6…`, exit 2, 결과 `b7a07e0ad614…`): **baseline lane만** `victory poke readback 0 != 1`로 FAIL(candidate lane PASS: poke 1/1·consumed ps 3·12/12). 원인 가설 = 하네스가 `write_flag(1)` 직후 `read_flag()`를 읽는 사이 원본 lane 게임 루프가 플래그를 먼저 소비하는 타이밍 경합(후보는 같은 읽기가 1이었음). **하네스·C 변경 금지(§7)라 수리하지 않고** 같은 명령으로 1회 재실행했다.
- 시도 2(`vs/`, 로그 `logs/gates/lap1135_tr2_2.log` `1de859edf834…`, exit 0, 결과 `5d23537f7631…`): 두 lane PASS(poke before 0·readback 1·consumed ps 3), 안전 7종 clean.

시도 2 후보 lane(candidate `victory_poke.present_summary`):

| 항목 | 값 | 판정 |
|---|---|---|
| criteria 12/12 | ps25_hd·ps29_hd·tab_soldiers/buildings/resources_hd·after_confirm_hd·safety_clean·ps29_reached·poke_consumed·banner_reached·readback_mirrored·bar_copy_mirrored 모두 true | PASS |
| readback calls/converted/rejects, 반환 | 1 / 1 / 0, 5013227 = `0x4C7EEB` | PASS |
| bar `0x468BB0` calls/mirrored/rejects | 2,714 / 2,714 / 0 | PASS |
| PS25(배너) HD min / stale max / present | 100 / 0 / 1,060 | PASS |
| PS29 HD min / stale max / present | 100 / 0 / 419 | PASS |
| 탭 3개·확인 뒤 PS9 HD min | 100 / 100 / 100 / 100 | PASS |
| trace dropped / Scale2x validator | 0 / PASS(3,782/3,782, outside 0) | PASS |
| cleanup | 두 lane ok·`game_removed` true | PASS |

mirror validator new-game `BLOCKED`(nearest oracle 0.77, 기존 종류)는 lap1133과 같은 공개 진단이다. 캡처는 열람하지 않았다(수치만, 중간 검수 몫).

## 3. TR2-3 DLL 동일성

- 스테이징 DLL = TR2-1 `pair/bridge/_inmm.dll`(`6cbb12ac…`) byte 복사(`cp -p`).
- TR2-2 `vs/bridge/_inmm.dll` = `c3b142c6…`(448,133 B 동일 크기). `cmp -l`로 다른 오프셋은 **6바이트**: `0x88·0x89`(PE `TimeDateStamp` 하위 2 B), `0xd8·0xd9`(`CheckSum` 하위 2 B), `0x53404·0x53405`(`.edata` 내보내기 디렉터리 `TimeDateStamp` 하위 2 B, 값 `e1a0c56a`→`22a7c56a`). 모두 빌드 시각 필드이고 타임스탬프 영역 밖 코드·데이터 차이는 0이다. 내보내기 디렉터리 타임스탬프는 사전등록이 예시한 PE 헤더 필드 밖이지만 같은 빌드 시각 값(상위 2 B `c56a` 일치)이라 같은 종류로 판정했다(middle이 독립 재조립에서 대조).
- lap1104 판(`94213374…`, 436,267 B)과 크기 448,133 B로 다르다(source 변경으로 정상).
- 문자열: `INMM_STUB_NO_UNIT_TICKS` 1, `SYW2_G1_PRIMARY_READBACK` 1, `SYW2_G1_BAR_COPY` 1, `SYW2_G1_PAUSE_SNAPSHOT` 1.

## 4. TR2-4 스테이징

`<공유 temp>/20261007_lap1135_work_htr2/user_test_staging/` 정확히 4파일(`260921_temp` 배치·APPROVALS 수정 안 함):

| 파일 | SHA256 |
|---|---|
| `_inmm.dll` | `6cbb12aca8be4e420ea303a9ab922bae25cd096736de6f6b2dd8db1bc00266cf` |
| `g1_trial_direct.bat` | `2da323e8bf53a984c612a282414ff33dbb15783b6505202e632206d87a026c19`(lap1103판 byte 복사, 일치) |
| `g1_trial_via_dxwnd.bat` | `29a35d2edf41dae2f7ac1b09a52d2c12bd301860733ca8cb70ce43c9e85d886c`(일치) |
| `G1_1600x1200_시험판_읽어주세요_20261007_lap1135.txt` | `f6593f5c6ec3d8ef1e54ef28c9725477a8fc76593021a890c8da491a9c62514f` |

안내문은 lap1103판에서 `scripts/make_guide.py`(`assert` 치환)로 생성했고 diff는 `guide_diff.txt` `4f958cb81572…`(32줄)다. 바뀐 것: ① DLL SHA·제목 개정 표기 ② 대체 문구 ③ 추가 수리 4개 쉬운 말 목록(위치·입력 동작 불변, 승리·패배는 합성 조건 측정 명시) ④ 파일 목록 "환경변수 3개"→4개·"이번 개정본(lap1101)"→"이 판에 포함된 lap1101 개정" 과거 표기 ⑤ 확인 3번에 선택 사항 한 줄(HUD 유지). 그 밖의 줄은 lap1103판 그대로다.

## 5. 판정

**H-TR2 `PASS(partial, 기술·격리)`** — TR2-1·TR2-2(시도 2)·TR2-3·TR2-4 충족. 사전등록 이탈: TR2-2 시도 1 baseline lane 하네스 경합 FAIL 1회(같은 명령 재실행으로 PASS, 수리 없음); TR2-3 비타임스탬프 후보 오프셋 2개가 `.edata` 타임스탬프 필드임을 추가 확인. 가설 실패 1회(60분 이내, 총 약 35분).

공개 한계: 승리·패배 화면은 합성 트리거 측정, 실전투 승리 UNKNOWN. mirror validator `BLOCKED` 진단(기존 종류). 사용자 시험 판단은 아직 없다.

## 6. 검사

- `checks/safety.sh check` SAFETY_PASS(로그 `logs/gates/lap1135-work-safety.log` `4ae1cfe7…`), `checks/context_limits.py` CONTEXT_PASS.
- 전체 `make check` SKIP — C·하네스·테스트 변경 0(lap1133 full PASS 1786 트리 그대로). 이번 회차가 늘린 증거는 런타임 run 2(+실패 1)·스테이징 4파일이다.
- game 사본: `local/runtime/lap1135_tr2_{pair,vs}` 아래 `game` 0개(런타임이 삭제, 시도 1 포함). prefix·manifest·output 보존, 디스크 여유 약 125G. 원본/참고 쓰기 0·커밋 0·`260921_temp` 미접촉.

## 다음 행동

middle(Opus, lap1136): 새 스크립트로 TR2-1 pair-result·TR2-2 raw 재계산(시도 1 baseline 경합 판정 포함) → 현재 트리 독립 재조립(타임스탬프 마스크, `.edata` 필드 포함) → 스테이징 DLL 대조 → 안내문 열람 → 수용 시 APPROVALS lap1104 항목에 "lap1135 판으로 대체" 메모 + 새 사용자 시험 요청, root 전달 `loop/ESCALATE_SOL`.
