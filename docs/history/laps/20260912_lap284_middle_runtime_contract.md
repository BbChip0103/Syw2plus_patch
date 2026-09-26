# 2026-09-12 | lap 284 | lap283 실행 계약 여섯 필수 입력 middle 판정

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high /
  middle tier(진단·계획·컨펌). 게임 구현 없음. 하위 모델·유료 세션·subagent 호출 없음.
- lap 출처: 사용자 첨부 runtime 표기는 283이나 `loop/.lap_counter`는 **284**였다.
  PROMPT 규칙대로 284를 사용했고 counter를 쓰거나 복원하지 않았다. `loop/STOP` 없음.
- 목표: `docs/STATUS.md`의 "다음 한 가지" — 새 middle이 lap283 실행 전 계약을 검수하고
  저장 fixture 하네스 work 범위를 확정한다.
- 가설: 계약의 여섯 필수 입력 중 미충족 항목은 문서 누락이 아니라 **저장소에 실제 근거가
  없기 때문**이며, 정적으로 채울 수 있는 것과 실행이 필요한 것을 분리하면 실행 예산 0으로도
  다음 측정 가능한 변경이 나온다.
- 예상 PASS/FAIL: 여섯 항목을 파일/필드 근거로 ACCEPT 또는 REJECT로 전부 판정하고,
  probe exit0/failures=[], `make check`/safety PASS, STATUS 130줄 이하·Blockers 1개,
  게임/Wine/Xvfb/Stage B 0, comparator/producer/PASS 규칙 무변경.

## 변경 파일

- `docs/work/active/G1_RUNTIME_CONTRACT_MIDDLE_LAP284.md` (신규 판정 문서)
- `docs/history/laps/probes/20260912_lap284_middle_runtime_contract_probe.py` (신규 probe)
- `docs/history/laps/20260912_status_lap284_compaction.md` (STATUS 원문 보존)
- `docs/STATUS.md` (121 → 113줄), `loop/ESCALATE_SOL`, 본 기록
- 신규 로그는 `logs/lap284/`. uncommitted, 커밋/푸시/배포/원본 변경 없음.
- 게임 코드·comparator·producer·회귀·테스트·하네스 **0바이트 변경**.

## 원본/후보 SHA·환경

- 원본 `Syw2plus/syw2plus_original.exe`
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 세션 전후 동일.
- 후보 SHA: N/A(생성 없음). 환경 Linux / `.venv` / 정적 objdump.
- 활성 인원·군대·생성/자원 fixture: N/A(게임 실행 0).
- 읽기 전용으로 연 fixture: `Syw2plus/save/save000.dat`, `save006.dat`,
  `local/fixtures/20260910/save011.dat`, `save012.dat` — 각 파일의 **앞 260바이트만** 읽었고
  쓰기·복사·이동은 없다. 게임/Wine/Xvfb/Stage B/원본 재실행/PNG 전부 0.

## 이전 바퀴(lap283) 검수

- lap283 기록의 파일 fingerprint **9/9 재계산 일치**(결정문서·STATUS·ESCALATE_SOL·
  `.omx/plans/…`·`logs/lap283/` 5종).
- lap282 probe `cdfa7c3c92…b42ae764`와 그 출력 `e0f07f3a…46f4be08`이 lap283 recheck 출력과
  바이트 동일. 기존 probe 재실행이며 새 독립 검수기를 만들지 않았다.
- 정정 1건(판정 불변): lap283 기록 **본문**의 recheck 출력 SHA가 62자로 잘려 있다
  (`…5d5d8c5e46f4be08`). 같은 기록의 fingerprint 절 값 `…5d5d8d8c5e46f4be08`이 실제 값이다.
- G3 초과 `0x1B5A4`를 이번 probe 자체 상수로 재계산해 일치.

## 실행 명령/수치

