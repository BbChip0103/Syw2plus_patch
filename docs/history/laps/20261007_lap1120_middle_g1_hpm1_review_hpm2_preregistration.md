# 2026-10-07 | lap1120 | G1 middle — H-PM1 귀속 독립 검수 + 수리 방식 결정(R-a) + H-PM2 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(진단·계획·확인) 1 lap. 게임 실행 0, 제품 source·하네스·테스트 변경 0, 커밋 0.
- 입력: `loop/ESCALATE_SOL`(lap1119 work → middle 수리 방식 결정 요청), STATUS 다음 한 가지, lap1119 기록, lap1118 사전등록 §5. INBOX 새 사용자 지시 없음, APPROVALS 새 반려 없음(G1 사용자 시험 lap1104 대기), `loop/STOP` 없음.
- ESCALATE_SOL 처리: 원문을 `docs/history/laps/20261007_lap1120_preserved_lap1119_escalate_sol.txt`로 byte 일치 보존(SHA256 `80f9993559bb8622…`, `cmp` 일치)한 뒤 삭제했다.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 직접 재계산 MATCH(읽기만).
- fixture: lap1119 raw만 사용(run a·b·c, 새 게임 경로 PS9→PS7→PS5→PS3→Esc PS23, 저장 실행 없음). artifact SHA 9개(screen_watch·trace_raw·new-game-path-result × 3)를 직접 재계산해 lap1119 기록 앞자리와 전부 일치.
- source 동일성: lap1119 기록의 파일 SHA 5개(probe `54c8abbbeebf`·test `0b6d92d01275`·watch.c `c59525803859`·watch.h `3470eff2c099`·direct_draw_trace.c `2cedc853f92f`) 일치, lap1119 full check 로그 뒤 수정된 tools/tests/checks 파일 0.

## 1. 독립 재계산 (새 스크립트)

- 스크립트: 공유 temp `20261007_lap1120_middle_review/recalc_lap1120.py`(`d3511d0d…`) → `recalc_lap1120.json`(`f0e2ab02…`). 저장 창 열림 = PS23에서 `partial_copy_pixels` 증가가 99,200(320×310)인 첫 present, 닫힘 = 그 뒤 PS23 stale 최대 present, watch `p` = seq − 첫 PS23 seq − 1(lap1119 상관식, 독립 유도).

| run | 첫 PS23 seq | 저장 창 열림 seq/p | 닫힘 seq/p | 닫힘 stale | 닫힘 전환 계수(partial/layer/menu/frame) | covered 직전→다음 present | 손실 | 닫힘 HD | 정착 PS23 HD p50(n) |
|---|---|---|---|---|---|---|---|---|---|
| a | 2361 | 3499 / 1137 | 4964 / **2602** | 95,886 | 0/0/0/0 | 479,692→435,673 | 44,019 | 79.96% | 90.765%(1,132) |
| b | 2321 | 3207 / 885 | 4651 / **2329** | 95,316 | 0/0/0/0 | 479,692→435,699 | 43,993 | 80.08% | 90.771%(885) |
| c | 2358 | 3248 / 889 | 4695 / **2336** | 95,985 | 0/0/0/0 | 479,692→435,672 | 44,020 | 79.94% | 90.765%(1,130) |

- 닫힘 p는 lap1119 work 값(2602·2329·2336)과 같다. 손실 약 44.0k는 lap1118 재계산(44,040/44,005, 다른 run)과 같은 크기다.
- **표본 writer(구간별 EIP/스레드 계수):**
  - A(260,250)·B(530,250): 메뉴 구간·닫힘 present·정착 PS23 = tid 288 `ucrtbase` `0x7AF3E6C9`(A)/`0x7AF3E6CE`(B)뿐. 저장 창 구간에만 tid 280 `0x004662DE`가 tid 288과 1:1로 더해진다(a 1,465·b 1,444·c 1,447). **닫힘 p ≤ p < 마지막 p 구간의 A·B `0x4662DE` = 0(3/3).** 마지막 p에 몰린 216건(b·c)은 PS3 복귀 뒤 월드 재그림이다.
  - C(400,380, 메뉴 패널): 메뉴·정착 구간에 `0x4662DE`와 `0x00466E67`(guard 1)이 매 present, 닫힘 present 자체는 tid 288 배경 쓰기뿐(lap1119 관찰 3과 같다).
  - k 레코드 dropped 0(3/3).
