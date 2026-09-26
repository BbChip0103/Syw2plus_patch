# 2026-09-22 | lap 464 | 목표 G2 — W24 Step D 실행 (혼합구성 24k soak)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5` / high / work.
  카드 `docs/work/active/G2_MIXED_COMPOSITION_COMBAT_CYCLE_SOAK_LAP461.md`(W24) 실행.
- 가설 / 사용자 관찰: STATUS 「다음 한 가지」 = lap463이 미실행한 Step D(혼합구성 24k soak)를
  이번 회차가 직행 실행하고, N90(allow-list 회귀테스트 0건)을 함께 채운다. lap463이 이미
  써 둔 `step_d_run.py`(669줄)를 발견해 실행 전 전문 검수(§0 op4 금지·§0-3 AI/production
  미변경·§0-5 F4 즉시중단·§6 시딩 구성·§7 판정식 고정)를 마치고 **수정 없이 그대로 실행**했다.
- 예상 PASS/FAIL 조건: 카드 §7 실행 전 고정 판정식 — `ARM_FAIL`(tick<24000 또는 fault),
  `CYCLE_UNSTABLE`(used>5000 또는 live≠Σcount 또는 랩/음수), `CYCLE_STABLE`(전원 [4900,5000]
  ∧ D≥50 ∧ R≥1), `NO_ENGAGEMENT`(cap근접 성립하되 D<50 또는 R=0). 카드 §7 실행 전 기대값:
  "구성 변경이 전투에 영향을 주지 않는다면 D≈4, R=0, verdict=NO_ENGAGEMENT".

## 0. 이전 바퀴(lap463) 검수 (독립, 이번 회차 착수 전)

- `patches/population/runtime_bridge.c` sha256 직접 재계산 = `2a3ad84bcd04a028fad8ed2f713cbcdae10a83549746a5a8f8aa6ada024d04df`
  — lap463 기록과 일치.
- 원본 `/home/dev_00/syw2plus-run/game.exe` sha256 직접 재계산 = `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`
  — 불변, 기록과 일치.
- `ps aux`로 make/pytest/wine/wineserver 잔류 프로세스 **0건** 재확인 — lap463 기록과 일치.
- **ACCEPT**(불일치 0). lap463의 게이트 회수(`make check` 791 passed 등)는 유효한 전제로 채택.

## 1. N90 수리 — allow-list/가드 핀 테스트 추가

신규 `tests/test_g2_runtime_bridge_fixture_type_allowlist_pin.py`(5 test) 추가:
`runtime_bridge.c` 소스 텍스트를 직접 읽어 (a) op5/op6 `fixture_type` allow-list가 정확히
`{5,7,46}`인지, (b) N88이 완화 금지한 `(flags&14)!=0`·width/height 1..8 가드, (c)
`fixture_exceeds_unreserved_supply`·`spawn_accounting_mismatch`·`fixture_locked_after_accounting_failure`
가드, (d) `Place(0x42ecb0)->Gate(0x43eda0)->Spawn(0x443190)` 순서/주소가 그대로인지 핀한다.
**역주입 자체검증** 1건 포함(`test_allowlist_pin_is_not_vacuous`) — allow-list에 `type!=99u`절을
인위 삽입한 변형 텍스트에 대해 정규식이 매치하지 않음을 확인해, 이 핀이 공허하지 않음을
증명한다. 5개 전부 단독 실행 PASS 확인 후 통합 `make check` 1회 실행:
**796 passed 530.49s**(=791+5) + Ruff/compileall/mypy(10 files) all clean + `CONTEXT_PASS`.
`checks/safety.sh check` → `SAFETY_PASS`. 원본 직접 재해시 불변(위 0절과 동일).
**이 회차 source 변경 = 테스트 파일 1개 추가뿐**(`runtime_bridge.c` 자체는 무변경, sha 위와 동일).

## 2. Step D 실행

- 발견: lap463이 중도 실패 전에 `step_d_run.py`(669줄, 2026-09-22 11:40 생성)를 이미 다
  작성해 두고 실행 직전에 회차를 종료했다. 이번 회차가 전문을 읽고 카드 §0(안전경계)·§6(구성
  규칙)·§7(판정식)과 대조 검수했다 — op1/op4 미사용(§0-2), `control_executor.c` 무변경 확인
  로직 내장(§0-3), F4 즉시중단 로직 내장(§0-5), 시딩 구성이 §6-1의 type5×100+type46×45+
  type7×50 = 4920(`P_max`71.1%≤0.85)과 일치, 판정용 D는 §7 정의와 동일 로직, 접촉 기하는
  lap448/452와 동일한 disjoint-anchor 공식(§6-2, 새 가설 없음). **검수 결과 카드와 완전히
  일치해 스크립트를 수정 없이 그대로 실행**했다.
