# lap332 middle — lap331 R1 실행 결과 독립 검수

2026-09-12 / Claude Code claude-opus-5 / high / 중간계획·컨펌(middle).
게임 코드 수정 0, 게임 실행 0, 입력 주입 0, 메모리 쓰기 0, 재클릭 0, PNG 0.
이 문서는 middle 기술 판정이며 사용자 마일스톤 승인도 제품 G1 증거도 아니다. 현재 큐는 docs/STATUS.md만 따른다.

입력: `G1_R1_MIDDLE_REPAIR_ACCEPTANCE_LAP330.md` §4 발효 조건, `G1_R1_MIDDLE_ENVELOPE_LAP326.md` §1~§5,
`docs/history/laps/20260912_lap331_work_r1_runtime.md`, AGENTS/PROMPT 안전 규칙, APPROVALS 2026-09-12 01:03.
증거: 본 lap 신규 probe `docs/history/laps/probes/20260912_lap332_middle_lap331_r1_artifact_probe.py`
(`e8dc8c7544a30572f37564e91218b9c6766f102077b3797af63b4915a1f9c367`), rc0 · `failures=[]` ·
stdout SHA256 `5efe92a02f3b6a42a8dee5bdf98a7e00e5d941c7549fb72a7a96bf956cc31afc`(연속 2회 byte-identical).
probe는 이전 lap probe를 **import하지 않고** run 자신의 게임 복사본 PE 바이트·스프라이트 헤더·보존된
artifact만 1차 출처로 읽는다. 재실행·입력·쓰기는 하지 않는다.

## 판정: lap331 R1 관측 **ACCEPT**. R1 연구 레인 종결. 제품 승격은 없음

`REACHED_CHANGED`는 lap330 §4가 요구한 모든 조건을 만족한 단일 관측으로 성립한다.
동시에 lap326 §1의 디스패처 서술에 **정정 1건**(수치 영향 0)이 있고, lap331 기록이 공개하지 않은
관측 사실 **2건**을 아래에 남긴다.

| 검수 항목 (lap330 §4) | 판정 | 근거 |
|---|---|---|
| 검수 SHA 그대로 실행 | **PASS** | §1 |
| 정확히 1회·≤90s·1600x1200x24·새 prefix | **PASS** | §1 |
| 네 모드 중 어느 것인가 | **PASS — REACHED_CHANGED** | §2 |
| `pending_state` 시계열 | **PASS (정정 C1 동반)** | §2·§3 |
| `origin_tag` / `ps_word` / `ps_dword` | **PASS** | §2·§4 |
| cleanup · elapsed | **PASS** | §1 |
| 제품 G1 / Stage B 승격 | **없음 — 변동 없음** | §5 |

## 1. 무결성·봉투 준수 — 1차 출처로 재확인

- 보존 artifact 3종 SHA가 lap331 기록과 **일치**: `r1_load_origin.json` `76ce7788…bfa442cf`,
  log `277fe226…072f2453`, manifest `4109704a…d18096a2`.
- 실행 SHA == lap330이 검수한 SHA: `tools/runtime_env.py` `997ff15b…cc46eed`,
  `tests/test_lap326_r1_load_origin.py` `81acc11e…cac72`. artifact provenance가 같은 harness SHA를 자칭한다.
- **정확히 1회**: `local/runtime/*/output/r1_load_origin.json` 전수 조회 결과 **1건**.
  하네스는 `.r1-load-origin.lock` + `r1_load_origin.json` 존재 검사 + 새 prefix 요구로 2회차를 구조적으로 막는다.
  PNG **0건**. 즉 "무변경 blind 재시도 금지"는 문서 약속이 아니라 파일 상태로 확인된다.
- run 게임 EXE SHA = `b56986e0…c08a8ac`(핀). `diagnostic_bridge_overridden=false`,
  fixture `synthetic/memory_writes/resource_grant` 모두 false.
- 봉투: screen `1600x1200x24`, timeout 90.0, elapsed **4.278s** ≤ timeout, root 1600×1200 · content child 800×600,
  클릭 root `(296,505)` == `content_crop + client`(lap326 §3 변환), focus/inject exit 0, input count **1**.
