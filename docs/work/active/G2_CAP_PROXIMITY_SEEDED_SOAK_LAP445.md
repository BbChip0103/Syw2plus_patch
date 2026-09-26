# W21 — G2 cap 근접 시딩 soak + owner0 활성화 + 저장/로드 재확인 (lap445 middle 발행)

- 발행: lap445 middle (Claude Code `claude-opus-5` / high), 2026-09-21 KST
- 상위 근거: `docs/work/active/G2_STRATEGY_FIXTURE_SCOPE_LAP444.md` §3(필수 Step 5개),
  `loop/ESCALATE_SOL` §27(N55~N58)·§28(판정), lap442 원시 `samples.jsonl` 721표본.
- 실행 역할: **work** (Claude Code `claude-sonnet-5` / high). 이 카드는 middle이 쓴 계획이며
  middle은 구현하지 않는다. work가 실행하고 **다음 middle이 독립 검수**한다.
- 후보: `a10024de5e1c1cbedcddde0c3b52f5b3a9cf0721ee066542669f4883a1bb2d68`
  (핀 복사 금지 — 현재 source 재빌드로 SHA 확인, N53).

## 0. 이 카드가 사는 경계 (lap444 §1, 위반 시 middle REJECT)

1. **(나) 직접 시딩 단독으로 G2 완료를 주장하지 않는다.** STATUS·산출물 기재는
   **"부분 증거(cap 근접 안정성)"** 로만 한다.
2. 시딩은 **gate-legal**. 아래 §2에서 확인했듯 브리지 op5/op6은 원본 생산 gate `0x43EDA0`을
   실제로 호출하고 반환 슬롯을 검증하므로 이 조건을 만족한다. **op4(장부 직접 write)는 금지**다.
3. **혼합 구성 최소 2계층**: op5(type 5, cost **35**)와 op6(type 7, cost **10**)를 함께 쓴다.
   단일 type 채우기로 "cap 근접" 을 주장하지 않는다.
   **알려진 범위 한계(숨기지 말 것):** 현재 브리지 fixture에 **건물 계층이 없다**. DESIGN §G2가
   요구하는 "건물 포함" 구성은 이번 카드로 충족되지 않으며 (가) 경로의 몫이다. 산출물에 명시한다.
4. **144k 카드 발행 금지 유지.** 해제 조건은 lap444 §1-4 그대로 — 이 카드 ACCEPT **그리고**
   (가) fixture 성립. 이 카드는 144k 근거가 아니다.
5. (가) 경로로 넘어가 **AI 코드/바이너리를 바꿔야 하는 순간 즉시 strategy 재에스컬레이션**
   (lap444 §2). 이 카드 범위는 fixture/설정뿐이다.

## 1. 실행 전에 고정하는 판정식 (사후 재채점 금지)

Step 실행 **전에** 아래를 고정한다. 결과가 어느 쪽이든 그대로 기록한다.

- **(U0) Step0 성립**: owner0의 `(used,count)`가 전 표본 단일값 `(20,2)`에서 벗어나 **증가**하면
  PASS. 아니면 FAIL이며 **이후 Step에서 "8인"을 주장할 수 없다**(lap444 §3-1). 이 경우 Step1은
  "7인 + 미활성 1" 으로만 기재하고 진행한다(중단하지 않는다).
- **(U1) cap 근접 도달**: 시딩 종료 시점에 **8 owner 전부** live `used` ∈ **[4900, 5000]**.
  8/8이면 U1 PASS. 도달 owner 수를 그대로 적는다.
- **(U2) cap 근접 안정성**: U1 성립 이후 **STOP_TICK ≥ 24,000** 까지
  fault/crash/read failure **0** ∧ live `used > 5000` 표본 **0건**.
- **(U3) 장부 정합**: 전 표본에서 `live == Σ owner.count`. 불일치 1건이라도 있으면 FAIL.
- **(U4) 메모리 해명(N57)**: §4 계측으로 RSS 하강이 (a) 호스트 페이지 회수 (b) 게임 측 해제
  (c) 미해명 중 무엇인지 **하나로 귀속**되면 PASS. 귀속 실패는 `UNKNOWN`으로 남기며 FAIL로
  세지 않되 **해명됐다고 쓰지 않는다**.
