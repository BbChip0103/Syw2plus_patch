# 2026-09-21 | lap 452 | 목표 G2 (W21 Step2)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5` / high / work(실무).
  `loop/PROMPT.md` ①~⑥, `docs/work/active/G2_CAP_PROXIMITY_SEEDED_SOAK_LAP445.md` §6·§11(lap449/451
  addendum "다음 work 회차가 이행할 것" 순서②③), `loop/ESCALATE_SOL` §31 §5 지시에 따라 진행.
- 가설 / 사용자 관찰: lap451 middle이 Step3 대조표를 ACCEPT하고 N66을 CLOSED한 뒤, 카드 §11
  순서②(Step2 신후보 저장/로드 왕복)를 다음 work의 첫 실행 항목으로, 같은 회차에 N69/N70 정정·
  N65 수리·(U4) 잔여 분리계측(smaps_rollup) 3건을 붙이라고 지시했다. 이번 lap은 그 4건을 전부
  수행한다. 게임 코드 변경 없음(진단 브리지 프로토콜 op2/op3/op5/op6/op7만 사용, WriteProcessMemory
  호출 0).
- 예상 PASS / FAIL 조건: (U5) 저장 직전(presave)과 로드 직후(postload) 사이에 owner별
  `(count,used,reserved)`와 슬롯 단위 `(slot,internal_id,type,owner)`가 소실·불일치 0이고, 로드가
  실제로 상태를 되돌렸다는 tick 역행 증거(단일 op3 호출의 `tick_before>tick_after`, 그리고
  preload→postload 전체 상태 tick 역행)가 함께 나오면 PASS. 역행 증거 없이 소실만 0이면 "로드가
  아무 일도 안 함"과 구분 불가하므로 FAIL로 취급한다(카드 §6-4).

## 변경 파일 / source fingerprint / 커밋

- **제품/도구 source 변경 0.** `patches/`, `tools/`, `tests/`, `docs/work/active/*.md` 전부 무변경.
  이번 회차는 새 표준 산출물 스크립트 1개(`temp/` 안, git 비추적)와 기존 fail-closed 대조표 2개
  사본(둘 다 `temp/` 안)만 편집했다. **N22대로 통합 `make check`는 생략**한다
  ("이번 회차 source를 바꾸지 않았다").
- 신규: `temp/Syw2plus_patch/g2_capacity/20260921_lap452_w21_step2_save_load_roundtrip/w21_step2_run.py`
  (lap448의 `w21_step1_run.py` 부트스트랩/시딩 시퀀스를 그대로 재사용하고 Step2 저장/로드 왕복 +
  N65 수리된 `compute_verdict()` + smaps_rollup 계측을 추가한 신규 스크립트, git 비추적).
- 정정: `temp/Syw2plus_patch/g2_capacity/20260921_lap450_step3_stock_comparison/lap413_stock_comparison.md`
  및 `temp/Syw2plus_patch/g2_capacity/20260921_lap448_w21_step1_cap_proximity_soak_root_recovery/lap413_stock_comparison.md`
  — 두 경로 동일 내용으로 N69(lap442 도달 tick 23,997→**24,030**, 각주로 완화 서술)·N70(stock
  "정상 종료성 정지"→"tick 정지+유닛0, 원인 UNKNOWN") 반영. 편집 후 두 파일 SHA256이 다시 동일함을
  `sha256sum`으로 확인: **`f733d46e49f41c89427a8af2ea16674b6d50e69ca1c794f24af6a11152d8e3d0`**
  (편집 전 공통 SHA `1a439f094f52ceccc904a01fc7169fc6fbc80533978984902b5bf787e6a7d577`에서 변경).
- 커밋: 없음(`LOOP_ALLOW_COMMITS` 기본0, uncommitted로 보존).

## 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture

