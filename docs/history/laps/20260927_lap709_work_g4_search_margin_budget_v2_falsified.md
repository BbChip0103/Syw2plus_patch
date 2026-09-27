# 2026-09-27 | lap 709 | 목표 G4 (길찾기 개선 후보 v2)

- 실제 provider/model/effort / 지정 역할: Claude Code Sonnet 5 (실무, 세션 자체 확인 "이번
  세션은 일반 작업자다"). STATUS "다음 한 가지"(lap708 handoff, 08:55 운영자 판정 계열,
  구현 우선) 수행: ① `analysis/memory_maps/g4_move_order_local_step_retry_20260927.md` §3이
  미조사로 남긴 `FUN_0041AF90` vtable 호출 대상을 정적으로 특정, ② 마진/탐색 본체 상수로
  후보 v2 빌드, ③ obstacle_row(world (93,56)) 원본 N=3 대 후보 N=3 paired 재측정.
- 가설 / 사용자 관찰: `FUN_0041AF90`(로컬 nudge 실패 시 `FUN_0040B810`이 호출하는 "진짜"
  경로 스텝 진입점)이 시작/목표 좌표를 `±0x1E`(30타일) 마진으로 클램프한 bounding box를
  만들어 전역 싱글턴 경로탐색 엔진(`ds:0xb92cbc`, 생성자 `FUN_0041AE70(this,200,200)` at
  `0x424ca6`, vtable `0x4e57e0`)의 vtable 두 번째 슬롯(`0x46b840`, `.rdata` 파일 오프셋
  `0xe57e4` raw 파싱으로 확정)을 직접 호출함을 확인했다(근거 §7.1). `FUN_0046B840`은 open-list
  기반 8방향 그리드 탐색 본체이나, per-call 스텝 예산 상수를 스택 인자에 수기로 역산 대응시키는
  데는 실패했다(컴파일러 재적재 패턴으로 오프셋 산수가 신뢰 구간을 벗어남, §7.2 — 과다 확신
  금지, 정직하게 미확정으로 기록). 반대로 마진 `0x1E`는 4개의 exact byte로 완전히 확정된다.
  **H2**: 이 마진을 30→60타일로 배증하면 obstacle_row `path_ratio_max`(2.540, world (93,56),
  lap707 baseline)가 개선된다. **반대 가설(사전 명시)**: obstacle_row 장애물(8타일 폭)은
  원본 30타일 마진 안에도 이미 들어오므로 마진을 넓혀도 개선이 없을 수 있다.
- 예상 PASS / FAIL 조건: 후보 obstacle_row N=3(world (93,56))의 `path_ratio_max`/`arrival_rate`가
  원본 N=3 대비 악화되지 않고(동률 이상 개선 기대) 개선되면 PASS, 변화 없거나 악화되면 H2
  FALSIFIED. 크래시 0, `source_unchanged=true`, `cleanup.ok=true` 전 실행 요구.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 신규
  `patches/pathing/g4_search_margin_budget_v2.py`(EDITS 4건, 파일 오프셋
  `0x1AFC1/0x1AFCB/0x1AFED/0x1AFF6`, `8d70e2`→`8d70c4` ×2 + `83c01e`→`83c03c` ×2),
  신규 `patches/pathing/test_g4_search_margin_budget_v2.py`(7 tests),
  `tools/g4_path_baseline_probe.py`(`--variant {original,candidate,candidate_v2}`로 확장,
  기본 `original`/`candidate` 무변경 — 회귀 22 tests로 확인),
  `analysis/memory_maps/g4_move_order_local_step_retry_20260927.md`(§7 추가: vtable
  해석·실측). uncommitted, `LOOP_ALLOW_COMMITS=0`. 게임 EXE/DLL 원본 미변경(사설 사본만 패치).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 SHA
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(8회 전부 불변). 후보 SHA
  `ab66669d795a1d89a018aa3e4c32a7d353fe7c03297becdddde55a5dbaf57a40`(4회 전부
  `patched_bytes` 재계산과 일치). 환경 `[ESL]Syw2plus/` 소스, 1600x1200x24 Xvfb,
  `SYW2_SUPPLY_PROBE=1`. 활성: 솔로(비고정 시드) 1인 × 8회(원본 4 + 후보 4). fixture:
  기존 워커(슬롯1198) + owner0 type2 55기 dense fixture, 원본 20-cap 드래그로 20기 선택,
  `obstacle_row` 목적지(8타일, 본진 footprint 방향).
