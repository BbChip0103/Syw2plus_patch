# 2026-09-28 | lap 724 | 목표 G5

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5`, 실무(work, 구현·실행).
- 가설 / 사용자 관찰: 2026-09-28 02:35 운영자 지시 ① — lap723이 `g5_command_coverage_probe.py`의
  자체 목적지 캘리브레이션 실패(월드(93,56)에서 6개 후보 중 1개만 `move_ok`)로 v5 ALT/Ctrl/Shift
  드래그·공격·부대저장로드를 직접 재측정하지 못했다. 이번 lap의 가설: (1) 이 실패는 세션마다
  랜덤한 worker 스폰 월드((93,56) vs (10,49), 기존 lap 25회 관측상 대략 반반)와 그 월드의 자원
  밀집도 조합 문제이며, 캘리브레이션 후보 오프셋을 늘리면(특히 이미 성공한 방향으로 더 멀리)
  자원 밀집 월드에서도 견고해질 것이다. (2) v5는 `check_count` 게이트 외 v4와 byte-identical이라는
  lap723 pytest 근거가 맞다면, 직접 raw 재측정에서도 v4(lap717/718) 결과와 같은 패턴이 나와야 한다.
- 예상 PASS / FAIL 조건: 캘리브레이션 확장 후 `g5_command_coverage_probe.py`가 `COMPLETE`로 끝나고
  이동·정지·홀드·순찰(버튼+단축키)·ALT/Ctrl/Shift 드래그가 50/50이면 PASS. `g5_candidate_drag_probe.py
  --ui-roundtrip`의 7개 check 전부 True면 PASS. `g5_worker_relative_move_attack_probe.py`의 이동
  50/50·표적 uid 일치·`ever_command4_count`가 v3/v4 N=5 분포(24~65%) 안이면 PASS(v4 lap717/718과
  다른 패턴이면 v5 회귀 의심).
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  - `tools/g5_command_coverage_probe.py`: 목적지 검증 루프(라인 387 부근)에 12개 fallback 오프셋
    추가(이미 확인된 성공 방향 `(0,-4)`을 `(0,-6)/(0,-8)` 등으로 연장 + 8방향 보강). 다른 로직 무변경.
    이 도구는 제품 EXE를 만들지 않는 순수 probe 스크립트이며 SHA 고정 테스트 대상이 아니다(확인함,
    `grep`으로 이 파일을 참조하는 테스트 없음). 수정 후 SHA256
    `554bacae32937dd869e29983f29080a8dd342e9963b7459e374033a57167bbd7`.
  - 신규 파일 없음. `patches/selection/g5_selection_cap50_v5.py`/`g5_r3_death_bridge.c`는 lap723
    그대로(무수정, uncommitted 유지).
  - 임시 monkeypatch 드라이버(`/tmp/lap724_*.py`, 파일 3개) — 제품/저장소 파일 아님, lap682/684/717/723
    선례와 동일 방식(모듈 전역 `g5`/`TARGET_SHA`만 교체). 세션 종료 시 사라지므로 산출물과 함께
    공유 temp에 사본 보존(아래 경로).
  - 커밋 없음(uncommitted, `LOOP_ALLOW_COMMITS=0`).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(3회 실행 전후 `source_unchanged=
  true`). v5 후보 `29e61074c622c77debb5053a412e3337fc8100f1eda29bd68efb163b1a9ee146`(lap723과 동일,
  독립 재빌드 3회 결정론 일치). 격리 Wine/Xvfb 1600×1200, PS3 solo, owner0 dense fixture worker
  (slot1198) 앵커 7×8 grid 55기 SEED_TYPE=2. worker 스폰 월드: coverage run은 (10,49)(운 좋게 기존
  후보만으로 통과, 확장 오프셋은 미사용), roundtrip·attack run도 각각 자체 월드에서 정상 진행
  (기존 방식과 동일, 특이 로그 없음). coverage 소스는 `[ESL]Syw2plus`(SHA기준 원본), roundtrip·attack
  두 도구는 `source/ORIGINAL_EXE` 고정 파일명 제약으로 legacy 경로
  `Syw2plus_re/Syw2plus/syw2plus_original.exe`(SHA 위와 동일, 읽기 전용 확인) 사용(lap717 선례와 동일).
- 실행 명령 / 로그 / 캡처 경로 및 해시: 전체 artifact(JSON+캡처+로그+드라이버 스크립트 사본)는
  `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260928_lap724_v5_coverage_roundtrip_attack/`
  {coverage-candidate,roundtrip-candidate,attack-candidate}/.
  1. (수정 전) `/tmp/lap724_v5_coverage_driver.py candidate local/runtime/lap724_v5_cov …` → 목적지
     캘리브레이션 `ProbeError`(월드(93,56), 6후보 중 1개 `move_ok`) — 오프셋 확장의 근거가 된 raw.
  2. (수정 후, 동일 드라이버) 재실행 → `COMPLETE`(월드(10,49) 착지, 기존 7후보 중 2개로 충분).
  3. `/tmp/lap724_v5_roundtrip_driver.py`(`g5_candidate_drag_probe.py --ui-roundtrip`을 v5로
     monkeypatch) → `PASS_UI_ROUNDTRIP`.
  4. `/tmp/lap724_v5_attack_driver.py`(`g5_worker_relative_move_attack_probe.py`를 v5로 monkeypatch)
     → `CONVERGENCE_COMPLETE`.
  5. `make check`(포그라운드 nohup, 로그 `logs/gates/20260928_lap724_make_check.log`),
     `bash checks/safety.sh check`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  1. **캘리브레이션 근본원인 확인 = 자원 밀집 월드 문제(도구 결함 아님).** 수정 전 raw: 월드(93,56)에서
     6개 후보 중 5개가 채집(`0x1000008`), 1개만 이동(`0x1000003`) — fixture 무관, 그 월드 자체가 worker
     주변 채집지 밀도가 높음(lap723과 동일 재현). fallback 오프셋 추가는 방어적 수정이며 이번 run은
     실제로 세션이 (10,49)로 착지해 미사용됐다 — **다음에 (93,56)이 다시 걸리면 검증 필요(미확정)**.
  2. **v5 명령범위 = PASS(50/50 전항목, raw).** 이동(지면 우클릭) `pending_changed_to 0x1000003=50/50`,
     정지(버튼+`s`) `0x1000002=50/50`, 홀드(버튼+`h`) `0x1000027=50/50`, 순찰(버튼+`p`)
     `0x1000023=50/50`. 미니맵 우클릭은 `mm_inv=None`(원본도 무반응, 기존 관측과 동일 — 회귀 아님).
  3. **v5 ALT/Ctrl/Shift/plain 드래그 = PASS(50/50 raw, 최초 v5 직접측정).** `plain/alt/ctrl/shift_fulldrag`
     전부 `count=50, unique=50`. shift만 `kept_from_first=3`(누적 선택, 나머지 0 — 기존 선택 교체 동작과
     대비되는 올바른 shift 시맨틱). 소형 드래그·단일클릭·2차 modifier 클릭 계열도 크래시 없이 완료.
  4. **v5 부대지정+저장/로드 roundtrip = PASS(7/7 checks, 최초 v5 직접측정).** `selected_50`·
     `group_stored_stock20_plus_overflow49`(group1=20, 나머지 30은 `+0x344` 필드로 표현·overflow49는
     50중 49임을 확인)·`deselected`·`recalled_50`·`save_created`·`group_retained_after_load`·
     `recalled_50_after_load` 전부 `true`. lap717 v4 결과와 동일 패턴.
  5. **v5 공격 단일측정 = PASS(회귀 신호 없음, 최초 v5 직접측정).** 이동 `ever_matched_count=50/50,
     converged=true, converged_at_s=0.153`(v4 lap717의 0.15와 동일). `attack_capable_count=49/50`(worker
     제외), `pending_xy_match_count=49/49`, `observed_target_uids=[853107]`(표적 1기 정확 일치),
     `ever_command4_count=32/49`(65%) — lap688 v3 N=5 분포(27,30,32,33,49→중앙값32)와 lap718 v4
     N=5 분포(24,28,30,31,32→중앙값30)에 정확히 들어맞는다. `attack_pass`(순간피크 bool)=False는
     v3/v4에서도 흔한 표본잡음과 같은 패턴(단일 run이므로 N=5 반복은 이번 lap 예산상 생략).
  6. **크래시 0.** 3개 probe(coverage/roundtrip/attack) 전부 정상 종료, `source_unchanged=true`(3/3),
     candidate SHA 결정론 일치.
  7. `make check` **1106 passed(929.16s)**, ruff/mypy/`CONTEXT_PASS` 전부 PASS, `SAFETY_PASS`(신규
     테스트 0개 — 이번 lap은 probe 실행/도구 견고화만, 제품 코드 무변경).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  - **프로세스 위생 결함 발견(probe 도구, 제품 무관):** attack probe(run 4) 종료 후 JSON은
    `cleanup.xvfb_stopped=true`를 보고했지만 실제로는 `Xvfb :92`/`:93`(1600×1200, 이 run이 만든 것과
    동일 해상도, 시작시각 정확히 일치) **2개가 고아 프로세스로 남아 있었다** — 세션 안에서 발견해
    수동 `kill`로 정리했다(`wine`/prefix 프로세스는 0으로 정상 보고돼 실제 위험은 낮음). 원인
    미조사(다음 work 후순위 — `runtime_env._xvfb`/probe의 `finally` 블록이 재시도 시 첫 Xvfb를
    추적 못 하는 경로 의심). 이 lap 종료 시점 `wine`/`Xvfb 1600x1200` 프로세스 잔류 0(직접 확인).
  - coverage probe의 목적지 캘리브레이션 fallback 오프셋 추가는 이번 run에서 **실전 검증되지
    않았다**(우연히 (10,49) 착지) — (93,56) 재현 시 다음 lap이 실제로 2개 이상 `move_ok`를 찾는지
    확인 필요.
  - lap723이 "byte-identical이므로 이전됨"으로 추론했던 항목(ALT/Ctrl/Shift 드래그·공격·
    부대저장로드)이 이번 lap의 **직접 raw 측정으로 확정**됐다 — 추론 의존 제거.
  - R2(미측정 명령 버튼 opcode, lap719 후순위)·멀티 동기화 `UNKNOWN`은 여전히 미해결.
  - G5 완료 체크리스트(A)(정적 전수 표)·(B)(중간/뒤 엔트리 사망, lap723은 앞쪽만 실측)·(C)~(H)는
    이 lap에서 다루지 않음(다음 work).
  - 독립 검수: 아직 없음(work tier 산출, 다음 middle 요청).
  - 사용자 승인: 없음(v5 확정·G1 재개는 체크리스트 A~H 완료 후 사용자/운영자 판단).
- 다음 한 가지: middle(Opus) 독립 검수 요청 — ① 이 lap의 coverage/roundtrip/attack raw 3건이
  lap717(v4)과 같은 패턴임을 재계산 확인, ② coverage probe 오프셋 확장이 안전한 변경인지(제품
  코드 미접촉 확인), ③ Xvfb 고아 프로세스 발견을 안전 위험으로 볼지(제품 무관 판단 동의 여부).
  확정되면 다음 work는 체크리스트 **(A) 정적 전수 표**(`analysis/memory_maps/
  g5_selection_consumers_inventory_<date>.md`)와 **(B) 중간/뒤 엔트리 사망** 케이스(lap723은 앞쪽
  30기만 실측)로 진행.
