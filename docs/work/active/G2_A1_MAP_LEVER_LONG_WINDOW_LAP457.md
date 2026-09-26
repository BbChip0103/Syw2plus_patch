# W23 — A1(지도 확대) 단일 arm 24k 연장 (lap457 middle 발행)

- 발행: lap457 middle (Claude Code `claude-opus-5` / high), 2026-09-21 KST
- 상위 근거: `G2_NATURAL_ARRIVAL_FIXTURE_LEVER_PROBE_LAP455.md`(W22) **§5 `PARTIAL` 조항**
  ("그 arm 하나에 대한 후속 probe 1건(1 arm, 1 회차)만 명시하고 끝낸다. 재계획 아님"),
  lap456 work 실행 결과, lap457 middle 독립검수(**ACCEPT** + **N77~N80**),
  `loop/ESCALATE_SOL` §35.
- 실행 역할: **work** (Claude Code `claude-sonnet-5` / high). 이 카드는 middle이 쓴 계획이며
  middle은 구현하지 않는다. work가 실행하고 **다음 middle이 독립 검수**한다.
- 후보: `a10024de5e1c1cbedcddde0c3b52f5b3a9cf0721ee066542669f4883a1bb2d68`
  (핀 복사 금지 — 현재 source 재빌드로 SHA 확인, N53).

## 0. 이 카드가 답하는 단 하나의 질문

> **W22에서 가장 높은 바닥을 만든 레버(A1, 지도 140×140)의 `used` 증가가 tick 8,000 이후에도
> 유지되는가, 아니면 baseline과 같은 모양으로 감쇠하는가?**

`SUSTAINED` / `DECAYED` / `LEVEL_SHORT` / `ARM_FAIL` 중 하나로 끝낸다. 이 카드는 G2 완료를
주장하지 않고, **144k 카드를 발행하지 않으며**, 게임 AI 코드/바이너리를 바꾸지 않는다.

## 1. 왜 "그냥 길게 돌린다"가 아니라 판정식을 바꾸는가 (N77)

lap457이 카드 §5의 `r_slow` 기준을 **lap442의 24k baseline 원시표본에 역적용**했다:

| 구간 | lap442 baseline owner1 증가율 |
|---|---|
| 2k→4k | 0.0371 |
| 4k→6k | 0.0460 |
| **6k→8k** | **0.0545** ← 정점. `r_req` 0.0341을 1.6배로 **통과** |
| 8k→16k | 0.0189 |
| 16k→24k | **0.0075** |

그 owner의 tick 7,986 `used`는 **359**(= 카드 고정상수와 정확히 일치)이고, 0.0545를 선형
외삽하면 tick 93,185에 5,000 도달을 예측한다. **그러나 같은 run에서 그 owner가 tick 24,030에
실제 기록한 값은 570이다**(예측 1,233의 46%).

⇒ **`r_slow`(6k→8k)는 5,000 도달 여부에 대해 예측력이 없다.** 카드 §2-5가 "감속"이라고 이미
적은 그 baseline조차 이 기준을 통과한다. W22 6 arm이 전부 `r_slow`를 넘긴 것은 레버의 성과가
아니라 **전 arm이 아직 증가율 정점 이전 구간에 있었다**는 뜻이다(A1도 0.0815→0.0935→0.1104로
단조 증가 중이었다).

따라서 이 카드는 **후반 구간 증가율**로 잰다. 그것이 144k 지평에서 유일하게 의미 있는 양이고,
baseline에서 0.0075 대 필요값 0.0369로 **4.9배 차이가 나 판별력이 확실**하다.

## 2. 조작 — A1 하나, W22와 완전히 동일한 설정

| 항목 | 값 |
|---|---|
| goal | W22 A1이 쓴 `_custom_game_chain_inject_g2_eight_ai_d4a1_seed42` 그대로 |
| 로비 config | `d42=0, d44=2, d46=0, d48=0, d4a=1, d4c=0, seed=42` |
| 지도 | 런타임 `0xb3de34`/`0xb3de36` 실측으로 **140×140 재확인** |
| owner | 8 전원 `ai=1` (owner0 포함, `(20,2)` 이탈 확인 — N59) |
| 자원 | op7로 rice/wood 1,000,000 (8 owner 전원), **op4 금지·시딩(op5/op6) 금지** |
| 창 | **tick 24,000 이상** |

- **새 레버값 추가 금지.** `d4a=2`를 포함해 어떤 새 값도 이 회차에서 시도하지 않는다
  (lap456이 지적한 대로 `d4a`는 0과 1 외에 검증된 값이 없다).
