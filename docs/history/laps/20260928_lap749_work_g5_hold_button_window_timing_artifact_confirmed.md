# 2026-09-28 | lap 749 | 목표 G5 (홀드버튼 편차 원인 — 관측 윈도우 확장 재측정)

- 실제 provider/model/effort / 지정 역할: Claude Code Sonnet 5 / high / work tier(구현 실행).
  STATUS "다음 한 가지"(lap747/748이 남긴 유일한 미해결 항목)를 그대로 수행.
- 가설 / 사용자 관찰: lap747이 candidate v8 `hold_button`(툴바 홀드 버튼 클릭, `window=3.0`)을
  3회 측정해 `pending_changed_to` 0/50→50/50→3/50으로 요동을 관측(원본 20용량 3회는 20/20 고정,
  candidate 홀드 **단축키** `H`는 3회 전부 50/50 안정)했다. STATUS 다음 한 가지: `hold_button`의
  관측 윈도우를 늘려 candidate 재측정 2~3회로 "표본 편차(타이밍 아티팩트)"인지 "실제 미전달(회귀)"인지
  가른다 — 매번 50/50 도달하면 타이밍 아티팩트로 결론(회귀 아님), 여전히 요동하면 gdb로 근본 원인
  추적.
- 예상 PASS / FAIL 조건: candidate 3회 전부 `pending_changed_to`가 50/50에 도달하면 "타이밍 아티팩트,
  회귀 아님"으로 결론. 1회라도 50 미만이면 회귀 가능성이 남아 gdb 트레이스로 이관.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 전부 uncommitted(`LOOP_ALLOW_COMMITS=0`):
  - `tools/g5_command_coverage_probe.py`: `hold_button` step의 `observe` 윈도우를 `3.0`→`10.0`으로
    확장(1줄 값 변경 + 주석). 다른 step(`stop_button` 3.0, `patrol_button` 6.0 등)은 그대로 둠 — 이번
    조사 대상은 `hold_button`만이다. 제품 EXE/패치 코드는 0 변경(도구 코드만).
  - 신규 파일: `/tmp/lap749_v8_coverage_hold_driver.py`(저장소 밖, lap747의 `/tmp/lap747_v8_coverage_
    driver.py`와 동일 패턴 — `probe.g5 = v8`, `probe.TARGET_SHA = "ef46d1ac…"`만 교체하는 monkeypatch
    드라이버).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 불변(3회 실행 전부
  `source_unchanged=true`). 후보 v8 `ef46d1acd55af2f6007824bb416b3c991ae4afb195fb369b3e86b5ee9182ff08`
  (lap746/747과 동일, 이번 lap에서 패치 자체는 0 변경). 솔로 로비, worker(slot 1198) 앵커 7×8 dense
  fixture(55기 SEED_TYPE=2) — 기존 G5 coverage probe와 동일 protocol/fixture. candidate만 재측정(원본은
  lap747에서 이미 3회 20/20 고정 확인, 재실행 불필요로 판단).
- 실행 명령 / 로그 / 캡처 경로 및 해시: 3회 synchronous 격리 실행(`kill -0` 폴링으로 세션이 완주까지
  대기, 게임 사본은 완료 직후 삭제):
  - `PYTHONPATH=. python3 /tmp/lap749_v8_coverage_hold_driver.py --variant candidate --runtime-root
    local/runtime/lap749_v8_cov_hold_candidate{,2,3} --artifact-root .../temp/Syw2plus_patch/
    20260928_lap749_v8_coverage_hold/candidate{,2,3}` — 로그 `/tmp/lap749_v8_coverage_hold_candidate{,2,3}.log`.
  - 이어서 `make check`(`/tmp/lap749_make_check.log`), `checks/safety.sh check`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **candidate 3회 전부 `hold_button` `pending_changed_to`
  = `{"0x1000027": 50}`(50/50), `alive_after=true`, `source_unchanged=true`, private_exe SHA v8 고정값과
  일치.** curve 상세(3회차)를 보면 목표값 `0x1000027`이 클릭 직후 딱 한 샘플(`t=0.051`, 10ms 간격 샘플
  구간)에서만 나타나고 바로 다음 샘플(`t=0.102`)부터 처리 완료 상태 `0x1000001`로 정착한다 — 즉 홀드
  명령의 pending 표식 자체는 매우 짧게(한 tick 내외) 나타났다 사라지는 진짜 transient 값이며, 이전
  window=3.0 측정에서 0/50·3/50이 나온 것은 **50기 규모에서 이 transient가 여러 차례(청크 단위로 추정)
  재발행되며 완결되기까지 걸리는 총 시간이 클릭 시점의 시스템/Wine 스케줄링 지연에 따라 3초 안에
  못 끝나는 경우가 있었기 때문**으로 설명된다(윈도우 10초로 늘리자 3/3 모두 전부 반영). **결론:
  운영자가 정의한 판정 기준("매번 50/50 도달하면 타이밍 아티팩트")을 충족 — 홀드 버튼 편차는
  **타이밍/관측 윈도우 아티팩트이며 v8의 실제 명령 회귀가 아니다.** `make check` **1115 passed,
  5 skipped(759.22s)**, ruff/compileall/mypy 전부 PASS, `checks/context_limits.py` `CONTEXT_PASS`,
  `checks/safety.sh check` `SAFETY_PASS`. 게임 실행 3회 전부 `source_unchanged=true`, 크래시 0.
  디스크: 게임 사본(각 1.4GB) 3회 실행 직후 삭제, 종료 시 116G 여유.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 제품 코드/EXE 0 변경(도구 코드 `hold_button`
  관측 윈도우 1줄만 변경, 회귀 검사 아님). 이 결론으로 **G5 체크리스트 (F) v8 최종 재검수를 막던
  마지막 미해결 항목이 해소됐다** — S3(lap748, 대체 경로 PASS)와 홀드버튼(이번 lap, 타이밍 아티팩트
  확정) 둘 다 처리 완료. 남은 절차는 middle(Opus5/high)이 v8 기준 A~H 전체를 최종 재검수하고, 그
  결과를 사용자에게 milestone 재상정하는 것 — 이번 work tier는 그 재검수를 대신하지 않는다(역할
  경계). 사용자 milestone 여전히 없음. `LOOP_ALLOW_COMMITS=0`이라 전부 uncommitted, 파일 해시는
  probe-result.json(`.../20260928_lap749_v8_coverage_hold/candidate{,2,3}/probe-result.json`)에 보존.
- 다음 한 가지: middle(Opus5/high)이 v8 기준 G5 체크리스트 A~H 전체 독립 최종 재검수를 수행 —
  (F) v8 raw(lap746 원본/v7/v8 3세트 + lap748 S4/S5 + 이번 lap 홀드버튼 3회) 재계산, `make check`/
  `SAFETY_PASS` 확인 → PASS면 middle이 사용자 milestone 재상정 여부를 판단.
