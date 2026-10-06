# G1 W70 P3c — compose 비용은 구조 한계가 아니라 픽셀당 env 조회 결함: 플래그 latch 수리 후 P3 gate (lap853 strategy, 2026-10-02)

> **종결(lap858 strategy):** lap854가 §2를 수행했고 lap855·857 middle 검수의 합으로 P3 2단을 `PASS(partial)` 통합 수용했다.
> 다음 단계와 P단계 판정 절차는 `G1_STRATEGY_W70_P4_TERRAIN_BLITTER_HD_LAP858.md`가 정한다. 아래 원문은 보존용이다.

- 발행: lap853 strategy. 실제 모델 Claude Code `claude-fable-5-1`(러너 지정 strategy 역할, effort 세션 비노출, 자동 폴백 아님).
  게임 실행0, 제품/하네스 source·binary 변경0, 커밋0. lap851 이후 2 lap 만의 재호출이며 사유는 lap852의
  P3b 카드 §4-1 `BLOCKED(structure)` 승격(`loop/ESCALATE_SOL`, 보존본
  `docs/history/20261002_lap853_prior_lap852_escalate_sol_archive.md`)이다.
- 입력 근거(이 세션이 직접 읽고 재계산): lap852 기록, 위 승격 원문, 공유 temp
  `lap852_p3b_{pre,pair1,viewport_probe,stride_probe}/pair-result.json`·`candidate/trace_raw.jsonl`,
  `lap849_perf_pair5/6/7/pair-result.json`, 현재 source `tools/inmm_stub/g1_mirror2x.c`·`g1_hd_asset.c`·
  `g1_perf_sections.c`·`direct_draw_trace.c`, `tools/g1_saved_scene_probe.py:990~1020`, W70 카드 §2·§3.
- 이 카드는 P3b 카드(`G1_STRATEGY_W70_P3B_CLIPPED_KEY_COST_LAP851.md`)를 **종결·대체**한다. P3b의 §2-A 계측과
  §2-B 클립 키 수리는 lap852에서 구현됐고 그 결과(전용 Scale2x validator PASS, full-frame call 0)는 유지한다.

## 0. 판정 요약

1. **lap852의 `BLOCKED(structure)` 승격을 구조 한계로 수용하지 않는다. P3 `FEASIBLE` 지속.** QPC `compose` 구간
   17.65초(창의 89%)는 sentinel 순회·key-bound lookup의 구조 비용이 아니라, **compose 내부 루프가 쓰인 픽셀마다
   `GetEnvironmentVariableA`를 2~3회 호출하는 구현 결함**이다(§1). 호출당 ≈1.61µs가 두 독립 실행에서 일치한다.
2. **compose 재설계(sentinel 1회화·dirty-rect present)는 지금 착수하지 않는다.** §4의 반증 조건이 실제로 성립할
   때만 strategy가 다시 판정하는 보류 대안이다.
3. 성능 기준 W70 §3.5(ratio ≥0.95, p95 ≤ baseline+16ms, fresh 3 pair)는 **불변**. P4 금지 유지.
4. 다음 work 1 lap = **P3c**(§2): env 플래그 latch → 같은 QPC 계측 1 pair로 예측 검증 → fresh 3 pair gate.
   구현→빌드→격리 실행→원인 수리 반복 최대 3회(INBOX 2026-09-29 20:11). middle 사전 재측정 없이 work로 직행한다.
5. **lap851(이 역할의 직전 판정) 귀속 정정:** "지배 비용 = 클립 프리미티브 full-frame 캐시 경로"는 Scale2x 블록
   수(blocks÷refresh≈511k)는 설명했지만 **시간**은 설명하지 못했다. lap852가 그 경로를 제거했는데도(full-frame
   call 0, 창 내 Scale2x 220,220 블록) ratio는 0.51→0.535에 머물렀다. 당시 배타 시간 계측 없이 counter 산술만으로
   시간 귀속을 한 것이 오류였고, lap852의 QPC 계측이 그것을 드러냈다. P3b 수리 자체는 정합성 결함 수리로 유효하다.
6. 이 카드는 계획 승인도 G1 마일스톤 판정도 아니다. 2단 middle 독립 검수·3단 사용자 승인은 그대로 남는다.

## 1. 근거 — raw 재계산 (pair/raw SHA는 lap852 기록과 대조해 일치)

### 1.1 픽셀당 비용이 env 호출 수에 비례한다 (자연 실험)

| run | 쓰인 픽셀당 env 호출 수(코드 경로) | compose 초(첫→끝 tagged row) | compose가 처리한 쓰인 픽셀 | µs/픽셀 | µs/env 호출 |
|---|---:|---:|---:|---:|---:|
| `lap852_p3b_pair1` (attempt1) | 2 | 16.4684 | 5,123,923 (hit+miss) | 3.214 | **1.607** |
| `lap852_p3b_stride_probe` (attempt3) | 3 | 17.6515 | 3,635,598 (hit) | 4.855 | **1.618** |