- **다른 arm 재실행 금지.** 비교 baseline은 이미 파일로 있다(W22 A0, lap442 24k).
- 소스 변경이 필요 없어야 정상이다. A1 goal 리터럴은 lap456이 이미 추가했다. 만약 계측을 위해
  `control_executor.c`를 다시 건드려야 한다면 **N80-3을 먼저 읽어라** —
  `owner0_ai`의 기본값이 opt-in에서 **opt-out으로 뒤집혀 있어**, `is_g2_eight_goal()`에 리터럴을
  추가하면 owner0 AI=1을 자동으로 얻는다.

## 3. 계측 (W22 §4를 상속 + N78 수리)

1. 표본 필드: `tick, t, live, sum_count, owners[{owner, ai, rice, wood, count, used,
   reserved, cap, count_cap}]` — W22와 동일(축소 금지).
2. fingerprint: `d42/d44/d46/d48/d4a/d4c/seed`, 런타임 `map_width`/`map_height`,
   활성 owner 수, `ai_flags_at_ps3`, `dll_sha256`(`bridge_sha256` 아님 — N62),
   후보 EXE SHA, `pid` + `cmdline`.
3. **N78 수리(이번 카드의 새 요구):** 모든 지표는 **목표 tick 최근접 표본**에서 계산하고,
   산출물에 **그 표본의 실제 tick과 owner id를 함께 적는다.** lap456은 "tick 8,000 시점"
   대신 최종 표본에서 계산해 A1 `U_min`이 661 대신 676으로 보고됐다(판정은 불변이었지만
   이번에는 경계 판정이 있으므로 계측점을 흐리지 말 것).
4. **N80-1 수리:** run 디렉터리에 `control_executor.c`의 **as-run sha256**을 기록하고,
   회차 종료 시점 repo 파일 sha256과 **둘 다** lap 기록에 적는다. 다르면 diff 결과를 적는다.
5. 하지 말 것: `max_slot_index_seen`을 점유/확장 근거로 쓰지 않는다(N55).
   `tools/inmm_stub/` 진단 채널의 유닛 수를 판정 근거로 쓰지 않는다(W21 §5-2).

## 4. 실행 전에 고정하는 판정식 (사후 재채점 금지 — W17 선례)

활성 owner 집합 = `ai_flags_at_ps3`가 1인 owner(A1은 8명 전원 예상).

- `U_min24` = **tick 24,000 최근접 표본**의 `used` 최솟값, 그 owner를 `o*`로 둔다.
- `U_med24` = 같은 표본의 중앙값.
- `r_late` = `o*`의 **tick 16,000 최근접 → tick 24,000 최근접** 구간 `used` 증가율(`used/tick`).
- `r_need` = `(5000 − U_min24) / (144,000 − 24,000)`.
  (W22 §1-5와 동일 — **외삽 산술이며 144k 실행 승인이 아니다.**)

**판정 (이 순서로 배타 적용):**

1. **`ARM_FAIL`** — tick 24,000 전에 fault/crash/진입 실패. fault tick과 마지막 표본을 적고
   끝낸다. 되살리려고 다른 경로를 즉흥 패치하지 않는다.
2. **`DECAYED`** — `r_late < r_need`. ⇒ **가장 유망한 fixture 레버조차 baseline과 같은 모양으로
   감쇠한다** ⇒ (가) 자연 도달은 **fixture 축에서 `NOT_FEASIBLE`**. W22 §7 되물음
   (ㄱ)/(ㄴ)/(ㄷ)를 기존 2건(lap404 (가)/(나), F4 (B)/(C))과 묶어 그대로 승격한다.
   **모델은 AI 변경에 착수하지 않는다.**
3. **`SUSTAINED`** — `r_late ≥ r_need` **그리고** `U_min24 ≥ 1,500`.
   ⇒ fixture 축이 살아 있다. strategy에 보고하되 **제품 완료도 144k 승인도 아니다.**
4. **`LEVEL_SHORT`** — `r_late ≥ r_need`이지만 `U_min24 < 1,500`.
   ⇒ 수치를 그대로 보고하고 **새 arm을 만들지 않는다.** strategy가 판단한다.

**고정 상수 `1,500`의 근거(실행 전에 박는다):** baseline의 24k 바닥은 **570**이다. A1이
baseline과 **같은 감쇠 모양**을 따른다면 8k 바닥의 배율(570/359 = 1.588)이 그대로 적용돼
`U_min24 ≈ 1,050`(tick-8,000 기준 661 사용) ~ **1,073**(lap456 계측점 676 사용)이 나온다.
1,500은 그 "같은 모양" 기대값의 약 1.43배이므로, 넘으면 **감쇠 모양 자체가 달라졌다**는
뜻이다. 참고로 `U_min24`=1,500일 때 `r_need`=0.0292이고 baseline `r_late`는 0.0075다.

