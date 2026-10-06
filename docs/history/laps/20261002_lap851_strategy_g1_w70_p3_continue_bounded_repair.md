# 2026-10-02 | lap 851 | G1 W70 P3 성능 FAIL 전략 판정 — 지속 FEASIBLE, P3b bounded 수리 발행

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-fable-5-1`, 러너 지정 strategy(큰 방향/master-plan) 역할,
  effort는 세션에 비노출. 자동 폴백 아님. `loop/.lap_counter`는 851을 읽었다(러너 evidence 블록은 lap=850을 표기했으나
  PROMPT 규칙대로 파일 값 851을 이번 lap 번호로 쓴다). 게임 코드/하네스/바이너리 수정0, 게임 실행0, 커밋0.
- 가설 / 사용자 관찰: lap849 통제 3 pair 성능 FAIL(ratio 0.505~0.517)의 지배 비용이 구조적 바닥(원본 2회 재호출)이 아니라
  클립된 프리미티브의 full-frame 캐시 경로(W70 §0.3 설계와 불일치)라면 P3는 bounded 수리로 지속 가능하다.
- 예상 PASS / FAIL 조건(이 판정의): raw cumulative counter로 Scale2x 블록÷refresh가 ≈480k(전체 프레임)이면 가설 지지 →
  `FEASIBLE`·bounded work 발행. 블록÷refresh가 작은 프레임 크기면 다른 원인 → 계측 우선 카드. 바닥 비용이 예산 초과 증거가
  있으면 `BLOCKED(structure)`.
- 변경 파일 / source fingerprint / 커밋: 신규 `docs/work/active/G1_STRATEGY_W70_P3B_CLIPPED_KEY_COST_LAP851.md`, 이 기록,
  `docs/STATUS.md`, `docs/feedback/INBOX.md`, `docs/feedback/APPROVALS.md`. uncommitted(`LOOP_ALLOW_COMMITS=0`).
  G1 source(`tools/inmm_stub/g1_mirror2x.c`, `g1_hd_asset.c`, `g1_scratch_bounds.h`, `direct_draw_trace.c`,
  `tools/g1_saved_scene_probe.py`) 불변 — 아래 검증란의 SHA.
- 원본 SHA / 후보 SHA / 환경 / fixture: 보호 원본 EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`,
  save006 `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064`(lap849/850 기록 재인용, 이번 lap 재해시 없음).
  lap849 후보 DLL SHA는 lap850 기록 참조. 새 runtime 없음.
- 실행 명령 / 로그: 읽기만 — lap849/850 기록, lap850 archive, `temp/Syw2plus_patch/lap849_perf_pair5/6/7/pair-result.json`
  (python json 열람), G1 source 열람. 검증 명령은 아래.
- 측정값 / 판정:
  - pair5/6/7 후보 window: Scale2x blocks 170,119,588/170,117,588/164,837,196 ÷ refresh 333/333/322 =
    **510,869/510,863/511,917 블록/refresh ≈ 800×600 전체 프레임**(480,000) + 신규 insert 몫. 전체 프레임 refresh만으로
    159.8M/170.1M(≥94%)을 설명한다.
  - baseline present 400/window(20Hz, tick당 1회) vs candidate 102/102/99(≈5fps); reinvoke 8,586/8,585/8,333 call →
    present당 ≈84 call, inclusive 평균 2.00/1.98/2.01ms/call(lap817-r5 sentinel-only 0.246ms의 ≈8배).
    전 run 단일 call 최대 461/465/467ms.
  - 코드 귀속: `g1_hd_asset.c:184`(`full_frame` 판정) → `:323~325`(800×600 캐시) → `:330~358`(매 call 480k 비교,
    mismatch 시 evict) → `:301`(전체 Scale2x 재생성); `g1_mirror2x.c:686~691`(클립 시 scratch 전체 clear).
  - **판정: P3 `FEASIBLE` 지속. 성능 기준 §3.5 불변, P4 금지 유지. 다음 work = P3b(배타 계측 + 클립 키 수리, 한 lap,
    구현→빌드→격리 fresh 3 pair→수리 ≤3회).** 상세·정지 규칙은 카드 §2~§4.
- 회귀 / 남은 위험 / 독립 검수·사용자 승인: 이 판정은 counter 산술과 코드 열람이며 배타 시간 계측이 아니다(카드 §2-A가
  먼저 확정). (0,0) 재호출의 렌더러 상태 부작용 위험은 state hash parity로 검사. present compose ≈10ms는 범위 밖 2순위.
  2단 middle 검수·3단 사용자 승인 없음. G1 마일스톤 판정 아님.
- 다음 한 가지: work가 P3b 카드 §2를 수행한다.

## 검증 (문서만 변경)

- 기록 후 G1 source SHA 불변 확인, `make lint`/`make typecheck`, `checks/context_limits.py`, `checks/safety.sh check`,
  최종 `make check` 1회 — 결과 수치는 STATUS에만 보강한다(PROMPT ⑥ fingerprint 규칙).
