# lap326 middle — R1 실행 봉투 심사: 도달 판정식과 표본 일관성

2026-09-12 / Claude Code claude-opus-5 / high / 중간계획·컨펌. 게임 구현·실행 0, 게임 코드 수정 0.
이 문서는 middle 기술 판정이며 사용자 마일스톤 승인도 제품 증거도 아니다. 현재 큐는 docs/STATUS.md만 따른다.

입력: `G1_R1_SCOPE_DIRECTION_LAP325.md`(Astra 조건부 허용), `G1_MIDDLE_OBSERVATION_PATH_LAP324.md` §2·§5,
`loop/ESCALATE_SOL`(lap325, 본 lap이 소비), AGENTS/PROMPT 안전 규칙, APPROVALS 2026-09-12 01:03.
증거: 본 lap 신규 probe `docs/history/laps/probes/20260912_lap326_middle_r1_reach_ordering_probe.py`
(`70c9cc17db880b54802db7d7d8af565df3e52e5fa73b247bc9a58e1675f17bd8`),
report stdout SHA `1bff28d40b55e1488d3c071445cabb9cf280389cabb49b0a1126c56110cf0785`
(연속 2회 byte-identical, rc0, failures=[]). probe는 이전 lap probe를 import하지 않고 원본 PE 바이트에서
섹션·절대 operand·rel32 제어이동·명령 바이트를 직접 재유도한다. 원본 SHA는 `b56986e0…c08a8ac`로 불변.

## 판정: R1 봉투 **ACCEPT**. 두 미결 항목은 바이트 근거로 해소됐고, 실행 전 조건은 §6에 남는다

lap325가 middle로 되돌린 두 항목(도달 관측 판정식, x/y 표본 일관성)은 이번 lap의 정적 재유도로
**둘 다 해소된다**. 해소 방식은 새 계측 기구를 만드는 것이 아니라, 원본이 이미 가진 **상태 전이 순서**를
판정식의 근거로 쓰는 것이다. 따라서 §14.7이 요구했던 exact-site 기구도, lap325가 임시로 상정했던
"안정 반복 관측 N회" 휴리스틱도 **필요하지 않다**.

| lap325 인계 항목 | 판정 | 근거 |
|---|---|---|
| 1. 도달 관측 판정식 | **해소 — ACCEPT** | §1 (PS WORD@`0x4ED818`==35, 원본 디스패처·점프테이블·유일 즉시 writer) |
| 2. x/y 표본 일관성 | **해소 — ACCEPT** | §2 (두 store는 PS:=35 **이전에** 완료. 게이트된 1회 read에 찢김 없음) |
| 좌표계·변환 근거 | **ACCEPT** | §3 (기존 PASS 입력 `(184,560)`과 동일 좌표계·동일 변환) |
| 4실패모드·deadline·소유 종료 | **ACCEPT-WITH-CONDITION** | §4 (lap324 §4 승계 + 신규 진단 필드) |
| evidence 분리·PS 대기 선언(N6)·N4 | **조건부 — work 구현 계약** | §5 |
| 즉시 실행 | **불가** | §6. 이 문서는 실행 허가가 아니다 |

## 1. 도달 판정식 — PS(WORD@`0x4ED818`) == 35. 순환 아님

lap325가 금지한 순환(=origin 값으로 도달을 정의)을 피하려면, origin 전역과 **다른** 객체를 읽어야 한다.
원본은 그런 객체를 이미 가지고 있고, 이번 lap이 바이트로 재유도했다:

- 디스패처 `0x4233B8`: `0f bf 05 18 d8 4e 00` = `movsx eax, WORD PTR ds:0x4ED818`.
  → PS는 **WORD**이며 부호 확장되어 분기에 쓰인다(폭 재확인, 추정 아님).
- 그 아래 `dec eax; cmp eax,0x22; ja <default>; jmp DWORD PTR [eax*4+0x423738]` →
  `0x423738`의 **35엔트리 점프 테이블**, 인덱스 = PS-1. 테이블 실값: PS=9→`0x423407`,
  **PS=34→`0x423411`**, PS=35→`0x42341B`.
- `0x423411`: `e8 ca 14 00 00` = `call 0x4248E0`. 즉 `0x4248E0`은 **PS=34 핸들러**다.
- `0x4248E0`: `call 0x4A2FF0` → `0x4248E5`: `66 c7 05 18 d8 4e 00 23 00`
  (`mov WORD PTR ds:0x4ED818, 35`) → `ret`.
- `.text` 전수 절대 operand 스캔: PS에 대한 **즉시(imm16) store는 71건이고 값 35는 정확히 1건**
  (`0x4248E5`). PS=35는 `player_offsets.md`의 상태표에서 **불러오기**다.