- **(U5) 저장/로드 왕복(신후보)**: 저장 전후 owner별 `(count, used, reserved)` 와 슬롯 단위
  `(slot, internal_id, type, owner)` 소실 0 · 불일치 0이면 PASS.

**종합 판정**: U1∧U2∧U3 = `CAP_PROXIMITY_STABLE`(부분 증거) / U1 미달 = `SEED_SHORTFALL` /
U2 위반 = `CAP_PROXIMITY_UNSTABLE`(= 새 결함, 즉시 중단·에스컬레이션).

## 2. middle이 이번 회차에 정적으로 확인해 준 것 (work는 재조사하지 말 것)

work가 같은 것을 다시 파느라 한 바퀴를 쓰지 않도록, middle이 소스로 직접 확인했다.

1. **N56 원인은 찾았다 — 추정이 아니라 소스 한 줄이다.**
   `tools/inmm_stub/control_executor.c:913`
   ```c
   record[2] = (BYTE)(owner == 0 ? 0 : 1);   /* lobby record, G2_LOBBY_VA=0x00632CC0, stride 6 */
   ```
   goal `_custom_game_chain_inject_g2_eight_seed42`가 8개 로비 레코드를 채울 때 **owner0만
   `record[2]=0`, owner1~7은 `=1`** 이다. lap442에서 owner0만 전 구간 `(20,2)` 고정이었던 관측과
   정확히 일치한다. ⇒ owner0은 AI가 붙지 않은 슬롯이고 **실질 활성은 7명**이다.
   **아직 확정이 아닌 부분:** `record[2]`의 의미(1=컴퓨터/AI 여부)는 이 소스에 주석이 없다.
   Step0은 이 한 가지만 실증한다.
2. **op5/op6 시딩은 gate-legal이다**(`patches/population/runtime_bridge.c:175-229`).
   원본 배치 `0x42ECB0` → **원본 생산 gate `0x43EDA0`** → 원본 spawn `0x443190`을 순서대로
   호출하고, 매 개체마다 `count`가 +1, `used`가 +cost 인지 검증한 뒤에만 카운트한다.
   전비 상한도 `old_used + [p+0x1c] + cost > [p+0x2012]` 로 **원본 cap을 존중**한다.
   ⇒ lap444 경계 2는 op5/op6으로 충족된다. op4는 장부 직접 write라 **금지**.
3. **1200 슬롯 천장 걱정은 없다.** `patches/population/build_runtime_bridge.py:45-54`가
   `--unit-pool-capacity` 로 빌드할 때 `runtime_bridge.c` 안의 `0x66b790u`/`0x8990c8u`/`1200`을
   재배치 주소와 N으로 치환한다. middle이 `runtime_bridge.c`의 `1200` 리터럴 **5곳 전부**가
   풀 슬롯 경계임을 확인했으므로 이 문자열 치환은 의미상 안전하다. N=4001이면 gate 수용 범위도
   `allocated < 4001`이 된다.
4. **산술은 성립한다.** 시작 2기/`used=20`에서 출발해 예: op5 **138기**(+4,830) + op6 **5기**(+50)
   = `used 4,900`, owner당 145기 → 8 owner **1,160기** ≪ 4,001. op5/op6은 요청당 `wanted ≤ 200`
   이므로 owner당 2요청이면 된다. 정확한 조합은 work가 정하고 **실제 달성값을 기록**한다.
5. **`fixture_attempts`는 요청마다 새로 0**(같은 파일 L110, 지역변수)이라 요청 단위 예산은
   `min(10000, map_width*map_height)`다. 누적 소진 걱정은 없다. 반면 **`fixture_failed`는
   static(L17)이라 한 번 회계 불일치가 나면 그 프로세스에서 fixture가 영구 잠긴다** → §5 함정1.

## 3. Step0 — owner0 활성화 (선행, 싸게, 새 진단 사슬 금지)

lap444 §3-1과 §27 항목2가 요구한 "설정 확인 1회". 위 §2-1로 **원인 탐색은 이미 끝났다**.
남은 것은 실증과 최소 수정뿐이다.

1. `record[2]`의 의미를 **1회** 실증한다: goal을 그대로 보내 PS3 진입 후, owner0과 owner1의
   PlayerStruct에서 AI/컨트롤러 구분 필드와 초기 `count`를 읽어 대조한다.
   **원본 `FUN_0041B9B0`의 정적 역추적을 새로 시작하지 않는다** — 런타임 대조 1회로 끝낸다.
