# 2026-09-23 | lap529 | 목표 G2 (W36 검수 → W37 발행)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5` / high, 지정 역할 **middle**(중간계획·컨펌). 하네스 대조 검토 1건은 native subagent(oh-my-claudecode:verifier, 읽기 전용)에 맡겼고, 지적 중 판정에 쓴 것은 본 세션이 코드 줄을 직접 읽어 확인했다.
- 가설 / 사용자 관찰: lap528의 `ARM_FAIL`(owner6 `used`=4768)은 AI 노이즈가 아니라 시딩 순서 결함이다. 생산자(type46)를 먼저 넣은 뒤 큰 항목을 채우면, 그 사이 AI 차례가 온 owner는 여유를 AI 주문에 빼앗긴다.
- 예상 PASS / FAIL 조건: 원시 receipt만으로 (1) `ARM_FAIL` 라벨, (2) `reserved` 0→220 시점, (3) 220의 구성을 재계산해 lap528 기록과 대조한다. 불일치가 있으면 REJECT한다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  - 신규 `docs/work/active/G2_S1_DRIVEN_COMBAT_CYCLE_SOAK_R1_LAP529.md`(W37 카드)
  - `docs/work/active/G2_S1_DRIVEN_COMBAT_CYCLE_SOAK_LAP527.md` 상태 줄(`CLOSED`) 1줄
  - 이 기록, `docs/STATUS.md`, `docs/feedback/INBOX.md`(추기 1줄), `loop/ESCALATE_SOL` §85
  - 제품 source·브리지·테스트·하네스 변경 0. 커밋 0(`LOOP_ALLOW_COMMITS` 미설정).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  - 원본 `syw2plus_original.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 재확인(불변). 게임 실행 0.
  - lap528 후보 EXE `a10024de…`(두 attempt summary 일치), 브리지 내부 SHA `bc7a7b0c…`(두 attempt 일치). wrapper `dll_sha256`은 attempt1 `2099fa9c…`, attempt2 `0c707c85…`로 다르다. 빌드 산출 차이이며 lap528 기록 설명과 맞다.
  - repo 3파일 현재 SHA: `runtime_bridge.c` `3555848d…`, 허용목록 핀 테스트 `2a8aa4f7…`, op8 계약 테스트 `0939f5b6…`. 브리지 `:198`이 `{5,7,46,2}` 조건인 것을 확인했다.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - 원시(lap528, 읽기만 함) `temp/Syw2plus_patch/g2_capacity/20260923_lap528_w36_s1_driven_cycle/`:
    `seed_receipts.json` `9e484176…`, `run_summary.json` `4f6c5564…`, `w36_orchestrator.log` `549cc735…`, `w36_run.py` `adb9214d…`,
    `attempt1_arm_fail/seed_receipts.json` `6e275cce…`, `attempt1_arm_fail/run_summary.json` `facd68ba…`.
  - `python3`으로 두 attempt의 receipt 61건(28+33)을 표로 풀어 재계산했다.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - **W36 `ARM_FAIL` 일치 ⇒ `CLOSED`.** attempt1: owner6 type2 receipt `ok=false`(`fixture_exceeds_unreserved_supply`), `fixture_added`=46, owner7은 시도하지 않았다(`used`=20).
    attempt2: A1 = `[4950×6, 4768, 4950]`. owner6만 범위 밖이고 receipt `ok=false`가 2건이다. 두 attempt의 owner0~6 결과가 tick까지 같다(결정적).
  - **N187 정밀화(N188):** owner6 `reserved`는 type46 receipt(tick 61)의 after에서 0이고, 바로 다음 type2 receipt(tick 62)의 before에서 220이다.
    220 = 생산자 22기(type46 20 + type110 2) × 비용 10이다. 그 순간 여유 830 중 610이 남았으므로 type5·type7은 주문을 내지 않았다.
    owner0~5는 type2까지 채운 뒤에 AI 차례가 와서 최종 `reserved`가 40~45(여유 50 이내)다. attempt2 owner7은 시딩 전에 `reserved`=10이었다(type110도 생산자).
    ⇒ 원인은 "시딩 도중 AI 생산" 일반이 아니라 **생산자를 큰 항목보다 먼저 넣은 순서**다. 순서를 바꾸면 산술로 막힌다(W37 §3).
  - **절차 단서(N189):** lap528 attempt2는 W36 §0-5의 2회째 허용 조건(1회째 하네스 결함 `BLOCKED`) 밖이었다. attempt1은 정당한 `ARM_FAIL`이었다. 결과 라벨은 같아서 판정에 영향은 없고 기록만 남긴다.
  - **하네스 결함(N190, 창 E 미실행이라 드러나지 않음):** `w36_run.py`를 W36 §4·§5와 대조했다. 원시 재계산을 막는 것은 둘이다.
    - 출생 이벤트가 없다(`diff_events` `:325-360`). 그래서 R_o를 원시로 셀 수 없다.
    - producer `production_type`/`progress`가 원시에 남지 않는다. 그래서 A3 양성 대조를 셀 수 없다.
    - 그 밖의 결함: 실패 경로에서 `source_sha_after`·잔류 프로세스가 비어 있다(`:1000-1007`이 성공 경로에만 있음). `do_wave` 예외는 `RUN_ERROR`로 빠진다(`:806`).
    - 자기판정 결함: `NO_ENGAGEMENT`를 `CYCLE_UNSTABLE`보다 먼저 평가한다(`:967/:969`). 창 B fault를 `BLOCKED`로 적는다(`:730-734`, 카드는 `ARM_FAIL`). A5에 음수·`count` 상한 검사가 없다(`:776-780`). A8' 비중이 고정 수량 기준이다(`:655`). A2 3등분 조건과 A6 둘째 절이 빠졌다.
    - op8 수락의 `+0x384` 변화는 브리지 receipt(`src_0x384_before/after`)에 원시로 남으므로 결함이 아니다.
  - `checks/safety.sh check` exit0 `SAFETY_PASS`. `checks/context_limits.py`는 아래 STATUS 갱신 뒤 실행 결과를 STATUS 검증 줄에 적는다.
  - source 변경이 없어서 `make check`는 생략했다(N22). 문서 무결성 검사이며 제품 증거가 아니다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  - 위험 R1: type2가 생산자이면 새 순서에서도 type46 직전 `reserved`가 커질 수 있다. W37 §3 반증 조건(`pre_producer_ledger.reserved` > 50)으로 드러나게 했고, 그때는 재실행하지 않고 strategy에 회부한다.
  - 위험 R2: 하네스 수리 H1~H5는 한 번도 실행되지 않은 코드다. 다음 middle이 원시로 재계산해 검수한다.
  - 사용자 승인 사항 아님: 측정식·A1·허용목록·가드를 바꾸지 않았고 순서와 기록만 바꿨다.
  - streak: 이 회차는 문서 회차 1회째다(lap528이 게임 실행). 다음 work가 게임 실행 없이 끝나면 STOP하고 사용자에게 보고한다.
- 다음 한 가지: **work(Sonnet5): W37 카드대로 하네스 H0~H5 → `make check` 1회 → S1 24k 게임 1회 foreground 완주.**
