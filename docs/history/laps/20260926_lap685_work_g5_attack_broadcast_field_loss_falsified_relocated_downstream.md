# 2026-09-26 | lap 685 | 목표 G5

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5`(세션 보고 모델ID), 실무(work), high. 이번 lap에서 실제 gdb 라이브 트레이스 3종 + 정적 전수 xref 스캔 1종 + v2 대조군 실행 1종을 수행하고 read-only 진단 도구 5개+회귀 테스트 4개를 추가했다. 제품 후보/원본 EXE는 0 변경.
- 가설 / 사용자 관찰: lap684 handoff("STATUS 다음 한 가지") 그대로 — `patches/selection/g5_selection_cap50_v3.py`의 청크 재호출 3회 사이에서 order-type4(공격) 전용 필드(공격 플래그/타겟)가 xy와 달리 취급되어 청크 경계에서 손실/복원되지 않는다는 가설을 gdb로 직접 검증한다.
- 예상 PASS/FAIL 조건: MOVE(type3)와 ATTACK(type4)의 청크별 내부 상태(override 플래그/타겟, packed word, staging record, 실제 per-unit writer 진입 횟수)를 나란히 비교해, ATTACK에서만 나타나는 손실/누락 지점을 찾으면 그 지점이 원인. 두 order type이 모든 관측 지점에서 동일하게 움직이면 가설은 반증되고, 원인을 더 하류(consumer/revalidation)로 좁혀 다음 work에 넘긴다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 전부 uncommitted(`LOOP_ALLOW_COMMITS=0`, 이 저장소는 아직 최초 커밋 자체가 없음 — `git status`가 전체를 `??`로 보고).
  - `tools/g5_v3_staging_snapshot_trace.py`(신규): `0x004E4F37`(v3 캐이브 안, 재배치된 `call 0x004A3C10` 직후, 즉 스테이징/디스패치 호출 직후) breakpoint로 매 청크 호출마다 `0x893130`(60바이트 주문 레코드)·`0x8931E8`(로컬 큐 헤드) 원자 스냅샷.
  - `tools/g5_v3_staging_snapshot_probe.py`(신규): 위 트레이스를 `g5_v3_chunk_dispatch_probe.py`의 드래그50+fixture+주문클릭 하네스에 얹어 move/attack 각각 실행하는 드라이버(런타임 셋업 로직은 재사용, `run_trace`만 교체).
  - `tools/g5_v3_pending_broadcast_loop_probe.py`(신규): lap678의 `g5_pending_broadcast_loop_entry_trace.py`(0x40ff90/0x4aec60 진입 카운터, v2 대상으로 작성됨)를 **v3 청크드 후보**(`e5004764…`)에 그대로 재사용하는 드라이버, move/attack order-kind 지원.
  - `tests/test_g5_v3_staging_snapshot_probe.py`(신규): 세 신규 모듈의 주소 핀·엔트리포인트 노출을 고정하는 회귀 테스트(gdb 트레이스 스크립트 자체는 `import gdb`가 있어 텍스트로만 검증, 기존 lap678 테스트와 동일 패턴).
  - `tools/g5_worker_relative_move_attack_probe_v2.py`(신규): `g5_worker_relative_move_attack_probe.py`(v3 전용)의 `g5`/`TARGET_SHA` 모듈 전역을 v2로 스왑해 재사용하는 얇은 드라이버 + `tests/test_g5_worker_relative_move_attack_probe_v2.py`(신규, SHA 핀 + 전역 스왑/복원 검증).
  - `tools/g5_stock_selection_array_xrefs.py`(신규): v1의 옛 선택 배열(`0x899024`/`0x899028`/`0x89902A`/`0x899078`) 참조를 Capstone 전수 오퍼랜드 스캔으로 독립 재검증 + `tests/test_g5_stock_selection_array_xrefs.py`(신규, 잔여 0건을 고정).
  - 제품 EXE/원본/바이너리 0 변경. 격리 실행마다 `local/runtime/g5-lap685-*/*/game` 사본(각 ~2.7GB, 총 6회 실행분)은 완료 직후 삭제(manifest/output/prefix/로그는 보존). 이번 lap 시작 시 디스크 29GB 여유로 안전선(20GB)에 근접해 있어, **다른 과거 lap들이 정책대로 지우지 않고 쌓아 둔 `local/runtime/*/*/game` 사본 40개(~108GB)도 정책(`게임 실행이 끝나면 그 회차가 만든 game 사본은 지운다`)에 따라 먼저 정리**했다(manifest/output/prefix/로그는 그대로 보존, 활성 wine/game 프로세스 없음을 `pgrep`으로 사전 확인).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(세션 종료 시 재확인, 불변). 후보는 lap680~684와 동일 v3 `e5004764e945350a0391d69035f8c8f0d305fcca7d6aaa54066836bac3de6977`(재빌드로 재확인). 격리 Wine/Xvfb 1600×1200, PS3 solo owner0, dense fixture worker(slot1198) 앵커 7×8 grid 55기 SEED_TYPE=2, 드래그50(worker+49).
- 실행 명령 / 로그 / 캡처 경로 및 해시(공유 `temp/Syw2plus_patch/g5_lap685_chunk_field_trace/`):
  1. `PYTHONPATH=. .venv/bin/python -m tools.g5_v3_chunk_dispatch_probe --artifact-root .../attack_run1 --order-kind attack`, 동일 `--order-kind move`(`.../move_run1`로 이름만 다름, 같은 아티팩트 루트 재사용) — 둘 다 크래시 없음, `source_unchanged=true`.
  2. `PYTHONPATH=. .venv/bin/python -m tools.g5_v3_staging_snapshot_probe --artifact-root .../staging_attack_run1 --order-kind attack`, 동일 `--order-kind move` → `.../staging_move_run1`.
  3. `PYTHONPATH=. .venv/bin/python -m tools.g5_v3_pending_broadcast_loop_probe --artifact-root .../loop_attack_run1 --order-kind attack`, 동일 `--order-kind move` → `.../loop_move_run1`(각각 독립 `--runtime-root`).
  4. `PYTHONPATH=. .venv/bin/python -m tools.g5_worker_relative_move_attack_probe_v2 --artifact-root .../v2_attack_run1 --variant candidate`(v2 대조군, `ever_command4_count` 판정) → **0/49**, `max_pending_exact_count=0`, `raw_command_histogram={'3':17,'1':32}`.
  5. `PYTHONPATH=. .venv/bin/python -m tools.g5_stock_selection_array_xrefs` → 원본 EXE `.text` 전수 스캔, `residual_count=0`(52건 raw 바이트 출현 전부 v1 `DIRECT_SITES`/`END_SITES`로 이미 설명됨).
  6. `PYTHONPATH=. .venv/bin/python -m pytest -q patches/selection/test_g5_selection_cap50_v{1,2,3}.py tests/test_g5_candidate_drag_probe.py tests/test_g5_worker_relative_move_attack_probe.py tests/test_g5_worker_relative_move_attack_probe_v2.py tests/test_g5_v3_staging_snapshot_probe.py tests/test_g5_stock_selection_array_xrefs.py tests/test_g5_pending_broadcast_loop_probe.py tests/test_g5_command_packer_xrefs.py` → **36 passed**.
  7. `make check`(nohup 백그라운드 + 짧은 명령 폴링으로 세션 안 완주 대기, lap659 방식) — 1차 실행은 신규 도구의 미사용 `import sys` 하나로 `ruff` 단계에서 실패(pytest 976 passed는 이미 통과), 즉시 수정 후 2차 재실행 **976 passed(657.45s)** PASS. v2 대조군/xref 스캔 도구 추가 후 3차 최종 재실행 → **980 passed in 683.48s**, ruff/compileall/mypy/`checks/context_limits.py` 모두 PASS. 로그 `logs/gates/20260926_lap685_make_check_run3.log`(2차: `..._run2.log`).
  8. `bash checks/safety.sh check` → `SAFETY_PASS`(2회, 최종 실행 후).
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - **① 빌더 내부(패커/오버라이드) 가설: 반증(FALSIFIED).** `g5_v3_chunk_dispatch_trace.py`의 `cave_call_site`/`packed_word_store` 이벤트를 move/attack 각 1회 실행으로 나란히 비교 — 단일-타겟 오버라이드 플래그(`0x8930A4`)·타겟(`0x8930A0`)은 두 order type 모두 3청크 전부 `0`/`0x0`으로 동일. packed word의 "aux" 상위 4비트 히스토그램(0~15 순환)과 "slot" 하위 12비트(항상 0)도 move·attack이 청크별로 **바이트 단위로 동일한 패턴**이다. lap684가 제시한 "청크 경계에서 order-type4 전용 필드만 다르게 취급된다"는 가설은 **이 레벨에서는 기각**된다.
  - **② 신규 관측(스테이징 레코드 정적 재사용): move/attack 모두 동일, 원인 아님으로 좁힘.** `g5_v3_staging_snapshot_trace.py`로 재배치된 `call 0x004A3C10`(스테이징/디스패치 호출) 직후 `0x893130`(60바이트 레코드)을 매 청크 호출마다 스냅샷 — **청크0·1·2가 헤더(`0x1000004`/`0x1000003` 등)와 unit-list 20워드까지 바이트 단위로 완전히 동일**하다(청크1은 entries[20:40], 청크2는 entries[40:50]+패딩을 넣어 호출했음에도 스테이징 결과가 바뀌지 않음 — 이 경로가 매 클릭 한 번만 유효하게 반영되고 반복 호출은 무시/no-op됨을 시사). 그러나 **이 현상은 move·attack 양쪽에서 동일**하게 나타나 move/attack 비대칭의 원인은 아니다(둘 다 무시되는데 move는 성공, attack은 실패하므로 이 경로 자체가 실제 커밋 경로가 아니거나 최소한 유일한 경로는 아님).
  - **③ 신규 관측(실제 per-unit writer 디스패치 루프): 반증(FALSIFIED), 핵심 재프레이밍.** lap678이 특정한 진짜 per-unit `+0x384` 작성 경로(디스패처 `0x4AEC60` → 래퍼 `0x40FF90` → writer `0x412540`)를 v3 청크드 후보에 그대로 재사용해 진입 횟수를 세었다: **MOVE `dispatch_entries=50`, ATTACK `dispatch_entries=50`** — 클릭 하나당 디스패처가 정확히 50회 진입한다(선택 50기와 일치), **두 order type이 동일**하다. 즉 청크드 빌더→실제 writer 디스패치 경로 자체는 50기 전원에 대해 정상 작동하며, 이 경로만 놓고 보면 v3가 attack에 대해서만 20으로 잘린다는 증거가 없다.
  - **종합 판정: NOT_FEASIBLE(이번 가설).** lap684가 "다음 한 가지"로 지정한 "청크 재호출 사이 order-type4 전용 필드 보존/복원" 가설은 빌더(`FUN_004AE550`) 내부 상태(①)와 빌더→writer 디스패치 경로(③) 두 지점 모두에서 move/attack이 바이트/횟수 단위로 동일함이 실측으로 확인되어 **기각**된다. lap684가 관측한 실제 결함(원본 `ever_command4_count` 100% vs 후보 ~0%)은 청크드 빌더나 그 직후의 디스패치 루프가 아니라, **그 이후 단계 — writer(`0x412540`)가 실제로 쓴 `+0x384` 값이 몇 tick 안에 되돌려지는 revalidation/consumer 로직(가장 유력한 후보: lap677이 찾은 `FUN_0040C640`), 혹은 애초에 청킹과 무관하게 v1 이후의 SELECTION_BASE 재배치 자체가 공격 유지에 영향을 주는지** 쪽으로 좁혀야 한다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 회귀 36 passed(신규 9 포함), `make check` 최종 980 passed(683.48s), ruff/compileall/mypy/`CONTEXT_PASS`/`SAFETY_PASS` 모두 PASS(2회 확인). 제품 후보/원본 EXE 0 변경. 이번 lap은 제품 코드를 고치지 않았다 — 원인이 아직 단일 지점으로 좁혀지지 않았기 때문(구현 우선 원칙에 따라 잘못된 지점을 추측 수정하지 않음). G5 2단 독립 검수·3단 사용자 milestone 승인은 여전히 없음(원래부터 없었음). v2 대조군 결과(`ever_command4_count=0/49`)는 lap684의 v3 결과(`≤1/49`)와 동일한 실패 패턴을 독립적으로 재확인했다. 디스크: lap 시작 시 29GB(다른 lap들의 미정리 game 사본 108GB 발견·정리) → 113GB로 회복, 이번 lap 실행분(6회, ~16GB) 정리 후 최종 110GB.
## 추가 조치 (2026-09-26 17:55 운영자 승인+순서 지정, 같은 lap 안에서 계속)

STATUS.md에 운영자가 정확히 위 (B) 방향의 실험을 **먼저** 지시했다: lap684 probe(`ever_command4_count`
기준)를 **v2(청킹 없음, 재배치만)** 후보로 실행해 v2도 실패하면 원인은 재배치(옛 선택 배열 `0x899024`/
`0x899028`/`0x899078`을 아직 읽는 attack 관련 코드)로 귀속하고 정적 전수 검색으로 재타깃, v2가 정상이면
청킹 쪽으로 (A)를 진행하라는 순서다. `tools/g5_worker_relative_move_attack_probe_v2.py`(신규, 기존
probe의 `g5`/`TARGET_SHA` 모듈 전역을 v2로 스왑하는 얇은 래퍼)로 실행:

- **v2 후보 결과: `ever_command4_count=0/49`**(원본과 대조하면 lap684의 v3 결과 `≤1/49`와 사실상 동일하게
  실패). `max_pending_exact_count=0`, `observed_target_uids=[]`, `raw_command_histogram={'3':17,'1':32}` —
  공격 계열(`command==4`)이 전혀 나타나지 않는다. (참고: 같은 실행의 MOVE는 `ever_matched_count=23/50`으로
  v2의 알려진 20-근처 상한과 일치, 별개 지표.) **이는 청킹이 원인이 아님을 실측으로 재확인한다** — v2(청킹
  없음)와 v3(청킹 있음) 둘 다 공격이 거의 완전히 실패하므로, 문제는 v1의 SELECTION_BASE 재배치 이후 두
  후보 모두에 공통으로 존재하는 회귀다.
- **정적 전수 검색(신규 `tools/g5_stock_selection_array_xrefs.py`): 잔여 참조 0건.** v1의 `DIRECT_SITES`/
  `END_SITES` 표가 손으로 특정 opcode 패턴만 찾은 것과 달리, Capstone로 `.text` 전체를 선형 디스어셈블해
  `X86_OP_IMM`과 절대주소 `X86_OP_MEM`(base/index 없음) 오퍼랜드를 전부 스캔했다. 원본 EXE 파일 전체의
  raw 4바이트 리틀엔디안 바이트 출현(코드/데이터 불문)도 별도로 세었다: `0x899024`=9회, `0x899028`=28회,
  `0x89902A`=1회, `0x899078`=14회, 합계 **52회 — v1의 `DIRECT_SITES`(38)+`END_SITES`(14) 표 크기와 정확히
  일치**한다. 즉 **원본 EXE 어디에도(코드·데이터 통틀어) v1이 아직 재타깃하지 않은 옛 선택 배열 참조는
  없다** — 운영자가 제시한 "아직 옛 배열을 읽는 공격 관련 코드" 가설은 **문자 그대로의 형태로는 기각**된다.
- **판정: 재배치 자체가 원인이되, 리터럴 주소 누락이 아니라 더 간접적인 경로다.** v2/v3 둘 다 동일하게
  실패하고(청킹 무관 확정) 옛 배열에 대한 잔여 리터럴 참조도 없으므로(누락된 재타깃 지점 없음), 남은
  후보는: (i) attack 전용 코드가 이 배열을 **레지스터 상대주소**(예: 어떤 다른 이미 재배치된 포인터로부터
  계산된 오프셋)로 읽어 리터럴 스캔에 안 잡히는 경우, (ii) 배열 재배치 자체와 무관하게 **`SELECTION_CONSUMER_LIMIT_SITES`/`HIT_TEST_APPEND_LIMIT_SITES`류의 프레임 크기 확장이 attack 전용 필드 하나를
  놓친 경우**, (iii) 애초에 배열 위치가 아니라 **재배치가 만든 새 메모리 레이아웃(예: 겹치는 다른 구조체)
  때문에 attack 검증이 실패하는 경우. lap677이 찾은 `FUN_0040C640`(pending 컨슈머) 직접 트레이스가 여전히
  가장 유력한 다음 단계다.

## 다음 한 가지 (갱신)

새 middle이 이번 lap의 두 반증(청크드 빌더/디스패치 무관, 옛 배열 리터럴 잔여 0건)을 검수한다. 다음 work는
middle 없이: **`FUN_0040C640`(pending command word `[esi+0x384]` 컨슈머, `0x40e720` 점프표 분기)에
non-invasive breakpoint**를 걸어 v2(가장 단순한 재현 케이스, 청킹 변수 제거) 후보로 attack-toolbar+지면
클릭 1회 동안 각 실행에서 어떤 유닛(슬롯)이 처리되고 `+0x384`가 유지/되돌려지는지 직접 상관시켜, "거의 즉시
대부분 되돌아간다"는 관측의 정확한 되돌림 지점(PC)과 그 근처에서 참조하는 메모리(재배치된 것인지 옛 위치인지)를
특정한다. 찾으면 최소 수정 후 v2/v3 각각에서 `ever_command4_count` 기준 원본·후보 각 2회 재실행해 lap684의
4-run 표를 재현·개선한다.