판정식 `PS == 35`는 `ds:0x1088B5C/5E` 값을 전혀 참조하지 않으므로 **순환이 아니다**.
그리고 PS=35의 의미는 상태표 문구가 아니라 **디스패처 테이블의 35번 엔트리가 부르는 핸들러가
바로 origin을 쓰는 다이얼로그 서브트리**라는 사실로 고정된다(§2).

**fail-open(명시):** PS로 가는 **레지스터 store 33건**(`66 a3`/`66 89 xx`)은 정적으로 값이 미상이므로
"35를 쓸 수 있는 명령은 하나뿐"이라고는 **쓰지 않는다**. 우리가 쓰는 명제는 "PS==35를 관측했다"이며
그 의미는 아래 호출 사슬이 준다.

## 2. 표본 일관성 — 찢김은 "안정 N회"가 아니라 **순서**로 닫힌다

lap325 항목 2의 전제는 "x와 y가 서로 다른 두 store이므로 인접 4바이트 read가 중간 상태를 볼 수 있다"였다.
그 위험은 **읽는 시점을 PS==35로 게이트하면 존재하지 않는다.** 이번 lap이 재유도한 사슬은 전부
무조건(conditional 아님) 간선이다:

```
PS=34 arm 0x423411  call 0x4248E0                    (e8 ca 14 00 00)
  0x4248E0          call 0x4A2FF0                    (e8 0b e7 07 00)
    0x4A2FF0        call 0x495110                    (e8 1b 21 ff ff)
    0x4A2FF5        jmp  0x493C40   ← 꼬리 점프        (e9 46 0c ff ff)
      0x493C40      push 8                           (6a 08)
      0x493C42      call 0x4D6A00                    (e8 b9 2d 04 00)
        0x4D6A00    mov ecx,0x1086278                (b9 78 62 08 01)
        0x4D6A05    call 0x4D60B0                    (e8 a6 f6 ff ff)
          0x4D632A  mov WORD ds:0x1088B5C,cx   ← x   (66 89 0d 5c 8b 08 01)
          0x4D6348  mov WORD ds:0x1088B5E,di   ← y   (66 89 3d 5e 8b 08 01)
        0x4D6A23    mov ds:0x1088B60,ax        ← tag (66 a3 60 8b 08 01)
  0x4248E5          mov WORD ds:0x4ED818,35    ← PS  (66 c7 05 18 d8 4e 00 23 00)
```

- `0x4A2FF0`의 유일한 참조자는 `0x4248E0`(call 1건)이고, `0x493C40`의 유일한 참조자는
  `0x4A2FF5`의 꼬리 `jmp` 1건이다. lap324의 E8-only 그래프는 이 꼬리 점프를 놓쳤고,
  그래서 "origin은 PS35 핸들러 안에서 쓰인다"로 보였다. **이번 lap이 그 누락을 정정한다.**
- 따라서 **PS가 35가 되는 순간에는 x·y·tag 세 WORD가 이미 전부 기록돼 있다.**
  `PS==35`를 본 뒤의 read는 세 store 모두의 **뒤**에 있으므로, 이 진입 경로에서 온
  x/y 찢김 표본은 발생할 수 없다. 반복 관측 횟수·간격을 "실행 전 가정"으로 정할 필요가 없어진다.
- x·y 두 store 사이 간격은 `0x4D632A+7 ~ 0x4D6348`의 **23바이트 직선 코드**
  (`8bf88b86f4100000992bc2d1ffd1f82bf80fbfc183c014`)다. 이 창은 PS 게이트 없이 폴링할 때만 의미가 있다.
- 세 전역의 직접 store 인구조사(절대 operand): `0x1088B5C` 출현 10 / 직접 store **1**(`0x4D632A`),
  `0x1088B5E` 출현 11 / 직접 store **1**(`0x4D6348`), `0x1088B60` 출현 3 / 직접 store **2**
  (`0x4D6A23`, `0x4D6A2F` — 둘 다 `0x4D6A00` 내부, 성공/실패 분기 각 1). lap324 수치와 일치하며
  이번 lap이 독립 재유도했다(과거 결과 승격 아님).
- 세 전역은 `.data` raw 끝(`0x4F9000`)을 넘으므로 **BSS, 로드 시 0**이다. 따라서 fresh run의
  PS9 시점 pre는 `(0,0)`이어야 하며, 그렇지 않으면 그 자체가 blocker다(§5 (P1)).

**tag(`0x1088B60`)의 쓰임:** `0x4D6A00`의 직접 호출자는 2개이고 인자가 다르다 —
`0x493C42`는 `push 8`, `0x493D6B`는 `push 0x3E8`(`68 e8 03 00 00` @ `0x493D66`). 두 분기 모두
`0x1088B60`에 그 인자를 쓴다. 그래서 **`tag == 8`은 이번 진입 경로(PS34→`0x493C40`)를 구별하는
2차 표지**다. 판정의 필요조건이 아니라 교차검증 필드로만 쓴다.