- 실행 방식: 이 세션이 `step_d_run.py`를 harness 추적 백그라운드로 기동한 뒤, 셸을 분리해
  회차를 끝내지 않고 **Monitor로 진행 로그를 직접 지켜보며 대기**했다(INBOX 2026-09-21 01:01
  준수 — lap463의 실패를 반복하지 않기 위해 완주까지 세션을 유지). 디스플레이 `:3973`
  사전 락 확인 후 기동, 잔류 프로세스 없음 확인.
- 진행: `12:07:33` 빌드 시작 → `12:07:40` 후보 재빌드 sha `a10024de…`(기대값 일치) →
  `12:08:10` Xvfb 기동 → PS9→PS7(goal `_custom_game_chain_inject_g2_eight_ai_seed42`,
  `chain_reached_ingame`)→PS3 → op7×8 자원공급 → op5/type5 smoke(trap1) → op6/type46 smoke
  (allow-list 확장 확인) → 8 owner 시딩(type5×100+type46×45(owner0은44)+type7×50) →
  `12:08:17` C1 census(tick61,live1577) → soak 샘플링(1Hz) → `12:14:16` C2 census
  (tick12020,live1623) → `12:20:17` tick24031로 STOP_TICK 도달, C3 census(tick24032,
  live1620) → `12:20:17` 종료 `stop_reason=stop_tick_reached f4_stop=False`.
  총 시딩+soak 실행시간 약12분(`MAX_WALL_S`1800s 한도 내), 게임 실행 **1회**.

## 3. 판정 (카드 §7 그대로 적용, 재채점 없음)

lap462가 쓴 `compute_verdict461.py`를 **무수정**으로 이번 회차 `samples.jsonl`(715표본)에
재실행 — `--samples` 모드로 채점, 음성대조 2건도 같은 실행에서 재확인(**both fired**,
`verdict_gate_negative_control_stepD.json`).

- `final_tick=24031 ≥ 24000` ∧ fault/read-failure 0 ∧ PS3 진입 성공 ⇒ `ARM_FAIL` 아님.
- `live==Σcount` 불일치 0표본(715/715) ∧ `used>5000` 0표본 ∧ 랩/음수 0 ⇒ `CYCLE_UNSTABLE` 아님.
- **D = 12**(스크립트 산출, 활성owner=표본별 `ai==1`). lap448 baseline(D=4)보다 높으나
  `D≥50` 문턱에 크게 못 미침.
- **R = 0**(이번 회차가 C1/C3 census로 독립 계산 — 스크립트는 R을 자동계산하지 않고 외부
  주입만 받으므로, 공통 슬롯 1,565개 전수를 직접 대조: `internal_id` 변경 0건. C1전용 12슬롯
  (죽고 재사용 안 됨)·C3전용 55슬롯(신규/시딩 잔여 배치, 죽은 슬롯 재사용 아님)).
- 시딩 종료시 8/8 owner가 `used∈[4900,5000]` 도달(`U1_pass=true`).
- ⇒ 카드 §7 배타 순서 3번째 조건(`CYCLE_STABLE`: 전원 band ∧ D≥50 ∧ R≥1) 불충족,
  4번째 조건(`NO_ENGAGEMENT`: cap근접 성립하되 D<50 또는 R=0) 충족.

**최종 판정: `NO_ENGAGEMENT`.** 카드 §7 실행 전 기대값(D≈4,R=0)과 사실상 일치 — N87의 예측
(기하 레버는 이미 소진됐고 구성(타입) 축도 실패하면 정답은 `NO_ENGAGEMENT`)이 **구성 축에서도
확인**됐다. cap근접+무결성 안정성(U1/U3 PASS, fault 0, 랩/음수 0)은 **유효한 부분 증거로 유지**
되나, 전투/사망/슬롯재사용 축은 fixture 범위에서 **닫히지 않는다**(카드 §0-3·N87에 따라
이번 세션은 AI/생산 로직에 착수하지 않았다).

## 4. 변경 파일 / source fingerprint / 커밋

- `tests/test_g2_runtime_bridge_fixture_type_allowlist_pin.py` — 신규(N90 수리).
- `patches/population/runtime_bridge.c` — **무변경**(sha `2a3ad84b…` 이번 회차 전후 동일,
  lap463이 만든 allow-list 확장을 그대로 둠).
- `tools/inmm_stub/control_executor.c` — **무변경**(sha `40003d06…`, as-run==종료시 동일,
  `control_executor_c_unchanged=true`).
- 커밋 **0**(`LOOP_ALLOW_COMMITS=0` 재확인). 파일 경로/해시로 이력만 보존.

## 5. 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture

- 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 불변(직접 재해시).
- 후보(재빌드) `a10024de5e1c1cbedcddde0c3b52f5b3a9cf0721ee066542669f4883a1bb2d68`(기대값 일치,
  N=4001 persistence-compat).
- 브리지 DLL(`_inmm.dll`) sha256 `af52568caa0d166d47e4816777d530d703f62df2a3d4e9c46992afd1f77c562e`
  (build-report의 별도 `bridge_sha256` 필드와 혼동 금지 — N62).
