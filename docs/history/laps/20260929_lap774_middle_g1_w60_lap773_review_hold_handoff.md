# 2026-09-29 | lap 774 | G1 W60 lap773 독립 검수와 work handoff

- 실제 provider/model/effort / 지정 역할: Codex native middle/high. 호출 표면은 실제 model ID를 노출하지
  않아 계약 지정 `gpt-5.6-sol/high`로 실행됐다고 단정하지 않으며, 다른 모델로 대체됐다는 주장도 하지 않는다.
- 가설 / 사용자 관찰: lap773 보존 raw를 독립 재계산하면 W60 후보 결함과 하네스 선행 실패를 구분하고,
  다음 work가 손댈 최소 범위를 확정할 수 있다.
- 예상 PASS / FAIL 조건: 원본 SHA·detour old bytes·lap773 source/raw 해시가 일치하고 메뉴/PS3 전환,
  primitive live metrics, same-frame oracle, gate=1 paired가 모두 raw로 판정 가능해야 PASS. 서술과 raw가
  충돌하거나 필수 지표가 없으면 `HOLD/BLOCKED` 후 work handoff.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 이 기록,
  `docs/STATUS.md`, `docs/feedback/APPROVALS.md`, `loop/ESCALATE_SOL`만 수정. 게임/bridge/하네스 source 0변경,
  커밋 없음(`LOOP_ALLOW_COMMITS=0`). lap773 source SHA 4건은 기록값과 재해시 일치.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` verified. lap773 bridge
  `d635e7c0…bbc`, 현재 in-tree build `76fe715c…9107c`; lap773 private 2-player random, synthetic=false,
  memory_writes=false. 이번 middle은 실패 runtime을 재시도하지 않고 보존 raw만 검수했다.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `make doctor` PASS; 원본 `objdump`로 `0x466D50`
  `83 ec 14 8b 54 24 1c`, `0x4664D0` `55 56 8b 74 24 10 8b e9` 일치; `jq -s` raw 재계산;
  `make check` **1144 passed, 5 skipped in 683.57s**, ruff/compileall/mypy/context PASS
  (`logs/gates/full-test-20260929-lap774b.output`, exit0); `make -C tools/inmm_stub` PASS.
  on raw `e4a8f2ce…6ea`, evidence `79132de6…763c`, verdict `03818723…034`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): 원본 old bytes PASS. on raw의 primary present 재계산은
  **PS3 `converted=1` 231회**(832x600→1600x1200, HRESULT0), 메뉴는 PS9 65·PS7 77·PS5 195회 모두
  `converted=0`(1600x1200 source, `src_rect=null`). 따라서 lap773/STATUS의 “PS3 converted=0”은 raw와
  충돌한다. `mirror2x_metrics`/summary 0건은 primitive call=0 증거가 아니라 minimap gate=0
  `FAIL_NO_EFFECT`가 clean finalization 전에 예외를 내 `trace_finalization=null`로 끝난 결과다.
  source/present dump·hash·nearest oracle 구현도 현재 source에 없다. 회귀 8개는 대부분 문자열 계약이라
  runtime patched bytes·byte-exact restore·sentinel 동작을 증명하지 않는다. **판정 `HOLD/BLOCKED(harness
  evidence conflict)`**.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: PS3 전환은 보존해야 하며 메뉴 peer/self-source 귀속,
  live metrics, same-frame oracle, gate=1 paired, runtime restore가 미검증이다. S1/S2·FEASIBLE·G1 완료·사용자
  승인은 모두 미통과.
- 다음 한 가지: `loop/ESCALATE_SOL`대로 work tier가 W60 전용 계측을 먼저 만들고 메뉴 source identity/rect를
  최소 수리한 뒤, gate=1 `(90,553)` off/on fresh paired를 실행해 새 middle에 넘긴다.
