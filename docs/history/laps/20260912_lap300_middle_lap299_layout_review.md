# 2026-09-12 | lap 300 | G1/S1 lap299 정적 레이아웃 + lap296 §4.7.6 가드 독립 검수

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5`/high, 지정 역할 **middle
  (진단·계획·컨펌)**. 게임 코드 hands-on 수정 없음. 제품 판정·마일스톤 승인 없음.
- 가설 / 사용자 관찰: lap299 work가 낸 800×600 슬롯 좌표가 원본 `FUN_004D60B0`에서 **무조건**
  따라 나오는지, 그리고 lap296 §4.7.6 가드 수리가 실제로 fail-closed인지 독립 확인한다.
- 예상 PASS / FAIL 조건: (a) lap299 report가 바이트 동일하게 재현되면 결정성 PASS. (b) 내가
  따로 뜬 objdump에서 lap299가 주장한 상수가 전부 재유도되면 상대 레이아웃 ACCEPT. (c) 함수가
  실제로 읽는 화면 전역의 writer가 전수 열거돼 800×600 하나로 좁혀지면 절대 좌표 ACCEPT,
  두 개 이상이면 REJECT. (d) lap296 가드 mutant가 전부 named failure면 가드 ACCEPT.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  - 신규 `docs/history/laps/probes/20260912_lap300_middle_lap299_layout_review_probe.py`
    SHA `718b1e4e4e99a7597dc470c4b9f980eee48d67e087397701894864bd17ea63cf`.
  - 신규 `logs/lap300/middle_layout_review.json`
    SHA `bcac0a410ca5bc7b3ee9f824beff074e221083083bcb1e2e389d4617764c67b2`.
  - `docs/work/active/G1_RUNTIME_CONTRACT_MIDDLE_LAP284.md` §11 handoff 추가, 본 history,
    `docs/STATUS.md`만 추가 갱신. 원본/참고/EXE·DLL/assets/하네스/comparator/producer/PASS 규칙
    변경 0. 기존 probe·`tools/`·`patches/` 수정 0. 커밋 없음(`LOOP_ALLOW_COMMITS=0`).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 EXE
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; 후보 없음. offline Linux
  `.venv` + `/usr/bin/objdump`; 게임/Wine/Xvfb/Stage B/PNG/runtime 실행 **0**. 활성 플레이어/지도/
  군대 없음. 읽기 전용 fixture 2개: `Syw2plus/yfnt/saveloadtitle.spr` 102,260 B
  `7d154cdb…3c08a5c5` header `[9,320,310,1]`, `Syw2plus/yfnt/SaveLoadBar.spr` 9,780 B
  `d0f5e8d8…541b632f` header `[9,280,24,1]`. 캡처 대조 0.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - `.venv/bin/python docs/history/laps/probes/20260912_lap300_middle_lap299_layout_review_probe.py`
    → exit0, report SHA `bcac0a41…764c67b2`.
  - `.venv/bin/python …20260912_lap299_work_save_load_layout_probe.py` → exit0, stdout SHA
    `8e735a9a7f7b4ddbd1ab249039c568b42b16af8b248f47e64681d05476d2bb0b` = lap299 기록과 동일.
  - `.venv/bin/python …20260912_lap280_middle_s1_crossverify_probe.py` → exit0, `failures=[]`,
    stdout SHA `3d4fe30703a4d3797bd233cb0d8b34026258356807173ec35240e6a86d6a9126` = lap299 기록 동일.
  - `.venv/bin/python …20260912_lap296_middle_lap295_guard_review_probe.py` → exit1, failure
    **1건뿐**(자기 stale pin), `blind_spot_verdict="guarded"`, W2 mutant 2종 `named_failure=true`,
    mutant A/B 전부 exit1 named failure, companions lap279/282/284×2 `matches_record=true`,
    `fresh_run.byte_identical_to_lap280_log=true`.
  - `make check` → **292 passed(49.83s)**, ruff/compileall/mypy/`CONTEXT_PASS`, log SHA
    `0c679f4527d5e364d4b45c7b05f7c69a464f2825bedc567a38b78dda0ba4b745`.
  - `bash checks/safety.sh check` → `SAFETY_PASS`, log SHA
    `4ae1cfe7183430cfef7225f54e2a6444b042294b0b6a9a50ec1c50f43217d192`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):

## 1. 결정성 — ACCEPT

lap299 probe/lap280 probe 모두 기록된 report SHA를 바이트 단위로 재현했다. 새 middle 환경에서도
동일하다. `make check` 292 passed와 `SAFETY_PASS`도 lap299 주장과 일치.

## 2. 상대 레이아웃 모델 — ACCEPT-WITH-CORRECTION

내가 따로 뜬 `objdump -d -Mintel` (0x4D60B0..0x4D656F)에서 lap299의 상수를 전부 재유도했다.
레코드는 `this+0x408` stride 16, 필드 `(x1,y1,x2,y2)`, count 7 (`[esi+0xF9C]=7`), rect
`[esi+0xFA4]=0x118` / `[esi+0xFA6]=0x18`. 모든 슬롯이 `x1=origin_x+0x14`, `x2=x1+0x118`,
`y1=origin_y+{-0x1A,0x08,0x2A,0x4C,0x6E,0x90,0xB2}`, `y2=y1+0x18`. 버튼 call point는
`origin+(0x24,0xD7)` / `origin+(0xBA,0xD7)`. 여기까지 **lap299와 일치**.

lap299에 없던 **독립 보강 2건**(이번에 처음 확보):
1. 스프라이트 정체가 가정이 아니라 로더 문자열로 확정된다. `0x4F7DF8="yfnt\saveloadtitle.spr"`가
   `[esi+0x10EC]`로, `0x4F7DC8="yfnt\saveloadbar.spr"`가 `[esi+0x1CE4]`로 적재되고,
   중심식이 읽는 다이얼로그 폭/높이는 `[esi+0x10F0]`/`[esi+0x10F4]` = 전자의 크기다.
2. 하드코딩 rect `0x118×0x18`은 선택 바 스프라이트 `SaveLoadBar.spr` 헤더 **280×24**와 정확히
   같다. 슬롯 rect 모델의 원본 독립 교차 증거다.

정정 2건:
- **C1 (앵커 구멍):** 슬롯0의 `-0x1A`는 lap299 probe의 어떤 disasm 앵커에도 걸리지 않는다
  (실제 명령은 `sub ecx,0x1a @ 0x004D6358`이고 앵커 튜플은 여섯 개 `add` 형태만 본다).
  이 상수만 드리프트해도 lap299 probe는 exit0으로 통과한다. 본 lap300 probe가 앵커를 추가했다.
- **C2 (fixture 미pin):** lap299 probe의 `EXPECTED_SPRITE_SHA = ""`라 스프라이트 SHA 검사가
  통째로 건너뛰어진다(헤더만 검사). 또 참조 저장소 경로 `Syw2plus_re/Syw2plus/yfnt/`에서 읽는다.
  이번에 원본 입력 `Syw2plus/yfnt/`의 사본과 바이트 동일(`7d154cdb…`)임을 확인해 **현재 수치에는
  영향 없음**. 그러나 참조 저장소가 드리프트하면 조용히 통과한다.

## 3. 절대 800×600 좌표 — **REJECT** (이번 바퀴 핵심 판정)

`FUN_004D60B0`은 800×600을 읽지 않는다. 0x4D6312~0x4D6348에서 중심식은
`origin_x=(ds:0xE5BF1C - [esi+0x10F0])/2`, `origin_y=(ds:0xE5BF20 - [esi+0x10F4])/2`를 계산해
`ds:0x1088B5C`/`ds:0x1088B5E`에 넣고, 이후 일곱 레코드와 두 버튼이 전부 그 전역을 다시 읽는다.
`0xE5BF1C`/`0xE5BF20`은 같은 함수가 `this`로 넘기는 그래픽 객체 `0xE5BF18`의 필드 **+4 / +8**이다.

.text 전수 스캔으로 이 두 전역의 writer는 정확히 네 곳이고 **두 함수**다:

| 주소 | 명령 | 의미 |
|---|---|---|
| 0x431B79 / 0x431B7F | `ds:0xE5BF1C,ebp` / `ds:0xE5BF20,edi` | `FUN_00431AB0`이 지도 표면 크기(`[esi+0x8C]<<6`, `[esi+0x8E]<<5 + 0xC8`)로 덮어씀 |
| 0x4324B8 / 0x4324C2 | `ds:0xE5BF1C,0x280` / `ds:0xE5BF20,0x1E0` | 같은 함수의 성공 exit이 **무조건 640×480으로 되돌림** |

세 번째 writer는 모드 테이블 `FUN_004644A0`이지만 그것은 같은 객체의 `[esi+4]`/`[esi+8]`에 쓰며
호출처는 디스플레이 초기화 2곳(0x4643C0, 0x464C64)뿐이다. 모드 표는 1→320×200, 2→640×480,
3→640×480×16, 4→**800×600**, 5→800×600×16, 6→1024×768, 7→1024×768×16, 8→1280×1024이다.
즉 800×600은 **선택 가능한 모드 중 하나**이고, `FUN_00431AB0`이 한 번이라도 돌면 그 뒤로 모드를
복원하는 writer가 없다.

따라서 다이얼로그 원점은 **진입 경로 의존**이며 lap299가 낸 단일 좌표표는 그 전제를 적지 않았다:

- 후보 A (타이틀 진입, `FUN_00431AB0` 미실행): screen 800×600 → title `(240,145)`,
  slots `[260,119,540,143]`…`[260,323,540,347]`, OK/Cancel `(276,360)`/`(426,360)`.
  = lap299 수치와 동일. lap298의 800×600 타이틀 캡처와 같은 경로다.
- 후보 B (인게임 진입, `FUN_00431AB0` 실행 후): screen 640×480 → title `(160,85)`,
  slots `[180,59,460,83]`…`[180,263,460,287]`, OK/Cancel `(196,300)`/`(346,300)`.

후보 B 쪽 방증: 같은 함수가 0x4D621E~0x4D6306에서 먼저 써 넣는 **덮어써지는 기본 테이블**의
`x1=0xB4=180`은 `origin_x(160)+0x14`, 즉 **640 폭 화면**을 전제로 작성된 값이다. 원본 저자가 이
다이얼로그를 640 기준으로 배치했다는 정적 흔적이다(그 테이블의 y는 512 높이 쪽에 맞고 480과
불일치하므로 y는 근거로 쓰지 않는다).

**판정:** 상대 모델 ACCEPT, `candidate_800x600` **단일 절대 좌표표는 REJECT**. lap299 probe는
0x4324B8의 640×480 저장을 스스로 앵커로 걸어 `"logical_screen_init": "0x004324B8: 640x480"`까지
보고서에 적어 놓고, 같은 보고서에서 800×600으로 계산한다. 내부 모순이며 화해되지 않았다.
어느 후보가 클릭 시점에 성립하는지는 **offline으로 결정되지 않는다** — `0xE5BF1C`/`0xE5BF20`의
관측값이 필요하고 그건 실행을 요구한다. runtime 예산은 이번 바퀴에도 요청하지 않는다.

## 4. lap296 §4.7.6 가드 수리 — ACCEPT

lap296 review probe를 그대로 재실행해 lap299의 서술을 확인했다. 실패는 자기 stale pin 1건뿐이고
mutation 판정은 전부 살아 있다: `blind_spot_verdict="guarded"`, W2 `type`/`owner` 상수 승격
mutant 2종 모두 `named_failure=true`·exit1·crash 없음, A(정의 삭제)×3·B(바인딩 상실/값 드리프트)
전부 named failure로 fail-closed, companion probe 4종 `matches_record=true`, lap280 fresh run이
로그와 바이트 동일. **가드 수리는 의도대로 동작한다.**

정정·잔여 2건:
- **C3 (STATUS 오기):** STATUS는 mismatch를 `88d86211…`로 적었으나 실제 기대값은
  `88d8628119cab28457fe32ce02e0be823e940e4a64a5f6b43da251daf2d9a18d`이다.
- **W3 (신규):** lap296 review probe의 `EXPECTED_SHA["target_probe"]`는 수리 전 SHA를 가리키므로
  이제 **영구적으로 exit1**이다. 회귀 게이트로 재사용할 수 없다. 재pin은 자기 검수 대상의 증거를
  스스로 갱신하는 행위라 middle이 단독으로 하지 않는다. Astra/사용자 결정 대기로 둔다.
- **알려진 사각(유지):** 가드는 `type`/`owner` 리터럴의 **소멸/개명**만 잡고 **값 드리프트는
  잡지 않는다**(`0x8D`/`0x8E` 기대값 단언이 없다). lap292 §4.5.4의 reader 이름 미검사 사각과
  같은 부류이며 이번에 수리하지 않는다(hands-on은 work 역할).

## 5. 판정 요약

| 항목 | 판정 |
|---|---|
| lap299/lap280 probe 결정성 | **ACCEPT** |
| 상대 레이아웃 모델(레코드/rect/오프셋/버튼 델타) | **ACCEPT-WITH-CORRECTION** (C1, C2) |
| `candidate_800x600` 단일 절대 좌표표 | **REJECT** (진입 경로 의존, 전제 미기재) |
| lap296 §4.7.6 가드 수리 | **ACCEPT** (C3 오기 정정, W3 신규) |
| 제품 G1~G4 증거 | 변화 없음 **0** |
| Stage B / runtime 예산 / 클릭 / 마일스톤 | 요청 없음, 전부 **금지 유지** |

- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: `tools/runtime_env.py` `dd2ad043…8500190`,
  `patches/population/runtime_driver.py` `ae4ff939…4e4291b5` 불변. `make check` 292 passed,
  `SAFETY_PASS`. 원본 캡처 대조·게임/Wine/Xvfb/Stage B/runtime 예산 금지·미검증 유지. 제품 G1
  승인·Stage B 허가·사용자 milestone 승인 **없음**. 이 문서 자체도 다음 새 세션이 독립 검수한다.
- 다음 한 가지: **work tier(Luna/Sonnet5/high)가 §11 handoff대로 lap299 probe를 수리한다** —
  (1) `sub ecx,0x1a` 앵커 추가, (2) `EXPECTED_SPRITE_SHA` pin + 원본 입력 경로 사용,
  (3) 하드코딩 `SCREEN=(800,600)` 제거 후 화면 전역 writer를 보고서에 열거하고 후보 A/B를 전제와
  함께 **둘 다** 출력. 그 전에는 게임 실행, 슬롯 클릭, Stage B, runtime 예산, G1 PASS 승격 금지.

## 6. 최종 파일 해시 (uncommitted, `LOOP_ALLOW_COMMITS=0`)

| 파일 | SHA256 |
|---|---|
| `docs/history/laps/probes/20260912_lap300_middle_lap299_layout_review_probe.py` | `718b1e4e4e99a7597dc470c4b9f980eee48d67e087397701894864bd17ea63cf` |
| `logs/lap300/middle_layout_review.json` | `bcac0a410ca5bc7b3ee9f824beff074e221083083bcb1e2e389d4617764c67b2` |
| `docs/STATUS.md` (lap300 갱신 후, 130줄) | `ad416c1bf2f4cca0595d87eaa69330fd3c6228915d9ff0515032f27751478f5c` |
| `docs/history/laps/20260912_status_lap300_compaction.md` (압축 전 원문 보존) | `ab6181c6e999b3794f55fcf5b24985a69e3349678d9cf0cbf13a61a236ebc717` |
| `docs/work/active/G1_RUNTIME_CONTRACT_MIDDLE_LAP284.md` (§11 추가 후) | `1cf839ddfece8406801edc2668dc5e44152f1c61ed63e96fcc1a9fb6f9672d09` |

압축 전 `docs/STATUS.md` 원문은 SHA `620d91fd8ab2a938e790c002897006db12dfd1b6db3c8199e5396fc7faebf426`,
125줄이며 위 압축본에 전문 보존했다. 어떤 승인·반려·미결 항목도 삭제하지 않았고 문장만 줄였다.
최종 재검증: `make check` **292 passed(46.04s) / All checks passed**, `CONTEXT_PASS`, `SAFETY_PASS`.
`loop/ESCALATE_SOL`은 만들지 않았다 — 필수 게이트 실패 없음, 마일스톤 경계 아님, 지정된 middle
검수 범위 안에서 판정이 끝났다. W3만 Astra/사용자 결정 대기로 남는다.
