# 2026-10-02 | lap 853 | G1 W70 P3 구조 비용 승격 판정 — compose는 픽셀당 env 조회 결함, P3c 발행

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-fable-5-1`, 러너 지정 strategy(큰 방향/master-plan) 역할,
  effort는 세션에 비노출. 자동 폴백 아님. `loop/.lap_counter`는 853을 읽기만 했다(러너 evidence 블록은 lap=852 표기,
  PROMPT 규칙대로 파일 값 사용). 게임 코드/하네스/바이너리 수정0, 게임 실행0, 커밋0.
- 가설 / 사용자 관찰: lap852가 승격한 "compose 구간 17.65초=구조 비용"이 sentinel 순회/lookup의 본질 비용이 아니라
  compose 픽셀 루프 안의 `GetEnvironmentVariableA` 호출(scale2x 모드에서 쓰인 픽셀당 2~3회) 때문이라면, 구조 재설계 없이
  플래그 latch만으로 P3 성능 gate에 도달할 수 있다.
- 예상 PASS / FAIL 조건(이 판정의): raw에서 compose 시간÷쓰인 픽셀이 (a) 같은 기계의 메모리 루프(ns/픽셀)보다 수백 배 크고
  (b) 픽셀당 env 호출 수가 다른 두 실행에서 호출당 비용이 일치하면 가설 지지 → `FEASIBLE` 지속·bounded work 발행.
  픽셀당 비용이 수십 ns 수준이면 구조 비용 → `BLOCKED(structure)` 수용·대안 판정.
- 변경 파일 / source fingerprint / 커밋: 신규 `docs/work/active/G1_STRATEGY_W70_P3C_ENV_LATCH_COMPOSE_LAP853.md`, 이 기록,
  신규 `docs/history/20261002_lap853_prior_lap852_escalate_sol_archive.md`(lap852 `loop/ESCALATE_SOL` 원문 26줄 그대로,
  SHA256 `b9be88c4f6942a32511e79575048511ade31766e970150755286b46286bb66f7`), P3b 카드 머리에 종결 포인터 2줄,
  `docs/STATUS.md`, `docs/feedback/INBOX.md`, `docs/feedback/APPROVALS.md`. `loop/ESCALATE_SOL`은 보존본 SHA 일치 확인 뒤
  제거했다(판정으로 해소, 다음 회차를 work로 보내기 위함). uncommitted(`LOOP_ALLOW_COMMITS=0`).
  G1 source 불변(열람만): `g1_mirror2x.c` `bf87ed69…ae03c800`, `g1_hd_asset.c` `9b191354…46b1707c`, `g1_hd_asset.h`
  `7a8b753c…fac86708`, `g1_perf_sections.c` `3bcb2ba6…1bd2fa57`, `g1_scratch_bounds.h` `779a6384…6c5e4670`,
  `direct_draw_trace.c` `170a7e5d…46246a3b`, `tools/g1_saved_scene_probe.py` `742260b1…bd0e9927`.
- 원본 SHA / 후보 SHA / 환경 / fixture: 보호 원본 EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`,
  save006 `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064`(pair-result에서 읽음, 이번 lap 재해시 없음).
  후보 DLL SHA는 lap852 기록 참조. 새 runtime 없음.
- 실행 명령 / 로그: 읽기·재계산만 — python json으로 공유 temp `lap852_p3b_{pre,pair1,viewport_probe,stride_probe}`와
  `lap849_perf_pair5/6/7` 열람. 재해시: stride `pair-result.json` `67a88165…a312cf954`, `candidate/trace_raw.jsonl`
  `2ec291bf…3588c6536`(lap852 기록과 일치). 검증 명령은 아래.