**여전히 fail-open:** 계산/간접 writer는 절대 operand 스캔으로 배제되지 않는다(N2 계열).
`0x4D60B0`이 store 전에 조기 반환할 가능성도 배제되지 않으며, 그 경우 post==pre이고 **UNKNOWN**이다.

## 3. 좌표계 — 새 근거가 필요 없다. 기존 PASS 입력과 동일 변환

`tools/runtime_env.py:3413-3421`의 이미 PASS한 타이틀 입력이 변환을 고정한다:
`content_crop = (content_info.x, content_info.y, 800, 600)`이고 클릭 root 좌표는
`(content_crop[0] + client_x, content_crop[1] + client_y)`다. 실제 PASS 사례는
client `(184,560)` → PS9→PS7이며, 그 앞에 `content_info`가 정확히 800×600임을,
root가 정확히 1600×1200임을 강제하는 검사가 있다(`3357-3362`).
따라서 `(296,505)`는 **같은 client 800×600 좌표계의 같은 변환**으로 보내면 되고,
새 좌표계 근거를 만들 필요가 없다. 스케일은 `(1.0, 1.0)`로 기존과 동일하다.

**클릭이 '불러오기'를 고른다는 정적 증명은 없다 — 그것이 이 실험이 측정하는 것이다.**
다만 진단은 가능하다: PS9 핸들러 `0x4248C0`은 `call 0x494BC0` 결과 ax를
`0x4248CC`에서 `ds:0xB92CC0`(WORD)에 쓰고 PS를 140(`0x8C`)으로 바꾼다. `0xB92CC0`은
`0x4257A7`/`0x4257C2` 등에서 `0x140`/`0x8`을 받는 **다음 상태 요청 WORD**다
(`player_offsets.md`가 "직전 상태 [추정] byte"라 적은 것과 다르다 — 폭은 WORD, 방향은 '다음'.
문서 정정은 근거와 함께 §5 (W) 항목으로 넘긴다). 그러므로 클릭 후 `0xB92CC0`을 함께 기록하면
미도달 시에도 "클릭이 어떤 메뉴 항목을 요청했는가"를 구분할 수 있다.

## 4. 예산·실패보존 — lap324 §4 승계, 진단 필드 3개 추가

lap324 §4의 기구(≤90초 강제, `1600x1200x24` 고정, run별 디렉터리 보존, `prepare_failure.json`,
`record_timeout`의 원인/관측 필드)와 배분 가정(준비·시작→PS9 ≤40s, 클릭→PS35 ≤20s, 관측·수집 ≤15s,
종료 ≤15s, 합 ≤90s)을 그대로 승계한다. **이 배분은 측정치가 아니라 설계 가정이며 첫 run이 실측해
재평가한다.** 자동 연장·무변경 blind 재시도 금지. 준비 시간에는 격리 사본 복사와 prefix 생성이
포함되며 숨기지 않는다. 종료 예산(15s)은 단일 deadline이 침범하지 않는다.

4실패모드는 lap324 그대로이되, 각 모드에서 아래 세 필드를 **추가로** 남긴다(§3의 진단 가치):
`pending_state`(WORD@`0xB92CC0` 시계열), `origin_tag`(WORD@`0x1088B60`), `ps_word`/`ps_dword` 쌍.

| 모드 | 구분 조건 | 새로 얻는 진단 |
|---|---|---|
| ① 미도달 | 예산 내 `ps==35` 없음 | `pending_state`가 34면 클릭은 맞고 전이가 느린 것, 7/기타면 클릭이 다른 항목을 눌렀다 |
| ② 도달·미변화 | `ps==35`인데 post==pre==(0,0) | `0x4D60B0` 조기 반환 또는 간접 writer → UNKNOWN |
| ③ timeout | 단일 deadline 소진 | 어느 stage에서 소진했는지 `record_timeout` 필드로 |
| ④ 수집 실패 | read 오류/짧은 read | errno·요청 길이·실제 길이·site |

## 5. work 구현 계약 (Luna 또는 Sonnet5 / high). 최소 변경, 제품 경로 무간섭

- **(F1) 파일:** `tools/runtime_env.py`에 연구 전용 서브커맨드 **`g1-r1-load-origin` 1개**를 추가한다.
  기존 `{prepare,check,smoke,g1-baseline,g1-presentation-trace}` 경로와 그 PASS 판정에 **손대지 않는다.**
- **(F2) 읽기:** 원시 read는 기존 `patches/population/runtime_driver.read`(단일 `process_vm_readv`)만 쓴다.
  `process_vm_writev`/`ptrace`/`int3`/`winedbg`/`gdb`는 **0회**를 유지한다(추가 시 금지 위반).
