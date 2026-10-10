# 2026-10-07 | lap1128 | G1 middle — H-RS1 독립 검수 + PS27 원인 정적 확정(HD primary 역읽기) + H-RS2 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(진단·계획·확인) 1 lap. 게임 실행 0, 제품 source·하네스·테스트 변경 0, 커밋 0.
- 입력: `loop/ESCALATE_SOL`(lap1127 work → middle 검수·방향 결정 요청), STATUS 다음 한 가지, lap1127 기록, lap1126 사전등록 §3. INBOX 새 사용자 지시 없음, APPROVALS 새 반려 없음(G1 사용자 시험 lap1104 대기), `loop/STOP` 없음.
- ESCALATE_SOL 처리: 원문을 `docs/history/laps/20261007_lap1128_preserved_lap1127_escalate_sol.txt`로 byte 일치 보존(SHA256 `220b6b76…`, `cmp` 일치)한 뒤 삭제했다.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 직접 재계산 MATCH(읽기만, objdump 디스어셈블).
- fixture: lap1127 raw만 사용(`g7defeat` = lap982 orig `save001.dat` `57872666…`).
- artifact SHA(work 기록과 일치): result m27 `63dc9b8c1833`·m29 `b5b2788ad533`·w27 `34f1a5f76f7d`·w29 `7a8d524a7004`·c27 `e6931c21d6d6`, mask m27 `958d9835dfbd`·m29 `995824ae2d1b`, screen watch w27 `9e83cc59b18b`·w29 `5d468385b815`, trace m27 `64860af3f4c0`.
- source 동일성: `g1_mirror2x.c` `529429696de1`·`g1_saved_scene_probe.py` `884c5baeda03`(work 기록과 같음), `direct_draw_trace.c` `6bf459cbf0c3`(lap1126과 같음). lap1127 full check 로그(08:21:54) 뒤 수정된 tools/tests/checks 파일 0(무시되는 `.omc/` hook 상태만).

## 1. 독립 재계산 (새 스크립트)

- 스크립트: 공유 temp `20261007_lap1128_middle_review/recalc_lap1128.py`(`c86c9ce2…`) → `recalc_lap1128.json`(`3a334785…`).
- 5 run(m27·m29·w27·w29·c27) 모두 같은 값이 나왔다.
  - 후보 `ps27.png` 하단(출력 y≥880) 비검정(>16) **164 px**, baseline 하단(논리 y≥440) **72,277 px**. 두 수는 해상도가 달라 직접 비율은 아니지만 차이가 결정적이다.
  - PS27 present 1,036~1,185개, 첫 present stale **92,383**, 이후 stale 최대 0, HD min **80.754%**.
- **work 판정 지표와 불일치 0**(RS1-1 위치·PS27 HUD 소실 5/5·PS29 수치는 lap1126 재계산 그대로).
- 정정 1(경미): PS27 소스 표면 주소 `0x01E71788`은 m27·m29에서만 그 값이다. w27·w29는 `0x01E71820`, c27은 `0x01E71780`이다(heap 주소). 그래서 주소가 아니라 **역할(렌더러 `0xE5BF18`+0x1520 = `[0xE5D438]` 뒤 버퍼)**로 식별한다. 판정 영향은 없다.
- PS29 `0x468BB0` 확인: `ret 0x28`, `0x468C01 rep movsd`·`0x468C08 rep movsb`, 원본 안의 호출처는 `0x4B5493` 1곳이다. work 귀속과 일치한다.

## 2. PS27 원인 — 정적 확정 + 캡처 정량 일치(writer UNKNOWN 해소)

원본 디스어셈블(공유 temp `disasm_excerpt_lap1128.txt` `a7e6276d…`):

- 패배 판정은 `0x41CA62`에서 일어난다: `[0x4ED818]=0x1A`(PS26). PS26 처리기 `0x424E50`은 `call 0x4C7CD0` → `0x4C7D00(0)` 순으로 부른 뒤 `[0x4ED818]=0x1B`(PS27)로 바꾼다. 승리 쪽은 `0x424DE0` → `0x4C7CA0` → `0x4C7D00(1)`로 **같은 함수**를 쓴다.
- `0x4C7D00`(배너 준비)의 끝부분은 `[0xE5D424]`(렌더러+0x150C) 값에 따라 갈린다.
  - 0이 아니면 `[0xE5D438]->Blt(NULL, [0xE5D434], NULL, DDBLT_WAIT)`를 부른다(`0x4C7EC7`).
  - 0이면 `0x469300(sel=1, 0, 0, [0xE5D434], NULL, 0x10)`을 부른다(`0x4C7EE6`).
- `0x469300`은 sel 0이면 `[렌더러+0x151C]`(= `[0xE5D434]` primary), sel 1이면 `[렌더러+0x1520]`(= `[0xE5D438]` 뒤 버퍼)의 vtable+0x1C, 즉 **BltFast**를 부른다. 반환 주소는 sel 0이 `0x469379`, sel 1이 `0x46934D`다.
  - 그래서 PS26 준비 = **`BltFast(뒤 버퍼, 0, 0, primary, NULL, WAIT)`: 화면(primary) 내용을 뒤 버퍼로 역읽기**한다.