- cleanup: owned launcher·Xvfb 종료, `prefix_processes_after=[]`, `global_kill_used=false`, error null.

## 2. 모드 판정 — `REACHED_CHANGED`가 맞다

- `status=OBSERVED`, `classification=REACHED_CHANGED`, `error`/`reason` 필드 **없음**.
  lap330 N7(클릭 후 `evidence['post']` 대입 전 예외가 `TIMEOUT`으로 기록되는 삼항)은 예외가 없어 **미발동**.
- (P1) 사전조건 충족: PS9 시점 origin `(0,0,0)` — BSS 0 예측이 실측으로 확인됐다.
- 선언 대기 상태 `[9,35]`(N6 해소 형태 유지), `ps_word`/`ps_dword` 모두 pre 9 · post 35.
- 표본 12건 전부 WORD read와 별도 DWORD read가 **일치**(상위 워드 0) ⇒ 이 창에서 찢김 징후 0.
  elapsed 단조 증가. 폴링 간격은 0.25s이고 클릭 직후 1회만 0.124s다(클릭 구간에 새 스테이지가 시작되기 때문).
- `pending_state`는 **0 → 34**로 한 번만 바뀌고 두 값이 섞이지 않는다. 마지막 표본은 PS=35 · pending=34.
  lap326 §3이 `0xB92CC0`을 "다음 상태 요청 WORD"로 재정의한 대로, **클릭이 요청한 다음 상태가 34**이고
  그 34번 arm이 origin을 쓰고 PS:=35를 놓는다. 즉 요청→핸들러→산출물 순서가 시계열로도 일관된다.

## 3. 정정 C1 (수치 영향 0) — 디스패처는 35엔트리 테이블이 전부가 아니다

lap326 §1은 디스패처를 `movsx eax,WORD ds:0x4ED818` → `dec eax; cmp eax,0x22; ja default;
jmp [eax*4+0x423738]`로 적었다. 원본 바이트를 다시 읽으면 그 사이에 **선행 사다리**가 있다:

```
0x4233B8  0f bf 05 18 d8 4e 00   movsx eax, WORD PTR ds:0x4ED818
0x4233BF  83 f8 28               cmp  eax, 0x28          ← 40
0x4233C2  0f 8f 57 01 00 00      jg   0x42351F           ← PS>40 전용 사다리 (그 머리는 cmp eax,0x131)
0x4233C8  0f 84 47 01 00 00      je   0x423515           ← PS==40 전용 arm
0x4233CE  48 83 f8 22            dec eax; cmp eax,0x22
0x4233D2  0f 87 f0 fe ff ff      ja   0x4232C8           ← default
0x4233D8  ff 24 85 38 37 42 00   jmp  DWORD PTR [eax*4+0x423738]
```

- **판정식에 대한 영향 0.** 35는 `>0x28`도 `==0x28`도 아니고 `35-1=34 ≤ 0x22`이므로 그대로 테이블
  34번 엔트리(`0x42341B`)로 간다. 테이블 실값 PS9→`0x423407`, PS34→`0x423411`, PS35→`0x42341B`도 재확인했다.
- **그러나 "PS ∈ 1..35"라는 암묵 가정은 틀렸다.** 관측 시계열의 `40 / 150 / 180`은 찢김이나 미매핑 read가
  아니라 **디스패처가 실제로 처리하는 정당한 상태값**이다(`==40` arm, `>40` 사다리). lap326 §3이 이미
  "PS9 핸들러가 PS를 140으로 바꾼다"고 적었던 것과 같은 계열이다.
- 이 정정이 없으면 후속 세션이 같은 시계열을 "read가 불안정하다"는 증거로 잘못 읽는다. C1은 lap324 §2.3
  (E8-only 그래프가 꼬리 `jmp`를 놓친 건)과 **같은 종류의 부분 서술 결함**이며, 같은 방식으로 보존한다.
