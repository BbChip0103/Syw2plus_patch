# 2026-09-24 | lap 546 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5` / high, work (하네스만 실행, middle 카드 없음 — `docs/work/active/G2_STRATEGY_W41R_PRESCAN_LAP545.md` §2·§6).
- 가설 / 사용자 관찰: lap545 strategy 판정 (B) — W41이 두 번(row40/42) T0 배치에서 owner2 type2 60기를 한 행에 못 담고 gap 행으로 스필오버한 것(N200')이
  하네스 배치 결함이며, 원본 배치 검사기(`FUN_0042ecb0`, N201)를 게임 메모리에서 읽기만 해서 시딩 전에 행별 자유 칸을 미리 계산하면
  스필오버 없는 행을 고를 수 있다는 가설(H21/H22). W41R은 이 가설을 기존 W41 하네스에 사전 스캔+자기검증+행 탐색만 얹어 1회 검증한다.
- 예상 PASS / FAIL 조건: H21a 8/8 앵커 일치(디코더 자기검증) 실패 시 `BLOCKED(gate: prescan_decoder_mismatch)`.
  L=42..34 중 조건①~⑤을 만족하는 L이 없으면 `BLOCKED(gate: no_front_row)`. 있으면 그 L로 시딩·H20 재확인 후 `ENGAGED_FRONT`/`NO_ENGAGE_*`/`PROBE_VOID`/`BLOCKED`로 판정. 카드 M2: 결과와 무관하게 재시도 0회.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 제품 source **0개 변경**(`patches/`, `tests/` 무변경). 새 파일은 전부 `temp/Syw2plus_patch/g2_capacity/20260923_lap546_w41r_prescan/`에만 있다:
  `w41r_run.py`(lap543 `w41_run.py`를 그대로 복사한 뒤 H21/H21a/H22만 추가 — diff 287줄, docstring/신규 함수/신규 상수/시딩 루프 앞 삽입 블록뿐, 기존 로직 미변경).
  SHA `w41r_run.py`=`ca6ccf1ac3d0ca165b3cec1b28f15ed4a5dc2008f81b739aef4e08333dfbdb5b`. 커밋 0(LOOP_ALLOW_COMMITS 미설정, 기본0).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 실행 전 `b56986e0…8a8ac`, 실행 후 `b56986e0…8a8ac`(`source_unchanged=true`).
  후보 `a10024de5e1c1cbedcddde0c3b52f5b3a9cf0721ee066542669f4883a1bb2d68`(lap524 고정 기대치와 일치, N=4001 persistence-compat). 브리지 dll `89e2ae369e…fb7233`.
  격리 Wine prefix/display `:6536`(lap543과 동일 번호, 재사용 전 lock 없음 확인). 활성 8 owner, cap5000 confirmed. 허용목록 {5,7,46,2} 수량 100/25/20/60, 순서 N187 불변.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `PYTHONPATH=/home/dev_00/sharedfolder/260320_Syw2plus/Syw2plus_patch timeout 2850 python3 w41r_run.py`(cwd=산출물 디렉터리).
  산출물: `run_summary.json`(`8c58870fe2f786f2105683d6b069d5234a9dbe1480f9bd7ccf0968d9296459bb`), `prescan.json`(`0343d4fae1da59f3f934796021c680197a19c461b8c8eae72e9c055b61f8dc6c`),
  `resource_receipts.json`(`741a5118d1abe4cd4e603ed2a70e46a3c1d27e8996dcb5380a9cab989c2c1978`), `w41_orchestrator.log`. 실행 전 게이트: lap543 `w41_run.py` SHA
  `a6ea50fb…dce8ba8`, 시도1/2 `t0_positions.json` SHA `ffdb070e…698956`/`064681fb…09fec2` 카드 지정값과 직접 대조 일치(bash sha256sum). `checks/safety.sh check` = `SAFETY_PASS`(사전 1회, 사후 1회).
  targeted `tests/test_g2_runtime_bridge_fixture_type_allowlist_pin.py`+`tests/test_g2_runtime_bridge_op8_order_engagement_contract.py` = 14 passed(source 불변, N22 — 전체 `make check` 생략).
  실행 전 `h21a_synthetic_self_test()`를 모듈 import 시 합성 5×6 보드로 단위 검증(행 우선 채우기·`extra_occupied`·지도 밖 `None` 3케이스) — 전부 PASS 후에만 실 프로세스에 연결.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **자기 라벨 `BLOCKED`(gate: `no_front_row`)**, `verdict=BLOCKED`.
  **H21a 디코더 자기검증 8/8 PASS** — 시도1 owner0~5(앵커 (20,24)(20,32)(20,40)(20,48)(20,76)(20,84))와 시도2 owner2·3(앵커 (20,42)(20,50)) 전부
  모사 좌표 집합이 실제 `t0_positions.json` 관측과 **정확히 일치**(불일치 0). 이것은 H21의 주소 산식(`MAP_BASE+0x4fdc` 행 오프셋, `+0x5980`/`+0x598c` 점유·지형 포인터,
  지형 거부 마스크 `0x236A`)이 실제 게임 메모리에서 검증됐다는 첫 실측 증거다(N201이 정적 판독이었던 것과 달리 이번은 런타임 재현).
  **H22 탐색: L=42부터 34까지 9개 후보 전부 조건①(owner2 60기가 오직 행 L에만) 실패**(cond1=False 9/9) — 매번 60기 중 일부가 다음 행으로 스필오버했다
  (예: L=42→row42+43, L=34→row34+35). 조건②(owner3 L+8..L+9 이내)는 9/9 성립했지만 조건①이 항상 깨져 조건⑤(gap 비어있음)도 9/9 실패했다.
  즉 **y=34~50 구간 전체가 지형상 60기를 한 행에 못 담는다** — W41의 row40/42 실패가 국소 지형 문제가 아니라 이 구간 전체의 특성이었음을 이번 lap이 처음으로 확인했다.
  op5/op6 seed 호출 0건(자원 op7 8건만 적용, H21 규정 순서대로 이 시점까지는 정상). 실행 시간 36초(00:02:48~00:03:24), 45분 상자 안에서 조기 종료.
  `residual_processes=[]`, Xvfb `:6536`/wineserver 잔류 0(수동 재확인 포함).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 카드 M2(§99) "W41R 뒤에는 결과가 무엇이든 재시도 0회"에 따라 **이 work 역할은 재시도하지 않는다**.
  카드 §3 결과표: `PROBE_VOID`·`BLOCKED`(gate 포함) → S1 op8 교전 경로 `BLOCKED` 확정, middle이 원인만 확인하고 사용자 보고(§4).
  이번 lap은 middle 독립검수 전이라 최종 확정이 아니다. 남은 위험: y=34~50 밖(예: y<24, y=52 이후, owner4/5 쪽 인접 행)에 대안 행이 있는지는 카드 범위(L=42..34 고정) 밖이라 미탐색 —
  §4 보고 시 이 잔여 가능성도 언급해야 한다. 제품 source 무변경, AI/생산 로직 변경 0.
- 다음 한 가지: **middle(Opus5.5) 독립 재계산** — `prescan.json`/`run_summary.json`을 원시로 재확인(H21a 8/8, H22 9개 후보 cond1 전부 False 재현),
  카드 §3 분기(`BLOCKED`(gate)→S1 op8 경로 `BLOCKED` 확정)를 그대로 승인하고 `docs/work/active/G2_STRATEGY_W41R_PRESCAN_LAP545.md` §4 (가)~(라) 선택지로 사용자에게 보고한다.
  보고에는 이번에 처음 확인된 사실(H21a로 주소 산식 실측 검증 완료, y=34~50 구간 전체가 지형상 60기 단일행 수용 불가)을 포함한다.