- 원본 SHA: `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(런 전/후 직접 재해시
  일치, `source_sha_before==source_sha_after==True`).
- 후보 SHA: `a10024de5e1c1cbedcddde0c3b52f5b3a9cf0721ee066542669f4883a1bb2d68`
  (핀 복사 아님 — `g2_full_capacity_persistence_compat_v1.build_candidate`로 **현재 source에서 재빌드**,
  N53 규칙 준수, 재빌드 SHA가 카드에 적힌 값과 정확히 일치).
- 격리 환경: `tools.runtime_env.prepare()`로 신규 전용 복사본+Wine prefix
  (`run_dir=local/runtime/20260921_101146_3574682_0`), 전용 display `:3972`(사전 lock 확인 후 사용,
  종료 후 lock 회수 확인). 진단 브리지는 N=4001 재배치 주소로 재빌드
  (`unit_pool_base=0x0108C000`, `unit_existence_base=0x017B8658`, `dll_sha256=41839d97…`).
- 활성 플레이어: 신goal `_custom_game_chain_inject_g2_eight_ai_seed42`로 8 owner 전원
  `ai=1`(`ai_flags_at_ps3=[1,1,1,1,1,1,1,1]`, N59/N60 계보와 일치).
- 지도: 100×100(`map_width=map_height=100`), 8 owner disjoint 앵커
  `[(2,2),(27,2),(52,2),(77,2),(2,52),(27,52),(52,52),(77,52)]`(카드 §4-1 disjoint 요구 충족).
- fixture: op7(자원 무한, SetResource만) 8owner → op5 `wanted=1` 스모크(함정1 준수, `ok=true`) →
  owner당 op5(type5,cost35)×138 + op6(type7,cost10)×5, gate-legal(원본 `Place 0x42ecb0`/
  `Gate 0x43eda0`/`Spawn 0x443190` 경로), op4(장부 직접 write) 사용 **0**.

## 실행 명령 / 로그 / 캡처 경로 및 해시

- 실행: `python3 temp/Syw2plus_patch/g2_capacity/20260921_lap452_w21_step2_save_load_roundtrip/w21_step2_run.py`
  (동기 실행, 셸 background로 회차를 끝내지 않음 — Bash 도구의 `run_in_background`로 띄운 뒤 같은
  세션 안에서 완료까지 대기했다. INBOX 01:01 운영 규칙이 문제 삼은 것은 "회차를 끝내며 자식이 정리되는
  경우"이고, 이번은 세션 종료 없이 대기했으므로 다르다).
- 산출물 디렉터리: `temp/Syw2plus_patch/g2_capacity/20260921_lap452_w21_step2_save_load_roundtrip/`
  (`run.stdout`, `step2_orchestrator.log`, `run_summary.json`, `trace.jsonl`, `presave_snapshot.json`,
  `preload_snapshot.json`, `postload_snapshot.json`, `resource_receipts.json`, `seed_receipts.json`,
  `bridge_build/`).
- 저장 파일: `local/runtime/20260921_101146_3574682_0/game/save/save092.dat`
  (3,944,402 B, SHA `76680017eb8f9e695036ab6629d9b7de8ca74520549ab77f3a66f6f13b8553e1`),
  오프셋 `0x38` 마커 `S2P1N4K1` **일치 확인**(`marker_match=true`).
- exit code 0 (`EXIT_CODE=0` in `run.stdout`).

## 측정값 / 판정

**(U5) PASS.** 시딩 종료 시 8 owner 전원 `used∈[4900,4935]`(`U1_owners_in_4900_5000=8/8`, 이번 run
자체 재확인 — 카드의 공식 U1/U2/U3는 이미 lap449/451 ACCEPT로 확정되어 재채점하지 않는다).

- **presave**(op2 save 직전, tick45): live **1,161**, owners `used=[4935,4900,4900,4900,4900,4900,4900,4900]`.
- **op2 save 결과**: `tick_before=46, tick_after=46`(저장은 tick을 바꾸지 않음, 정상), `ok=true`.
- 저장 후 **45초 실시간 대기**(트레이스 30샘플, tick·장부 단조 진행 확인, `live_count_match` 전 표본
  참).
- **preload**(op3 load 직전, 대기 후): tick **1,557**, live **1,186**,
  owners `used=[4965,4920,4930,4930,4930,4930,4940,4945]` — presave 대비 tick +1,512, 실질 생산
  계속되어 live/used 소폭 증가. **살아있는 게임이 계속 진행했다는 직접 증거.**
- **op3 load 결과 — 단일 호출 내부 tick 역행**: `tick_before=1557 → tick_after=46`
  (`load_tick_regression_within_call=True`). 브리지의 `tick_before`는 `load()` 호출 **직전**,
  `tick_after`는 반환 **직후** 값이라 이 한 줄만으로 로드가 실제로 엔진 상태를 tick46 시점으로
  되돌렸음을 증명한다(별도 연속 폴링 없이도 원자적 증거).
- **postload**(load 직후 즉시): tick **48**, live **1,161**,
  owners `used=[4935,4900,4900,4900,4900,4900,4900,4900]` — **presave와 사실상 동일**
  (tick 45→48은 postload 스냅샷을 잡기까지 실시간 폴링 지연 동안 자연 진행된 2틱, live/used
  완전 일치). `tick_regression_full_state=True`(postload.tick(48) < preload.tick(1557)),
  `postload_close_to_presave=True`.
- **슬롯 단위 전수 대조(presave 1,161개 vs postload 1,161개)**: `lost=0`, `mismatched=0`,
  `new_after_load=0`. presave에 있던 슬롯이 postload에 정확히 그대로 있고(`internal_id`/`type`/
  `owner` 전부 일치), 손실도 초과 생산도 0건 — **완전 결정론적 원복**.
- **owner 장부 대조**: `owner_ledger_mismatches=[]`(8 owner `count`/`used`/`reserved` 전부
  presave==postload).
- **종합 (U5) = PASS.**

**post-load 짧은 안정성 확인(카드 공식 U-series 아님, 보너스 30초 창):** 30표본, fault 0, cap 초과
0, 장부 불일치 0 표본 → `post_load_window_verdict=CAP_PROXIMITY_STABLE`(N65 수리된
`compute_verdict()`로 계산, `U1 and U2 and U3` 전부 반영). 이것은 카드의 24k soak를 대신하지
않는다 — lap449/451이 이미 ACCEPT한 U1~U3와 별개의, "왕복 직후 게임이 계속 정상 동작하는가"에
대한 저비용 부가 확인이다.

**N65 수리**: `w21_step1_run.py:551-558`의 verdict 식은 `U3_pass`를 쓰지 않는 결함이 있었다.
`w21_step2_run.py`의 `compute_verdict(u1_pass, u2_pass_no_fault_no_overcap, u3_pass)`는
`U1 ∧ U2 ∧ U3`를 명시적으로 강제한다. **카드의 공식 U1~U3 판정식 자체는 바꾸지 않았다**(lap449/451
ACCEPT 유지) — 이번 수리는 "다음에 이 verdict 로직을 재사용할 스크립트"에 적용된 코드 수리다.

**(U4) 잔여 계측**: 이번 run의 모든 표본(대기창 30개 + post-load창 30개, 합 60개)에
`private_clean_kb`/`private_dirty_kb`/`referenced_kb`(`/proc/<pid>/smaps_rollup`)를
`rss_kb`/`vm_size_kb`/`vm_swap_kb`/`host_mem_available_kb`와 함께 기록했다(예:
sample t=45.4s `rss=240,064KB, private_clean=77,480KB, private_dirty=143,680KB,
referenced=240,064KB`). 이번 run은 60초 규모라 RSS 하강 이벤트가 관측되지 않아(장기 soak가
아니므로 예상된 결과) lap448의 −65,760KB 구간을 **소급 해명하지 않는다**(그 run에는 이 필드가
없어 재귀속이 불가능함을 카드/lap449가 이미 명시). 계측 자체는 이제 존재하며 다음 장기 soak가
재사용하면 그 구간을 새로 가를 수 있다.

**N69/N70**: `lap413_stock_comparison.md` 두 사본에 동일 정정 반영, 편집 후 두 사본
SHA256 재일치 확인(`f733d46e…d8e3d0`).

## 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태

- **독립(다음 새 세션) 검수 미완료** — 이 lap은 work 역할이므로 자기 결과의 최종 컨펌이 아니다.
  다음 middle이 `run_summary.json`/`presave_snapshot.json`/`postload_snapshot.json`/`trace.jsonl`을
  **재계산**으로 재확인해야 한다(요약 필드를 그대로 인용하지 않는 절차, N22/기존 계보와 동일).
- 남은 위험/미검증: (1) 이번 왕복은 **단발 1회**다 — 반복 저장/로드, 다른 slot 번호, PS 전환을 낀
  저장/로드는 다루지 않았다. (2) 24k/144k 규모에서의 저장/로드는 여전히 미검증(이번은 cap 근접
  직후 즉시 왕복). (3) (U4)의 lap448 −65,760KB 구간은 여전히 UNKNOWN으로 남는다(이번 계측 추가가
  소급 해명하지 않음, 카드 규정과 일치). (4) LAN/지원 동기화·건물 포함 구성·전투/사망/재생산 순환
  전부 미검증(카드 §9 명시 범위 밖). (5) 카드 §0 경계 그대로 — (나) 단독으로 G2 완료 주장 금지,
  op4 금지, **144k 카드 발행 금지 유지**(이 lap으로 카드 §1의 U0~U5가 전부 갖춰졌으므로 **W21 카드
  자체는 CLOSED 후보**이지만, 그 판정은 다음 middle의 몫이다 — work가 스스로 CLOSED를 선언하지
  않는다).
- 목표 숫자·범위·사용자 마일스톤 승인 변경 없음. G2 제품 완료 아님(부분 증거 누적일 뿐).
- 프로세스/디스플레이 정리 확인: 게임/Xvfb 프로세스 잔류 0(`ps aux` 확인), `/tmp/.X3972-lock`
  회수 확인. 실행 중 다른 프로젝트(`Syw2plus_re_loop`)의 무관 프로세스는 건드리지 않았다.

## 이번 회차 검사

targeted `tests/test_g2_eight_owner_setup.py` **6 passed**(0.02s), `checks/safety.sh check` →
`SAFETY_PASS`, 원본 **직접 재해시** `b56986e0…c9c08a8ac` 불변, **이번 회차 제품/도구 source
변경 0**(N22로 통합 `make check` 생략, 근거: git 비추적 `temp/` 스크립트 신규 작성과 기존 `temp/`
평가 파일 정정뿐), 게임 실행 **1회**, 커밋 **0**.

## 다음 한 가지

다음 새 세션(middle, Opus5/high)이 이번 lap의 원시 산출물을 **재계산**으로 독립 검수한다
(`run_summary.json`을 인용이 아니라 `presave_snapshot.json`/`postload_snapshot.json`/`trace.jsonl`
원본에서 직접 재도출). ACCEPT 시 카드 §1의 **U0~U5 전부 갖춰짐**을 근거로 **W21 카드 CLOSED**
여부를 판정하고, CLOSED라면 다음 단계(144k 발행 조건 — lap444 §1-4: 이 카드 ACCEPT **그리고**
(가) 자연 도달 fixture 성립, 후자는 아직 미착수)를 strategy/middle이 정한다. 카드 §0 경계
(op4 금지, 144k 금지, AI/바이너리 변경 시 즉시 재에스컬레이션)는 변경 없이 유지.
