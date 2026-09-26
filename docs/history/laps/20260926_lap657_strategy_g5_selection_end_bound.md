# 2026-09-26 | lap 657 | 목표 G5 — strategy 49 경계 원인 특정

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`(세션 표기 Opus 5.5) / strategy(03:32 운영자 위임 "strategy가 원본 디스어셈블로 원인을 특정") / 기본. 게임 코드·패치·테스트·바이너리 수정 없음.
- 가설 / 사용자 관찰: lap653~655 선택 `49/55`(항상 slot1141..1147 누락). 03:32 운영자 후보는 hit-test 셀 순서 또는 dedupe 워드 혼합. 판정: **둘 다 아님. 후보 빌더 `END_SITES`의 재배치 끝 주소가 한 칸(4바이트) 짧아 선택 저장소가 49칸만 쓰인다.** `FEASIBLE`.

## 귀속 근거 (재현 가능한 계산)

원본 `b56986e0…` 선택 저장소: count dword `0x00899024`, 항목 `0x00899028`부터 20×4. 루프 끝 상수 `0x00899078` = **항목 시작 `0x00899028` + 0x50** (= count 주소 + 0x54).
원본 전체에서 `0x00899078` 참조는 정확히 14곳(`0x412DD6 0x412E53 0x412EB4 0x4170BF 0x41DD6A 0x41DFB1 0x41F06A 0x445E0D 0x499014 0x499050 0x499579 0x4998CA 0x49ACEE 0x4A4259`)이고 모두 `END_SITES`에 있다. `0x899074/76/7C` 참조는 0.

후보 빌더(`patches/selection/g5_selection_cap50_v1.py:52,307`): `SELECTION_BASE=0x0108C000`(count), 항목 `SELECTION_BASE+4`, 끝 = `SELECTION_BASE + SELECTION_BYTES` = `0x0108C000 + 50*4` = **`0x0108C0C8`**. 항목 시작 기준으로는 `0xC4` = **49칸**. 올바른 끝은 `SELECTION_BASE + ENTRY_BYTES + SELECTION_BYTES` = **`0x0108C0CC`**. 후보 `6f6a4f85…`에서 `0x0108C0C8` 14회, `0x0108C0CC` 0회 확인.

선택 기록 경로(후보 capstone): consumer `FUN_0041DC40` 끝 `0x41E1C9..0x41E1E6`이 hit-test 목록 각 핸들에 `0x40F7D0 → FUN_00412D90`을 호출한다. 그 add 경로 `0x412E3C..0x412E57`은 빈 칸을 `cmp eax,0x0108C0C8; jge 0x412E73`으로 찾으므로 50번째는 **저장되지 않고**, 그래도 `mov byte [ebp],1`(선택 플래그)과 `eax=1`을 반환한다(유령 선택 위험).

수치 대조: 드래그 후보 56(일꾼+55), 순회는 slot 내림차순(1198, 1195→1141; 1196·1197은 비후보).
- hit-test append 상한 `0x0043877A cmp ax,0x32`(count 0..49 허용, lap656 판정과 일치) → 목록 50 = 1198 + 1195..1147, 1141..1146(6기) 제외.
- 저장소 49칸 → 50번째 1147 미저장 → 선택 49, 누락 1141..1147(7기). lap653/654/655 관측과 **완전 일치**하며 fixture 위치·사각형과 무관한 이유도 설명된다.
- 원본 20은 끝 상수가 정확하므로 20/20(lap640 hit-test 반환 20, reader 20).

append helper `FUN_004386E0`(`0x4386E0..0x4387FC`)의 dedupe는 `0x40F540`으로 핸들 dword를 읽어 하위·상위 워드를 각각 비교한다(`0x4387A2`, `0x4387B0`) — 혼합 없음. 비아군/`0x2000` 플래그/`0x40F940` 대상은 목록이 아닌 단일 후보 슬롯에만 쓰인다. 03:32 후보 두 가지는 기각.

## 다음 work 지시 (middle 없이 바로 구현·실행)

1. 빌더 `patches/selection/g5_selection_cap50_v1.py:307`의 치환값을 `SELECTION_BASE + ENTRY_BYTES + SELECTION_BYTES`(=`0x0108C0CC`)로 바꾼다. provenance `selection_end_exclusive`(line 325)도 같은 값으로. 14개 old bytes·길이 불변, 다른 사이트 변경 금지.
2. `patches/selection/test_g5_selection_cap50_v1.py` END_SITES 기대값도 같은 식으로 고치고, 회귀 assert를 추가한다: `end - (SELECTION_BASE + 4) == TARGET_CAPACITY * ENTRY_BYTES` 및 원본 `0x00899078 - 0x00899028 == STOCK_CAPACITY * ENTRY_BYTES`. `end ≤ CONTROL_GROUP_BASE` 확인(0xCC ≤ 0x100).
3. 새 후보 빌드 → SHA를 `tools/g5_candidate_drag_probe.py`에 반영 → lap655와 **동일** fixture/입력(worker slot1198, x39..45/y139..146, drag `(200,170)→(730,445)`)으로 fresh isolated 실행. 이번엔 동일 입력 재실행이 목적에 맞다(변수는 끝 상수 하나).
4. 측정식: PASS = 선택 unique **50**(1198+1195..1147), 누락 정확히 1141..1146(=51번째 이후 제외), 이동 명령 50, crash 없음, 유령 선택 0(slot1141..1146 선택 플래그 미설정 확인 가능하면 기록). FAIL-B1 = 여전히 49 → 끝 상수 반영/사이트 누락을 bytes로 재확인. FAIL-B2 = 선택50·명령<50 → 그때만 `FUN_004AE550` 명령 패커 조사. FAIL-A = crash → EIP/ESP 기록.
5. PASS 뒤: 원본 20 대조(같은 fixture) → `make check` → UI/부대지정/save/load. 사용자 마일스톤 승인은 별도.

- 예상 PASS / FAIL 조건: 이번 strategy 회차 PASS = 원인이 기존 runtime 수치와 정확히 일치하고 단일 변경·측정식이 결정됨. 실행 증거는 다음 work가 만든다.
- 변경 파일 / source fingerprint / 커밋: 이 파일, `analysis/memory_maps/g5_selection_end_bound_lap657.md`, `docs/STATUS.md`, `docs/feedback/INBOX.md`, `docs/history/20260926_lap657_escalate_sol_archive.md`(기존 `loop/ESCALATE_SOL` 97줄·SHA256 `8f759c2f…c928` 전문 보존 후 해제). 제품·패치·테스트·바이너리 0, 커밋 0(LOOP_ALLOW_COMMITS=0).
- 원본 SHA / 후보 SHA / 환경 / fixture: 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(읽기 전용, 불변); 후보 `6f6a4f859be4b2281ec2014e817b7692adf2d04226b0ac14b3ac32ac06f4e091`(lap655 artifact, 읽기만); fixture는 lap655 `probe-result.json` 값. 이번 회차 게임 실행 0.
- 실행 명령 / 로그: `.venv/bin/python` capstone/pefile 디스어셈블(원본 `0x4384B0..0x4387FC`, `0x40F540..0x40F5BC`, `0x40F7D0`; 후보 `0x41DC40..0x41E200`, `0x412DB0..0x412EE0`), 원본·후보 상수 바이트 스캔, lap655 `probe-result.json` 선택 slot 목록 읽기. 산출 파일 없음(stdout).
- 측정값 / 판정: 귀속 계산 PASS(56 후보 − hit-test 제외 6 − 저장 제외 1 = 49, 누락 1141..1147 일치); G5 제품 판정 UNKNOWN(실행 0); 50/51·command50·save/load SKIP.
- 회귀 / 남은 위험: add 경로가 가득 차도 선택 플래그를 세우는 원본 동작은 hit-test 상한(50)과 저장소(50)가 같으면 도달하지 않는다. 명령 패커 20 전제는 현재 명령49가 나오므로 낮음. 제품 코드 없는 회차 연속: lap656·657 = 2(한도 도달) → 다음은 반드시 work 구현·실행.
- 다음 한 가지: 위 1~4를 work가 즉시 구현·실행한다.