- 환경: 격리 전체 게임 사본(`local/runtime/20260922_120740_3457291_0`), 전용 WINEPREFIX,
  전용 Xvfb `:3973`(사전 락 확인), `WINEARCH=win32`, `WINEDLLOVERRIDES=ddraw=b`,
  `SYW2_SUPPLY_PROBE=1`.
- 활성 플레이어: 8/8(`ai==1` 전원, PS3 진입시 확인).
- 지도: 100×100(실측).
- 군대/fixture: owner당 op5(type5×100)+op6(type46×45, owner0은44)+op6(type7×50)+baseline20
  = 4920, `P_max`71.1%(type5). op4 미사용, op7 자원공급(rice/wood 각 1,000,000)만 장부 직접
  조작. op1 미사용(Step D는 rider 아님).

## 6. 실행 명령 / 로그 / 캡처 경로 및 해시

- 실행: `python3 step_d_run.py`(무인자, 상수 in-file) — 경로
  `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/g2_capacity/20260922_lap463_w24_stepD_mixed_composition_soak/`.
- 산출물(같은 디렉터리): `run_summary.json`, `samples.jsonl`(715줄), `census_c1.json`,
  `census_c2.json`, `census_c3.json`, `seed_receipts.json`, `resource_receipts.json`,
  `stepD_orchestrator.log`, `driver_out/wine.log`, `verdict_gate_negative_control_stepD.json`
  (이번 회차 채점 산출), **`w24_mixed_cycle_soak.md`**(카드 §8 fail-closed 요구 산출물, 이번
  회차 작성).
- 판정 스크립트: `.../20260921_lap462_w24_stepA_type_table_inventory/compute_verdict461.py`
  (lap462 원본, 무수정 재사용) — `python3 compute_verdict461.py --samples <run>/samples.jsonl
  --out <run>/verdict_gate_negative_control_stepD.json`.
- 신규 캡처 PNG 없음(이 카드는 화면 캡처를 요구하지 않는다).

## 7. 측정값 / 판정

위 3절과 `w24_mixed_cycle_soak.md` 전문 참조. 요지: `stop_reason=stop_tick_reached`,
`final_tick=24031`, `U1_pass=true`(8/8), `U3_pass=true`(715/715), `f4_violation=false`,
`D=12`, `R=0`, **`NO_ENGAGEMENT`**. (U4) 메모리: `vm_size` 전 구간 상수(주소공간 해제 0),
`vm_swap` 전 구간 0(이번 run은 swap 미관여, lap449와 다름), RSS 1MB+ 하강 6건 전부
Private_Dirty 변화 없음 ⇒ **UNKNOWN**(호스트 clean-page 회수와 게임측 해제 구분 불가, 신규
해소 아님). 최소 rice987,900/wood988,080. `used+reserved>5000` 2,122 owner-표본(N68계열,
판정 외 부수기록).

## 8. 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태

- 회귀: 없음(원본/`control_executor.c` 불변, `runtime_bridge.c`는 lap463 변경 그대로 유지,
  이번 회차는 테스트 1개만 추가).
- 남은 위험: 없음(F4 미발동, 무결성 전수 통과). N90은 **CLOSED**(핀 테스트 5개, 역주입
  자체검증 포함). (U4)는 이번 run에서도 미해결 잔존(UNKNOWN, 새 악화는 아님).
- **독립 검수 대기**: 이 회차는 work 자기실행이며, 다음 middle의 원시 산출물 비참조 재계산이
  필요하다(`samples.jsonl`+census 3종+`compute_verdict461.py` 재실행 권장, 서술/본 파일을
  판정 입력으로 쓰지 말 것).
- 사용자 승인 상태: G2 제품 완료 아님, 마일스톤 승인 아님. `NO_ENGAGEMENT`는 카드 §0-3에
  따라 "(ㄴ) 사용자 승인 없이는 전투축이 닫히지 않는다"는 사실 보고이며, 이번 세션은
  AI/생산 로직 변경에 **착수하지 않았다**.

## 9. 다음 한 가지

1. **다음 middle(Opus5)이 이번 lap464 Step D를 독립 재계산으로 검수**한다 — 원시
   `samples.jsonl`(715)+`census_c1/c2/c3.json`만으로 D/R/U1/U3/무결성을 재확인하고,
   `w24_mixed_cycle_soak.md`의 최종 `NO_ENGAGEMENT`를 ACCEPT/REJECT 판정한다.
2. ACCEPT 시 **W24 카드는 CLOSED**(cap근접+혼합구성+무결성 부분증거 확정, 전투축은
   `NO_ENGAGEMENT`로 정직 보고 완료) — §38 판정5 의무 5건 전부 이행 완료.
   144k 카드 발행 금지 해제 여부와 Step C `RIDER_NO_REPRO`가 연 **lap404(가) 재심**
   (§5 방법론 유보 포함)을 strategy/middle이 함께 판단해야 한다.
3. 전투축의 유일한 남은 기술 경로는 **(ㄴ)**(2026-09-21 00:20 지시의 명시 예외 승인) —
   여전히 **사용자 전권 대기**이며 모델은 착수하지 않는다.
