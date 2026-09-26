# W11 — `0x00414133` fault: H1 기각 후 H2(stale 참조) 결판 (발행: lap418 middle, 수행: 다음 work 회차)

- 발행자 / 역할: lap418 Claude Code `claude-opus-5` / high / middle(진단·계획·확인).
  근거는 `docs/history/laps/20260921_lap418_middle_g2_pb_independent_review.md`.
- 수행 역할: **work (Sonnet5/high)**. 이 카드는 **실행 probe 1회 + 판정**이다. 재계획 회차로 되돌리지 않는다.
- 선행 상태: W10 P-A(lap416) 실행됨, P-B(lap417) 실행됨 → lap418이 P-B를 독립 검수해
  **`0x00422dc0` 경로와 그에 딸린 수리 카드를 무효화**했다. W10의 P-C는 폐기한다.
- 목표 연결: G2 = 활성 8인 각각 전비 5000. 이 카드는 "원본 생산·AI 경로에서 후보가 죽지 않는다" 축이다.
- 우선순위 근거: INBOX 2026-09-21 00:20 KST — G2 성립 전까지 G1/G4 잠정 중단, G3는 계속 포기 범위.

## 0. 이 회차는 반드시 실제 실행 회차다

lap417·lap418이 연속으로 제품 코드/실행 증거 0이다. PROMPT ③의 "연속 최대 2회"에 도달했으므로
**이 회차는 게임을 실제로 실행해 증거를 만든다.** 정적 분석만으로 끝내야 할 사유가 생기면 착수하지
말고 strategy(Astra/Fable)/Sol 판정을 먼저 받는다.

## 1. lap418이 바이트로 확정한 것 (재조사 금지)

1. **`FUN_00422dc0`은 C++ 전역 정적 생성자다.** `.data` 초기화 표 `[0x004ec000,0x004ec1bc)`(110항목)의
   `0x004ec02c` 항목 → thunk `0x00422db0: jmp 0x00422dc0`, 그 표를 `0x004de170`(`_initterm`)이
   `0x004de0ac`에서 훑는다. **main 이전 1회** 실행이며 매 틱이 아니다.
2. **그 루프는 풀 메모리를 건드리지 않는다.** `FUN_0048aff0`은 `mov esi,ecx; call 0x4119f0; mov eax,esi; ret`,
   `FUN_004119f0`은 `mov eax,ecx; ret`(빈 생성자). `esi`는 `0x758`씩 전진하나 역참조 0회.
   ⇒ **`0x00422dc7`의 `0x4B0`→`0xFA1` 수리는 no-op이다. 착수 금지.**
3. **나머지 두 site는 fixture에서 도달하지 않는다.** `FUN_004183a0` 호출자 3곳
   (`0x0043ff8d` 매치설정 / `0x0049ba0e`·`0x004a863f` UI), `FUN_00444ef0` 호출자 8곳
   (전부 `0x004be000~0x004c2000`). lap417·lap418이 독립적으로 같은 집합을 얻었다.
4. **후보 기준 `.text` 0x4B0은 즉치 35 + 메모리 변위 1 = 36곳**이며 전부 분류됐다
   (후보 고유 `0x0041b56d`는 owner 개수 cap 250→1200 기록으로 풀과 무관).
5. **4001 슬롯 풀 구간 `0x0108c000..0x017b8658`은 전부 후보 `.data`(`..0x017c6f04`) 안**이다.
6. ⇒ **H1("잔존 1200-bound 순회가 슬롯 ≥1200의 초기화/수명주기를 건너뛴다")은 기전 부재로 기각.**
   468 생존 중 **1기만** 돌발 손상되는 모양도 구간 전체 초기화 누락과 맞지 않는다.

## 2. 이번에 가를 가설

- **H2 (주 가설):** `0x0040be55`가 `0x00414000`에 넘기는 유닛이 **live 집합에 없는 슬롯**
  (사망 직후 / 미할당 / 재할당된 슬롯)이다. 값 손상이 아니라 stale 포인터·수명주기 문제.
- **H1r (H1 잔존형):** 손상 순간에도 slot 3565는 살아 있었고 `+0x692`만 외부에서 덮였다(wild write).
  이 경우 원인은 "1200-bound 순회"가 아니라 **그 유닛에 인접한 무언가를 쓰는 주체**다.
- **H3:** 원본 고유 엣지 케이스(후보 회귀 아님) ⇒ stock에서도 재현돼야 한다. 이번엔 보류.

## 3. 수행 순서와 측정식 (먼저 적고 시작한다)

### P-D. 단일 실행 probe (lap416 하네스 재사용, 게임 코드 변경 0)

`temp/Syw2plus_patch/g2_capacity/20260921_lap416_fault_root_cause_pa_run2/movement_state_probe.py`를
복사해 다음 세 가지만 바꾼다. **새 probe를 처음부터 쓰지 않는다.**

1. **생존/사망 양쪽 기록.** 현재는 `absmove > 100`인 것만 `anomalies`에 남긴다. 슬롯 3565를 포함한
   **추적 대상 슬롯 집합**에 대해서는 생존 플래그와 관계없이 매 샘플 전 필드를 남긴다.
2. **N31 정정 흡수.** `max_abs`를 `absmove > 100` 분기 **밖에서** 갱신해 밴드별 `|+0x692|`의 **실제**
   최댓값을 남기고, 추가로 분포(예: 0 / 1~50 / 51~100 / >100 구간 개수)를 샘플마다 기록한다.
   ⇒ "매치 내내 정확히 0"인지 "±100 안에서 커지고 있었는지"를 이번에 확정한다.