- 코드 경로: `g1_mirror2x.c:405` `g1_hd_asset_enabled()` → `g1_hd_asset.c:121~124` `identity_env() || scale2x_env()`
  (각각 `GetEnvironmentVariableA`, `:71~87`; scale2x 모드에서는 둘 다 실행돼 **2회**) → hit 경로는
  `lookup_identity_block_for_key`의 `scale2x_env()`(`g1_hd_asset.c:512`)로 **1회 추가**.
- attempt1/2는 clip replay mismatch로 `g_current_valid==0`이라 lookup이 env 호출 전에 miss로 반환했다
  (창 내 miss 5,118,488 / hit 5,435) → 픽셀당 2회. attempt3는 전부 hit(miss 0) → 픽셀당 3회. 픽셀당 시간 비
  3.214/4.855=0.662 ≈ 2/3. 즉 compose 시간은 **픽셀 수×env 호출 수**로 결정되고 lookup/쓰기 자체는 잡음 수준이다.
  (hit 3회·miss 2회로 정확히 세면 pair1 10,253,281회 → 1.606µs, stride 10,906,794회 → 1.618µs.)
- **한계(독립 재계산에서 지적):** pair1은 attempt1 시점 빌드로 돌았고 그 source snapshot은 남아 있지 않다. "픽셀당 2회"는
  현재 source의 같은 경로가 그 빌드에도 있었다는 가정이다(lap852 수리 범위는 캐시 키·clip·stride였고 compose 루프는 아니다).
  데이터 점은 2개뿐이고 `GetEnvironmentVariableA` 단독 측정이나 latch A/B는 아직 없다 — §2-B가 바로 그 A/B다.
- 같은 실행·같은 기계의 순수 메모리 루프: `scratch_clear` 0.82ns/byte, `bind_compare` 0.71ns/byte,
  `scale2x_build` 6.9ns/픽셀(compose보다 무거운 픽셀 연산). compose 4,855ns/픽셀은 이보다 약 700~6,000배 느리다.
- 방증: `hash_lookup` 4.96µs/call은 `g1_hd_asset_begin`의 `g1_hd_asset_enabled()` 2회(≈3.2µs)+`VirtualQuery`+128B FNV로
  설명된다. compose 이외 전 구간 합은 창당 0.069초뿐이다.
- 추정: 이 결함은 P2(`g1_hd_asset` 도입, lap832~) 때 들어온 것으로 보이며, lap847 전까지 성능 지표가 실제 sim tick이
  아니었기 때문에 드러나지 않았다. lap817-r5의 0.246ms/call(hd asset 이전, 전체 clear 포함) → lap849의 2.0ms/call과 맞는다.

### 1.2 프레임 예산 추정 (예측이며 결과가 아니다)

- baseline: 400 present / 400 tick / 19.9996Hz, present p95 0ms → 50ms deadline 타이머로 페이싱.
- candidate: tick÷present = 214/107 = **2.00**(stride), 298/149 = **2.00**(pair1). 프레임이 늦으면 프레임당 2 tick까지
  따라잡는 구조로 보인다(프레임 187ms·133ms 두 경우 모두 정확히 2).
- 프레임 분해(ms/present): stride 184.3 = reinvoke 158.4 + present copy 6.9 + 나머지 19.0; pair1 133.1 = 107.5 + 7.1 + 18.5.
- latch 후 예상: reinvoke ≤ ~2ms/프레임(≈84 call × ≤25µs), present copy ≈7ms, 나머지 ≈19ms → **≈28ms < 50ms**.
  따라서 ratio≈1.0, p95 delta ≈ +11ms(현재값 유지)를 예측한다. 틀리면 §4.

### 1.3 입력 parity `drag_exact=false`는 sim 시간 발산과 일치한다

- 20초 창 종료 시 sim tick: baseline 24975, candidate 24789(186 tick 뒤짐). 그 뒤 같은 좌표 드래그가 baseline
  `[124,140,151,170]`, candidate `[124,140,151]`을 골랐다. lap849 pair5/6/7·lap852 전 실행에서 동일하게 false이고,
  20초 창 도입 전인 lap844는 drag PASS였다. 살아 있는 장면에서 유닛 위치가 tick에 따라 달라진 결과로 본다(가설).
- 예측: rate parity가 회복되면 `drag_exact=true`. 아니면 §2-C의 수리 대상이다.
- `minimap_gate_restore`/`production_effect` false는 양쪽 lane 모두 `UNKNOWN`인 원본 parity 항목이다(INBOX
  2026-09-30 22:2x, lap816). gate 값 원복은 `minimap_diagnostic_parity.exact_gate_restore=true`로 확인된다.