- PS27 매 프레임 `0x4C7F00`은 다음 순서로 돈다: 렌더러 lock `0x464E20(1)` → 배너 RLE `0x466D50` → unlock `0x464E70(1)` → `0x469300(sel=0, 0, 0, [0xE5D438], NULL, 0x10)`(= present BltFast primary ← 뒤 버퍼). trace의 PS27 호출처 `0x469379`·NULL rect·flags 16과 일치한다.
- **원본(800×600)**에서는 primary가 마지막 게임 프레임(HUD 포함)이므로 역읽기 결과가 1:1 복사다.
- **후보(1600×1200)**에서는 primary가 미러가 쓴 HD 1600×1200 화면이다. 그래서 뒤 버퍼(desc 1600×1200)에 HD 화면 전체가 복사된다. 게임과 미러는 그 **왼쪽 위 800×600을 논리 프레임으로 쓴다** → 논리 (0..400, 0..300) 4분면이 2배 확대돼 보이고, 논리 y≥300(HUD·미니맵·로고·커서)은 사라진다.
- 캡처 정량 일치(5/5): 후보 상단 띠(출력 y<200) 비검정 22,248 px 가운데 22,132 px(99.5%)가 "baseline 4분면 4× 확대" 가설과 겹친다. "baseline 2× 정상" 가설과는 792 px만 겹친다. ≤8 일치율은 4분면 가설 99.462% vs 정상 가설 91.567%다. 배너는 매 프레임 논리 좌표로 그려져 정상 위치에 보인다.
- 정리하면 PS27 stale 92,383은 "미러 밖 writer"가 아니라 **게임이 HD 출력면을 논리 프레임으로 다시 읽어 생긴 내용 변화**다. lap1127의 "감시 hit 0"도 이것으로 설명된다. 변화는 PS27 첫 present 전 ddraw 복사 1회이고, 렌더러 버퍼 쓰기 감시 대상이 아니다.
  - 이 BltFast(반환 `0x46934D`)는 lap1127 trace에 기록이 없다. 원인(이벤트 한도/집계 여부)은 H-RS2에서 확인한다.
- lap1127 미검증 가설 "원본이 primary 보존에 의존한다"는 **원본이 primary를 뒤 버퍼로 역읽기한다**로 확정한다. 승리 화면(PS24→PS25)도 같은 `0x4C7D00`을 쓰므로 **같은 결함이 정적으로 예상된다**(런타임 UNKNOWN).
- 동류 사이트(진단 대상):
  - `0x41C7E5`: `[0x4ED818]==3`이고 `[0xB93984]==1`일 때 `BltFast([0x104FB2C], 0, 0, primary, NULL, WAIT)` 뒤 PS22로 간다(역읽기, 장면 미확인).
  - `0x41C3E1`·`0x493E59`·`0x492728`·`0x49273C`는 primary가 **목적지**인 present 계열이라 역읽기가 아니다.

## 3. 결정

- **H-RS1 수용:** RS1-0·RS1-1 `PASS`, RS1-2는 PS29 `PARTIAL`(미후킹 `0x468BB0` 확정, hit 귀속 55%)·PS27 `BLOCKED`. PS27은 이번 middle 정적 분석으로 **원인 확정(writer = 게임 역읽기 BltFast `0x46934D`, 호출 `0x4C7EE6`)**이 됐다. 수리 미실시는 사전등록과 맞다.
- **PS27을 PS29보다 우선한다(work 제안 채택).** 실제 가시 결함이고 원본 대비 회귀다: HUD 소실 + 4분면 확대. 승리 화면도 공유할 가능성이 크다.
- **lap1127 제안 H-RS2(전환 구간 호출 표·`0x01E71788` 덤프·baseline 대조 = 추가 귀속)는 기각한다.** 원인이 정적·캡처로 확정됐다. 그래서 구현 우선 원칙에 따라 **다음 work는 바로 수리**한다(아래 §4 H-RS2 재정의).
- PS29 `0x468BB0` 미러 hook은 H-RS2 수용 뒤 H-RS3로 둔다(FEASIBLE 후보, 호출처 1곳).
- 사전등록 기준 PS27/PS29 HD ≥98.6%는 유지한다.

## 4. 다음 work 사전등록(Sonnet) — H-RS2: primary 역읽기를 논리 프레임으로 되돌리기(R-PB)