2. 실증되면 `control_executor.c:913`을 `record[2] = 1;`(8 owner 동일)로 **최소 변경**하거나,
   기존 goal을 건드리지 않도록 **새 goal 이름**(예: `..._g2_eight_ai_seed42`)을 추가한다.
   **권고는 새 goal 추가** — 기존 goal로 만든 lap419~442 증거의 의미가 바뀌지 않는다.
3. 재빌드 후 PS3 진입만 시켜 **owner0의 `count`가 2를 넘어 증가하는지** 짧게(≤3,000 tick) 본다.
   ⇒ (U0) 판정. 여기서 소스를 바꿨다면 **INBOX 21:58 규칙에 따라 통합 경계에서 `make check` 전체를
   1회 실행**한다("이번 회차 source를 바꿨다"를 기록에 명시, N22).

## 4. Step1 — cap 근접 시딩 + soak (이 카드의 본체)

fixture는 lap442와 동일 축(N=4001 신후보 / 8 owner / seed42 / 격리 사본·prefix·빈 display)에
Step0 결과를 반영한 goal을 쓴다.

1. PS3 진입 → op7로 8 owner 자원 공급(기존과 동일) → **owner마다 disjoint 앵커**로
   op5/op6 요청을 보내 `used`를 [4900, 5000]로 올린다. 앵커·요청·receipt를 전부 남긴다.
2. 매 요청 receipt에 `ok/reason/fixture_added/fixture_attempts/before/after 장부`를 기록한다.
   `reason`이 `fixture_original_gate_rejected` / `spawn_accounting_mismatch` /
   `fixture_exceeds_unreserved_supply` 중 하나면 **그 자리에서 멈추고 기록**한다(재시도 금지 —
   함정1).
3. 시딩 완료 후 **STOP_TICK ≥ 24,000** 까지 샘플링한다(lap442와 같은 규모라 비교 가능).
4. **계측 필드 (N57 해소용 — 이것이 이번 Step의 새 요구다).** 표본마다:
   - `rss_kb`(유지) **+ `vm_size_kb` + `vm_swap_kb`**: 모두 게임 PID의 `/proc/<pid>/status`.
   - **`host_mem_available_kb`**: `/proc/meminfo`의 `MemAvailable`.
   - `pid` 와 최초 1회 `/proc/<pid>/cmdline` — 표본이 같은 프로세스임을 파일로 증명한다.
   - **요약(`run_summary.json`)에도 RSS 시계열 요약을 넣는다**(min/max/최종/최대 하강 3건의
     `(sample, tick, delta_kb)`). §27 N57이 지적한 "요약에 필드조차 없음"을 이 카드가 갚는다.
   판정: 하강 구간에서 `vm_size`가 함께 줄면 **게임 측 해제**, `vm_size`는 그대로인데 `rss`만
   줄고 `host_mem_available`이 낮으면 **호스트 회수**, 둘 다 아니면 `UNKNOWN`. ⇒ (U4).
5. **하지 말 것:** `max_slot_index_seen`을 점유량/확장슬롯 사용 근거로 쓰지 않는다(N55 — 721표본
   전부 4000 상수였고 live 16뿐인 sample0에서 이미 4000이었다).

## 5. 사전 등록 함정 (실행 전 고정 — 나중에 변명으로 쓰지 말 것)

1. **`fixture_failed` 영구 잠금**(`runtime_bridge.c:17,222`). 회계 불일치 1회로 그 프로세스의
   모든 후속 op5/op6이 `fixture_locked_after_accounting_failure`가 된다. ⇒ 본 시딩 전에
   **op5 `wanted=1` 스모크 1건**을 먼저 보내 성공을 확인하고 시작한다. 실패하면 장문 soak를
   띄우지 말고 그 사실만 보고한다.
2. **진단 DLL의 stock 하드코딩**(lap410 정정2). `build_runtime_bridge.py`의 주소 치환은
   **`runtime_bridge.c` 에만** 적용된다. `tools/inmm_stub/` 의 `inmm_stub.c`/`ai_shadow.c`/
   `sfx_hook.c`/`control_executor.c`는 여전히 stock `0x008990C8`/1200을 하드코딩한다.
   ⇒ **그 채널들(`C:\inmm_unit_ticks.jsonl` 등)의 유닛 수를 이번 판정 근거로 쓰지 않는다.**
   "0기 관측"을 전멸로 오판하지 않는다.