- **fail-open은 닫히지 않는다.** PS로 가는 레지스터 store 33건은 여전히 값 미상이므로 명제는 계속
  "PS==35를 관측했다"이지 "35를 쓴 명령은 `0x4248E5`뿐이다"가 아니다. C1은 이 fail-open을 넓히지도 좁히지도 않는다.

## 4. 산출물 — 후보 A와 tag가 동시에 맞았다

- run 자신의 `yfnt/saveloadtitle.spr`(`7d154cdb…3c08a5c5`) 헤더를 직접 파싱: `[9, 320, 310, 1]`.
  중심식 재계산 → **A `(240,145)`** = `((800-320)/2, (600-310)/2)`, B `(160,85)` = 640×480판. 두 후보는 구별된다.
- 실측 post origin = **`(240,145)`** = A. lap304 R6의 정적 우세(초기 모드 3 → 800×600)가 이 fixture에서
  실측으로 확인됐다. 단, **이 run의 content는 실제로 800×600**이므로 이는 원본 동작의 확인이지
  1600×1200 후보에 대한 진술이 아니다.
- `origin_tag` 0 → **8**. `0x493C41`의 `push 8` 즉시값과 바이트 단위로 일치하며, 형제 호출자
  `0x493D6B`(`push 0x3E8`, tag 1000)를 **배제**한다. 즉 산출물은 PS34 → `0x4248E0` → `0x4A2FF0` →
  꼬리 `jmp 0x493C40` → `0x4D6A00` 경로에서 왔다. 사슬 7개 지점 바이트와 rel32 3개를 본 lap이 재유도했다.
- lap326 §2의 순서 논거(세 store가 PS:=35보다 **먼저** 완료)는 그대로 성립하고, 게이트된 1회 read라
  x/y 찢김 창(23바이트 직선 코드)은 열리지 않는다.

## 5. 남는 한계 — 이 판정이 아닌 것

- **n=1.** 재현성·결정성은 미측정이며 재클릭은 계속 **금지**다. 1회 관측은 결정성 주장이 아니다.
- **원본 baseline이지 후보 증거가 아니다.** root 1600×1200 안의 content 800×600은 단순 확대 경로이며,
  G1이 요구하는 "1600×1200 구성"에서 origin이 어떻게 되는지는 **여전히 미관측**이다. Stage B 실행 0.
- 배분 40/20/15/15는 실측 4.278s와 대조해도 **여전히 가정**이다(도달까지 3.8s는 단일 표본).
- `manifest.runtime_config`는 prepare 시점 스모크(`screen 1024x768x24`, `input (184,560)`)를 기술하며
  **R1 run을 기술하지 않는다**. 판정은 artifact 자체 필드로만 했다. 수치 영향 0, 오독 위험만 있다(N9).
- lap331 기록·STATUS는 "PS 9→35"만 적고 out-of-table 표본 3건을 공개하지 않았다. 본 lap이 공개한다(N8).
- S1 종결 REJECT, R17/R31 금지, R29 범위 승인 거부, R30 M11 생존, R6-B-R2 미결, WM_CLOSE 결함,
  offline 8건 주차, G3 저장 포맷 블로커, N1~N7 · W2 · W3 재pin 대기, (W) `player_offsets.md` 정정 대기는 전부 유효하다.
- G2~G4 증거는 **0**이다. `make check` 368 passed와 probe rc0은 계획 승인도 제품 검증도 아니다.

## 6. 다음 방향은 middle 권한 밖 — Astra로 올린다

R1 연구 레인은 이 판정으로 닫힌다. 그 다음은 "사용자 승인된 Stage B(원본/1600×1200 후보 실제 비교)를
재개할 것인가, 아니면 R1과 같은 읽기 전용 관측을 후보 쪽에 먼저 적용할 것인가"의 **상위 방향 선택**이고,
같이 묶인 W3 재pin과 40/20/15/15 재평가도 middle/work 단독 금지 항목이다. 따라서 `loop/ESCALATE_SOL`로
올리고, 이 lap은 구현이나 Stage B 실행을 시작하지 않는다.