- **ddraw 호출 표(b·c 마지막 `{"t":"q"}`):** distinct 2·overflow 0. #0 BltFast caller `0x00493CCB` 대상 `0x01E6D560` ← 원본 `0x01E6D8F0`, src rect 없음(has 0), flags 16, count = 3200(b)/3450(c) = PS23 present 수. #1 BltFast caller `0x00469379` primary ← `0x01E6D560` [0,0,800,600]. work 표와 같다.
- **불일치 0.** lap1119 판정 `PM1-0 PASS`, `PM1-1 PASS(귀속) 3/3`, 가설 문장 부분 반증(전환 전용 writer 없음, 매 present 전면 배경 복원 + 저장 창 패널 복사 중단), (ii) 조기 return 배제를 수용한다. `0x01E6D8F0`을 채우는 writer는 UNKNOWN 그대로다(수리에 필요 없음, §2).

## 2. 수리 방식 결정 — R-a(일시정지 진입 스냅샷 복원) 채택

원인 모형(코드 확인 `g1_mirror2x.c` 1813~1831): present 루프는 `g_covered[p] && g_expected_snapshot[p] == pixel`일 때만 `g_mirror` HD를 쓰고, 아니면 stale로 세고 `g_covered[p] = 0`. 일시정지 동안 매 present 맨 앞에서 `0x493CC8` BltFast가 화면 버퍼를 원본 surface `0x01E6D8F0`(정지된 월드 화면)로 되돌린다. 메뉴 구간에서는 띠 픽셀 = 월드 값 = expected라 HD가 유지된다(lap1117 pause 100%). 저장 창이 열리면 패널 복사 미러가 띠의 expected·`g_mirror`를 저장 창 패널 값으로 덮어 월드 HD가 사라진다. 닫히면 띠 픽셀이 다시 월드 값이 되지만 expected는 패널 값이라 stale → covered 해제 → 일시정지 동안 월드 재그림이 없어 nearest로 고정된다.

- **R-a 채택:** PS23 진입 present에서 그때 유효한 HD 상태(`covered && expected == pixel`인 픽셀의 expected·`g_mirror` 2×2)를 별도 버퍼에 스냅샷하고, PS23 동안 present 루프에서 "기존 경로로는 HD가 아닌 픽셀"(covered 0 또는 expected ≠ pixel) 중 스냅샷이 유효하고 스냅샷 expected == pixel이면 스냅샷에서 `g_expected_snapshot`·`g_covered`·`g_mirror` 2×2를 복원하고 HD로 출력한다. PS23을 벗어나는 첫 present에서 스냅샷을 무효화한다.
- 채택 근거: (1) writer와 무관 — 띠를 덮은 것이 저장 창이든 다른 PS23 하위 창(backlog 옵션 하위 창)이든 배경이 정지 화면으로 돌아오면 복원된다. (2) 기존 미러 경로가 우선 — 이미 HD인 픽셀은 건드리지 않으므로 메뉴·저장 창 패널 HD에 영향 없음. (3) 적용 범위가 PS23 한 상태로 한정돼 PS3 월드·스크롤 경로는 바이트 동작 불변. (4) `0x01E6D8F0` writer 귀속이 필요 없다.
- **R-b 기각:** 패널 복사(`0x466280` → `transfer_block_copy_to_screen`) 경로마다 사각형별 save-under 장부가 필요하고, 다른 writer가 덮은 하위 창에는 듣지 않으며, 같은 픽셀이 여러 번 덮일 때 복원 순서 문제가 생긴다.
- 알려진 한계(공개, PASS 판정에서 제외): 저장 창 패널 값 == 월드 값인 약 1,840 px(lap1118)은 닫힌 뒤에도 기존 경로로 패널 HD가 남는다(값은 같고 2×2 세부만 다름). 저장 창 열림 1 present 일시 stale 약 51.6k는 별개(미러 밖 열림 그리기) — 이번 수리 대상 아님, 비회귀만 본다. 거짓 복원 위험: 미러 밖 writer가 우연히 스냅샷 값과 같은 값을 쓴 픽셀에 월드 HD 2×2가 나올 수 있다(같은 논리 색, 세부만 다름). 이를 계수로 공개한다.

## 3. 다음 work 사전등록(Sonnet) — H-PM2: PS23 정지 화면 스냅샷 복원