3. **RSS의 PID 혼동 가설은 이미 배제됐다.** middle이 `w20_step2_run.py:176-184,262,332`를 읽어
   `read_rss_kb(pid)`가 **메모리 read가 전부 성공한 바로 그 게임 PID**를 쓴다는 것을 확인했다
   (lap415/416의 Wine 런처 PID 혼동과 다른 상황). ⇒ N57을 "PID를 잘못 봤다"로 닫지 말 것.
4. **하강은 단발이 아니다.** middle 재계산 결과 하강은 최소 두 국면이다 —
   ①tick 14,623(최대 248,636KB)→14,890 구간에 −126MB ②tick 22,963~23,730에 추가 하강,
   종료 시 **50,120KB(live 583)** 로 **초기 236,416KB(live 16)보다 낮다**. §27의 "−95MB 단발"
   서술은 가장 큰 한 계단만 본 것이다. 카드는 **두 국면 모두** 계측 대상으로 잡는다.
5. **1 tick 분해능 한계**(N40/N44 계보). 20ms 간격은 tick당 약 2표본이라 두 필드의 동시성을
   원자성으로 읽지 않는다.

## 6. Step2 — 신후보 저장/로드 왕복 (lap444 §3-3)

현 왕복 증거(lap409/411/412)는 **전부 구후보** 것이다. 신후보 `a10024de…`로 재확인한다.

1. lap409의 **marked compat 방식 재사용**(마커 `S2P1N4K1`, 파일 오프셋 `0x38` 확인).
2. Step1의 cap 근접 상태에서 op2(save `0x440C20`) → op3(load `0x440FF0`) 1왕복.
3. 저장 직전 / 로드 직후 **같은 표본 경계**에서 owner별 `(count, used, reserved)` 와 슬롯 단위
   `(slot, internal_id, type, owner)` 전수 대조. ⇒ (U5).
4. **로드가 실제로 상태를 교체했다는 증거를 반드시 남긴다** — lap410이 쓴 `trace.jsonl`의
   **tick 역행**이 그것이다. 이것이 없으면 "소실 0"은 "로드가 아무 일도 안 함"과 구분되지 않는다.

## 7. Step3 — lap413 구후보/stock 대조표 (**fail-closed**, N58/N54 재발 3회차 방지)

두 카드 연속(W19 Step4, W20 Step3) 누락됐으므로 **서술 의무에서 판정 조건으로 승격**한다.

- work는 다음 **파일**을 반드시 만든다:
  `temp/Syw2plus_patch/g2_capacity/<이번 run 디렉터리>/lap413_stock_comparison.md`
- 최소 컬럼: `축 | lap413 구후보 | lap413/기존 stock 대조군 | 이번 신후보`
  최소 행: `fault tick(11,928 통과 여부)`, `도달 tick`, `표본 수`, `max live`,
  `owner별 max used`, `fault/crash/read failure 수`, `fixture(op/자원/seed/N)`.
- **이 파일이 없으면 다음 middle은 내용을 보지 않고 자동 REJECT 한다.** 수치를 모르면
  `UNKNOWN`이라고 쓰되 **행 자체를 비우지 않는다**.

## 8. 운영 규칙 (lap444 §3-5, INBOX 01:01)

- 장기 실행은 **동기 실행 또는 root 소유 exec 세션**. 셸 background로 넘기고 회차를 끝내지 않는다.
  "background 실행 중"이라는 문구만으로 활성 프로세스를 주장하지 않고 PID/산출물 갱신을 확인한다.
- **work는 자체 lap 기록을 `docs/history/laps/`에 남긴다.** lap440·lap442 두 번 연속 누락됐다.
  기록이 없으면 다음 middle이 **관찰 결함으로 기재**한다.
- 원본 저장소 쓰기 금지, 격리 전체 복사본/전용 prefix/빈 display만. 전역 pkill 금지.
- 커밋 금지(`LOOP_ALLOW_COMMITS=0`). 변경 파일은 경로와 해시로 남긴다.
- Step0에서 source를 바꿨다면 통합 경계에서 `make check` 전체 1회(N22). 안 바꿨으면
  표적 테스트 + `checks/safety.sh check` + 원본 직접 재해시만 한다.

## 9. 이 카드가 끝나도 **아직 아닌 것**

