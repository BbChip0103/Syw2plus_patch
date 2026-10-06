# 2026-09-28 | lap 726 | 목표 G5

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5`, 실무(work, 구현·실행).
- 가설 / 사용자 관찰: 2026-09-28 03:36 운영자 판정의 (B) 잔여 항목 중 **Shift+클릭 제거**(이미 선택된
  유닛을 Shift+클릭하면 선택에서만 제거되고 나머지 선택·이후 명령 전달은 유지)와 **51번째 유닛 드래그
  거부**(55기+일꾼 pool 56에서 v5 후보는 정확히 50만, 원본은 정확히 20만 선택)가 v5에서도 성립한다는
  가설. 제거 코드 경로(`DIRECT_SITES`의 제거 함수 `0x412e9f..0x412efc`)는 lap720/721/723이 이미
  사망-기반 제거로 구조를 확정했으므로(zero-fill, 압축 없음), 플레이어 조작(Shift+클릭)이 같은 경로를
  타면 라이브로도 누출 없이 동작해야 한다는 경험적 연결.
- 예상 PASS / FAIL 조건: PASS = ① 이미 선택된 유닛A를 Shift+클릭하면 A가 선택에서 빠지고 다른 선택
  유닛B는 유지, 그 뒤 이동 명령이 B에게만 가고 A는 받지 않음(원본·v5 둘 다). ② 55+1=56 pool에서
  일반 드래그 시 원본=20/20, v5=50/50 선택(51번째=이후 거부). 크래시 0, `source_unchanged` true,
  cleanup 정상, `make check`/`SAFETY_PASS` 유지.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  - `tools/g5_command_coverage_probe.py`: 기존 modifier 테스트 루프(라인 536~565, ALT/Ctrl/Shift
    드래그·클릭 — lap717/723/724가 이미 검증) 바로 뒤에 새 블록 2개를 추가했다. 제품 EXE/원본 무접촉,
    이 파일을 참조하는 pytest 없음(lap724가 이미 확인한 사실 재확인, `grep` 결과 동일).
    1. **Shift 토글-제거 블록**: 서로 다른 두 유닛(anchor1/anchor2)을 Shift+클릭으로 순서대로 선택 →
       `record("shift_toggle_before_remove")` → anchor1을 Shift+클릭으로 다시 클릭 →
       `record("shift_toggle_after_remove")` → `mods["shift_toggle_removed_anchor1"]`
       (before에 있고 after에 없음)·`mods["shift_toggle_kept_anchor2"]`
       (after에 anchor2 있음)·`mods["shift_toggle_count_delta"]`를 계산. 이어서 `step()`(내부에서
       전체 드래그로 재선택함)을 쓰지 않고 `observe(pid, [anchor1, anchor2], ...)`를 **직접** 호출해
       toggle 직후 선택 상태 그대로 지면 이동 클릭을 보낸다 — `step()`을 썼다면 `reselect()`가 즉시
       50/20기 전체를 다시 뽑아버려 "제거된 유닛이 명령을 못 받는지"를 가릴 수 없었다(1차 시도에서
       실제로 이 실수를 했고, `command_changed_to={'3': 50}`이 나와 즉시 재설계). 결과는
       `mods["shift_toggle_anchor1_excluded_from_move"]`(관찰한 2슬롯 중 정확히 1개만 command 3으로
       바뀌었는지)에 기록.
    2. **51번째 거부 요약 블록**: 이미 기록된 `plain_fulldrag`(무수정 전체 드래그, 기존 modifier 루프의
       plain 반복)의 count/unique를 `SEED_COUNT`(55, `g5_candidate_drag_probe.py`에서 import 추가)와
       `sel_cap`에 대조해 `result["fifty_first_rejection"]`(fixture_total/pool_total_with_worker/
       selected_count/selected_unique/capacity/matches_capacity)로 명시적 판정 필드를 만든다.
    수정 후 SHA256 `709724bb9e3c18ccbdb1bfe1571e711c6d134357e771c1640d9ee338836105d9`.
  - 신규 파일 없음. 임시 monkeypatch 드라이버 `/tmp/lap726_v5_coverage_driver.py`(lap724 드라이버를
    그대로 복사, v5 `g5`/`TARGET_SHA` 교체만 — 제품/저장소 파일 아님, 사본을 아래 temp 경로에 보존,
    SHA256 `b7e6ba3bb4d4a1d4c135af1946e9720248876b0e1d3f8a3c2085319d8a62c9d8`).
  - 커밋 없음(uncommitted, `LOOP_ALLOW_COMMITS=0`).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(양 실행 전후
  `source_unchanged=true`). v5 후보 `29e61074c622c77debb5053a412e3337fc8100f1eda29bd68efb163b1a9ee146`
  (lap723/724/725와 동일, 독립 재빌드로 재확인). 격리 Wine/Xvfb 1600×1200, PS3 solo, owner0 dense
  fixture worker(slot1198) 앵커 7×8 grid 55기 SEED_TYPE=2(+일꾼 1기, pool 56). 소스
  `[ESL]Syw2plus`(SHA 위와 동일).
- 실행 명령 / 로그 / 캡처 경로 및 해시: 전체 artifact는
  `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260928_lap726_v5_shift_toggle_coverage/`
  {coverage-candidate(1차, 설계 결함 있던 시도 — 보존만), coverage-candidate-r2(수정 후, 채택),
  coverage-original}/.
  1. `PYTHONPATH=. .venv/bin/python /tmp/lap726_v5_coverage_driver.py candidate local/runtime/lap726_v5_cov_candidate .../coverage-candidate` → `COMPLETE`이나 `move_after_shift_toggle`이 `step()`으로 재선택해 무의미(설계 결함 발견, 즉시 파일 수정).
  2. 파일 수정 후 `... candidate local/runtime/lap726_v5_cov_candidate_r2 .../coverage-candidate-r2` → `COMPLETE`. 결과 JSON SHA256 `692a42ca941138f1c00e1c12d7ab0b9b137b55e5ff19375114e8c73b92cb3087`.
  3. `... original local/runtime/lap726_v5_cov_original .../coverage-original` → `COMPLETE`. 결과 JSON SHA256 `195dc629747ff93d65f23d90122763eddc8bc86af563b00e36e002c9ea9ad4ae`.
  4. `PYTHONPATH=. .venv/bin/python -m pytest -q patches/selection/ tests/test_g5_candidate_drag_probe.py tests/test_g5_command_packer_xrefs.py tests/test_g5_stock_selection_array_xrefs.py` → `44 passed`.
  5. `make check`(foreground nohup, 로그 `logs/gates/20260928_lap726_make_check.log`), `bash checks/safety.sh check`.
  6. 각 run 뒤 `local/runtime/lap726_v5_cov_*/*/game`(약 600~810MB) 삭제, output/manifest/prefix/log는 보존(디스크 위생).
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  1. **Shift+클릭 제거 = PASS(원본·v5 둘 다, raw).**
     - v5(r2): `shift_toggle_before_remove` slots=[1195,1148](anchor1=1195,anchor2=1148) →
       `shift_toggle_after_remove` slots=[1148]. `removed_anchor1=True`, `kept_anchor2=True`,
       `count_delta=1`. 직접 관찰(`observe`, reselect 없이): `command_changed_to={'3': 1}`
       (관찰한 2슬롯 중 정확히 1개, 즉 살아남은 anchor2만 이동 명령 수신) →
       `shift_toggle_anchor1_excluded_from_move=True`. curve 확인: t=0.05s에 1개만 command 3으로
       전환, 도착(t≈2.0s) 후 둘 다 command 1로 복귀 — anchor1은 관찰창 내내 command 3을 한 번도
       보이지 않음.
     - 원본: `shift_toggle_before_remove` count=**3**(slots=[1179,1195,1189]) — 이는 이 세션에서
       앞선 기존 modifier 루프의 `shift_click_unit` 단일클릭이 이미 같은 좌표에서 겹친 스프라이트
       2기(1179,1195)를 동시에 선택했던 것과 일치하는 fixture 밀집 아티팩트이며(원본 800×600 렌더에서
       인접 그리드 셀 스프라이트가 화면상 겹침), 이번 Shift 토글 메커니즘 자체와 무관하다(제거 대상을
       클릭 위치가 아니라 "이전에 선택된 특정 슬롯"으로 특정하는 별개 판정식으로 확인).
       `shift_toggle_after_remove` slots=[1179,1189] → **anchor1(1195)만 정확히 제거되고 겹쳐 있던
       1179와 anchor2(1189)는 그대로 유지** — `removed_anchor1=True`, `kept_anchor2=True`,
       `count_delta=1`. 직접 관찰도 v5와 동일 패턴: `command_changed_to={'3': 1}` →
       `shift_toggle_anchor1_excluded_from_move=True`.
     - 원본·v5 모두 크래시 없음, `alive_after` true.
  2. **51번째(21번째) 거부 = PASS(원본·v5 둘 다).** `fifty_first_rejection`: v5 `{fixture_total:55,
     pool_total_with_worker:56, selected_count:50, selected_unique:50, capacity:50,
     matches_capacity:true}`; 원본 `{..., selected_count:20, selected_unique:20, capacity:20,
     matches_capacity:true}`. 56기 pool에서 원본은 정확히 20, v5는 정확히 50만 선택 — 상한 밖 유닛은
     드래그로 선택되지 않는다(51/21번째 거부).
  3. 크래시 0(2/2 성공 run, 1차 시도의 설계 결함 run 포함 3/3 프로세스 정상 종료),
     `source_unchanged=true`(2/2), `cleanup.prefix_processes_after=[]`(2/2, 고아 없음).
  4. `make check` **1106 passed(787.21s)**, ruff/compileall/mypy/`CONTEXT_PASS` 전부 PASS,
     `SAFETY_PASS`. 신규 pytest 0개(이번 lap은 probe 도구 확장 + 라이브 측정, 제품 코드 무변경이므로
     패치 회귀 스위트는 44 passed 그대로).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  - 1차 시도(`coverage-candidate/`)는 `step()`이 매번 전체 재선택(`reselect()`)을 하는 것을 놓쳐
    "toggle 직후 명령이 제거된 유닛까지 다시 받는" 무의미한 결과(`command_changed_to={'3': 50}`)를
    냈다 — 같은 lap 안에서 원인을 파악하고 `observe()` 직접 호출로 재설계, 재실행해 해소했다(자체
    발견·자체 수정, 제품 코드 무관, 보존만 하고 삭제하지 않음).
  - 원본 run에서 관찰된 "Shift+클릭 1회가 겹친 스프라이트 2기를 동시에 선택"은 이 그리드 fixture의
    밀집도 아티팩트로 기록만 하고 조사하지 않는다(원본에도 나타나는 현상이므로 회귀 아님, 후순위).
  - (B)의 나머지 항목 — **ALT/Ctrl "같은 종류 전체 선택"(모디파이드 클릭으로 화면상 같은 타입 전체
    선택), 더블클릭 같은 종류 전체 선택, 포트레이트 클릭 해제** — 은 이번 lap에서 다루지 않았다.
    포트레이트 클릭 해제는 다중 선택 시 초상화 행의 화면 좌표가 아직 특정되지 않아 캡처 기반 좌표
    발견이 먼저 필요하다(더블클릭·ALT/Ctrl-클릭도 이 게임에 그 메커니즘이 실제로 존재하는지부터
    라이브로 확인 필요 — 원본 20/후보 50 paired로).
  - 독립 검수: 아직 없음(work tier 산출, 운영자 판단에 따라 middle은 체크리스트 전체가 채워진 뒤
    한 번에 진행하기로 함, 2026-09-28 03:36 판정 유지).
  - 사용자 승인: 없음(G5 확정은 체크리스트 A~H 완료 후).
- 다음 한 가지: (B) 잔여 — 더블클릭 같은 종류 전체 선택(라이브로 먼저 "이 게임이 더블클릭 select-type을
  지원하는가"부터 확인) → 지원하면 원본 20/후보 50 paired, 지원 안 하면 그 사실을 기록하고 다음 항목.
  이어서 ALT/Ctrl-클릭 같은 종류 선택(같은 방식), 포트레이트 클릭 해제(다중 선택 캡처로 초상화 행
  좌표 먼저 특정). 셋 다 끝나면 (C) 명령 전부로 진행.