### 1.4 generic nearest-oracle `BLOCKED`(0.9835~0.9909)의 지위

- W70 카드 §2는 단계별 오라클을 다르게 정했다: **P2(identity) = nearest ≥0.999**, **P3(scale2x) = HD 마스크 밖
  diff 0 + 마스크 안 diff>0 + 팔레트 위반 0**. scale2x 모드에서 nearest 일치율이 1 미만인 것은 P3가 동작한 결과다.
- stride raw 361/361 present에서 `hd_mask_outside_diff_subpixels==0`이고
  `mismatch_blocks ≤ hd_mask_inside_diff_subpixels ≤ 4×mismatch_blocks`(mismatch_blocks=(nearest_total−nearest_matches)/4)가
  위반 0으로 성립한다. 즉 nearest 결손 전부가 HD 마스크 안 Scale2x 서브픽셀로 설명된다.
- **판정:** scale2x 모드의 P3 gate는 legacy `mirror_validator.status`를 소비하지 않고 전용 `scale2x_validator`를
  소비한다(W70 §2 그대로이며 기준 완화가 아니다). legacy validator·임계값·identity 모드 0.999 기준은 **수정 금지**.
  work는 위 부등식을 `scale2x_validator`에 **추가 검사**로 넣어(강화) raw에 남긴다. "미해결 진단"은 이것으로 닫는다.

## 2. P3c work 범위 (한 lap, 구현 우선)

### A. env 플래그 latch (수리 본체)
1. G1 opt-in env를 **프로세스당 1회만** 읽어 정적 변수에 고정한다. 이미 저장소에 있는 패턴
   (`g1_perf_sections.c:8~18`의 `InterlockedCompareExchange` 1회 초기화)을 그대로 쓴다.
   - `g1_hd_asset.c`: `identity_env()`/`scale2x_env()` → latch된 모드 1개(nearest/identity/scale2x).
   - `g1_mirror2x.c`: `env_enabled()`, `hd_negative_probe_enabled()`, `g1_mirror2x_s3_pattern_enabled()`.
   - `direct_draw_trace.c`·`g1_census.c`: present/프리미티브마다 불리는 `*_enabled()`(예: `:236`, `:853`, `:1010`,
     `:1065~1127`, `:1200`, `:1342`의 window id)도 같은 방식. work가 `grep GetEnvironmentVariableA`로 전수 확인.
2. `g1_mirror2x_compose_sentinel`은 모드를 **호출당 1회** 읽고 픽셀 루프 안에서는 함수 호출 없이 분기한다.
   lookup도 같은 latch 값을 쓴다. 그 외 로직(fail-closed 비교, negative probe, full-key search, viewport 원복)은 불변.
3. 의미 보존 확인: 하네스가 이 env들을 **프로세스 시작 전에만** 설정하는지 `tools/g1_saved_scene_probe.py`·
   `tools/runtime_env.py`에서 확인한다. 성능 창은 env가 아니라 파일 표식(`C:\inmm_g1_perf_window.active`)이므로
   latch의 영향을 받지 않는다. 실행 중 env를 바꾸는 경로가 있으면 latch하지 말고 그 사실을 기록·보고한다.
4. 회귀 가드(Fast): 기존 `tests/test_g1_mirror2x.py`의 source-scan 방식으로 "G1 C 파일에서 `GetEnvironmentVariableA`는
   latch 초기화 함수 안에서만 등장한다"와 "compose 픽셀 루프 본문에 `*_env(`/`*_enabled(` 호출이 없다"를 고정한다.
   기존 assert(`GetEnvironmentVariableA(G1_MIRROR_ENV` 등)는 의미를 유지하는 범위에서만 조정한다.
5. 금지: EXE 패치, 임계값·legacy validator 변경, P4 코드, 새 의존성, compose/present 구조 변경(§2-B-3의 값 불변 병합 제외),
   G2/G5 source·`local/runtime/g2_*`·`*g5_esl2608*` 접촉, 기존 raw 덮어쓰기, 커밋.

