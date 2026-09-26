# lap249 STATUS pre-compression provenance

- original_sha256: `951ec062728bea44729b5b1520eb2c4c736e14bc42d6dd7a77ee78985e433b18`
- original_line_count: `135`
- reason: STATUS exceeded the 130-line loop contract after the lap249 update.

## 원문

# STATUS — 매 바퀴 갱신하는 기억

## 지금 상태

G1~G4는 제품 단위로 모두 미완료다. G1은 원본 800×600 논리 구도/UI를 유지한 1600×1200
정수 2배 출력, G2는 8인 전비 5000과 실제 개체 풀/메모리 확장, G3은 최대 16인, G4는
길찾기·자유대전 AI 개선이다.

DxWrapper 후보는 fresh runtime에서 1600×1200 client/capture, 800×600 logical, 2×2 scale,
선변환 없는 입력, PS9→PS7→PS3와 30초 지속 렌더를 확인했다. WM_CLOSE teardown 결함은
builtin ddraw 대조로 DxWrapper native 경로에 귀속했고 P6 Lock 계측은 주차했다.

사용자는 2026-09-12 01:03 KST “승인. 루프 계속 돌아”로 Stage B evidence가 성립할 때까지
bounded repair→fresh validation을 승인했다. blind retry, run 재사용, 보호 자산 변경은 금지다.

Stage A A-1~A-16과 R1~R5-C/N1~N3, comparator F1/F4/F5, 후보 producer F6은 구현 후
Opus 독립 승인을 받았다. lap204 fresh 원본 drag는 count 1→1이지만 slot/type
1199/70→1198/21로 실제 선택 효과가 있었다. 이에 `FAIL_NO_EFFECT`, 절대 slot id, `count>=2`
규칙을 기각했다. lap214 Astra/medium 이후 Opus가 판정 계약을 재결했고, F3는 `after.last`, F2는
`(owner,type,장면 상대 world offset)` parity를 사용하도록 수리·독립 승인했다.

R6-B는 선택 count 또는 identity의 비퇴행 변화를 응답으로 삼는다. 후속 수리 상태:
- R1: 손상 slot/type 관측 fail-close — lap226 Opus 범위 승인.
- R3: 음수 count fail-close — lap228 Opus 13,689-case 범위 승인.
- R4: 최종 관측 상태 갱신+손상 provenance 보존 — lap230 Opus 범위 승인.
- R6: 읽기 실패 0관측/tail을 UNKNOWN으로 닫음 — lap232 Opus 18-case 범위 승인.
- R5: 실제 reader 손상 회귀 — lap234 Opus 31-case 범위 승인.
- R7: review probe 기존 보고서 덮어쓰기 방지 — lap236 Opus 범위 승인.
- R8: 읽기 오류율 25% 초과를 `UNKNOWN_STATE_READ_COVERAGE`로 닫음 — lap238 Opus 16-case
  전수 행렬 + 5개 변이 범위 승인. lap237 STATUS 길이 게이트 실패도 해소를 확인했다.
- R9: `_g1_run_input_sequence`의 직접 selection reader 실패를 단계/지점/provenance와 함께
  `UNKNOWN_STATE_READ_FAILURE`로 flush — lap239 work 구현, lap240 middle이 독립 하네스로
  call-site 6개 전수 + raising 15-case + production 3-case + 변이 5/5 검출로 범위 승인.
- R10: review probe 쓰기 불가 부모를 본문 실행 전에 `exit 2`로 분류 — lap241 work 구현,
  lap242 middle 검수 **FAIL**, lap243 work가 R16 `OSError` fail-close와 R17 조기 거부 회귀를
  수리했고 lap244 middle이 독립 하네스로 재검수해 **범위 승인**했다.

- R11: review probe 배타 생성(open("x")) 단독 가드의 dangling symlink 회귀 — lap245 work 구현,
  lap246 middle이 깊이를 맞춘 미러에서 변이가 R11 **하나만** 죽이는 것을 실측해 **범위 승인**했다.
  단, lap245가 제출한 비공허성 증거는 **무효**다(아래 lap246). 제품 G1 증거는 여전히 없다.

- R12: 읽기 오류/커버리지 부족이 이미 관측한 selection `CORRUPTED`를 `UNAVAILABLE`로 덮지 않게
  보존 — lap247 work 구현, lap248 middle이 81-case 전수 + M0 대조군 + 변이 3종으로 **범위 승인**.
- R13: PASS 입력 stage의 poll/read-error coverage를 stage record와 input verdict에 노출 — lap249
  work 구현, targeted·Fast·safety PASS; middle 독립 검수 전.