G2 제품 완료 아님. 이 카드 전부 PASS여도 얻는 것은 **"cap 근접(≈4,900) 상태에서 24k tick 안정 +
저장/로드 1왕복"** 이라는 **부분 증거**다. 미검증으로 남는 것: 원본 생산 경로로의 자연 도달((가)),
144k, LAN/지원 동기화, 건물 포함 혼합 구성, 전투/사망/재생산 순환.

## 10. lap447 middle addendum — Step0 ACCEPT 후 Step1 착수 조건 (추가만, 완화 없음)

lap447 middle이 lap446의 Step0을 독립 검수해 **(U0) ACCEPT(재계산 불일치 0)** 했다.
§1의 판정식 (U0)~(U5)는 **실행 전 고정된 그대로이며 이 addendum이 바꾸지 않는다**.
아래 4건은 Step1 착수 전/중에 work가 **추가로** 이행할 의무다(상세 근거는
`docs/history/laps/20260921_lap447_middle_g2_w21_step0_independent_review.md`).

1. **(N59) 신후보 기준 (U0) 재확인 — Step1 안에서 공짜로.** Step0은 **stock** 빌드
   (`unit_pool_capacity=1200`, `unit_pool_base=0x0066B790`, `unit_existence_base=0x008990C8`,
   원본 EXE 무패치, `dll_sha256=4a74b8d8…`)에서만 실증됐다. Step1은 **N=4001 재배치 신후보
   `a10024de…`** 위에서 돈다. ⇒ Step1의 **첫 표본에서 owner0의 `(used,count)` 이탈을 재확인해
   기록**한다. 재확인 실패(= owner0이 `(20,2)` 고정)면 "8인"을 주장하지 말고 §1 (U0) 후단대로
   "7인 + 미활성 1"로 기재하고 그 사실을 보고한다. **별도 lap을 쓰지 않는다.**
2. **(N60) 같은 바이너리 A/B 대조 1회 — ≤1분, Step1 회차에 붙인다.** 이번 run은 처치군
   (8 owner 전부 `ai=1`)만 있고, `ai`/PlayerStruct`+2`를 기록한 과거 run은 **하나도 없다**
   (lap440 run2·lap442 표본 필드에 `ai` 없음). ⇒ **기존 goal `_custom_game_chain_inject_g2_eight_seed42`**
   로 PS3 진입만 시켜 PlayerStruct`+2`를 1회 읽고 **owner0=0, owner1=1**을 파일로 남긴다.
   soak 불필요. 이것이 없으면 "`record[2]`=AI 플래그"는 소스 추론 + 교차 run 행동 대조에 머문다.
3. **(N61) 샘플러 `final_tick` 결함을 Step1 전에 고친다.** `step0_owner0_ai.py:307-314`가
   `tick >= STOP_TICK`에서 **break 뒤에** `last_tick`을 갱신해 `run_summary.json.final_tick`이
   실제 마지막 표본 tick보다 작다(Step0 실측: 보고 2986 vs 실제 3019). Step1의 (U2)는
   **`STOP_TICK ≥ 24,000` 도달**이 조건이므로 같은 샘플러를 그대로 재사용하면 **도달을 과소
   보고**한다. (판정식 변경이 아니라 계측 버그 수리다.)
4. **(N63) 표본 필드는 lap442 합집합 이상.** Step0 필드(`ai/count/nation/owner/used`)는 lap442
   (`live`, `max_slot_index`, `rss_kb`, `reserved`, `cap`, `count_cap`)보다 좁다. Step1은
   **lap442 필드 ∪ `ai` ∪ §4-4 메모리 필드**(`vm_size_kb`/`vm_swap_kb`/`host_mem_available_kb`/
   `pid`/`cmdline`)를 기록한다. 그래야 §7 대조표와 lap442 비교가 성립한다.

**기록 의무 재확인(N62):** 변경한 source는 **경로와 sha256**을 함께 남긴다(카드 §8). DLL을
인용할 때는 `supply_bridge_build.json`의 **`dll_sha256`** 을 쓴다 — `bridge_sha256`은
runtime_bridge blob의 해시이지 DLL 해시가 아니다. 재빌드된 DLL 바이트는 기존과 **다르므로**
"기존 goal 동작 유지"는 **동작(소스 수준) 항등**으로만 서술한다.

