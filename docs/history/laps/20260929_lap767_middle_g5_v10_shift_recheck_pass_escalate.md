# 2026-09-29 | lap 767 | 목표 G5 (middle: v10 Shift paired 독립 재검수)

- 실제 provider/model/effort / 지정 역할: Codex native session, middle(진단·계획·확인) 역할. 실제 served
  model ID는 이 surface가 노출하지 않아 `gpt-5.6-sol`이라고 주장하지 않는다. 게임 패치/제품 코드는 수정하지 않았다.
- 가설 / 사용자 관찰: lap765의 v10 Shift 단일 추가 `2→0`, 제거 `0→1`이 제품 회귀가 아니라 해당 실행의
  선택 상태/클릭 이상치라면, lap766의 같은 coverage 계약 원본20/v10 50 paired raw에서 두 후보가 같은
  anchor 전이를 보이고 현재 원본에서 v10 패치 안전성과 Fast가 다시 PASS한다.
- 예상 PASS / FAIL 조건: PASS = 양쪽 Shift 추가 `1→2`, 제거 `2→1`, anchor1 제거·anchor2 유지·anchor1
  명령 배제, 선택 상한 원본20/v10 50, raw SHA/fixture/후보 SHA 일치. FAIL/HOLD = 후보만 의미 지표가
  어긋나거나 현재 패치/Fast 검사가 실패. 마일스톤 경계면 기술 판정만 기록하고 `ESCALATE_SOL`로 넘긴다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 제품·패치·probe 0 변경. 이 기록과
  `docs/STATUS.md`, `docs/feedback/{INBOX,APPROVALS}.md`, `loop/ESCALATE_SOL`만 갱신. Fast 대상 validation
  fingerprint `767fe3f4bafc16d71af1058bd8a09ad83238ca90`, implementation fingerprint
  `29ca58a7109e9c6c175ac1b0169f0f714f811661`, HEAD `a944d6ca5e95f4b525a09d3cf882cf8d894356fc`,
  커밋 없음(`LOOP_ALLOW_COMMITS=0`).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; v10
  `c3ceaa25dea98232234759a332b867d92a669f63a03c3f453d3199cc329ebfad`. lap766 raw는 fresh private full
  copy/Wine prefix/Xvfb, PS3 solo owner0, synthetic type2 55기+worker slot1198, original20/v10 50 paired다.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `make doctor`; lap765/766 JSON `sha256sum`+`jq` 재계산;
  v1~v10 selection patch 집중 pytest; 임시 copy-only v10 build와 wrong-version/same-path 거부;
  `make check`; `checks/safety.sh check`. lap766 JSON SHA는 original
  `5e8f742d901a2332f57db3654823c9aff55f15eefda6922a9af099a4762deb7f`, candidate
  `813435cb69fdc9b52ac364441da9897af7ced48cac0b884587885ce162863bf4`. Fast 로그
  `logs/gates/full-test-20260929-lap767.output` SHA256
  `fd0fedb456a9835db00ca86de533a35a86621817cdb6a6359c65c061ef3b8ad6`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): raw 독립 재계산에서 original은 anchor `1195/1189`, v10은
  `1195/1171`; 양쪽 모두 Shift 추가 `1→2`, 제거 `2→1`, `removed=true`, `kept=true`, 명령 배제 true,
  full drag/51번째 상한 원본20·v10 50. lap765 raw는 첫 Shift 클릭부터 비anchor `1149`가 섞인 `2`였고
  다음 클릭에서 `0`이 되어 paired 정상 전이와 다르다. 따라서 재현되지 않은 단일 실행 이상치로 분류한다.
  패치 체인 59 passed; 원본 SHA/mtime 불변, candidate SHA 일치, wrong-version 출력 없음, same-path 거부,
  exact restore/unknown-byte 거부·허용 diff/non-overlap 테스트 PASS. `make check` 1134 passed·5 skipped
  (714.43s), ruff/compileall/mypy/context PASS; `SAFETY_PASS`. 최초 `.venv/bin/pytest` 명령은 실행 파일
  부재로 본문 전 실패했고, 같은 환경의 `.venv/bin/python -m pytest`로 실행 표면만 바로잡아 PASS했다.
  `make doctor`는 원본·도구를 PASS했지만 활성 runtime manifest 부재로 `runtime.ok=false`; runtime PASS로 쓰지 않는다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: Shift HOLD는 해소한다. v10 G5 2단은
  `PASS_WITH_LIMITS`(A/B/C/D/F/H PASS, E 조건부, G `BLOCKED(env)` 수용)로 사용자 3단 재상정 가능하다.
  진단 gate 미니맵은 정상 game_type UI 경로 미검증, 체력바 가림·기존 N/A/edge, 멀티 실동기화 미검증을
  유지한다. 이것은 제품 마일스톤 승인이나 G1 착수 승인이 아니다.
- 다음 한 가지: 마일스톤 경계이므로 승격 작업자가 이 판정·제한·후보 SHA를 확인해 사용자 G5 3단 판단에
  재상정한다. 사용자 승인 전 G5 종료·G1 재개 금지.