3. **크래시 창 조밀 샘플링.** tick **11,860~11,928**은 **매 tick** 샘플한다(lap416은 17~18 tick 간격이라
   onset이 17 tick 창 안에 묻혔다). 그 이전 구간은 lap416과 같은 간격으로 둬 실행 시간을 늘리지 않는다.

fixture는 **lap413/416과 동일**하게 고정한다: op7(원본 SetResource) resource-only, 7 AI, N=4001,
동일 seed/goal, 신규 prefix/display. `op=6` 직접 주입 금지.

### 판정식 (실행 전에 고정)

- **H2 지지:** 손상이 처음 관측되는 tick에서 slot 3565의 생존 플래그가 **false**이거나, 그 직전 구간에
  3565의 사망→재할당(owner/type 변화)이 있다. ⇒ 다음 카드는 수명주기/해제 경로.
- **H1r 지지:** 손상 tick에도 3565가 **계속 살아 있고** owner/type이 불변인데 `+0x692`만 튄다.
  ⇒ 다음 카드는 `0x0108c000 + 0x758*3565 + 0x692`(= 절대주소 계산해 기록) 인근에 쓰는 주체 추적
  (예: 이웃 슬롯 오버런, 보조 인덱스 off-by-N).
- **어느 쪽도 아니면**(예: 손상 tick에 3565가 아닌 다른 슬롯이 먼저 튄다) 그 사실을 그대로 적고
  **추측 수리를 쌓지 않는다.**
- 이 probe 하나로 H2 / H1r 중 하나는 **반드시** 결론난다. 결론 없이 다음 단계로 가지 않는다.

### 실패 예산

실패 가설 2회 또는 60분 안에 `FEASIBLE`/`NOT_FEASIBLE`/`BLOCKED`로 판정한다.
probe가 두 번 연속 샘플링에 진입조차 못 하면(= lap415형 하네스 실패) 그것은 가설 판정이 아니라
**하네스 blocker**로 적고 멈춘다.

## 4. 대상 고정 (변경 금지)

- 후보 `4331d9cd646c03a0102394727894beaf893e5b9aa3505c4ddb41eb26a4ef9bbe`,
  원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(읽기 전용, 실행 전후 재해시).
- stock 대조 `0a1da2263ff099b9fc35d8c63bb82bbefec6dffbae0dcc7458e32887f3f34ad3`.
- 목표 숫자(8인/5000/4001), 핀 SHA, baseline/golden 변경 금지. `4001`은 공학 시험값이다(N23).
- `0x00414133` 명령 자체 패치 금지(W10 §1.4: 원본과 바이트 동일).
- `roster_add 0x0043ee39`의 `cmp ax,0x4B0` 변경 금지(lap397: owner당 개수 상한).
- `0x00422dc7` 수리 금지(lap418: no-op으로 확정).
- 격리: `tools.runtime_env.prepare()` 신규 사본 + prefix + 빈 display. 종료 후 잔류 0.
- **장기 probe는 모델 세션이 직접 기다린다**(INBOX 2026-09-21 01:01 운영 규칙).
  셸 background로 띄우고 회차를 끝내지 않는다. PID/산출물 갱신으로 실행을 확인한다.

## 5. 범위 밖

- strict cap 정책 / 전비 장부 32bit(F4·N19·되물음) — 사용자 답변 대기.
- LAN(P4), G1, G4, G3(중단), 풀 최종 용량 결정, soak 번들 검증기 승격(N24).
- H3(stock 재현) — H2/H1r이 갈린 뒤에 판단한다.
- 되물음1 귀속 probe(stock에서 `used=5000,reserved=10` 재현)는 아직 미수행이며, 여유가 있으면
  20분 상자로 끼울 수 있으나 §3을 미루는 사유가 되면 안 된다.

## 6. 검사

- 표적: `pytest patches/population/test_g2_full_capacity_persistence_compat_v1.py
  patches/population/test_runtime_bridge_contract.py -q` (기준선 **6 passed**).
- source를 바꿨으면 통합 경계에서 `make check` 1회(현재 기준선 **786**). 안 바꿨으면 재실행하지 않되
  **"이번 회차에 source를 바꾸지 않았다"를 기록에 함께 적는다**(N22 재발 방지).
- 매회 `checks/safety.sh check` → `SAFETY_PASS`, 원본 2경로 재해시 불변, 잔류 프로세스 0.
- 산출물에 **"이 회차 결론은 `inmm_stub.c`/`ai_shadow.c`/`sfx_hook.c`/`control_executor.c` stub 채널에
  근거하지 않는다"**를 명시한다(N21 재발 방지).
- **기록 의무(N29 재발 방지):** 이 회차는 `docs/history/laps/`에 LAP_TEMPLATE 필드로 기록하고
  `docs/STATUS.md`를 갱신한다. INBOX에만 적고 끝내지 않는다.

## 7. 산출물

`temp/Syw2plus_patch/g2_capacity/<날짜>_lap<N>_fault_h2_stale/`에 두고 lap 번호는 `loop/.lap_counter` 값을 쓴다.
재사용 가능한 선행 산출물: lap416 하네스
`temp/Syw2plus_patch/g2_capacity/20260921_lap416_fault_root_cause_pa_run2/`,
lap418 정적 근거 `temp/Syw2plus_patch/g2_capacity/20260921_lap418_middle_review/`
(`findings.json`, `xref418.json`, `scan418_sites.json`).

## 8. 중단 조건

- 포인터 손상/저장 이상/원본 변조가 보이면 숨기지 말고 수치와 함께 보고하고 멈춘다.
- baseline·핀·golden을 고쳐 통과시키지 않는다. 자기 결과를 자기가 최종 승인하지 않는다.
- H2와 H1r이 **둘 다** 기각되면 추가 추측 수리 금지 — 근거를 모아 `loop/ESCALATE_SOL`에 올린다.
