# 2026-09-28 | lap 743 | 목표 G5 ((G) BLOCKED 수용 → (H) 장시간 안정성)

- 실제 provider/model/effort / 지정 역할: Claude Code Sonnet 5 / high / work tier(구현 실행).
- 가설 / 사용자 관찰: lap742가 (G) 멀티를 `BLOCKED(env: native ipxwrapper crashes on room
  creation, wine9.0)`로 근본 원인까지 확정(Wine builtin `dplayx.dll`이 네이티브/빌트인 어느 쪽
  서비스 공급자를 써도 구조적으로 기능을 낼 수 없음)했고, 마지막 줄에 "이 판정을 (G)의 최종 답으로
  수용하고 (H) 장시간으로 넘어갈지"를 다음 판단으로 남겼다. 이 질문은 비가역(원본/참고 저장소 쓰기,
  커밋/푸시, 유료 세션, 제품 목표 변경)에 해당하지 않고 이미 가설 2회(원인 규명 + 조합 축소 실험)로
  결론이 난 절차적 판단이므로, 상시 지시("묻지 말고 결정", 2026-09-24)에 따라 이번 lap이 직접
  수용하고 STATUS가 지정한 다음 작업인 (H)로 진행했다. 가설: 기준 후보 v7로 50기를 드래그 선택한
  뒤 이동/정지/보류/순찰 명령을 반복 발행해도 수천 tick 동안 크래시나 선택 배열 손상 없이 안정적으로
  유지된다.
- 예상 PASS / FAIL 조건: 단일 격리 실행에서 v7 후보 50기 선택 → 이동(A)/정지/이동(B)/보류/순찰/정지
  6단 명령을 주기적으로 반복하며 목표 수천 tick(8000) 도달까지 매초 샘플링. PASS = 프로세스 생존,
  게임 tick이 목표까지 단조 증가, 매 샘플의 선택 count/unique가 50/50 유지(회귀 0), cleanup 정상,
  원본 SHA 불변. 크래시나 선택 손상이 1건이라도 있으면 FAIL.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 신규 저장소 파일 1개, uncommitted
  (`LOOP_ALLOW_COMMITS=0`): `tools/g5_long_run_stability_probe.py`(신규 진단 도구, 제품 코드
  0 변경). 기존 `tools/g5_candidate_drag_probe.py`·`tools/g5_command_coverage_probe.py`·
  `tools/g5_attack_move_broadcast_probe.py`의 검증된 헬퍼(선택 스냅샷, dense fixture, 목적지 검증,
  BUTTONS, MINIMAP_CLICK)를 그대로 재사용했다.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(`[ESL]Syw2plus/`, 실행 전후
  재확인 불변). 후보 v7 EXE `30efafa067b6cb524bd68594dedee4d0d4c68e1efef348e2f16c211dc8229bef`
  (lap740이 기록한 v7 후보 SHA와 완전 일치 — 빌드 재현성 확인). 솔로 로비, worker(slot 1198, type 7)
  앵커 7×8 dense fixture(55기 SEED_TYPE=2, +worker=56, 기존 G5 probe와 동일 fixture),
  드래그(200,170)→(730,445)로 50기 선택.
- 실행 명령 / 로그 / 캡처 경로 및 해시: 1회 synchronous 격리 실행(PID를 파일에 저장 후
  `kill -0` 폴링으로 완주까지 대기, 세션 종료 없음):
  `PYTHONPATH=. .venv/bin/python tools/g5_long_run_stability_probe.py --runtime-root
  local/runtime/lap743_g5_h_longrun --artifact-root
  ../../temp/Syw2plus_patch/20260928_lap743_g5_h_longrun/candidate` → `probe-result.json`
  (status `COMPLETE`). 캡처·JSON `../../temp/Syw2plus_patch/20260928_lap743_g5_h_longrun/candidate/`
  (progress 스크린샷 10장 + 00/01/99 경계 3장). 실행 직후 `game` 사본(810MB)만 삭제
  (output/manifest/prefix/로그는 `local/runtime/lap743_g5_h_longrun/`에 보존, 디스크 위생 준수).
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - **(H) 장시간 안정성: PASS.** `first_tick=251` → `last_tick=8270`, `ticks_observed=8019`
    (목표 8000 초과 달성, 실측 약 401초 벽시계 = 약 20 tick/s, lap168/G2 24k의 참고치 33.3 tick/s
    보다 이 환경에서는 다소 느렸으나 안정적).
  - `crash_detected=false`, `selection_regressions=0`(387개 샘플 전부 `selection_count=50`,
    `selection_unique=50`), 최종 선택 slots가 초기 선택 slots와 완전히 동일한 순서로 보존됨.
  - 78개 입력(move_a 13·stop 26·move_b 13·hold 13·patrol 13, 6단 주기 13회 반복)이 모두 전달됐고
    매 샘플 `moving_count=50`(선택 50기 전원이 매 순간 유효한 live command 상태를 가짐, 브로드캐스트
    경로가 수천 tick 뒤에도 여전히 50기 전원에 작동).
  - `cleanup.ok=true`(`prefix_processes_after=[]`, xvfb/children 정상 종료), `source_unchanged=true`.
  - `make check`(별도 실행, 아래) **1116 passed(862.74s)**, ruff/compileall/mypy(핀 파일 목록)
    전부 clean, `checks/context_limits.py` → `CONTEXT_PASS`, `checks/safety.sh check` →
    `SAFETY_PASS`. 신규 pytest 0개(진단 도구 1개만 추가, 제품 코드 무변경).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 이번 lap은 정보 제공용(work tier)이며 새 middle
  독립 검수 요청이 아니다 — 2026-09-28 03:36 운영자 판정에 따라 middle은 A~H 체크리스트 전체가
  채워진 뒤 한 번에 진행한다. **이로써 G5 체크리스트 A~H 전부(A~F 기존 완료, G=BLOCKED 확정,
  H=PASS)가 채워졌다.** 남은 위험: (H)는 사망/재생산/저장로드가 섞이지 않은 순수 명령 반복
  시나리오만 측정했다(체크리스트 (D)/(F)가 이미 그 조합을 각각 커버함). 장기 실행 중 8000 tick보다
  훨씬 긴(수만 tick) 구간에서의 메모리 누수 여부는 미측정(디자인 목표 "수천 tick" 범위 안에서는
  PASS). (G)는 여전히 `BLOCKED(env)`이며 사람 승인으로 대체되지 않는다.
- 다음 한 가지: middle(Opus5/Sol)이 A~H 전체를 한 번에 독립 재검수하고(2026-09-28 03:36 판정대로),
  그 뒤 G5 milestone을 사용자에게 재상정한다(멀티는 `BLOCKED`로 명시). 통과하면 G1(1600×1200 원본
  구성)이 그 다음이다.