**이 기대값 1,050~1,073을 산출물에 실행 전에 적어라.** 실행 후에 "예상대로였다"를 쓰기 위한
사후 서사를 막는 장치다.

**부수 기록(판정에 쓰지 않음, 반드시 보고):** `U_min8`(tick 8,000 최근접)과 그 owner.
W22 A1은 **owner5 / 661**이었다. 같은 시드·같은 설정이므로 카드 §2-3(결정성)대로라면
재현돼야 한다. 크게 다르면 **arm 간 차이를 레버에 귀속한 W22의 전제가 약해진다** —
그 사실 자체가 중요한 산출물이니 숨기지 말고 적어라.

## 5. fail-closed 산출물 (없으면 다음 middle은 내용을 보지 않고 REJECT — N66 선례)

`temp/Syw2plus_patch/g2_capacity/<이번 run 디렉터리>/w23_a1_long_window.md`

최소 내용:
- 설정 fingerprint 표(§3-2 전 항목, 실측 `map_width`×`map_height` 포함)
- 실행 전 기대값 `U_min24 ≈ 1,050~1,073`(§4)과 그 근거 한 줄
- `U_min8` / `o*` / `U_min24` / `U_med24` / `r_late` / `r_need` — **각각 계산에 쓴 표본의
  실제 tick을 함께** (N78)
- 증가율 구간표: 2k→4k, 4k→6k, 6k→8k, 8k→16k, 16k→24k (baseline 대조 열 포함:
  0.0371 / 0.0460 / 0.0545 / 0.0189 / 0.0075)
- 무결성: `live==Σcount` 불일치 수, `used>5000` 표본 수, tick 역행 수, 최소 rice/wood
- 마지막 줄에 §4 판정식을 적용한 **최종 한 단어**
- 수치를 모르면 `UNKNOWN`이라고 쓰되 **행 자체를 비우지 않는다**

## 6. 운영 규칙

- 창은 약 12분(33.33 tick/초 × 24,000) + setup이라 **동기 실행**으로 60분 상자 안에 든다.
  셸 background로 넘기고 회차를 끝내지 않는다(INBOX 2026-09-21 01:01). "background 실행 중"
  문구만으로 활성 프로세스를 주장하지 않고 PID/산출물 갱신을 확인한다.
- **work는 자체 lap 기록을 `docs/history/laps/`에 남긴다(N64).** lap456이 3회 연속 누락을
  끊었다 — 되돌리지 말 것.
- 격리 전체 게임 사본 + 전용 Wine prefix + 빈 Xvfb display. 원본/참고 저장소 쓰기 금지,
  전역 pkill 금지, 다른 프로세스/로그 정리 금지.
- 커밋 금지(`LOOP_ALLOW_COMMITS=0`). 변경 파일은 경로와 sha256으로 남긴다.
- source를 바꿨으면 통합 경계에서 `make check` 전체 1회 + "이번 회차에 source를 바꿨다"를
  명시(N22). 안 바꿨으면 표적 테스트 + `checks/safety.sh check` + **원본 직접 재해시**만.
- 후보는 **재빌드로 SHA 확인**(N53). 원본 `b56986e0…c9c08a8ac` 불변 재확인.
- `local/runtime`이 82G/37개다(여유 255G). 이번 1회 실행은 정리 없이 진행하되, 여유가
  10G 아래로 떨어지면 lap429 선례대로 **실행 전에 중단하고 보고**한다.

## 7. 이월된 미수리 계측 결함 (이 카드가 상속하지 않더라도 소멸하지 않는다)

`temp/.../20260921_lap452_w21_step2_save_load_roundtrip/w21_step2_run.py`의
**N71**(창 전용 라벨이 24k 판정과 같은 문자열 `CAP_PROXIMITY_STABLE`, `u1_pass` 하드코딩),
**N72**(`U5_pass`가 `new_after_load` 미게이트), **N73**(presave 스냅샷이 op2 save 이전)은
W22가 새 스크립트를 썼으므로 이번에도 손대지 않았다. **그 파일을 다시 쓰는 회차가 진다.**
추가로 **N80-3**(`test_g2_legacy_goals_compute_identical_config_to_pre_w22_source`가 C 소스를
읽지 않아 C 변경으로는 실패할 수 없음)은 `tests/test_g2_eight_owner_setup.py`에 살아 있다.

## 8. 이 카드가 끝나도 **아직 아닌 것**

G2 제품 완료 아님. `SUSTAINED`여도 그것은 "이 레버로 계속 갈 수 있다"이지 "5,000에 도달했다"가
아니다. 미검증으로 남는 것: 실제 5,000 자연 도달, 144k, 건물 포함 혼합 구성, 전투/사망/재생산
순환, LAN/지원 동기화. 사용자 마일스톤 승인(3단)은 별개다.