- 실행 명령 / 로그 / 캡처 경로 및 해시: `.venv/bin/python tools/g4_path_baseline_probe.py
  --scenario obstacle_row --variant {original|candidate_v2} --runtime-root
  local/runtime/g4-lap709-<variant>-run<N> --artifact-root
  .../temp/Syw2plus_patch/20260927_lap709_g4_search_margin_v2/<variant>-run<N>`.
  원본 run1은 world (10,49)로 착지해 제외(`ever_move_command_count=0`). 후보 run2도
  world (10,49)로 제외. `make check` 로그
  `logs/gates/20260927_lap709_g4_search_margin_v2_make_check.log`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): world (93,56) 착지분(원본3/후보3)만 비교:

  | variant | unit_type | arrival_rate | arrived/expected | path_ratio_max |
  |---|---:|---:|---|---:|
  | original ×1 | 21 | 0.85 | 17/20 | 1.9328098099980875 |
  | original ×2 | 31 | 0.70 | 14/20 | 1.9428090415820636 |
  | candidate_v2 ×2 | 31 | 0.70 | 14/20 | 1.9428090415820636 |
  | candidate_v2 ×1 | 21 | 0.85 | 17/20 | 1.9328098099980875 |

  두 unit_type(21, 31) 모두 원본·후보 사이에서 `arrival_rate`·`path_ratio_max`가 소수점까지
  완전히 동일하다. **판정: `H2 FALSIFIED`** — bounding-box 마진 30→60타일 확대는 이
  시나리오의 `path_ratio_max`/도착률을 전혀 바꾸지 못했다(반대 가설과 일치: 장애물이 이미
  원본 마진 안에 있었다). 크래시 0, `source_unchanged=true`, `cleanup.ok=true` 8/8.
  `make check` **1049 passed(837.09s)**, ruff/compileall/mypy/`CONTEXT_PASS` 전부 PASS,
  `checks/safety.sh check` **SAFETY_PASS**. 신규 테스트 7개 전부 PASS. 각 run 종료 후
  `local/runtime/g4-lap709-*/*/game` 사본 삭제(디스크 위생, manifest/output/prefix/로그
  보존; 최초 정리 명령의 경로 깊이가 한 단계 부족해 뒤늦게 재정리했다 — 디스크 여유는
  47GB로 20GB 하한을 넘지 않았다).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 회귀 없음(make check/ruff/mypy/safety
  전부 PASS, 기본 `--variant original`/`candidate`는 기존 산출물과 동일함을 22개 회귀
  테스트로 확인). **남은 위험**: (1) `FUN_0046B840`의 실제 per-call 스텝 예산 상수는 이번
  lap도 확정하지 못했다(§7.2, 정적 조사로 스택 슬롯 산수가 신뢰 구간을 벗어남 — gdb 런타임
  확인 필요). (2) 엔트리[0](`0x41ae90`, footprint 겹침 검사)과 엔트리[2](`0x421fe30`)는
  미조사로 남았다. (3) 이번 v2 바이트 패치는 **채택하지 않는다** — falsified 가설의 증거로만
  보존한다(패치 파일/테스트는 남기되 다음 후보에 이어 쓰지 않음). 독립 검수/사용자 승인
  없음(work tier 자체 raw 측정, 정보 제공용).
- 다음 한 가지: STATUS 2026-09-27 08:55 지시가 예고한 대로 **실패 가설 2/2 도달**(v1=로컬
  재시도 한도 lap708, v2=탐색 bounding-box 마진 lap709, 둘 다 FALSIFIED). 다음 work는 같은
  obstacle_row 장면에서 세 번째 정적 추측 패치를 반복하지 않고 **strategy 판정을
  요청**한다: (a) gdb로 후보 원본에 breakpoint를 걸어 `FUN_0046B840`의 실제 스텝 예산 상수를
  런타임으로 직접 확정한 뒤 그 상수로 후보 v3를 시도할지, (b) obstacle_row/`path_ratio_max`
  지표 자체를 다른 시나리오·지표로 바꿀지, (c) G4 이 개선-후보 하위 트랙을 보류하고 다른
  G4 미충족 항목(사용자 승인, AI 개선 제품 비교 자체의 정의)으로 넘어갈지.