- `.venv/bin/python docs/history/laps/probes/20260912_lap284_middle_runtime_contract_probe.py`
  → `logs/lap284/runtime_contract_probe.json`, **exit 0, failures=[]**.
  - save entry `0x440C20` 페이로드 순서 **50개**: 스택 헤더 `0x40` → literal 17 →
    **map layer 28** → literal 3 → bulk `fwrite(0x892410,0xE397C)` → literal 1 → 로스터 `0x40F4B0`.
  - `map_bounds_precede_layers=true`, `bulk_follows_layers=true`,
    `fixed_bytes_before_first_layer=22978`, map block `0xB3DDA8`의 파일 오프셋 **70**.
  - 유도한 폭/높이 파일 오프셋 **210/212** 적용 결과: save000 180×180, save006 180×180,
    save011 100×100, save012 100×100 — 전부 선언 가드 `1..180` 안.
  - 같은 지도 쌍 크기 차이가 `0x758` 정수배: `save006-save000=344,040=183×0x758`,
    `save012-save011=3,760=2×0x758`. 다른 지도 쌍은 정수배 아님.
  - 하네스: `tools/runtime_env.py`의 save 파일 참조 **0**, PS35 참조 **0**,
    대기 PS `[3,5,7,9]`, `g1_baseline` timeout 상한 **90초**.
  - tick `0x008924B8`은 bulk 블록 `+0xA8`. 과거 PS3 도달 run 8건의 `scene.tick`은
    **6이 7건 / 7이 1건**, 소요 8.4~19.1초(실패 run은 90초 상한).
- `make check` → `logs/lap284/make-check-before.log`, **292 passed in 44.47s**,
  Ruff All checks passed, compileall, mypy 10 files Success, `CONTEXT_PASS`.
- `LOOP_DRY_RUN=0 bash checks/safety.sh check` → `logs/lap284/safety.log`, **SAFETY_PASS**.
- 문서 변경 후 `make check` 재실행 → `logs/lap284/make-check-after.log`.
- 필수 게이트 예상 밖 실패 없음. 재시도 없음.

## 판정 (PASS/FAIL/SKIP)

여섯 필수 입력: **ACCEPT 1 / ACCEPT-WITH-CONDITION 1 / REJECT 4.**

| 항목 | 판정 | 핵심 근거 |
|---|---|---|
| 1 fixture 선택 | REJECT | 파일·SHA·`prepare()` 복사 경로는 확정. 로드 메뉴 좌표와 PS 전이 근거 0 |
| 2 하네스 연결 | REJECT | 하네스에 저장 로드 경로 0줄, 수정 대상 미지정, PASS 규칙 계열 충돌 |
| 3 측정식 | ACCEPT | lap277 §3 (A)+(B)와 §3.1을 변경 없이 유효화 |
| 4 tick | REJECT | 허용오차 근거 미제출. 순환 의존 명문화, 상위 결재 대상 |
| 5 실행 봉투 | REJECT | 복사/prefix/해시/90초 상한은 있으나 로드 명령·수집·예산 5건 누락 |
| 6 실패 보존 | ACCEPT-WITH-CONDITION | 기존 기구 충족. PS35 도달·PS3 미도달 실패 모드 선언 필요 |

**결론: runtime 예산 요청 없음(원본↔원본 1쌍도 요청하지 않음), Stage B 0 유지.**
제품 G1 합격·마일스톤 종료·G2~G4 전환 아님. `make check` PASS는 계획 승인도 제품 검증도 아니다.

## fixture / 한계

- fixture는 선택하지 않았다. 잠정 선호는 save000(같은 180×180 지도에서 레코드 183개 적음)이나
  절대 유닛 수·nation 구성이 나오기 전에는 확정하지 않는다.
- §2.1의 폭/높이 오프셋 210/212는 **유도된 가설이며 네 파일에서 가드 범위 안으로 읽혔다는
  것까지가 근거**다. 저장 포맷 전체가 확인됐다는 주장이 아니다.
- 28개 layer의 레이어별 원소 수 동일성은 여전히 미검증이다.
- 계약의 fixture 열거가 save011/012를 빠뜨린 사실을 기록했으나 후보를 넓히지 않았다.

## 회귀/남은 위험

S1/F2-R2 실제 결정성, 로드 메뉴 좌표, tick 순환 의존, R6-B-R2, WM_CLOSE, R17,
나머지 offline 8건, G2~G4, G3 저장 포맷 `0x1B5A4` 초과는 전부 미결이다.
implementation-unchanged 상태를 구현 진척으로 세지 않는다. 이번 바퀴는 서술만이 아니라
새 기계 근거(저장 파일 레이아웃 순서·유도 오프셋·크기 산술·하네스 공백 수치)를 남겼다.

## 다음 행동

현재 큐는 `docs/STATUS.md`만 사용한다. work tier 새 세션이
`docs/work/active/G1_RUNTIME_CONTRACT_MIDDLE_LAP284.md` §7의 offline 카드 한 장을 수행한다.
상위(Astra) 큐 3건은 같은 문서 §8이다. 마일스톤 이동/종결 없음. 자기 승인 없음.

## 파일 fingerprint

최종 파일과 로그의 SHA는 `logs/lap284/final_sha256.json`에 둔다(자기 참조 해시를 만들지 않음).
