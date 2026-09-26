# 2026-09-11 | lap 58 | 목표 G1-A alternate UI-list raw snapshot

- 실제 provider/model/effort / 지정 역할: 사용자 지정 실무 Codex `gpt-5.6-luna` / high / hands-on work.
  현재 세션 표면은 실제 model ID/effort를 별도 노출하지 않아 실행 증거로 주장하지 않는다.
- 가설 / 사용자 관찰: lap57이 확인한 stable-ineligible type58/slot1199는 `0x0049B6D0` group2..5
  대상이 아니므로, false branch의 alternate count/records/flags/geometry를 보존하면 화면 icon과
  production action을 섞지 않고 다음 Sol 검수가 가능한 raw 근거를 만들 수 있다.
- 예상 PASS / FAIL 조건: original SHA gate를 유지하고 `unit+0x6BE` count, 첫10 records
  `unit+0x6C2+4*i`, flags `0x00893118+2*i`, geometry `0x009E2BA4..AA`를 범위 고정으로
  캡처한다. count>10, 선택 identity 변화, alternate 값 변화는 증거를 붙여 fail-closed한다.
  stable-ineligible는 즉시 FAIL이며 production PASS가 아니다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `tools/runtime_env.py` (`e605e041816856bc88458df8bfad85e2e77cdac40f4ba6cab1e6e7d4e3d32dd5`),
  `tests/test_runtime_env.py` (`58ea272f06d78f1edc672d4f569d7a7e3bd6ea0d644f3b68d6a6bd06931e024c`).
  runtime helper에 alternate raw block decoder와 before/after coherence evidence를 추가했고,
  tests에는 zero/nonzero, count bound, value change 및 기존 identity 회귀를 추가했다.
  `tests/test_runtime_guards.py`와 원본/참고 EXE/DLL/assets는 변경하지 않았다. Git unborn,
  `LOOP_ALLOW_COMMITS=0`, commit/push 없음.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 SHA
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 유지, 후보 EXE 없음.
  새 Wine/Xvfb/game run 없음. fixture는 virtual read-memory로 selected slot7/type58,
  stable false-branch predicate, count 0 또는 3, 첫10 WORD쌍/flag10개/geometry4개와
  pool 전후 alternate value change를 명시했다.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `.venv/bin/python -m pytest -q tests/test_runtime_env.py
  tests/test_runtime_guards.py` → **46 passed**; `make check` → **116 passed**, Ruff/
  compileall/mypy/context PASS; `bash checks/safety.sh check` → `SAFETY_PASS`.
  binary patch generation/restore와 real runtime/24k/144k 실행은 N/A/SKIP이며 새 캡처 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): helper/test contract **PASS**. stable-ineligible
  evidence는 alternate snapshot before/after와 raw_hex, addresses, values를 보존하고 즉시
  `49B6D0 ineligible` FAIL로 끝난다. count=11은 bounds FAIL, before/after record 값 변화는
  coherence FAIL이다. G1 실제1600×1200 제품 입력/생산, G2~G4 및 사용자 승인은 UNKNOWN/
  미완료.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: eligible group2..5 경로의 기존 fixture와
  전체 Fast 회귀는 통과했다. alternate list 값의 실제 의미와 worker production callback 연결은
  아직 UNKNOWN이며 raw 계측만으로 제품 기능을 승인하지 않는다. 다음 Sol/high 독립 검수와
  사용자 승인은 없음.
- 다음 한 가지: 새 Codex `gpt-5.6-sol`/high middle이 lap58 source SHA, address/width/
  bounds, before/after snapshot 및 46/116 회귀를 독립 검수하고 alternate list의 다음 좁은
  runtime probe 허용 여부만 판정한다. 그 전에는 새 game run, 좌표/timeout/binary 변경 금지.