- **가설 H-RS2:** 미러가 켜져 있을 때 원본에 맞는 출처는 "마지막으로 present한 논리 800×600 프레임"이다. 이 경우는 게임이 primary를 소스로, 비-primary 표면을 목적지로 Blt/BltFast하는 경우다. 그 프레임을 목적지에 넣으면 PS27 HUD가 원본처럼 보인다. 첫 PS27 present의 stale 92,383도 거의 0이 된다(배너는 hook된 `0x466D50`).
- **RB-0 진단(TDD, 같은 회차):** `hook_blt_fast`·`hook_blt`에서 `source`가 primary(`surface_record(source)->is_primary` 또는 caps PRIMARYSURFACE)이고 목적지가 비-primary인 호출을 셈한다.
  - 기록: 상태·반환 주소·목적지 desc·x/y·src rect.
  - 이벤트 한도와 무관한 trace 계수 `primary_readback_calls`도 둔다.
  - 기대: g7defeat run에서 PS26 1회(반환 `0x46934D`). 다른 장면 수는 공개한다.
- **RB-1 수리(구현 우선):** 위 조건이고 미러가 켜져 있으면 HD primary 복사 대신 **마지막 present의 논리 프레임(800×600)**을 `(x, y)`부터 목적지 크기로 잘라 넣는다.
  - 방식(work 선택, 둘 중 하나):
    - (a) 매 present 논리 소스 스냅샷을 보관한다.
    - (b) 마지막 present 소스 표면·rect로 원본 BltFast를 다시 부른다. (b)는 present 뒤 소스가 바뀌지 않았음을 해시로 확인해야 한다.
  - 기본 켬, env `SYW2_G1_PRIMARY_READBACK=0`이면 이전 동작이다.
  - 판정이 순수 헬퍼면 테스트한다: 조건 경계, 잘림, 키 없음/있음 flag 보존.
  - trace에 `primary_readback_converted`·readback 뒤 목적지 논리 해시·마지막 present 소스 해시를 남긴다.
  - flip 분기(`0x4C7EC7` Blt)는 `[0xE5D424]`가 0인 현 환경에서 실행되지 않을 수 있다. 같은 조건으로 덮되 실행 여부를 공개한다.
- **측정(격리):**
  - g7defeat `--result-screen` 켬 2 run과 `SYW2_G1_PRIMARY_READBACK=0` 끔 1 run을 돌린다(끔은 결함 재현 대조).
  - 비회귀 1 run: new-game 경로 `--new-game-start --new-game-act --new-game-menu`. PS3 100%·PS23 닫힘 99.939% 근처·readback 계수를 공개한다.
- **PASS(수리, 켬 2/2):**
  - RB-a: readback 1회 이상 converted, 그 목적지 논리 해시 = 마지막 PS3 present 소스 해시.
  - RB-b(가시): 후보 `ps27.png`를 2× 축소(짝수 좌표 표본)해 baseline `ps27.png`와 비교한다. 배너 상자(논리 x270..530·y245..355)와 커서 주변 32×32를 뺀 영역에서 ≤8 일치 ≥99%이고, 하단(논리 y≥440) 비검정 수가 baseline 72,277의 ±3% 안이어야 한다. 끔 run은 기존 164/4분면 패턴을 재현해야 한다.
  - RB-c: PS27 min HD ≥98.6%(첫 전환 present 1개는 공개만). 확인 뒤 PS9 100%.
  - RB-d: V1/안전 7종/fallback/hresult 0, dropped 0, scale2x PASS, 경과 p95 증가 ≤2ms. 캡처를 직접 열람한다.
  - PS29 min 98.36%(기존 FAIL)는 이번 판정 항목이 아니다. 값이 변하면 공개한다.
- **FAIL/BLOCKED:**
  - readback 호출이 관측되지 않거나(정적 경로와 불일치) 해시가 다르면 원인을 남기고 middle로 넘긴다.
  - 실패 가설 2회 또는 60분이면 BLOCKED.
- 공개 한계(미리 적음): 승리 화면 UNKNOWN(같은 함수, fixture 없음), `0x41C7E5` 장면 미확인, PS29 마지막 present stale 478,002 backlog.
- 공통:
  - C·하네스 변경 뒤 lint·typecheck → 기록 freeze → `make check` 1회.
  - 디스크 ≥20GiB(현재 약 144GiB), game 사본 삭제.
  - 원본/참고 쓰기 금지, 커밋 금지, 시험판 재스테이징 없음(lap1104 판본 유지; 수리 수용 뒤 재스테이징 여부는 middle이 정한다).
  - 사용자 G1 시험 결과가 오면 그것이 최우선이다.

## 5. 검사

- 기록 freeze 뒤 `checks/safety.sh check`·`checks/context_limits.py`를 돌린다. 결과는 STATUS에만 쓴다.
- 전체 `make check` SKIP: 이번 변경은 문서뿐이다. 하네스·테스트·C source는 lap1127 full PASS(1770) 때와 같다(위 source 동일성, check 로그 뒤 변경 0).

## 다음 한 가지

work(Sonnet): §4 H-RS2 — RB-0 역읽기 계수 → RB-1 논리 프레임 되돌리기(env 끔 스위치, TDD) → g7defeat 켬 2·끔 1·new-game 비회귀 1 → middle 검수 요청.
