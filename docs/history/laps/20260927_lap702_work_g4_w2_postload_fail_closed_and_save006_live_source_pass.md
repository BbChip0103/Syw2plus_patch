# 2026-09-27 | lap 702 | 목표 G4

- 실제 provider/model/effort / 지정 역할: Claude Code claude-sonnet-5 / high / work(실무).
- 가설 / 사용자 관찰: lap701 middle이 `BLOCKED(postload_contract:marker_source_absent)`로 홀드하고
  다음 한 가지를 지정했다: ① `_g4_postload_contract`를 fail-closed로 보강(marker
  `full_id!=0`·`slot!=0`·`(full_id&0xffff)==slot`, 첫 row `source.live is True` 아니면 FAIL),
  ② `g1_s1_original_load_evidence`에 옵트인 fixture 선택(기본 save000 불변, `--g4-exact-postload`
  전용)을 추가해 pinned `save006.dat`(slot 7)로 fresh 실행, ③ save006도 무유닛이면 반복 금지·raw
  보존 후 다음 middle 판정. 가설: save000의 tick `(50590+1)&7=7`이 결정적으로 owner7(무유닛)을
  가리키는 것과 달리 save006(~600유닛, 8인 활성)은 next_owner에 살아있는 유닛이 있을 것이다.
- 예상 PASS / FAIL 조건: (a) 신규 fail-closed 체크가 run3류 전부-0 fixture를 FAIL시키고 기존 PASS
  fixture는 유지해야 한다. (b) save006 fresh 실행이 `EXACT_POSTLOAD_EDGE_PASS` 7조건 + marker/첫 row
  source가 **실제 살아있는 유닛**(0이 아닌 full_id/slot, `live=true`)이어야 확정.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): uncommitted(LOOP_ALLOW_COMMITS=0).
  - `tools/runtime_env.py` SHA256 `d2b4b0ab0aaa04ef56ca4da2f7493287a3d2dff612b14009deb40b109c3108b4`
    (이전 `036c3672…81779`). 세 변경:
    1) `_g4_postload_contract`에 fail-closed 체크 추가: marker `source.full_id`/`slot`이 정수이고
       0이 아니며 `(full_id & 0xffff)==slot`, 첫 row `source.live is True` 아니면
       `RuntimeSafetyError("... source is absent ...")`. 0==0 공허 일치를 더 이상 PASS시키지 않는다.
    2) `g1_s1_original_load_evidence`에 `g4_load_fixture: str | None = None` 파라미터(옵트인,
       `g4_exact_postload` 필수, `s1.FIXTURES`에 pinned된 이름만 허용) 추가. 하드코딩된
       `selected_index=1`을 전부 `fixture_spec.selected_index`로 교체(4곳: evidence fixture dict,
       direct-pre 단언, load-trigger precondition, `s1.evaluate` 호출). CLI에
       `--g4-load-fixture`(choices=["save006.dat"]) 추가.
    3) **신규 `slot_navigation` 스테이지**: PS35 진입 시 selected WORD가 항상 1로
       하드초기화된다는 사실(`docs/history/laps/20260912_lap362_middle_s1_execution_envelope.md`
       §정적판정 `0x4D5CA0`)을 실측으로 재확인(1차 시도: 사본 save 디렉터리에서 save000.dat만
       제거해 "가장 낮은 번호가 기본 선택"을 가정 — **반증**, selected_index는 여전히 1). 2차
       가설(채택): PS35 도달 후 `fixture_spec.selected_index != 1`이면 `tools/x11_send_keys.py
       DOWN`을 보내고 `SELECTED_INDEX_ADDRESS`를 재읽어 목표값 도달을 확인하는 반복(최대
       `G1_S1_SLOT_NAV_MAX_PRESSES=12`회, 회당 5초 예산)을 `pre` 스냅샷 이전에 삽입. 좌표 추측
       없이 직접 읽기로 도달을 검증하므로 실패 시 raise, 성공 시 실측 시도횟수를 기록.
       `G1_S1_TOTAL_DEADLINE`(150s) 상수는 불변이며 이 스테이지는 `operation_deadline` 벽시계
       한도 안에서만 동작(옵트인 외 기본 save000 경로는 조건 `!= 1`이 거짓이라 완전히 건너뜀).
  - `tests/test_runtime_env.py` SHA256 `ac99d8f0e206a5534b48efd4f570f5b2b9c7b85d5f0ac2dee4ec732a9d6bbdaf`.
    기존 PASS/mismatch 픽스처의 `full_id`를 101→`0x10001`(하위16비트가 slot=1과 일치하도록,
    find_source 불변식 재현)로 교정하고 row source에 `"live": True` 추가. 신규
    `test_g4_exact_postload_provenance_rejects_absent_source`(run3류 전부-0 픽스처가 FAIL함을 고정,
    회귀 방지) 추가.
  - `tools/inmm_stub/ai_shadow.c`/`_inmm.dll`: 무변경(lap700 상태 그대로, SHA
    `252b1a06…b8ba5`/`4e5f64e5…a971f6` 유지, 재확인만).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본
  `Syw2plus_re/Syw2plus/syw2plus_original.exe` 재해시 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`
  실행 전/후 불변(직접 재확인). fixture `save006.dat`(3,437,942B, SHA
  `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064`, LEGACY_SOURCE
  `Syw2plus_re/Syw2plus/save/`에서 확인, 새 기본 `[ESL]Syw2plus/`엔 없음 — lap700과 동일 사유로
  `--source`에 LEGACY_SOURCE 명시). candidate 없음(read-only shadow, `candidate_present=false`).
  save006은 lap284/lap289 등에서 owner 히스토그램 `0:95,2:92,3:95,5:104,6:97,7:75`로 8인 중 6인이
  실제 유닛을 보유한 것으로 이미 알려져 있었다(owner1/4는 0) — 이번 fresh 실행에서 실제 next_owner가
  살아있는 owner였다.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  1. `.venv/bin/python -m pytest -q tests/test_runtime_env.py tests/test_g4_ai_shadow.py
     tests/test_s1_load_evidence.py` → 233 passed(2.05~2.26s, 코드 변경 전후 각 1회).
  2. run1(1차 가설, FALSIFIED): `.venv/bin/python tools/runtime_env.py
     g1-s1-original-load-evidence --source .../Syw2plus_re/Syw2plus --bridge
     tools/inmm_stub/_inmm.dll --g4-exact-postload --g4-load-fixture save006.dat`
     (당시 코드: sibling save 파일 삭제 방식) → run `20260927_045427_2614949_0`,
     `RuntimeSafetyError: S1 direct pre did not observe PS35/group0/slot7`(실제 관측
     `selected_index=1`). sibling 삭제 로직을 되돌리고 keyboard-nav로 교체.
  3. run2(2차 가설, PASS): 같은 커맨드, run `20260927_045937_2645001_0`. `slot_navigation`
     6회 DOWN으로 selected_index 1→7 실측 도달(각 시도 0.27s 간격), `status=PASS`,
     `classification=LOAD_RESTORED_PLAYER_STRUCTS`, `cleanup.ok=true`,
     `residue_pids=[]`, `g4_postload_wait={marker_count:1, postload_rows:22,
     min_rows_observed:true}`. Shadow jsonl SHA256
     `b19dfbbe3606a721bb1dfc895053504872c246a107f40f53dbcdb164d6680a09`(23행)를 별도
     스크립트로 `_g4_postload_contract(expected_run_id="20260927_045937_2645001_0")` 재평가
     (아래 측정값). `local/runtime/20260927_04{5427,5937}_*/game` 사본 삭제(디스크 위생, output/
     manifest/prefix/log는 보존).
  4. `make check` → **1027 passed(868.40s)**, ruff/compileall/mypy(0 issue, 10 files)/`CONTEXT_PASS`
     전부 PASS. 로그 `logs/gates/20260927_lap702_g4_w2_save006_make_check.log`.
  5. `bash checks/safety.sh check` → `SAFETY_PASS`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - 신규 fail-closed 유닛 테스트 4/4 PASS(기존 PASS/mismatch 유지, 신규 absent-source 케이스 FAIL 고정).
  - **run2 raw 재평가: `_g4_postload_contract` → `pass=true, marker_seq=1, first_seq=2`.**
    marker `source={full_id:983091, slot:51, owner:0, command:1, pending:1, pending_xy:0}`,
    `983091 & 0xffff = 51 = slot` 일치(불변식 충족, 공허 아님). 첫 post-load row
    `source={full_id:983091, slot:51, live:true, hp:900, command:1, pending:1, pending_xy:0,
    x:135, y:93}` — **실제 살아있는 유닛**(hp=900>0). 이는 lap701이 지적한 "0==0 공허 일치"가
    아니라 진짜 non-vacuous 일치다. **`EXACT_POSTLOAD_EDGE_PASS`(fail-closed 계약 기준, save006
    fixture) 최초 raw 달성 — G4 W2 load-boundary 계측 계약이 실질적으로 닫혔다고 판정할 근거.**
  - candidate_present=false 전 구간 유지(read-only shadow, AI 정책 비교는 여전히 별도 미착수 항목).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: `make check` 1027 passed, SAFETY_PASS, 코드
  경로 회귀 없음(기본 save000 경로는 `g4_load_fixture=None`이라 `slot_navigation`을 완전히
  건너뛰어 무변경). **독립 검수 없음** — 다음 middle이 (a) `_g4_postload_contract` 신규 체크의
  논리(불변식 `full_id&0xffff==slot`, `live is True`)를 코드 대조, (b) run2 jsonl
  (`b19dfbbe36…d09`)을 별도 파서로 재확인, (c) `slot_navigation`이 옵트인 경로에서만 실행되고
  기본 save000 플로우 산출물이 불변임(diff)을 확인해야 한다. 제품 G4 PASS·사용자 승인은 아직
  없음 — 이 lap이 닫은 것은 lap701이 요구한 fail-closed 계약과 그 계약 위에서의 최초
  non-vacuous PASS다. G4의 "AI 개선이 저장/로드 후 유지되는가" 자체는 candidate 정책이 없어
  여전히 미착수.
- 다음 한 가지: middle이 위 (a)(b)(c)를 독립 재확인하고, `EXACT_POSTLOAD_EDGE_PASS`(save006,
  non-vacuous)를 최종 확정할지 판정한다. 확정되면 G4 다음 단계(candidate AI 정책 설계, 또는
  `G4_REENTRY_ORIGINAL_AI_BASELINE_LAP612.md` 베이스라인 재개)를 middle/strategy가 정한다.
  `[ESL]Syw2plus/save/` 새 기본 경로에 save000/save006 fixture가 없는 문제(LEGACY_SOURCE 우회 중)는
  여전히 미결이며 G4 W2 이후 별도로 다뤄야 한다.