## 11. lap449 middle addendum — Step1 ACCEPT, Step3 fail-closed 집행 (추가만, 완화 없음)

lap449 middle이 lap448의 Step1을 원시 712표본만으로 **비참조 재계산해 독립 검수**했다
(상세 `docs/history/laps/20260921_lap449_middle_g2_w21_step1_independent_review.md`).
§1의 판정식 (U0)~(U5)는 **실행 전 고정된 그대로이며 이 addendum도 바꾸지 않는다.**

**검수 결과(재계산 불일치 0):** **(U1) PASS 8/8**(첫 표본 tick312 `used` 4,900~4,945) ·
**(U2) PASS**(tick 24,029 도달, `stop_tick_reached`, live `used`>5000 **0표본**, fault/read
failure 0) · **(U3) PASS**(712표본 전부 `live == Σ count`) · **(U4) PARTIAL** ·
카드 §10 의무 4건(N59/N60/N61/N63) **전부 이행 확인**. 종합 `CAP_PROXIMITY_STABLE`(부분 증거).
**(U5)는 미실행**이므로 **이 카드는 아직 CLOSED가 아니다.**

**(U4) 귀속:** `vm_size`가 712표본 전부 3,463,564 KB 단일값 ⇒ 주소공간 해제 0건.
1MB 이상 RSS 하강 26건(합 −197,584 KB) 중 **23건(−131,824 KB)은 swap 증가 동반(+129,340 KB)
⇒ (a) 호스트 회수 확정**, **3건(tick 11,288~11,355, −65,760 KB)은 swap이 그 시점까지 0이라
clean 페이지 축출과 게임 측 `madvise` 해제를 분리할 수 없어 UNKNOWN**으로 남긴다.

### 다음 work 회차가 이행할 것 (순서 고정)

1. **Step3 대조표를 Step2보다 먼저, 게임 실행 없이 만든다 — N66 fail-closed 집행.**
   §7이 요구한 `lap413_stock_comparison.md`가 lap448 run 디렉터리에 **없다**(W19 Step4 ·
   W20 Step3 · W21 Step3로 **3회 연속 누락**). 필요한 입력(lap413 구후보 / stock 대조군 /
   lap442 구 soak / lap448 신후보)은 **전부 이미 파일로 존재**하므로 추가 run이 필요 없다.
   새 run 디렉터리와 **lap448 run 디렉터리 양쪽**에 같은 파일을 둔다.
   **이 파일이 생기기 전에는 Step2를 시작하지 않는다.**
2. **그 다음 Step2**(§6 신후보 저장/로드 왕복). tick 역행 증거 필수(§6-4).
3. **Step2용 스크립트 재사용 전 계측 수리 2건**(판정식 변경 아님):
   - **(N65)** `w21_step1_run.py:551-558`의 verdict 식이 `U3_pass`를 **쓰지 않는다** —
     U3가 깨진 run에서도 `CAP_PROXIMITY_STABLE`이 나온다. 이번 run은 U3 통과라 무영향이지만
     재사용 전에 종합판정 `U1 ∧ U2 ∧ U3`와 일치시킨다.
   - **(U4) 잔여 UNKNOWN 분리**: 표본에 `/proc/<pid>/smaps_rollup`의 `Private_Clean` /
     `Private_Dirty`(가능하면 `Referenced`)를 추가한다. 새 게임 실행 없이 위 −65,760 KB를
     가른다.
4. **자체 lap 기록 필수(N64).** lap440 · lap442 · lap448 **3회 연속 누락**이다. 장기 실행은
   동기 실행 또는 root 소유 exec 세션 — 셸 background로 넘기고 회차를 끝내지 않는다.
5. **서술 정직성(N67):** 이번 시딩은 owner당 op5(type5,cost35)×138 + op6(type7,cost10)×5로
   **비용 기준 99.0%가 단일 type**이다. "혼합 구성"이라고만 쓰지 말고 이 비율을 함께 적는다.

### 경계 재확인 (변경 없음)

§0 그대로다 — (나) 단독으로 G2 완료 주장 금지 · op4 금지 · **144k 카드 발행 금지 유지**
(해제 조건은 이 카드 ACCEPT **그리고** (가) fixture 성립인데, (U5) 미실행으로 전자가 아직 아니다) ·
AI 코드/바이너리 변경이 필요해지는 순간 즉시 strategy 재에스컬레이션.