최상위 증거 차단 S1은 원본↔원본도 nation/player spawn이 달라 scene mismatch가 나는
비결정성이다. F2-R2 때문에 장면 통제는 slot 대응 결정성도 함께 풀어야 한다. 상위 재결 전에는
fresh Stage B를 실행하지 않고 게임 없는 수리만 한 바퀴 한 건씩 진행한다.

모델 라우팅: Luna/high(work), Claude Opus5/high(middle), Astra/medium(strategy). Astra는 큰
분기·교착에서만 약 10 lap당 1회 이하이며 마지막 호출은 runtime lap214였다.

| 목표 | 판정 | 현재 근거 / 미충족 |
|---|---|---|
| G1 1600×1200 원본 구성 | 미완료 | 표시·논리 좌표 증거 있음; R14~R15, R2/S1, fresh pair, WM_CLOSE 필요 |
| G2 8인 전비5000 안정성 | 미완료 | 숫자 패치 외 8인 부하·개체 풀/메모리 확장 증명 없음 |
| G3 최대16인 | 미완료 | 9~16인 로비/상태/통신/시뮬레이션 미구현 |
| G4 길찾기/AI 난이도 | 미완료 | 원본 대비 지표·개선 구현 없음 |

## 다음 한 가지

새 middle tier(Opus5/high)가 게임 없이 lap249의 **R13**(PASS 경로 read coverage 노출)을 독립
검수한다. 범위 승인 후 큐는 R14 → R15 → R19 → R20 → R21 → F2-R1 → F3-R1 → F3-R2 → F6-R2다.

## 지금 막힌 것 (Blockers)

- 원본/제품 EXE·DLL/assets/baseline/golden 변경, evidence 재사용, blind retry, PASS 완화 금지.
- production 클릭 금지. 정상 비활성은 BLOCKED로 남기고 후속 입력은 계속한다.
- **S1/F2-R2:** random seed·scene·slot 대응 결정성이 없다. 상위 재결 전 Stage B 양쪽 run,
  원본 재실행, R6-A/R6-C 금지.
- **R6-B-R2:** count 1→0 선택 상실을 응답으로 볼지는 Astra/사용자 재결 전 수정 금지.
- offline 큐: R14(production 레코드가 읽기 실패를 UNAVAILABLE로 표기),
  R15(직접 reader 실패가 budget 소진보다 우선 분류), **R19**(R17 회귀가 함수명 `drive_wait`
  하나에만 걸려 있어 개명 시 조기-거부 삭제를 놓친다 — lap244 실측), **R20**(저장소 밖 미러
  변이 하네스에 M0 대조군이 없어 재배치 실패를 "검출"로 오독 — lap246 실측), **R21**(probe 출력이
  직렬화 전에 `open("x")`로 파일을 만들어 쓰기 실패가 절단 증거를 남기고 R7이 재시도를 막는다 —
  lap248 실측), F2-R1/F3-R1/F3-R2/F6-R2.
- 후보 WM_CLOSE teardown 결함과 실제 후보 scene/input evidence는 미해결이다.
- G2~G4는 제품 증거가 없다.

## 검증 상태

- lap146~213: 2배 표시·입력·지속 렌더, Stage A/R1~R5/F1~F6 구현·독립 승인.
- lap214~222: Astra/Opus 재결, F3/F2 수리·독립 승인, Fast 238/safety PASS.
- lap223~236: R6-B 및 R1/R3/R4/R6/R5/R7 수리·Opus 범위 승인, Fast 255/safety PASS.
- lap237: R8 work, targeted 13, Fast 257; 종료 safety만 STATUS 188줄로 FAIL해 압축했다.
- lap238: R8 middle 검수 — 16-case 불일치 0, 무반응 PASS 0건, 변이 5/5 검출, Fast 257,
  safety PASS, 게임 0회. lap237 게이트 실패 해소 확인.
- lap239~240: R9 work 구현과 middle 검수 — call-site 6/6, raising 15-case·production 3-case
  불일치 0, 변이 5/5 검출, Fast 263, safety PASS, 게임 0회. 하네스 결함은 attempt1+PROVENANCE 보존.
- lap241: R10 work — probe 쓰기 불가 부모 3종 조기 `exit 2` 분류와 raw traceback 부재 회귀,
  Fast 266, safety PASS, 게임/Wine 실행 0회. 기존 R7 보호·보고서 작성 회귀 유지; middle 검수 전.