### B. 예측 검증 pair 1회 (`SYW2_G1_PERF_SECTIONS=1`, 라벨 예: `lap<N>_p3c_latch_probe`)
사전 등록한 기대값(save006 same-save pair, 20초 고정창, lap852와 같은 probe):
1. `compose` ≤ **50ns/쓰인 픽셀**(현재 4,855)이고 창 벽시계의 ≤2%. `hash_lookup` ≤ 2.5µs/call.
2. `full_frame_calls=0`, `clip_replay_mismatches=0`, viewport mutation/restore failure 0, Scale2x validator PASS(§1.4 추가 검사 포함).
3. tick ratio ≥0.95, present p95 delta ≤16ms, tick÷present ≈1.0, candidate present/window ≥380.
- 1~3 충족 → 바로 C. 1 충족·3 미충족 → 같은 lap 안에서 최대 구간을 수리한다. present copy(`g1_mirror2x.c:486~558`,
  800×600 2회 순회+FNV 2회)가 최대면 **출력 값이 바이트 단위로 같은** 순회 병합만 허용한다(필드 삭제·표본화 금지).
- 1 미충족(compose가 여전히 >500ns/픽셀) → 이 카드의 귀속이 반증된 것이다. 수리를 더 하지 말고 §4-1.

### C. fresh 3 pair gate (계측 env OFF, W70 §3.5 불변)
- 3 pair 모두: `tick_rate_ratio ≥ 0.95`, `present p95 ≤ baseline + 16ms`, scene equal·source unchanged·cleanup PASS,
  Scale2x validator PASS, loaded 캡처 non-black·1600×1200, `selection_target`·`empty_click` true, **`drag_exact` true**.
- `drag_exact`가 false면: 양 lane의 드래그 시점 sim tick과 선택 slot을 raw에 남기고, tick 차 ≤2인데 선택이 다르면 입력
  회귀로 보고 수리(이 lap의 반복 예산 안), tick 차가 크면 rate 문제로 되돌아간다.
- 보고(판정 근거, gate 아님): QPC 구간 표(수리 전 stride probe 대비), 평균 inclusive/call, present/window, refresh/window.

### D. 판정 변경 1건 — viewport 예외 경로 원복
- P3b §2-B-5의 "예외 시 원복 보장"은 **P3 gate 조건에서 뺀다.** 원본 프리미티브 안의 fault는 handler가 없어 baseline에서도
  프로세스 종료이고, 원복만 하려면 예외를 삼켜야 하는데 손상 은폐는 PROMPT ③ 위반이다. 대신 gate 3 pair 전부에서
  `viewport_field_mutations=0`·`viewport_restore_failures=0`·crash 0을 요구하고, 이 한계를 잔여 위험으로 공개한다.

## 3. 다음 middle 검수 조건 (work PASS 주장 시)

- latch 구현 열람(플래그 전수, 의미 보존), DLL/raw/pair SHA·build 입력, QPC 표와 tick rate·p95·tick÷present 독립 재계산,
  §1.4 부등식 재계산, drag slot·tick 대조, source unchanged·cleanup. 통과 시 P3 2단 수용 → **P4 구조 판정 회차** 전환
  가능(사용자 승인 아님). "수리 대상이 명확한 구현 결함"이면 짧게 확인만 하고 work로 되돌린다.

## 4. 정지/승격 규칙 (strategy 재호출 조건)

1. **반증:** latch 후에도 compose >500ns/픽셀이면 `BLOCKED(structure)`로 승격한다. 그때 strategy가 판정할 보류 대안:
   (a) sentinel 1회화(scratch 1장+원본 버퍼 사전값 비교), (b) present dirty-rect/지속 미러 직접 present,
   (c) 진단 순회의 opt-in 분리. 지금은 어느 것도 착수하지 않는다.
2. compose는 예산 안인데 3회 수리 후에도 ratio <0.95이면, 최대 구간과 프레임 분해 표를 남기고 **같은 카드로 work 1회
   추가**(총 2 work lap). 2회째도 FAIL이면 strategy.
3. latch 뒤 state/scene hash가 달라지거나 크래시가 나면 즉시 ESCALATE(안전·근거 충돌).
4. 3 pair gate PASS는 P3 마감 경계다 → work는 임의 마감하지 말고 middle 독립 검수로 넘긴다(PROMPT ⑥ 2단).

## 5. 남은 위험

- §1.2의 프레임 예산은 두 실행의 분해에서 나온 추정이다. deadline 페이싱·2-tick 따라잡기는 정적 확인이 아니다.
- present copy ≈7ms/프레임(p95 +11ms)은 gate 안이지만 여유가 5ms뿐이다. P4/P5에서 coverage가 늘면 다시 봐야 한다.
- latch는 실행 중 env 변경을 무시한다. 현재 하네스가 그렇게 쓰지 않는다는 것은 §2-A-3에서 work가 확인한다.
- 측정은 Xvfb/Wine 환경이며 `GetEnvironmentVariableA` 비용(≈1.6µs)도 그 환경 값이다. 사용자 하드웨어 수치가 아니다.
- lap852 한계 유지: input parity 전체는 HOLD, product minimap/production `UNKNOWN(original parity)`, GDI/P4/전체 HD
  coverage·사용자 3단 승인 미충족.
