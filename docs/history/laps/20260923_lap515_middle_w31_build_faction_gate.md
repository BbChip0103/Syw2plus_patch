# 2026-09-23 | lap 515 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5` / high, 지정 역할 middle(진단·계획·컨펌).
  게임 코드 hands-on 수정 0, 게임 실행 0, 커밋 0.
- 가설 / 사용자 관찰: STATUS「다음 한 가지」= 트랙②(2026-09-23 12:55 "27종 중 18종을 AI가 왜 안 짓는지") W31 카드 발행.
  카드 작성 전 표적을 바이트로 확인하다가 **전제 정정**: 건물 건설 결정은 `FUN_00406C70`(유닛 생산 추첨)이 아니라
  `FUN_0043E0E0`→`FUN_0043DBB0`이며, 18종 미건설은 진영 블록으로 설명된다는 가설을 세우고 정적 probe로 검증했다.
- 예상 PASS / FAIL 조건(착수 전 probe 머리말에 고정): A1 원본 SHA, A2 jump table 특수 kind {7,21,70,75},
  A3 블록 4집합(참고 저장소 표와 대조), A4 생산 건물 27종 서로소 분할, A5 N151 합집합=조선 생산 건물·미건설 18=타 진영,
  A6 fixture 전원 nation 1, A7 조선 천장 2,835·전65종 8,077 재현·단일 진영 천장 <5,000, A8 `FUN_0043DB00` 건물 게이트
  `+0x200E >= +0x2010/5`·typemax 비교 없음, A9 종별 한도 typemax×N/6(+typemax). 하나라도 실패하면 가설 기각.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 신규 probe
  `docs/history/laps/probes/20260923_lap515_middle_build_faction_gate.py`, 신규 근거
  `analysis/memory_maps/ai_build_faction_gate_0043dbb0_lap515_20260923.md`, 신규 카드
  `docs/work/active/G2_BUILD_PACE_STATE_PROBE_LAP515.md`(W31), 이 기록, STATUS, INBOX 진행 메모, `loop/ESCALATE_SOL` §73.
  제품 source(`patches/`) 변경 0. uncommitted.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 `b56986e0…a8ac`(probe A1). 후보 없음.
  런타임 값은 lap507 W29 원시(8 owner AI, `_custom_game_chain_inject_g2_eight_ai_d4a1_seed42`, 자원 각 1,000,000,
  cap 5,000, `+0x2010` 1,200, N=4001 후보 `a10024de…`) 재사용, lap513 원시(stock `+0x2010` 250) 건물 시계열 재사용.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `python3 docs/history/laps/probes/20260923_lap515_middle_build_faction_gate.py`
  exit 0, 2회 결정적 → `…/temp/Syw2plus_patch/g2_capacity/20260923_lap515_middle_build_faction_gate/build_faction_gate.json`
  SHA256 `7acf03c92ef0838728651608cf8db0e83992fe4418977232ffe7ea025f36cc69`. lap513 `samples.jsonl` `030f6a0e…` 재해시 일치.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): 단언 **18/18 PASS**.
  **N158** — 미건설 18종 = 일본 9 + 명 9, 18/18 `FACTION_BLOCK`. fixture 8 owner 721표본 전원 nation 1 ⇒ N151 "27종 중 9종"은
  "조선 생산 건물 9/9 전부"로 정정. **N159** — N152의 7종 경로는 3진영 혼합이라 단일 AI 불가(포획 제외). 단일 진영 유닛 천장
  조선 2,835·일본 2,527·명 2,715 전부 <5,000. **N160** — 건물도 `used`에 들어가고 건물 수는 고정 typemax로 막히지 않는다
  (한도 typemax×N/6, 전체 상한 `+0x2010/5`=240). 조선 5,000 = 건물 보급 ≥2,165 ≈160채. **N161** — lap513 원시에서 8 owner
  건물 수 종단 11~20·마지막 증가 tick 17,988~23,885 ⇒ 건설은 정지가 아니라 **느림**. `+0x1D8&2`·`+0x290==0xC` 의미는 추정.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: N158~N161은 이 lap 단독 관측 — 2단 독립 검수 없음(다음 middle 또는
  W31 검수 회차가 probe 재실행으로 확인). 참고 저장소는 읽기만 했다(`Syw2plus_re/analysis/memory_maps/ai_build_*`).
  Q8 선택지 전제가 바뀐다(자연 도달 = "레퍼토리" 아닌 "건설 속도" 문제). Q9·Q8·Q7-B·"8인" 정의 미결 불변.
- 다음 한 가지: work(Sonnet5)가 W31 M-0 정적 + M-1 24k 런타임 표본(포그라운드 동기 완주) → 라벨 판정.
- 검사(문서 갱신 후 동기 완주): `make check` exit 0 **819 passed**(520.44s)·ruff "All checks passed"·mypy 무이슈·`CONTEXT_PASS`,
  `checks/safety.sh check` `SAFETY_PASS`. 원본 SHA 종료 시 재확인 `b56986e0…a8ac`. STATUS 132줄 초과분은
  `docs/history/20260923_status_lap515_precompaction.md`(SHA `eee576e0…`, 132줄)에 전문 보존 후 lap510~511 블록 압축(117줄).
