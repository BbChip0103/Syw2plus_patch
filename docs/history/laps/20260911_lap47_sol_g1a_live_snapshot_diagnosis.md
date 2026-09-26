# 2026-09-11 | lap 47 | 목표 G1-A live command-cell 독립 진단

- 실제 provider/model/effort / 지정 역할: 사용자 지정 Codex `gpt-5.6-sol`/high middle.
  현재 세션 표면은 실제 model ID/effort를 별도로 노출하지 않았다. 게임 코드·helper·tests·좌표·
  원본/후보는 수정하지 않았고 새 게임을 실행하지 않았다.
- 가설 / 사용자 관찰: lap46의 `groups 2..5 -> []`가 고정 원본 pool 주소/stride/layout 오류인지,
  아니면 helper가 frame 중 재구성되는 live pool을 읽는 전제와 진단 보존의 오류인지 독립 판정한다.
- 예상 PASS / FAIL 조건: lap46 SHA/artifact, 원본 SHA, allocator/초기화/선택 UI/생성 raw chain,
  helper read 호출 구조가 한 분류로 수렴하면 범위 판정 PASS. 충돌하거나 필수 gate가 실패하면 구현·
  재실행 없이 증거와 blocker를 보존한다.
- 변경 파일 / source fingerprint / 커밋: 구현 변경 없음. 진단 장부
  `analysis/memory_maps/player_offsets.md`, `docs/STATUS.md`, 본 이력, `loop/ESCALATE_SOL`만 갱신.
  검수 source SHA는 `tools/runtime_env.py`
  `9e82a19e2888c04701dca40baf22fa5391c13775e7e60b531671829342d84845`, tests
  `0d02e81cc50e230813c63e0b2275aa1988a2237b6499a91501130dff41e0df84`/
  `93e3af951805a773ddd298d1636db84304d2cd708218c9eb68f64bfa126ff8e3`다. Git unborn,
  `LOOP_ALLOW_COMMITS=0`, commit/push 없음. 검수 전 STATUS SHA `c283a589...`, 이전 handoff
  SHA `cd1718d3...`, map SHA `b2897bde...`다.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 읽기 전용 원본 및 lap46
  private copy SHA는 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`.
  새 후보/game/runtime fixture는 N/A. lap46의 기본 2인 random game, owner0/1 active2/2,
  PS3/tick6은 과거 실패 evidence로만 대조했다.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `sed`/`rg`/`jq`/`sha256sum`, 원본 `objdump -h` 및
  `objdump -d -Mintel`의 `0x41E60C`, `0x41FAC0..0x41FCC8`, `0x498EE0..0x499583`,
  `0x49B6D0..0x49B9E0`, `xxd`; 보존 `selection_after` PNG를 직접 확인했다. `make doctor`;
  targeted runtime/guard pytest; 사전·최종 safety; 최종 `make check`. 새 로그/PNG/game/patch 없음.
- 측정값 / 판정: lap46 manifest/verdict/full/input SHA가 기록과 일치하고 screenshot은 선택 HQ와
  command panel을 보인다. allocator는 first `0x00B38B5C`, stride `0x124`, exclusive bound
  `0x00B3AC70`, 즉 slot1..29다. 생성부는 allocator slot을 `0x00B38A38+slot*0x124`로 계산해
  group2..5를 만든다. 주소/stride/field는 **CONFIRMED**. `0x498F50`은 매 호출마다
  `0x498EE0→0x41FB60` reset 후 UI를 재구성하며 helper는 pool object를 분리 read하고 filter 전
  raw를 버린다. 따라서 **HARNESS LIVE-SNAPSHOT CONTRACT REVISE / GAME RUN BLOCKED**다.
  lap46이 reset window였는지 exact predicate mismatch였는지는 UNKNOWN이다. helper의 slot30 추가
  read는 경계 오류지만 유효 slot1..29를 누락하지 않아 `[]`의 단독 원인은 아니다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: doctor top-level `ok=true`, 원본 verified;
  targeted **36 passed**, 사전 safety **SAFETY_PASS**. 최종 gate 수치는 아래 후속 기록에 보존한다.
  patch가 없어 binary old/new/version reject/copy-only/non-overlap/restore는 SKIP. 기존 reader의
  executable SHA reject는 유지해야 한다. G1 제품/worker 의미/production/drag/minimap과 사용자
  승인은 미완료다. implementation-unchanged-streak=2라 추가 narrative run을 금지한다.
- 다음 한 가지: 새 Codex `gpt-5.6-luna`/high work가 source precondition을 확인한 뒤 유효 slot
  1..29의 contiguous pool snapshot 파서와 bounded empty→valid polling, 최종 실패 raw summary를
  최소 구현하고 직접 회귀/Fast/safety를 남긴다. 좌표/click/timeout/게임/EXE/DLL/assets는 변경·
  실행하지 않으며, 새 Sol/high 독립 확인 전 runtime 재실행을 금지한다.

## 최종 gate 후속 기록

- 편집 후 `docs/STATUS.md` line count: **54** (결과 기록 뒤 55).
- `make check`: **106 passed**, Ruff/compileall/mypy/context PASS.
- `bash checks/safety.sh check`: **SAFETY_PASS**.