- lap242: R10 middle 검수 **FAIL** — 분류 11-case 중 10건 `exit 2`/분류 메시지/traceback 0,
  정상 3/3 `exit 0`, 조기 실행은 AST 순서+프로파일 추적(본문 함수 0회)으로 확인, 보고서는
  `source_sha256`만 다르고 측정 전 구간 동일. 신규 **R16**(부모 `0o600`이면 `path.exists()`가
  `PermissionError`로 raw traceback+`exit 1`), **R17**(조기 기존-증거 거부 변이 M3 미검출),
  **R18**(lap241 기록의 runtime_env 지문 72자 손상). Fast 266, safety PASS, 게임 0회.
  하네스 결함 2건은 attempt1/attempt2+PROVENANCE로 보존하고 제품 코드는 바꾸지 않았다.
- lap243: R10 work 수리 — `output_refusal` 조회 OSError를 `output path unavailable`+`exit 2`로
  fail-close하고 기존 evidence 조기 거부를 프로파일 회귀로 고정. targeted 7 passed, R10 probe
  분류 11/11·정상 3/3·변이 5/5·verdict PASS, `make check` 268 passed, safety PASS, 게임 0회.
- lap244: R10 middle 재검수 **PASS/범위 승인** — 새 하네스로 분류 14/14(거부 9건 traceback 0,
  경로 상태 불변), 조기성은 라인 트레이싱으로 거부 5종 본문 0줄·정상 대조군 205줄, 변이 6/6
  검출, 보고서 2회 바이트 동일·`game_executions=0`. Fast 268, safety PASS, 게임 0회.
  신규 R19는 동작 결함이 아니라 회귀 내구성 결함으로 큐에 등록했다.
- lap245: R11 work — tests/test_review_probe_output.py에 exists()가 false인 dangling output
  symlink 배타 생성 거부를 고정했다. targeted 8 passed, Fast 269, safety PASS, 게임 0회.
  제출한 "변이 8 failed" 비공허성 증거는 lap246이 무효 판정했다.
- lap246: R11 middle 검수 — **회귀는 범위 승인, lap245 증거는 무효**. C0 실제 probe 8 passed,
  C1 변이 없는 lap245식 얕은 재배치 복사본도 동일한 8 failed(원인은 `parents[4]` IndexError로
  probe가 import 단계에서 사망), C2 깊이를 맞춘 미러 8 passed, C3 같은 미러의
  open("x")→open("w") 변이는 R11 **1건만** 죽이고 preflight 6건 생존. 직접 관측은 x=exit 2·
  target 미생성, w=exit 0·target 생성. Fast 269, safety PASS, 게임/Wine/Xvfb/PNG 0회.
  자체 하네스 결함 1건은 보고서 미생성 상태로 PROVENANCE 보존, SUT 무변경.
- lap247: R12 work — `_wait_state`가 selection `CORRUPTED`를 읽기 오류/커버리지 부족으로
  `UNAVAILABLE`에 덮어쓰지 않게 수리. 겹침 2-case targeted와 기존 경로 회귀 포함 4 passed,
  `make check` 271 passed, `CONTEXT_PASS`, safety PASS, 게임/Wine/Xvfb/PNG 0회.
- lap248: R12 middle 검수 **PASS/범위 승인** — C0 회귀 7 passed, C1 계약 기대 모델 대조 81-case
  전수 불일치 0(CORRUPTED 보존 32건 provenance 유지, SOUND 강등 20건), C2 깊이 일치 무변이 미러
  M0 136 passed, C3 변이 M1 가드삭제=R12만 / M2 무조건보존=기존 UNAVAILABLE만 / M3 역전=양쪽.
  Fast 271, safety PASS, 게임 0회, SUT 무변경. 신규 R21(하네스 규약)만 큐에 올렸다.
- lap249: R13 work — PASS stage의 `read_coverage`를 stage record와 `input_checks` verdict에
  투영하고, transient read error 성공 반환의 기존 비대칭을 유지. 신규 회귀 1건 포함 21 targeted,
  `make check` 272 passed, `CONTEXT_PASS`, safety PASS, 게임/Wine/Xvfb/PNG 0회; middle 검수 전.
- latest work: `docs/history/laps/20260912_lap249_work_r13.md`.
- latest middle: `docs/history/laps/20260912_lap248_middle_r12_review.md`; probe/report
  `...probes/20260912_lap248_r12_review_probe.py`, `..._report.json`;
  attempt1 절단 사유 `..._report.PROVENANCE.md`.
- pre-compaction 원문: `docs/history/laps/20260912_status_lap237_compaction.md`.

## 바퀴 기록

- lap2~247과 STATUS 원문: `docs/history/laps/`; probe는 `docs/history/laps/probes/`.
- current escalation: `loop/ESCALATE_SOL`; handoff: `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md` (lap248 R12 검수).