- 측정값 / 판정:
  - stride probe(attempt3, 픽셀당 env 3회): compose 17.6515s ÷ lookup hit 3,635,598 = 4.855µs/픽셀 = **1.618µs/env 호출**.
  - pair1(attempt1, `g_current_valid==0`로 lookup 조기 miss → 픽셀당 env 2회): 16.4684s ÷ (hit+miss) 5,123,923 =
    3.214µs/픽셀 = **1.607µs/env 호출**. 비 0.662 ≈ 2/3.
  - 같은 실행의 메모리 루프: scratch_clear 0.82ns/byte, bind_compare 0.71ns/byte, scale2x_build 6.9ns/픽셀.
    compose 외 전 구간 합 0.069s/창. hash_lookup 4.96µs/call(env 2회 포함).
  - 코드 귀속: `g1_mirror2x.c:405` → `g1_hd_asset.c:121~124`(`identity_env`/`scale2x_env` `:71~87`) + `:512`.
  - 프레임 분해(ms/present): stride 184.3 = reinvoke 158.4 + present 6.9 + 나머지 19.0; pair1 133.1 = 107.5 + 7.1 + 18.5.
    tick÷present = 214/107, 298/149 = 2.00; baseline 400/400, 19.9996Hz.
  - drag: 창 종료 sim tick baseline 24975 vs candidate 24789, 선택 `[124,140,151,170]` vs `[124,140,151]`.
  - nearest-oracle: stride 361/361 present에서 outside diff 0, `mismatch_blocks ≤ inside_diff ≤ 4×mismatch_blocks` 위반 0.
    lap852 기록의 0.990946은 PS9 record 값이고 전 run 최솟값은 0.98351875(PS3)다(전사 불일치 아님, 서로 다른 통계).
  - **판정: `BLOCKED(structure)` 불수용, P3 `FEASIBLE` 지속. 기준 §3.5 불변, P4 금지 유지. compose 재설계 미착수(보류 대안).
    다음 work = P3c(env latch → QPC 예측 검증 1 pair → fresh 3 pair, 수리 ≤3회).** lap851의 시간 귀속(full-frame 캐시)은
    정정한다. scale2x 모드 P3 gate는 legacy nearest-oracle이 아닌 전용 Scale2x validator를 쓴다(W70 §2, 기준 완화 아님).
    viewport 예외 경로 원복은 gate 조건에서 제외하고 mutation/restore failure 0·crash 0으로 대체한다. 상세는 카드 §0~§4.
- 회귀 / 남은 위험 / 독립 검수·사용자 승인: 이 판정은 raw 산술과 코드 열람이며 수리 후 실측이 아니다 — latch 후 compose가
  >500ns/픽셀이면 반증이고 그때 구조 대안을 판정한다(카드 §4-1). 프레임 예산(≈28ms)은 추정. present copy 여유 5ms.
  2단 middle 검수·3단 사용자 승인 없음. G1 마일스톤 판정 아님.
  - 같은 세션 안의 읽기 전용 native subagent(verifier, Claude `opus`)에게 결론을 주지 않고 코드 경로·raw를 따로 계산시켰다:
    픽셀당 API 호출 miss 2회/hit 3회(`g1_hd_asset.c:74,83`, `:512→:83`, latch 없음), compose 16.4684s/17.6515s,
    호출당 1.606/1.618µs, 2변수 해(T=α·영역픽셀+β·호출)에서 α≈−0.03µs·β≈1.64µs, drag slot·nearest 부등식 위반 0 — 내 수치와 일치.
    판정 "env 호출 가설 지지, 신뢰도 중상". 지적된 한계: pair1 빌드의 source snapshot 부재, 데이터 점 2개, 단독 µbench·latch A/B 없음.
    이것은 판정 전 사실 확인이며 2단 middle 계획 수용이 아니다.
- 다음 한 가지: work가 P3c 카드 §2를 수행한다.

## 검증 (문서만 변경)

- 기록 후 G1 source SHA 불변 확인, `make lint`/`make typecheck`, `checks/context_limits.py`, `checks/safety.sh check`,
  scoped `git diff --check`, 최종 `make check` 1회 — 결과 수치는 STATUS에만 보강한다(PROMPT ⑥ fingerprint 규칙).