- **(F3) 표본 형태:** origin 표본은 **`read(pid, 0x1088B5C, 6)` 단일 호출**로 x·y·tag를 한 번에 받는다.
  분리된 2회 read 금지. PS는 **`read(pid, 0x4ED818, 2)`를 `<h`로** 해석하고, 비교용으로 4바이트 값도
  같이 기록한다(lap17 폭 규칙; 기존 `runtime_driver.state`의 4바이트 PS 읽기는 **바꾸지 않는다**).
- **(F4) PS 대기 선언(N6 해소):** 모듈 상수 `G1_R1_WAIT_PS_STATES = (9, 35)`를 두고, 대기 술어가
  그 상수만 참조하게 한다. 형태 무관 가드가 이 집합을 검사할 수 있어야 하며, 정규식이 집합 소속
  형태에 fail-open 되지 않게 한다. 대기는 기존 `_wait_state`의 관측 필드(poll 수, read 오류 비율,
  timeout 원인)를 재사용한다. 무거운 `state(detailed=True)` 대신 경량 reader를 쓴다.
- **(F5) evidence 분리:** 산출물은 **연구 전용 파일** `r1_load_origin.json` 하나이며
  `evidence["inputs"]`/`_g1_flush_input_stage` 계열 제품 소비 경로에 **편입하지 않는다**.
  기존 `PS5→PS3` PASS 계보에 끼워 넣지 않는다.
- **(F6) N4 선행조건:** 이 evidence 스키마나 검사 스크립트가 lap319/320 probe의 `main()` **선평가**
  형태(존재하지 않는 행 조회가 KeyError로 FAIL JSON 자체를 막는 형태)를 재사용하면
  §14.8 단서에 따라 **N4 수리가 선행 조건**이다. 재사용하지 않으면 발동하지 않는다.
  (본 lap probe는 이 형태를 쓰지 않는다.)
- **(F7) 합성 검사:** 새 `tests/test_lap326_r1_load_origin.py`에 실행 없이 도는 합성 검사 4종 —
  ①미도달 ②도달·미변화 ③timeout ④짧은 read/수집 실패 — 을 두고, 각각이 PASS가 아니라
  선언된 실패 레코드를 남기는지 본다. `test.skip`/`.only`/스텁 금지.
- **(F8) 금지 유지:** Stage B, 원본/후보 쌍, PNG 비교, W3 재pin, baseline/golden 갱신,
  INT3·원본 실행 이미지 변경, 게임 데이터/EXE 커밋, 재클릭(입력 정확히 1회), 다른 세션 정리.
- **(P1) 실행 전 예측(사전 등록):** fresh run의 PS9 시점 pre는 `(x,y,tag)==(0,0,0)`이어야 한다.
  아니면 BSS 가정이나 진입 경로 가정이 틀린 것이므로 **blocker**로 보고한다.
- **(W) 문서 정정 대기:** `analysis/memory_maps/player_offsets.md`의 `0x00B92CC0`
  "직전 프로그램 상태 (추정) byte" 행은 §3 근거상 **WORD·다음 상태 요청**이다.
  수치 영향 0이며 이번 R1 범위 밖이므로 별도 카드로 넘긴다. 지금 고쳐 쓰지 않는다.

## 6. 이 판정이 실행 허가가 아닌 이유

Astra 봉투의 발효 조건은 `middle 봉투 수용 + work 구현 + 필수 검사 통과 + 새 middle의 실행 전 독립 검수`다.
본 문서는 그중 **첫 번째**만 충족한다. 남은 순서: work가 §5를 구현하고 `make check`/합성 검사를 통과시킨 뒤,
**다른 새 middle 세션**이 구현을 독립 검수해야 1회 측정이 발효한다. 이번 lap의 실행 예산은 여전히 **0**이다.

## 7. 이 판정이 아닌 것

제품 G1 합격, Stage B 허가, runtime 예산 승인, 클릭 결과 승인, 마일스톤 종료/이동이 **아니다**.
후보 A `(240,145)`와 B `(160,85)`는 여전히 정적 후보다(이번 lap이 `(800-320)/2,(600-310)/2` 및
`(640-320)/2,(480-310)/2`로 산술을 재유도했을 뿐이다). `(296,505)` 클릭 결과는 여전히 미관측이다.
S1 종결 REJECT, R17/R31 금지, R29 범위 승인 거부, R30 M11 생존, R6-B-R2 미결, WM_CLOSE 결함,
offline 8건 주차, G3 저장 포맷 블로커, N1~N3·N5·W2·W3는 전부 이전 판정 그대로 유효하다.
`make check` 통과와 probe rc0은 계획 승인도 제품 검증도 아니다.
