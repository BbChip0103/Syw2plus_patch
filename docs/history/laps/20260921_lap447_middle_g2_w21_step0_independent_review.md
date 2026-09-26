# 2026-09-21 | lap 447 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high, 역할 **middle**
  (중간 tier — 진단·계획·확인. 게임 코드 hands-on 수정 없음. 이번 세션은 loop runtime이 아닌
  일반 세션이나 동일 역할 계약 적용).
- 가설 / 사용자 관찰: lap446(work)이 W21 카드
  (`docs/work/active/G2_CAP_PROXIMITY_SEEDED_SOAK_LAP445.md`) Step0을 실행해 `(U0) PASS`를
  자기 판정했다. 카드 §5(실행 역할)·PROMPT ⑥ 2단에 따라 **다음 middle이 독립 검수**한다.
  검수 원칙: lap446의 요약/결론을 근거로 쓰지 않고 **원시 산출물과 현재 소스로 재계산**한다.
- 예상 PASS / FAIL 조건: 카드 §1 (U0) — owner0의 `(used,count)`가 전 표본 단일값 `(20,2)`를
  벗어나 **증가**하면 ACCEPT. 판정식은 실행 전 고정된 것이며 **재채점하지 않는다**.
  더해 (a) 기존 goal 동작 불변 주장, (b) 산출물↔기록 내적 정합, (c) 게이트/원본 안전을 검수한다.

- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  - **이번 회차 제품/도구 source 변경 0** (middle은 구현하지 않는다). 커밋 0
    (`LOOP_ALLOW_COMMITS=0`). 새로 쓴 파일은 이 lap 기록, STATUS, W21 카드 §10 addendum뿐이다.
  - **lap446이 빠뜨린 변경 파일 해시를 여기서 회수해 기록한다**(카드 §8 "변경 파일은 경로와
    해시로 남긴다" 미이행 — 아래 N62):
    - `tools/inmm_stub/control_executor.c`
      `0a2e2921e5e8f67fa2bb173cd19745824a398679636ff86ffcdc7003f04d2f19`
    - `tests/test_g2_eight_owner_setup.py`
      `6c9c01d14aee9a1adabb44234d92f00c50022b04742722a63d3323bf0a80a79a`
  - **강한 provenance 연결(신규, 긍정 소견):** 실행 run 디렉터리의
    `bridge_build/control_executor.c` 해시가 위 repo 소스 해시와 **동일**하다 ⇒ 테스트된 DLL이
    현재 repo 소스에서 빌드됐음이 파일로 증명된다(추정 아님).

- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  - 원본 EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` — middle이
    safety 결과에 기대지 않고 `/home/dev_00/sharedfolder/260320_Syw2plus/syw2plus_original.exe`를
    **직접 재해시**해 불변 확인.
  - **후보 EXE 없음(중요).** lap446 Step0은 원본 EXE 무패치 + **stock 진단 DLL**로 돌았다.
    `bridge_build/supply_bridge_build.json`: `unit_pool_capacity=1200`,
    `unit_pool_base=0x0066B790`, `unit_existence_base=0x008990C8`, `dll_sha256=4a74b8d8…`.
    ⇒ W21 본체(Step1)가 쓸 **N=4001 재배치 신후보 `a10024de…`가 아니다**(아래 N59).
  - 환경: 격리 복사본 `local/runtime/20260921_085544_3103469_0`, 전용 wine prefix, 빈 Xvfb
    `:3950`, `WINEDLLOVERRIDES=ddraw=b`, `SYW2_SUPPLY_PROBE=1`.
  - fixture: goal `_custom_game_chain_inject_g2_eight_ai_seed42` → PS9→PS7→PS3 체인 → 8 owner
    전원 op7(resource-only). 지도 = 원본 100x100 small-map(`d4a=0`), seed42.
  - **seed 축 동일성 확인(신규):** `chain_inject_seed_from_goal`은 **접미사** 비교이므로
    `..._ai_seed42`도 `_seed42`로 파싱돼 `seed=42`다 ⇒ lap442와 **같은 seed 축**이 유지된다
    (goal 이름이 바뀌었으니 middle이 직접 확인했다).

- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - 검수 대상 원시 산출물(읽기 전용):
    `temp/Syw2plus_patch/g2_capacity/20260921_lap446_w21_step0_owner0_ai_activation/`
    — `samples.jsonl`(91표본), `run_summary.json`, `step0_orchestrator.log`,
    `resource_receipts.json`, `bridge_build/`.
  - middle 재계산: `samples.jsonl`만 입력으로 owner0 이탈 시점/최종 장부/ai 필드 분포/단조성/
    owner별 max를 **직접 재계산**(lap446의 `run_summary.json` 결론값을 입력으로 쓰지 않음).
  - 게이트: `python3 -m pytest tests/test_g2_eight_owner_setup.py -q` → **6 passed**.
    `bash checks/safety.sh check` → **SAFETY_PASS**. 원본 EXE 직접 재해시 일치.
    이번 회차 **source 미변경**이므로 INBOX 2026-09-20 21:58 규칙(N22)에 따라 통합 `make check`
    전체는 재실행하지 않았다.
  - 게임 실행 **0회**(middle 역할, 기존 산출물 재계산만).

- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - **(U0) ACCEPT — 재계산 불일치 0.** 91표본, tick 18→3019 단조 비감소.
    owner0 baseline `(used=20,count=2)` 이탈: **sample 8 / tick 284 → `count=3, used=30`**
    (lap446 기재와 정확히 일치). owner0 `used` 시계열 **하강 0회**, 최종 `used=150/count=13`.
    최종 8 owner `count=[13,13,13,14,13,11,11,11]`, `used=[150,145,145,160,145,120,120,115]`
    ⇒ owner0은 더 이상 이상치가 아니며 다른 7명과 동급. **owner0은 (20,2)를 벗어나 증가했다.**
  - **기존 goal 동작 불변 — ACCEPT(소스 수준 항등).** `control_executor.c:900,924`에서
    `owner0_ai = (goal == G2_EIGHT_AI_GOAL)`이고 기존 goal에서는 `FALSE`이므로
    `record[2] = (owner == 0 && !FALSE) ? 0 : 1` ≡ 기존 `(owner == 0 ? 0 : 1)`. 또
    `is_g2_eight_goal`은 기존 goal에서 첫 절로 short-circuit하므로 나머지 호출부
    (L666/759/783/794)의 기존 goal 경로도 동일하다. ⇒ lap419~442 증거 의미 불변.
  - **`ai` 필드 독립성 확인(긍정):** probe가 읽는 `ai`는 우리가 쓴 로비 레코드
    (`G2_LOBBY_VA=0x00632CC0`, stride 6)가 아니라 **PlayerStruct**
    (`PLAYER_BASE=0x956770`, stride `0x3ABC`, `+2`)다 ⇒ 게임이 로비 blob을 소비해
    PlayerStruct를 만든 **결과**를 읽은 것이며 우리가 쓴 값의 되읽기가 아니다.
  - **정정/신규 소견 4건(판정을 뒤집지 않음): N59~N62 — 아래 「회귀 / 남은 위험」.**
  - 종합: **W21 Step0 = ACCEPT.** 단 이 ACCEPT가 주는 것은 카드 §1이 정의한 (U0) 하나뿐이며,
    G2 제품 완료도, cap 근접 안정성도, "8인 전비5000"도 아니다(카드 §9 그대로).

- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  - **N59 (범위, Step1이 반드시 이행): (U0)은 stock 빌드에서만 실증됐다.**
    Step0은 `unit_pool_capacity=1200`/stock base/원본 EXE 무패치로 돌았고, Step1은 **N=4001 재배치
    신후보 `a10024de…`** 위에서 돈다. 로비 write 경로는 동일해 전이 가능성이 높지만 **실측은 아니다**.
    ⇒ Step1은 자기 **첫 표본에서 owner0의 `(used,count)` 이탈을 재확인해 기록**한다. 재확인 실패
    (owner0이 `(20,2)` 고정)면 Step1은 "8인"을 주장하지 말고 그 자리에서 보고한다(카드 §1 (U0)
    후단과 동일 취급). **추가 lap 불필요 — Step1 내부에서 공짜로 얻어진다.**
  - **N60 (귀속 강도): 같은 바이너리에서의 대조군(A/B)이 없다.** 이번 run은 8 owner 전부
    `ai=1`인 **처치군만** 있다. middle이 과거 산출물을 전수 확인한 결과 `ai`/PlayerStruct`+2`를
    기록한 run은 **이번이 최초**다(lap440 run2 필드=`live/sample/slot3565/t/tick`,
    lap442 필드=`cap/count/count_cap/owner/reserved/used` — 둘 다 `ai` 없음).
    ⇒ "`record[2]`=AI 컨트롤러 플래그"는 (a) 소스(lap445 §2-1) (b) 처치군 런타임 읽기
    (c) **다른 바이너리·다른 fixture**인 lap442의 행동 대조, 세 가지로 **지지**되지만 동일
    바이너리 A/B로 **확정된 것은 아니다**. 카드 §3-1이 요구한 것은 "런타임 대조 1회"였고
    lap446은 owner0↔owner1 대조(둘 다 1)만 했다 — 이는 goal 간 대조가 아니다.
    ⇒ 값싼 해소: Step1 착수 전 **기존 goal로 PS3 진입만 시켜 PlayerStruct+2를 1회 읽어
    owner0=0을 기록**한다(≤1분, soak 불필요). **별도 lap을 쓰지 말고 Step1 회차에 붙인다.**
  - **N61 (계측 스크립트 결함, Step1 재사용 전 수리 필요):** `run_summary.json`의
    `final_tick=2986`은 실제 마지막 표본 tick **3019**보다 작다. 원인은
    `step0_owner0_ai.py:307-314` — `tick >= STOP_TICK`에서 **break 한 뒤에** `last_tick`을
    갱신하는 순서라 마지막 표본이 반영되지 않는다. 이번 판정에는 무해하나(이탈 tick/최종 장부는
    표본에서 직접 계산), Step1의 (U2)가 **`STOP_TICK ≥ 24,000` 도달**을 조건으로 하므로 같은
    샘플러를 재사용하면 **도달을 과소 보고**할 수 있다. work가 Step1 전에 고친다(middle은 구현 안 함).
  - **N62 (provenance 오기 + 카드 §8 미이행):** lap446 기록은 검증 대상 DLL을
    "`_inmm.dll`, `bridge_sha256=15aa1715…`"로 적었으나, `15aa1715…`는 `supply_bridge_build.json`의
    **`bridge_sha256`(runtime_bridge blob)** 필드이고 **실제 DLL은 `dll_sha256=4a74b8d8c3a84d8f56b0cd1fadfaff33fed50adaa282b38a6cd1276a7fd4729f`** 다.
    또 lap446은 카드 §8이 요구한 **변경 source 2개의 해시를 남기지 않았다**(위 「변경 파일」에서 회수).
    **용어 정정:** "기존 goal 동작을 **바이트 단위로** 유지"는 느슨하다 — 유지되는 것은 **동작
    (소스 수준 항등)** 이고 재빌드된 **DLL 바이트는 다르다**(`4a74b8d8…`).
  - **N63 (Step1 비교 가능성):** Step0 표본 필드(`ai/count/nation/owner/used`)는 lap442
    (`live/max_slot_index/rss_kb/reserved/cap/count_cap` 포함)보다 **좁다**. Step1은 lap442 필드
    **합집합 + `ai` + 카드 §4-4 메모리 필드**를 기록해야 lap442와 대조 가능하다.
  - 절차 준수(긍정): lap446은 카드 §8이 요구한 **자체 lap 기록을 남겼다**(lap440·442 연속 누락
    전례가 끊겼다). 동기 실행으로 완료까지 대기·회수했고(INBOX 01:01 준수), source를 바꿨으므로
    통합 `make check` 전체 1회를 면제 없이 실행했다(N22 준수).
  - 독립 검수 상태: **이 lap이 그 독립 검수다(ACCEPT).** 사용자 마일스톤 승인은 **없음** —
    G2 제품 완료 아님. 144k 카드 발행 금지 유지(카드 §0-4).
  - 미검증으로 남는 것(변동 없음): cap 근접 도달(U1)·24k 안정성(U2)·장부 정합(U3)·메모리 해명
    (U4, N57)·신후보 저장/로드(U5)·건물 포함 혼합 구성·원본 생산 경로 자연 도달((가))·144k·LAN.

- 다음 한 가지: **work 회차가 W21 Step1→Step3을 실행한다**(카드 §4·§6·§7 그대로, 판정식
  (U1)~(U5)는 실행 전 고정된 것이며 변경 없음). 착수 전 이 lap이 추가한 의무 4건을 이행한다 —
  ① Step1 첫 표본에서 신후보 기준 (U0) 재확인(N59) ② 기존 goal PlayerStruct+2 대조 1회 기록
  (N60, ≤1분) ③ 샘플러 `final_tick` 결함 수리(N61) ④ 표본 필드 합집합(N63).
  Step3 `lap413_stock_comparison.md`는 **fail-closed**(파일 없으면 다음 middle이 내용 미열람 REJECT).
