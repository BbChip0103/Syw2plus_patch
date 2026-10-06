# 2026-09-27 | lap 717 | 목표 G5

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5`, 실무(work).
- 가설 / 사용자 관찰: 2026-09-27 15:49 운영자 판정(`docs/history/laps/20260927_direct_g5_v3_command_coverage.md`)을
  그대로 수행 — v3 후보(`e5004764…de6977`)에서 정지(pending `0x1000002`)·홀드(`0x1000027`)·순찰(`0x1000023`)이
  50 중 정확히 20만 수신하는 FAIL의 원인은 v3 청크 래퍼(`0x004AE550`→cave `0x004E4D50`)가
  `word [esp+8]`(order-type 헤더) ∈ 알려진 실제주문타입 화이트리스트 `{1,3,4,7,8,9}`일 때만 분할하고,
  그 외는 20칸 원본 본문으로 보내기 때문이라는 추정. 지시된 다음 work: ① gdb로 정지/홀드/순찰의
  `word [esp+8]` 실측(1회), ② v4: 분할조건을 '알려진 비명령 opcode가 아니면 분할'로 뒤집기(권장),
  ③ 원본 대 v4 paired 재측정(정지·홀드·순찰·이동 50/50), ④ 회귀+`make check`.
- 예상 PASS / FAIL 조건: v4 후보에서 정지·홀드·순찰이 원본20 대비 50/50 pending을 받으면 PASS,
  아니면(여전히 20/50 등) FAIL.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 전부 uncommitted(`LOOP_ALLOW_COMMITS=0`).
  **제품 EXE 0 변경**(신규 후보 바이트는 이 lap이 만든 파일에서 재현 가능한 산출물일 뿐, 원본/참고
  저장소에는 아무것도 쓰지 않았다).
  - `tools/g5_stop_hold_patrol_header_probe.py`(신규, read-only): lap681의 hook-site gdb 트레이스를
    정지/홀드/순찰에 재사용 — 아래 §①에서 **BLOCKED**로 결론.
  - `patches/selection/g5_selection_cap50_v4.py`(신규): v3의 청크 래퍼 게이트를 반전 — "알려진
    실제주문 화이트리스트 {1,3,4,7,8,9}면 분할"이 아니라 "lap676이 정적으로 확정한 알려진
    비명령/UI-알림 opcode 집합(`{0x52,0x56,0x19b,[0x19d-0x1a1],[0x1ae-0x1bc]}`)이면 그대로 두고,
    아니면 분할"로 반전. 청크 본체(80바이트 백업버퍼·3회 청크 분배·복원)는 v3와 바이트 단위 동일
    (`test_gate_reproduces_v3_body_modulo_call_site_relocation`으로 검증, call site 재배치로 인한
    2개 rel32만 차이).
  - `patches/selection/test_g5_selection_cap50_v4.py`(신규, 4개): 결정론적 빌드+SHA 고정, cave 여유
    (153바이트), v3 본체 동일성(call relocation 제외), 게이트의 `cmp` 즉치값·분기 순서가 lap676
    집합과 정확히 일치하는지 capstone 구조 검증.
  - `tools/g5_stop_hold_patrol_v4_probe.py`(신규): `g5_command_coverage_probe.py`의 이미 검증된
    dense-fixture+대형 재선택+`observe()` 방식을 재사용해 원본20/v4후보50 정지·홀드·순찰 paired
    측정.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(모든 실행 전후 불변,
  `source_unchanged=true`). v4 후보 `0e472792410ddc87eb5eee9809c99761da61d8afa23e73638db0fae5e10f9cbb`
  (결정론적, 3회 빌드 동일 — pytest 고정값·probe 실측값·재빌드 모두 일치). 격리 Wine/Xvfb 1600×1200,
  PS3 solo(시드 없음, lap682가 이미 확인한 기존 한계), owner0 dense fixture worker(slot1198) 앵커
  7×8 grid 55기 SEED_TYPE=2, 전체 재선택 `(12,40)→(788,470)`.

## 실행 명령 / 로그 / 캡처 경로

1. `PYTHONPATH=. .venv/bin/python tools/g5_stop_hold_patrol_header_probe.py --artifact-root
   .../20260927_lap717_stop_hold_patrol_header/run{2..5}` — gdb hook-site 실측 시도 4회.
2. `PYTHONPATH=. .venv/bin/python tools/g5_stop_hold_patrol_v4_probe.py --variant candidate
   --runtime-root local/runtime/g5-v4-shp-candidate --artifact-root
   .../20260927_lap717_v4_shp/candidate3` → exit 0, `status=COMPLETE`.
3. `PYTHONPATH=. .venv/bin/python tools/g5_stop_hold_patrol_v4_probe.py --variant original
   --runtime-root local/runtime/g5-v4-shp-original --artifact-root
   .../20260927_lap717_v4_shp/original1` → exit 0, `status=COMPLETE`.
4. `make check`(세션 내 포그라운드 완주, 로그 `logs/gates/20260927_lap717_make_check.log`),
   `bash checks/safety.sh check`.
   전체 artifact(JSON+캡처+probe.log)는
   `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260927_lap717_stop_hold_patrol_header/`,
   `.../20260927_lap717_v4_shp/`에 보존. `local/runtime/g5-v4-shp-*`·`g5-lap717-stop-hold-patrol-header`의
   `game` 사본(각 실행 직후, 디스크 위생 규칙)은 삭제, output/manifest/prefix/로그는 보존.

## 측정값 / 판정

**①(gdb 실측): BLOCKED.** hook site(`0x004AE550`) breakpoint는 4회 재시도(단일 worker 선택→목적지
검증 추가→dense-fixture 20기 그룹 선택까지 방법을 계속 강화) 모두 `hits∈{0,1}`이지만
`post_marker_hits=0` — 확인된 실제 MOVE(원본에서 pending `0x1000003` 달성 확인) 클릭조차 단 한 번도
관측 후 hit이 없었다. 이는 lap681이 **이미 독립적으로 발견한 동일 현상의 재현·확장**이다
(lap681: candidate 55기 선택으로 MOVE/ATTACK 모두 pending 50/50을 실측했음에도 hook site는
"클릭 이후 단 한 번도 히트하지 않았다"). 즉 이 non-invasive breakpoint 방법 자체가 실제 주문 발행
경로를 관측하지 못한다는 것이 이번 lap으로 원본 단일선택·목적지검증·20기그룹선택 3가지 조건에서
추가 확정됐다 — 정지/홀드/순찰의 실제 `word[esp+8]` 값은 이 방법으로는 끝내 측정하지 못했다
(**실패 가설 2회 초과, 이 방법은 이 지점에서 중단**). v3 문서가 주장한 "라이브 트레이스로 헤더 3/4
확인"도 lap681·lap717 양쪽 다 재현되지 않아, **화이트리스트 불일치 인과관계 자체가 정적 분석 수준의
가설**이라는 점을 분명히 한다(②에서 행동 결과로 직접 검증해 우회).

**②(v4 반전 게이트 구현): 완료, `FEASIBLE`.** `patches/selection/g5_selection_cap50_v4.py`. cave
여유 153바이트(한도 초과 없음), 신규 pytest 4/4 PASS.

**③(원본20 대 v4후보50 paired, 실제 행동 결과로 검증): PASS.** ①의 헤더값을 몰라도 되는 방식 —
가설 대신 **기능적 결과**를 직접 측정.

| 명령 | 원본 (20 선택) | v4 후보 (50 선택) | v3 후보(2026-09-27 15:49 기록) |
|---|---|---|---|
| 정지 (`0x1000002`) | `pending_changed_to` 20/20 | **`pending_changed_to` 50/50** | 20/50 FAIL |
| 홀드 (`0x1000027`) | `pending_changed_to` 20/20 | **`pending_changed_to` 50/50** | 20/50 FAIL |
| 순찰 (`0x1000023`) | `pending_changed_to` 20/20 | **`pending_changed_to` 50/50** | 20/50 FAIL |

두 실행 모두 `status=COMPLETE`, `cleanup.prefix_processes_after=[]`(잔류 프로세스 0),
`source_unchanged=true`, 후보 SHA 실측값이 report의 결정론적 빌드 SHA와 일치. 크래시 0.

## 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태

- `make check` **1101 passed in 890.28s**, ruff/compileall/mypy/`CONTEXT_PASS` 전부 PASS,
  `checks/safety.sh check` → `SAFETY_PASS`.
- **미실행(시간 예산, 다음 middle/work가 이어서):** lap682 이동 paired, lap684 부대지정/저장로드
  50/50/50, lap688/689 공격 재검증을 v4 후보로 다시 실행하지 않았다 — v4는 게이트 조건만 바꾸고
  본체(`test_gate_reproduces_v3_body_modulo_call_site_relocation`로 확인)는 v3와 동일하므로 이동·
  공격·부대지정·저장로드가 v3와 달라질 기술적 이유는 없으나, **실측 없이 무회귀로 단정하지 않는다.**
  미니맵 우클릭은 원본도 무반응이라 여전히 `UNKNOWN`(이번 lap 범위 밖).
- **잔여 위험(v4 docstring에 이미 명시):** 반전 게이트는 lap676의 22개 "비명령" 호출 부위가 아닌
  **모든** 헤더값(정지/홀드/순찰뿐 아니라 아직 카탈로그되지 않은 값 포함)을 이제 20초과 선택에서
  분할 대상으로 삼는다. lap676·lap679가 이미 확립한 "원본 본문은 읽기전용·멱등이라 반복 호출이
  안전하다"는 근거에 기반한 추론이며, 이번 lap이 직접 측정한 것은 정지·홀드·순찰 3가지뿐이다.
  2단 독립 검수에서 이 확장 범위(반전 게이트가 22개 비명령 부위를 실제로 건드리지 않는지, 즉
  UI/알림 이벤트가 20기 초과 선택 상태에서 발생해도 안전한지)를 우선 검토 요청한다.
- 2단 독립 검수·3단 사용자 milestone 승인 없음. G5 최우선 지시는 미처리로 유지(다음 middle 검수
  요청 후에도 사용자 승인 전까지는 제품 G5 PASS 아님).

## 추가 조치 (2026-09-27 16:45 운영자 지시 반영, 같은 lap 안에서 계속)

운영자가 이 문서를 보고 STATUS/INBOX에 새 방향을 남겼다: v4 정지·홀드·순찰 50/50 PASS는 수용하되,
middle 회부 전 **lap682 이동 paired, lap684 부대지정·호출·저장로드 50/50/50·51번째 미선택, lap688/689
공격, 크래시 0**을 v4 후보로 먼저 재확인하라는 지시다. v4는 v1/v2(선택 배열)를 그대로 두고 v3의
`FUN_004AE550` 청크 게이트만 반전하므로, `tools/g5_candidate_drag_probe.py`(`--ui-roundtrip`)와
`tools/g5_worker_relative_move_attack_probe.py`(이동+공격)를 새로 만들지 않고 모듈 전역 `g5`/`TARGET_SHA`를
v4로 monkeypatch해 그대로 재사용했다(두 파일 자체는 무수정 — 각각 v3 SHA를 문서화한 기존 lap
근거와 충돌시키지 않는다).

실행: legacy 원본 경로(`Syw2plus_re/Syw2plus/syw2plus_original.exe`, SHA `b56986e0…` 일치 확인 —
이 두 도구는 아직 `source/ORIGINAL_EXE` 고정 파일명이라 2026-09-26 22:52 경로 이전 전 위치가 필요)
사용, v4 후보 SHA `0e472792…f9cbb`(결정론적, lap717 앞부분과 동일).

| 검사 | 결과 |
|---|---|
| 이동(원본20/v4후보50, lap682 방식) | **PASS** — `ever_matched_count=50/50`, `converged=true`, `converged_at_s=0.15` |
| 부대지정+저장/로드(lap684 `--ui-roundtrip`) | **PASS** — `checks` 7개 전부 True: `selected_50`·`group_stored_stock20_plus_overflow49`(group1=20, fixture overflow 49, 56개 중 50 선택·6 미선택과 일치)·`deselected`·`recalled_50`·`save_created`·`group_retained_after_load`·`recalled_50_after_load`. `status=PASS_UI_ROUNDTRIP` |
| 공격(lap688 `ever_command4_count`, 1회) | **참고용 단일측정, v3 기존 승인범위와 일치** — `ever_command4_count=30/49`(61%), `attack_capable_count=49/50`(worker 제외), `pending_xy_match_count=49/49`, `observed_target_uids`=표적1기 정확 일치. lap688의 v3 N=5 분포(27,30,32,33,49 → 중앙값32)에 정확히 들어맞는다(v4가 이 단일 run에서 그 분포 밖으로 벗어나지 않음). N=5 반복은 이번 lap 예산에서 생략 — v4는 이 order-type(4)의 청크 게이트 판단을 v3와 동일하게 "실제주문"으로 분류하므로(반전 게이트가 v3 화이트리스트의 상위집합) 통계적 동일성이 기대되는 코드 경로이며, 이번 단일 실측은 그 기대와 모순되지 않는다. `attack_pass`(probe 내부의 순간피크 기준 bool)는 False이지만 이는 v3 lap684 run1/lap688 단일 실행에서도 흔했던 표본잡음 패턴과 같다. |
| 크래시 | **0** — v4로 실행한 4개 probe(정지/홀드/순찰, 이동, roundtrip, 공격) 전부 `status` 정상 종료·`cleanup.ok`(또는 `prefix_processes_after=[]`)·`source_unchanged=true`. |

**추가(16:45 지시 원문 그대로): `tools/g5_command_coverage_probe.py` 전체(ALT/Ctrl/Shift 드래그
포함) v4 1회.** 위 개별 도구 재사용과 별개로, 16:45 지시가 명시한 이 도구 자체를 monkeypatch로
v4에 연결해 원문 그대로 재실행했다(파일 무수정, `--variant candidate`, 1회) — direct session의
15:49 FAIL을 만든 바로 그 방법론.

| 단계 | v4 후보 결과 |
|---|---|
| 지면 이동(우클릭) | `pending_changed_to: {'0x1000003': 50}` — 50/50 |
| 정지(버튼) | `pending_changed_to: {'0x1000002': 50}` — 50/50 |
| 홀드(버튼) | `pending_changed_to: {'0x1000027': 50}` — 50/50 |
| 순찰(버튼) | `pending_changed_to: {'0x1000023': 50}` — 50/50 |
| 정지(`s` 단축키) | `pending_changed_to: {'0x1000002': 50}` — 50/50 |
| 홀드(`h` 단축키) | `pending_changed_to: {'0x1000027': 50}` — 50/50 |
| 순찰(`p` 단축키) | `pending_changed_to: {'0x1000023': 50}` — 50/50 |
| ALT/Ctrl/Shift/일반 전체드래그 | 전부 `count=50, unique=50` |
| 미니맵 우클릭 이동 | 여전히 무반응(원본도 동일, `UNKNOWN` 유지 — 회귀 아님) |

`status=COMPLETE`, `cleanup.prefix_processes_after=[]`, `source_unchanged=true`, 후보 SHA
`0e472792…f9cbb`(동일 결정론적 값). 이로써 **STOP/HOLD/PATROL이 버튼·단축키 두 입력경로 모두에서
50/50**임이 direct-session이 15:49에 v3 FAIL을 발견한 것과 정확히 같은 도구·방법으로 확인됐다.

| 크래시(종합) | **0** — 이번 lap이 v4로 실행한 5개 probe(정지/홀드/순찰, 이동, roundtrip, 공격, 전체
  command_coverage) 전부 정상 종료·cleanup 프로세스 잔류 0·`source_unchanged=true`. |

## 다음 한 가지

work tier 판단으로 다음 middle 독립 검수를 요청한다: (a) v4 게이트 반전 로직 코드 대조(특히
`KNOWN_NON_ORDER_SINGLES`/`RANGES`가 lap676 원문과 정확히 일치하는지), (b) 확장된 위험 범위(22개
비명령 호출부가 20기 초과에서 안전한지) 판단, (c) monkeypatch 방식으로 얻은 이동/부대지정/저장로드
PASS와 공격 단일측정이 v3의 기존 middle 조건부 승인(lap689) 범위를 그대로 유지한다는 판정, (d) 필요
시 공격 N=5 반복 추가 여부 결정. ①의 gdb 방법론 실패(BLOCKED)는 별도 기록만 하고 재시도하지 않는다
(대안이 필요하면 strategy/Sol 판정 요청).
