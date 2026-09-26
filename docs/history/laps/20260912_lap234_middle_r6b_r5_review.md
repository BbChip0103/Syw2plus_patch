# 2026-09-12 | lap 234 | 목표 G1

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high, middle tier
  (진단·계획·확인). 게임 코드 hands-on 수정 없음, 제품/도구 코드 변경 0.
- 가설 / 사용자 관찰: lap233이 추가한 R6-B-R5 reader 기반 손상 회귀가 (a) 실제
  `_read_g1_selection_evidence` 경로에서 도달 가능한 관측만 고정하는지, (b) 가드가 약해지면
  실제로 실패하는 비공허 회귀인지, (c) 기존 PASS/semantics를 완화하지 않는지 독립 검증한다.
- 예상 PASS / FAIL 조건: PASS = 4개 케이스 전부 실제 reader가 낼 수 있는 관측이고
  `responded=False`+`status=CORRUPTED`로 닫히며, 가드 변이 시 lap233 테스트가 실패하고,
  count 0 / count 1→0 / 식별자 변화 PASS 경로가 불변. FAIL = 손으로 만든 dict에만 성립하거나,
  가드를 약화해도 테스트가 통과(공허)하거나, 기존 semantics가 느슨해진 경우.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 신규 검수 산출물만 —
  `docs/history/laps/probes/20260912_lap234_r6b_r5_review_probe.py`,
  `..._report.json`, `..._report.attempt1.json`, `..._report.PROVENANCE.md`,
  `docs/history/laps/20260912_lap234_middle_r6b_r5_review.md`, `docs/STATUS.md`,
  `loop/ESCALATE_SOL`. 검수 대상 fingerprint 재계산:
  `tools/runtime_env.py` `103ec280b50ac658504b5263a200896c1b39d66244269bc373dcfd23225ce02b`
  (lap231/lap233 기록과 일치, lap233에서 변경 0),
  `tests/test_runtime_env.py` `c8830c1277c8ab57ecfbddeecda3be22b63b21b6898fd8b4c4d889ce1691ce64`
  (lap233 기록과 일치). 모두 uncommitted (`LOOP_ALLOW_COMMITS=0`).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 EXE pin
  `b56986e0…c08a8ac`가 `tools/check_binary_contract.py`, `tools/check_setup.py`,
  `patches/population/fixed_supply_5000.py`, `patches/resolution/qhd_probe.py`에서 불변.
  후보 EXE 없음, 게임 실행 0회, 활성 플레이어/지도/군대 N/A. fixture는 검수자가 직접 만든
  최소 byte-level reader(SELECTION_COUNT / FIRST_SLOT / UNIT_EXISTS+slot*2 /
  UNIT_BASE+slot*STRIDE+TYPE_OFFSET 4주소만)이며 저장소 테스트 헬퍼를 재사용하지 않았다.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `.venv/bin/python -m pytest -q tests/test_runtime_env.py -k 'selection_response or
  selection_reader_failures or selection_sequence'` → 18 passed (lap233 수치 재현).
  `make check` → 253 passed, Ruff All checks passed, compileall, mypy 10 files Success,
  `CONTEXT_PASS`. `LOOP_DRY_RUN=0 bash checks/safety.sh check` → `SAFETY_PASS`.
  자체 probe → reachability 12/12, fail_close 15/15, mutation 4/4 AGREES (총 31/31, DEFECT 0),
  보고서 `docs/history/laps/probes/20260912_lap234_r6b_r5_review_report.json`.
  lap232 probe 재실행(`--output /tmp/lap234_rerun_lap232.json`, 원본 미덮어씀) → 18/18 AGREES,
  defects 0. PNG 0장.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **R6-B-R5 범위 승인(scope approval).**
  1) 도달성: 실제 reader가 A2 C4(OSError, count 1/slot 7/UNKNOWN),
  A3 C5(비활성 slot, `_CommandCellSnapshotError`), A4 D1(count −1 → slot None/UNKNOWN),
  A7 type 0, A6 slot 범위밖, A5 count>pool(1201), A8 struct.error, A9 type 주소 읽기 실패까지
  모두 만들 수 있고 전부 CORRUPTED로 분류된다. A11 count 0은 여전히 SOUND(=R6-B-R2 semantics 불변).
  2) 비공허성: `_g1_selection_responded`를 약화한 변이 3종에서 lap233 테스트가 실제로 실패한다 —
  M1(UNKNOWN type 허용) → c4/c5/c7 실패, M2(음수 count 허용) → d1 실패, M3(항상 SOUND) → 4/4 실패.
  변이 없음(M0)에서는 4케이스 모두 통과. 즉 회귀가 가드를 실제로 고정한다.
  3) 완화 없음: 손상 관측 7종 × 양방향 14케이스가 전부 `responded=False`+`CORRUPTED`+
  first/last provenance 보존이고, 건전한 식별자 변화 1케이스는 여전히 `responded=True`+`SOUND`다.
  제품 G1, R6-B 전체, Stage B는 여전히 미승인 SKIP이다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: lap233은 테스트만 추가했고 제품 코드
  fingerprint가 불변임을 재계산으로 확인했으므로 회귀 위험은 없다. 검수 중 확인한 설계 사실:
  `_read_selection`은 reader의 `try` 앞에서 실행되므로 selection count/first-slot 주소의 읽기
  실패는 CORRUPTED 관측이 아니라 예외로 reader 밖으로 나간다(probe A10/A12). 이는 결함이 아니라
  `_wait_state`의 `read_error_count`→`UNKNOWN_STATE_READ_FAILURE`(R6-B-R6)와 `g1_baseline`의
  OSError 처리로 한 단계 위에서 fail-close된다. 다만 `_g1_run_input_sequence`가 `_wait_state`
  바깥에서 직접 부르는 `read_selection()` 5곳(runtime_env.py:2478/2516/2560/2607/2628)은 그
  경우 단계 분류 없이 run 전체 `evidence["error"]`로만 남는다 — 안전하지만 진단성이 떨어진다.
  이를 비차단 **R6-B-R9**로 신규 등록한다(정확성 구멍 아님, 분류/진단성만). S1/F2-R2,
  R6-B-R2/R7/R8, WM_CLOSE, Stage B는 미해결. 사용자 승인 범위(2026-09-12 01:03 KST)는 유지되며
  이 lap은 기술 검수이지 마일스톤 승인이 아니다.
- 다음 한 가지: 새 work tier(Claude Code `claude-sonnet-5`/high 또는 Codex `gpt-5.6-luna`/high)가
  **R6-B-R7**(검수 probe 출력 경로 재실행 덮어쓰기 방지)을 한 건으로 수리한다. 이번 lap의 probe는
  기존 파일이 있으면 쓰기를 거부하고 경로 인자를 받도록 이미 작성했으니 R6-B-R7 구현 참고로 쓴다.
  그 뒤 R6-B-R8 → R6-B-R9 → F2-R1 → F3-R1 → F3-R2 → F6-R2. S1/F2-R2와 R6-B-R2 재결 전
  게임 실행·Stage B run 금지.