- **가설 H-PM2:** R-a를 넣으면 저장 창 닫힘 뒤 띠 약 44k px가 같은 present에 월드 HD로 복원되고, 정착 PS23 HD가 90.77% → ≥98.6%가 된다. PS3 경로는 변화 없다.
- **PM2-0 구현(TDD):** `tools/inmm_stub/g1_mirror2x.c`(필요하면 `.h`).
  - 버퍼 3개(800×600 valid·expected, 1600×1200 HD)를 기존 `g_mirror`와 같은 방식으로 할당(실패 시 기능 끔, 기존 동작 유지).
  - `g1_mirror2x_copy_present`에서 `G1_PROGRAM_STATE_VA`를 present마다 읽어(현재 stale mask 설정 때만 읽음) 직전 present 상태와 비교: 23이 아닌 상태 → 23 전이 present에서 루프가 픽셀을 처리할 때 그 present의 기존 판정이 HD인 픽셀을 스냅샷(valid=1·expected=pixel·2×2 복사), 23 → 다른 상태 전이에서 valid 전부 0. 스냅샷은 루프 안 같은 순회에서 만들거나 루프 앞에서 만들되, 기준은 "그 present 시점 기존 판정 HD"로 한다.
  - 복원 판정은 순수 헬퍼로 분리(예: `g1_pause_restore_pick(covered, expected, pixel, snap_valid, snap_expected)` → 기존 HD / 복원 / nearest)하고 RED→GREEN 단위 테스트: 기존 HD 우선, 스냅샷 일치 복원, 스냅샷 불일치 nearest, valid 0 nearest, PS23 밖 무효.
  - trace `mirror2x_present`에 `pause_snapshot_pixels`(진입 present 스냅샷 수)·`pause_restore_pixels`(이번 present 복원 수)·`pause_restore_total` 추가. 기존 필드 의미 불변.
  - env로 끄는 스위치 `SYW2_G1_PAUSE_SNAPSHOT=0`(기본 켜짐) — 비회귀 대조용.
- **PM2-1 격리 run 2회:** `--hd-source scale2x --new-game-path --new-game-start --new-game-act --new-game-menu`(act 뒤 메뉴, PS3 비회귀 동시 확인). 옵션 조합이 안 되면 하네스 결함으로 고쳐 다시 실행한다.
  - **PASS(2/2):** 닫힘 present HD ≥98.6%(직전 79.94~80.08%)·정착 PS23 HD 최소 ≥98.6%·`pause_restore_pixels` 닫힘 present 40k~46k·PS3 복귀 뒤 HD 100% 유지·PS3(act) 구간 HD/stale이 lap1115 NG5 수준(PS3 창 HD min ≥99.9%)·V1/안전 7종/fallback/hresult 0·dropped 0·scale2x PASS·경과 p95 증가 ≤2ms. 저장 창 열림 1 present HD는 ≥89%(비회귀만, 기존 89.11~89.18%).
  - 거짓 복원 공개: 저장 창 열림 구간·메뉴 구간의 `pause_restore_pixels` 합계를 적는다(0 기대, 0이 아니면 위치를 캡처로 확인해 기록, 판정은 middle).
  - 캡처: `pause_return.png`에서 띠 x240..313·x486..559 × y100..409의 2×2 균일 비율(lap1118 방식, 수리 전 96.0~96.2%)이 ≤10%인지 적는다.
  - **FAIL:** 위 수치 중 하나라도 2/2에서 미달. 원인이 구현·하네스 결함이면 같은 회차에 고쳐 재실행(구현 우선). 실패 가설 2회 또는 60분이면 BLOCKED로 근거와 함께 넘긴다.
- 공통: source 변경 뒤 lint·typecheck → 기록 freeze → `make check` 1회. 디스크 ≥20GiB(현재 162GiB 여유) 확인, 끝나면 game 사본 삭제. 원본/참고 쓰기 금지, 커밋 금지, 시험판 재스테이징 없음(사용자 시험 lap1104 판본 유지). 사용자 G1 시험 결과가 들어오면 그것이 최우선이다.

backlog: lap1118 §3 커서 영역 −308/−101, 저장 창 열림 1 present 일시 stale 51.6k(미러 밖 열림 그리기), `0x01E6D8F0` writer UNKNOWN. 나머지는 STATUS backlog 그대로.

## 4. 검사

- 기록 freeze 뒤 `checks/safety.sh check`·`checks/context_limits.py`. 결과는 STATUS에만 쓴다.
- 전체 `make check` SKIP: 이번 변경은 문서뿐이고 하네스·테스트·C source는 lap1119 full PASS(1742) 때와 같다(§ 머리 source 동일성).

## 다음 한 가지

work(Sonnet): §3 H-PM2 — PM2-0 R-a 스냅샷 복원 구현(TDD) → PM2-1 격리 2회(act+menu) → 수치 PASS/FAIL, middle 검수 요청.
